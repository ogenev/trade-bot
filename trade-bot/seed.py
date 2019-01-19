from bittrex.bittrex import Bittrex
from twisted.internet import task, reactor
import pymongo
import json

with open('secrets.json', 'r') as f:
    config = json.load(f)

API_KEY = config['DEFAULT']['API_KEY']
API_SECRET = config['DEFAULT']['API_SECRET']
URI = config['DEFAULT']['URI']

my_bittrex = Bittrex(API_KEY, API_SECRET)

client = pymongo.MongoClient(URI) # connect to MLab MongoDB
db = client.ogi
market_summaries = db.market_summaries

# Get market summaries every 10 seconds and send to MLab
timeout = 10.0 # ten seconds

def seed_market_summaries():
    seed = my_bittrex.get_market_summaries()
    market_summaries.insert_one({'result': seed['result']}).inserted_id
    pass

l = task.LoopingCall(seed_market_summaries)
l.start(timeout) # call every ten seconds

reactor.run()