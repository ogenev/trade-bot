import pymongo
import json
from bittrex.bittrex import Bittrex

with open('secrets.json', 'r') as f:
    CONFIG = json.load(f)

API_KEY = CONFIG['DEFAULT']['API_KEY']
API_SECRET = CONFIG['DEFAULT']['API_SECRET']

MY_BITTREX = Bittrex(API_KEY, API_SECRET)

client = pymongo.MongoClient()
db = client.trade

MARKET_AVERAGES = db.market_averages

orders = MY_BITTREX.get_open_orders()
print(orders)

for change in MARKET_AVERAGES.watch():
    x = change['fullDocument']['x']
    y = change['fullDocument']['y']
    z = change['fullDocument']['z']

    if (x > y and y > z):
        print('buy')
    elif (x < y and y < z):
        print('sell')

