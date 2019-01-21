import pymongo
import json
from bittrex.bittrex import Bittrex

# Load API keys from 'secretс.json' file
with open('secrets.json', 'r') as f:
    CONFIG = json.load(f)

API_KEY = CONFIG['DEFAULT']['API_KEY']
API_SECRET = CONFIG['DEFAULT']['API_SECRET']
MY_BITTREX = Bittrex(API_KEY, API_SECRET)  # access Bittrex API

# Connect to MongoDB
client = pymongo.MongoClient()
db = client.trade

MARKET_AVERAGES = db.market_averages
MARKET = "BTC-ETH"  # market to trade on

BUY_SIGNAL = None
SELL_SIGNAL = None


# Place buy order
def buy_order():
    # Get BTC balance
    get_btc_balance = MY_BITTREX.get_balance('BTC')
    btc_balance = float(get_btc_balance['result']['Available'])

    if btc_balance == 0:
        print('No BTC to buy')
        return
   
    # get sell orders from book
    sell_orders = MY_BITTREX.get_orderbook(MARKET, depth_type='sell')
    book_buy_rate = float(sell_orders['result'][0]['Rate'])
    book_buy_quantity = float(sell_orders['result'][0]['Quantity'])
    converted_eth_balance = (btc_balance / book_buy_rate)  # convert BTC balance to ETH

    # if the total balance is more than the first sell order quantity, look for second sell order
    if converted_eth_balance <= book_buy_quantity:
        # Place buy order
        MY_BITTREX.buy_limit(MARKET, converted_eth_balance - 0.001, book_buy_rate)
        print('buy order activated')
    else:
        # Place buy order
        MY_BITTREX.buy_limit(MARKET, converted_eth_balance - 0.001, book_buy_rate)
        print('buy order activated')
        # Get data from the second sell order
        remaining_quantity = converted_eth_balance - book_buy_quantity
        book_buy_rate = float(sell_orders['result'][1]['Rate'])
        # Place second buy order with the remaining balance
        MY_BITTREX.buy_limit(MARKET, remaining_quantity - 0.002, book_buy_rate)
        print('second buy order completed')


# Place sell order
def sell_order():
    # Get ETH balance
    get_eth_balance = MY_BITTREX.get_balance('ETH')
    eth_balance = float(get_eth_balance['result']['Available'])

    if eth_balance == 0:
        print('No ETH to sell')
        return
    
    # get buy orders from book
    buy_orders = MY_BITTREX.get_orderbook(MARKET, depth_type='buy')
    book_sell_rate = float(buy_orders['result'][0]['Rate'])
    book_sell_quantity = float(buy_orders['result'][0]['Quantity'])

    # if the total balance is more than the first buy order quantity, look for second buy order
    if eth_balance <= book_sell_quantity:
        # Place sell order
        MY_BITTREX.sell_limit(MARKET, eth_balance, book_sell_rate)
        print('sell order activated')
        
    else: 
        # place sell order
        MY_BITTREX.sell_limit(MARKET, eth_balance, book_sell_rate)
        print('sell order activated')
        # Look for second buy order
        remaining_eth_balance = eth_balance - book_sell_quantity
        book_sell_rate = float(buy_orders['result'][1]['Rate'])
        # place second sell order
        MY_BITTREX.sell_limit(MARKET, remaining_eth_balance, book_sell_rate)
        print('second sell order activated')


# Check for new data in MongoDB collection 'market_averages' and calculate
# Tripple Moving Average crossover strategy
for change in MARKET_AVERAGES.watch():
    x = change['fullDocument']['x']  # MA for last 21 ticks
    y = change['fullDocument']['y']  # MA for last 50 ticks
    z = change['fullDocument']['z']  # MA for last 89 ticks

    # Check for strategy requirements and place buy or sell signal
    if x > y > z:
        if not BUY_SIGNAL:
            BUY_SIGNAL = True
            SELL_SIGNAL = False
            buy_order()
    elif x < y < z:
        if not SELL_SIGNAL:
            SELL_SIGNAL = True
            BUY_SIGNAL = False
            sell_order()
