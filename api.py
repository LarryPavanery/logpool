#!/usr/bin/python3

from flask import Flask
from flask_bootstrap import Bootstrap
from flask import render_template
from flask import jsonify
import cryptocompare

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


