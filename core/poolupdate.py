#!/usr/bin/env python
from config.pool_config import PoolConfig
import json
import requests_unixsocket

# get configuration
poolconfig = PoolConfig()
if (poolconfig.error):
    print("FATAL: pool_config.ini not found! Terminating POOL.", file=sys.stderr)
    sys.exit(1)

# request unpaid balances & write to file
session = requests_unixsocket.Session()
r = session.post('http+unix://%2Ftmp%2F{0}%2Fsolar-core%2F{1}%2Ftbw-pay.sock/unpaid'.format(poolconfig.username, poolconfig.network), json = {"username": poolconfig.delegate})
unpaid = r.json()

with open('pool_unpaid.json', 'w') as outfile:
    json.dump(unpaid, outfile)
