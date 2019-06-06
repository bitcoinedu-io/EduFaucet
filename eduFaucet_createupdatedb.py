#!/usr/bin/env python3
#
# chainview-createupdatedb.py
#
# Create or update chainview database based on existing version number

import sqlite3
from eduFaucet_config import DBFILE

print('Using database file:', DBFILE)

con = sqlite3.connect(DBFILE)
c = con.cursor()
ver = '0.0'
exists = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='version'")
if len(exists.fetchall()) > 0:
    print('Reading existing version...')
    # table exists, read version
    ver = c.execute('SELECT ver FROM version').fetchone()[0]

print('Database version:', ver)

if ver == '0.0':
    c.executescript("""
CREATE TABLE version (ver TEXT);

CREATE TABLE eduAddress (
    address TEXT PRIMARY KEY,
    time INTEGER,
    txid TEXT,
    bte INTEGER
);

CREATE TABLE ipAddress (
    address TEXT PRIMARY KEY,
    time INTEGER
);

INSERT INTO version VALUES ('1.0');
    """)
    print ('Created database v1.0!')
else:
    print('Already up to date. Doing nothing!')
