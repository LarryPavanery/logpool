#!/usr/bin/python3

import flexpoolapi
from datetime import datetime
import redis
import json
import schedule
from time import sleep

r = redis.Redis(host='localhost', port=6379, db=0)

def time():
    return str(datetime.now())

def process_profit(address):
    address = address.decode('utf-8')
    miner = flexpoolapi.miner(address)
    balance = miner.balance()
    result = r.get(address).decode('utf-8')

    if result is None or result == 'null':
        store = json.dumps([{
                'timestamp': time(),
                'balance': balance,
                'increase': 0
                }])
        r.set(address, store)
    else:

        result = json.loads(r.get(address).decode('utf-8'))
        result.append({
                'timestamp': time(),
                'balance': balance,
                'increase': balance - result[-1].get('balance')
                })
        store = json.dumps(result)
        r.set(address, store)

    return balance

def job():
    wallets = r.keys()
    for wallet in wallets:
        print('Wallet %s found' % wallet)
        process_profit(wallet)

schedule.every(20).minutes.do(job)

while 1:
    schedule.run_pending()
    sleep(1)