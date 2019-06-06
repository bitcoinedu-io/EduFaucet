# Common config for EduFaucet

VERSION = '1.0'
GITHUB = 'https://github.com/bitcoinedu-io/EduFaucet'

DBFILE = 'eduFaucet-db.sqlite3'

rpc_user = 'BTE'
rpc_pass = 'BTE'
URL = 'http://%s:%s@localhost:8908' % (rpc_user, rpc_pass)

chaininfo = {
    'name': 'EduFaucet',
    'unit': 'BTE'
    }

params = {
    'SubsidyHalvingInterval': 210000,     # blocks, miner reward halving
    'PowTargetTimespan': 1*24*60*60,      # sec, retarget time: one day
    'PowTargetSpacing': 10*60,            # sec, block time 10 min
    'DifficultyAdjustmentInterval': 144   # blocks, PowTargetTimespan / PowTargetSpacing
    }
