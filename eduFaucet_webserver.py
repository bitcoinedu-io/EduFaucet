#!/usr/bin/env python3

# Run via flask framework:
# pip3 install flask
# FLASK_APP=eduFaucet-webserver.py flask run

import sys
import requests
import json
import sqlite3
from flask import Flask, url_for, abort, request, redirect
from flask import render_template
import datetime
import time
import decimal
from eduFaucet_config import VERSION, GITHUB, DBFILE, URL, chaininfo, params

app = Flask(__name__)

print()
print('Using database file:', DBFILE)


# Given db cursor cur, fetch info to display on top
def latest_topinfo(cur):
    return {'version': VERSION, 'github': GITHUB}

def eduCall(method, *args):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": list(args),
    }
    return requests.post(URL, data=json.dumps(payload), headers=headers).json()['result']

def getLastTransactions(cur,numTrans):
    # Create the list of last numTrans transactions.
    res = cur.execute('SELECT * FROM eduAddress ORDER BY time DESC LIMIT ' + str(numTrans))

    info = []
    for item in res.fetchall():
      time = datetime.datetime.fromtimestamp(int(item[1]))
      temp = {'address': item[0], 'time': time, 'txid': item[2], 'amount': item[3]}
      info.append(temp)
    return info

############## main page is same as block list page
# startblock is the highest block number to display at the top

@app.route("/")
def faucet_page():
    con = sqlite3.connect(DBFILE)
    cur = con.cursor()

    topinfo = latest_topinfo(cur)
    info = getLastTransactions(cur,10)
    return render_template('faucet-page.html', chaininfo=chaininfo, topinfo=topinfo,
                           info=info)
   

@app.route("/payout/")
def payout():
    now = int(time.time())
    lastTime = 0
    err = 'Incorrect address format.'
    eduAddress = request.args.get('payout','').strip()

    con = sqlite3.connect(DBFILE)
    cur = con.cursor()
    topinfo = latest_topinfo(cur)
    info = getLastTransactions(cur,10)
    msg = 'An error occured when processing the request.'

    # Perform a quick invalidation, if it fails here we dont have to parse anything else
    if len(eduAddress) < 28:
        err = 'Incorrect address format.'
        return render_template('payout-fail.html', chaininfo=chaininfo, topinfo=topinfo, info=info, msg=msg, err=err)
   
    # AdB: Here we should check so the address really is correct

    
    # Here we should check so we didnt pay this eduAddress during the last hour.
    res = cur.execute('SELECT time FROM eduAddress WHERE address=?', (eduAddress,))
    try:
      lastTime = res.fetchone()[0]
    except TypeError:
      pass

    # So if we made a payout during the last hour lets send that message if not lets remove it
    if lastTime+3600 > now:
      msg = 'A donation was recently made to BTE address: ' + eduAddress
      nextTime = (lastTime+3600)*1000
      err = 'Try again in '
      return render_template('payout-fail.html', chaininfo=chaininfo, topinfo=topinfo, nextTime=nextTime, info=info, msg=msg, err=err)
    elif lastTime > 0:
      res = cur.execute('DELETE FROM eduAddress WHERE address=?', (eduAddress,))
      try:
        res.fetchone()[0]
      except TypeError:
        pass

    lastTime=0
    ipAddress = request.remote_addr
    # And check so we didnt pay to this ipAddress during the last hour.
    res = cur.execute('SELECT time FROM ipAddress WHERE address=?', (ipAddress,))
    try:
      lastTime = res.fetchone()[0]
    except TypeError:
      pass

    # So if we made a payout during the last hour lets send that message if not lets remove it
    if lastTime+3600 > now:
      msg = 'A donation request was recently made from a computer with this ip-address.'
      nextTime = (lastTime+3600)*1000
      err = 'Try again in <p id=\"time\"></p>.'
      return render_template('payout-fail.html', chaininfo=chaininfo, topinfo=topinfo, nextTime=nextTime, info=info, msg=msg, err=err)
    elif lastTime > 0:
      res = cur.execute('DELETE FROM ipAddress WHERE address=?', (ipAddress,))
      try:
        res.fetchone()[0]
      except TypeError:
        pass 


    # AdB: Create and send payment from bc1q62ys5jm0ay6adwxm2wz3zkxndk52st4uzaa6rg
    txid = eduCall('sendtoaddress',eduAddress,'4')

    # AdB: Add the payout to the database
    cur.execute('INSERT INTO eduAddress (address,time,txid, bte) VALUES (?,?,?,?)', (eduAddress, now, txid, 4))
    cur.execute('INSERT INTO ipAddress (address,time) VALUES (?,?)', (ipAddress, now))
    con.commit()

    return render_template('payout-complete.html', chaininfo=chaininfo, topinfo=topinfo, info=info, eduAddress=eduAddress, err=txid)

