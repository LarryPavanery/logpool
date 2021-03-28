#!/usr/bin/python3

from flask import Flask
from flask_bootstrap import Bootstrap
from flask import render_template
from flask import jsonify
import cryptocompare
from datetime import datetime

import flexpoolapi
import json
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def create_app():
  app = Flask(__name__)
  Bootstrap(app)

  return app

app = create_app()

@app.route('/')
def hello_world():
    return 'Hello, World!'

#get
@app.route('/w/<address>')
def wallet(address):
    miner = flexpoolapi.miner(address)
    balance = miner.balance()

    return str(balance)

#register
@app.route('/r/<address>')
def register_wallet(address):
    miner = flexpoolapi.miner(address)
    balance = miner.balance()
    result = r.get(address).decode('utf-8')

    if result is None or result == 'null':
        store = json.dumps([{
                'timestamp': str(datetime.now()),
                'balance': balance,
                'increase': 0
                }])
        r.set(address, store)
    else:

        result = json.loads(r.get(address).decode('utf-8'))
        result.append({
                'timestamp': str(datetime.now()),
                'balance': balance,
                'increase': balance - result[-1].get('balance')
                })
        store = json.dumps(result)
        r.set(address, store)

    return balance

@app.route('/s/<address>')
def show_stats(address):
    eth_price = cryptocompare.get_price('ETH', currency='USD', full=True)['RAW']['ETH']['USD']['PRICE']
    result = json.loads(r.get(address).decode('utf-8'))
    for res in result:
        res['balance'] = float(res['balance']) / 1000000000000000000
        res['increase'] = float(res['increase']) / 1000000000000000000
        res['ethprice'] = float(eth_price)
    if result is None or result == 'null':
        return jsonify({'balances': []})
    else:
        return render_template('balance.html', balance=result)


