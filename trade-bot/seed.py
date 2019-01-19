import json
import time
from statistics import mean
from bittrex.bittrex import Bittrex
from twisted.internet import task, reactor
import pymongo


with open('secrets.json', 'r') as f:
    CONFIG = json.load(f)

API_KEY = CONFIG['DEFAULT']['API_KEY']
API_SECRET = CONFIG['DEFAULT']['API_SECRET']
URI = CONFIG['DEFAULT']['URI']

MY_BITTREX = Bittrex(API_KEY, API_SECRET)
CLIENT = pymongo.MongoClient(URI) # connect to MLab MongoDB
MARKET_SUMMARIES = CLIENT.ogi.market_summaries
MARKET_AVERAGES = CLIENT.ogi.market_averages

# Get market summaries every 10 seconds and send to MLab
TIMEOUT = 10.0 # ten seconds

MARKET = "BTC-ETH" # market to trade on

def cal_mean_averages(market):
    results = MARKET_SUMMARIES.find().sort('_id', pymongo.DESCENDING).limit(89)
    last_89_ticks = []

    for result in results:
        for r in result['result']:
            if r['MarketName'] == market:
                last_89_ticks.append(float(r['Last']))
    
    x = mean(last_89_ticks[:21])
    y = mean(last_89_ticks[:50])
    z = mean(last_89_ticks)

    MARKET_AVERAGES.insert_one({'_id': time.time(), 'x': x, 'y': y, 'z': z})

def seed_market_summaries():
    seed = MY_BITTREX.get_market_summaries()
    MARKET_SUMMARIES.insert_one({'_id': time.time(), 'result': seed['result']})
    cal_mean_averages(MARKET)

TASK = task.LoopingCall(seed_market_summaries)
TASK.start(TIMEOUT) # call every ten seconds

reactor.run()