import json
import time
from statistics import mean
from bittrex.bittrex import Bittrex
import pymongo

# Load API keys from 'secrets.json' file
with open('secrets.json', 'r') as f:
    CONFIG = json.load(f)

API_KEY = CONFIG['DEFAULT']['API_KEY']
API_SECRET = CONFIG['DEFAULT']['API_SECRET']

MY_BITTREX = Bittrex(API_KEY, API_SECRET) # connect to Bittrex API
CLIENT = pymongo.MongoClient() # connect to MongoDB
DB = CLIENT.trade
MARKET_SUMMARIES = DB.market_summaries
MARKET_AVERAGES = DB.market_averages
MARKET = "BTC-ETH"  # market to trade on


def cal_mean_averages(market):
    # Get last 89 documents from the collection 'market_summaries
    results = MARKET_SUMMARIES.find().sort('_id', pymongo.DESCENDING).limit(89)

    last_89_ticks = []  # store last 89 documents

    # Check for market value and append results
    for result in results:
        if result['result']:
            for r in result['result']:
                if r['MarketName'] == market:
                    last_89_ticks.append(float(r['Last']))

    # Calculate the means for last 21, 50 and 89 ticks
    x = mean(last_89_ticks[:21])
    y = mean(last_89_ticks[:50])
    z = mean(last_89_ticks)

    # Write moving averages to new collection 'moving_averages'
    MARKET_AVERAGES.insert_one({'_id': time.time(), 'x': x, 'y': y, 'z': z})


# Get market summaries every 10 sec, write results to 'market_summaries' collection and calculate averages
def seed_market_summaries():
    while True:
        seed = MY_BITTREX.get_market_summaries()
        MARKET_SUMMARIES.insert_one({'_id': time.time(), 'result': seed['result']})
        cal_mean_averages(MARKET)
        time.sleep(10)  # 10 seconds


seed_market_summaries()
