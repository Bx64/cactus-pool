#!/usr/bin/env python
from __init__ import __version__, __version_info__
from config.pool_config import PoolConfig
from network.network import Network
from utility.sql import Sql
from utility.utility import Utility
from flask import Flask, render_template
from multiprocessing import Process
from threading import Event
from solar_client import SolarClient
import datetime
import json
import logging
import requests_unixsocket
import signal
import sys
import time

app = Flask(__name__)


def get_round(height):
    mod = divmod(height,network.delegates)
    return (mod[0] + int(mod[1] > 0))


#def get_yield(netw_height, dblocks):
#    drounds = dblocks['meta']['count'] #number of forged blocks 
#
#    missed = 0
#    forged = 0
#    netw_round = get_round(netw_height)
#    last_forged_round = get_round(dblocks['data'][0]['height'])
#
#    if netw_round > last_forged_round + 1:
#        missed += netw_round - last_forged_round - 1
#    else:
#        forged += 1
#
#    if drounds > 1:
#        for i in range(0, drounds - 1):
#            cur_round = get_round(dblocks['data'][i]['height'])
#            prev_round = get_round(dblocks['data'][i + 1]['height'])
#            if prev_round < cur_round - 1:
#                if cur_round - prev_round - 1 > drounds - missed - forged:
#                    missed += drounds - missed - forged
#                    break
#                else:
#                    missed += cur_round - prev_round - 1
#            else:
#                forged += 1
#
#    yield_over_drounds = "{:.2f}".format(round((forged * 100)/(forged + missed)))
#    return yield_over_drounds


@app.route('/')
def index():
    stats = {}
    ddata = client.delegates.get(poolconfig.delegate)

    stats['handle']   = ddata['data']['username']
    stats['wallet']   = ddata['data']['address']
    stats['rank']     = ddata['data']['rank']
    stats['forged']   = ddata['data']['blocks']['produced']
    stats['productivity'] = ddata['data']['blocks']['productivity'] # replacement for yield
    stats['rewards']  = ddata['data']['forged']['total']
    stats['votes']    = "{:,.2f}".format(int(ddata['data']['votesReceived']['votes'])/poolconfig.atomic)
    stats['voters']   = int(ddata['data']['votesReceived']['voters'])
    stats['approval'] = ddata['data']['votesReceived']['percent']
    stats['version']  = ddata['data']['version'] if stats['rank'] <= network.delegates else 'N/A'

    # get all forged blocks in reverse chronological order, first page, max 100 as default
    dblocks = client.delegates.blocks(poolconfig.delegate) 
    stats['lastforged_no'] = dblocks['data'][0]['height']
    stats['lastforged_id'] = dblocks['data'][0]['id']
    stats['lastforged_ts'] = dblocks['data'][0]['timestamp']['human']
    stats['lastforged_unix'] = dblocks['data'][0]['timestamp']['unix']
    age = divmod(int(time.time() - stats['lastforged_unix']), 60)
    stats['lastforged_ago'] = "{0}:{1}".format(age[0],age[1])
    stats['forging'] = 'Forging' if stats['rank'] <= network.delegates else 'Standby'

    # get pending balances from file
    with open('/home/{}/cactus-pool/core/pool_unpaid.json'.format(poolconfig.username), 'r') as f:
        unpaid = json.load(f)

    # get synchronisation data (# yield)
    node_sync_data = client.node.syncing()
    stats['synced'] = 'Syncing' if node_sync_data['data']['syncing'] else 'Synced'
    stats['behind'] = node_sync_data['data']['blocks']
    stats['height'] = node_sync_data['data']['height']
#    stats['yield'] = get_yield(stats['height'], dblocks)

    return render_template(poolconfig.pool_template + '_index.html', node=stats, pend=unpaid, tags=tags)


@app.route('/payments')
def payments():
    sql.open_connection()
    xactions = sql.history().fetchall()
    sql.close_connection()

    tx_data = []
    for i in xactions:
        data_list = [i[3], i[4], i[7]]
        tx_data.append(data_list)

    return render_template(poolconfig.pool_template + '_payments.html', tx_data=tx_data, tags=tags)


# Handler for SIGINT and SIGTERM
def sighandler(signum, frame):
    global server
    logger.info("SIGNAL {0} received. Starting graceful shutdown".format(signum))
    server.kill()
    logger.info("< Terminating POOL...")
    return


if __name__ == '__main__':    
    # get configuration
    poolconfig = PoolConfig()
    if (poolconfig.error):
        print("FATAL: pool_config.ini not found! Terminating POOL.", file=sys.stderr)
        sys.exit(1)

    # set logging
    logger = logging.getLogger()
    logger.setLevel(poolconfig.loglevel)
    outlog = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(poolconfig.formatter)
    outlog.setFormatter(formatter)
    logger.addHandler(outlog)

    # start script
    msg='> Starting POOL script %s @ %s' % (__version__, str(datetime.datetime.now()))
    logger.info(msg)

    # subscribe to signals
    killsig = Event()
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)

    # load network
    network = Network(poolconfig.network)
    
    # load utility and client
    utility = Utility(network)
    client = utility.get_client()

    # connect to tbw script database
    sql = Sql()

    tags = {
       'dname': poolconfig.delegate,
       'proposal1': poolconfig.proposal1,
       'proposal2': poolconfig.proposal2,
       'proposal2_lang': poolconfig.proposal2_lang,
       'explorer': poolconfig.explorer,
       'coin': poolconfig.coin}

    #app.run(host=data.pool_ip, port=data.pool_port)
    server = Process(target=app.run, args=(poolconfig.pool_ip, poolconfig.pool_port))
    server.start()
