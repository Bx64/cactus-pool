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
import os.path
import requests
import requests_unixsocket
import signal
import sys
import time

app = Flask(__name__)


@app.route('/')
def index():
    stats = {}
    ddata = client.delegates.get(poolconfig.blockproducer)

    # request share rate
    s = requests.get('https://delegates.solar.org/api/delegates/{}'.format(poolconfig.blockproducer)).json()

    # get stats
    stats['handle']   = ddata['data']['username']
    stats['wallet']   = ddata['data']['address']
    stats['rank']     = ddata['data']['rank']
    stats['produced']   = ddata['data']['blocks']['produced']
    stats['reliability'] = ddata['data']['blocks']['productivity']
    stats['voters']   = int(ddata['data']['votesReceived']['voters'])
    stats['votes']    = "{:,.2f}".format(int(ddata['data']['votesReceived']['votes'])/poolconfig.atomic)
    stats['approval'] = ddata['data']['votesReceived']['percent']
    stats['share']    = s['payout']
#    stats['version']  = ddata['data']['version'] if stats['rank'] <= network.blockproducers else 'N/A'

    # get all produced blocks in reverse chronological order, first page, max 100 as default
    dblocks = client.delegates.blocks(poolconfig.blockproducer) 
    stats['lastproduced_no'] = dblocks['data'][0]['height']
    stats['lastproduced_id'] = dblocks['data'][0]['id']
    stats['lastproduced_unix'] = dblocks['data'][0]['timestamp']['unix']
    age = divmod(int(time.time() - stats['lastproduced_unix']), 60)
    stats['lastproduced_ago'] = "{0}:{1}".format(age[0],age[1])
    stats['active'] = 'Active' if stats['rank'] <= network.blockproducers else 'Standby'

    # get pending balances from file
    with open('/home/{}/cactus-pool/core/pool_unpaid.json'.format(poolconfig.username), 'r') as f:
        unpaid = json.load(f)
        int_unpaid = {k:int(v) for k, v in unpaid.items()}
        sorted_unpaid_dict = dict(sorted(int_unpaid.items(), key=lambda item: item[1], reverse=True))
        pend_total = 0
        pend_total = sum(sorted_unpaid_dict.values())

    # get synchronisation data
    node_sync_data = client.node.syncing()
    stats['synced'] = 'Syncing' if node_sync_data['data']['syncing'] else 'Synced'
    stats['height'] = node_sync_data['data']['height']

    return render_template(poolconfig.pool_template + '_index.html', node=stats, pend=sorted_unpaid_dict, pendtotal=pend_total, tags=tags)

@app.route('/payments')
def payments():
    sql.open_connection()
    xactions = sql.history().fetchall()
    sql.close_connection()

    tx_data = []
    for i in xactions:
        data_list = [i[2], i[3], datetime.datetime.fromtimestamp(i[6])]
        tx_data.append(data_list)

    return render_template(poolconfig.pool_template + '_payments.html', tx_data=tx_data, tags=tags)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('40x.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('40x.html'), 403

@app.errorhandler(410)
def page_not_found(e):
    return render_template('40x.html'), 410

@app.errorhandler(500)
def page_not_found(e):
    return render_template('50x.html'), 500


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
        print("FATAL: pool_config.ini not found, please fix your configuration file! Terminating POOL.", file=sys.stderr)
        sys.exit(1)

    # check if pool_unpaid.json exists
    if not os.path.exists('./pool_unpaid.json'):
        print("FATAL: pool_unpaid.json not found, please run the poolinit.py script before restarting! Terminating POOL.", file=sys.stderr)
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
       'dname': poolconfig.blockproducer,
       'proposal1': poolconfig.proposal1,
       'proposal2': poolconfig.proposal2,
       'proposal2_lang': poolconfig.proposal2_lang,
       'explorer': poolconfig.explorer,
       'coin': poolconfig.coin}

    #app.run(host=data.pool_ip, port=data.pool_port)
    server = Process(target=app.run, args=(poolconfig.pool_ip, poolconfig.pool_port))
    server.start()

    # loop: request pending balance & write to file
    while True:
        start_time = end_time = elapsed_time = timer = 0
        start_time = time.perf_counter()

        session = requests_unixsocket.Session()
        r = session.post('http+unix://%2Ftmp%2F{0}%2Fsolar-core%2F{1}%2Ftbw-pay.sock/unpaid'.format(poolconfig.username, poolconfig.network))
        unpaidloop = r.json()

        with open('pool_unpaid.json', 'w') as outfile:
            json.dump(unpaidloop, outfile)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        timer = 600 - elapsed_time

        killsig.wait(timer)
