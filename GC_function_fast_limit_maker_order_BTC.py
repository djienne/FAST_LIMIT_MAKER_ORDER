# requirements :
# ccxt == 1.58.70
# FOR BINANCE ONLY
# For SPOT ONLY.
# Tuned for BTC/BUSD, some changes have to be done for other pairs
# MUST BE A FIRST GENERATION GOOGLE CLOUD FUNCTION
# USER MUST PUT HIS OWN API KEYS
# THE GOAL OF THIS CODE IS TO CATCH A TradingView WEBHOOK AND PROCESS A LIMIT ORDER ACCORDINGLY, AS FAST AS POSSIBLE
# PASSPHRASE HERE HAS TO BE CONSISTENT WITH THE ONE SEND BY TradingView

# AS IT IS SET NOW (EASY TO CHANGE):
# - opens position of size amount_BUSD BUSD
# - closes position by selling all the available BTC
# (make sure this runs on a specific sub-account or update the code accordingly if you want somehting else)
# !!!!! WARNINGS: !!!!!
#   - PROBABLY STILL SOME BUGS
#   - MAY NOT WORK AS EXPECTED FOR LARGE ORDERS (>1000 BUSD) OR FOR LOW LIQUIDITY COINS

import math
import ccxt
import time
import pickle
import os
import datetime as dt
################################

PASSPHRASE = 'myPassphrase'
API_KEY = 'apiKey'
API_SECRET = 'secret'

BOT_ID = os.environ.get('FUNCTION_NAME')

symbol = 'BTC/BUSD'

amount_BUSD = 20  # WILL DO A 20 BUSD BUY, can be changed here or code can be updated to get this information otherwise
# (for example coming from TradingView with the webhook)

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
    },
})
# HERE enableRateLimit is important to be able to send orders as quickly as possible

exchange.verbose = False  # debug output

markets = exchange.load_markets()
market = exchange.market(symbol)

tick_size_in_BTC = 10**float(-1.0*market['precision']['amount'])
tick_size_in_USD = 10**float(-1.0*market['precision']['price'])

extra_delta_bid_ask_USD = 2.0
amount_BTC = 0.001  # initialization, will be updated (calculated)
# time to wait (in seconds) before canceling limit order and trying again
max_time_order_sec = 10.0
clock = 0.0
t0 = time.time()

################################################################################
# assumes a minimal possible buy amount of 10.5 BUSD of BTC


def calculate_min_amount():
    global exchange
    global symbol
    pri = float(exchange.fetch_ticker(symbol)['last'])
    min_amount = math.floor(10.5/pri*100000.0)/100000.0
    return min_amount


def calculate_position_size_in_BTC(amount_BUSD):
    global exchange
    global symbol

    min_amount = calculate_min_amount()

    # not used: getting available BUSD (e.g. for makign a percent based order)
    #balance = exchange.fetch_balance()
    #BUSD_free = float(balance['free']['BUSD'])
    #BUSD_total = float(balance['total']['BUSD'])

    pri = float(exchange.fetch_ticker(symbol)['last'])

    output_value = math.floor(0.9999*amount_BUSD/pri*100000.0)/100000.0

    if output_value < min_amount:
        output_value = min_amount

    print(f"position size to open (BTC): {output_value}")

    return output_value

##################################################################################################################
# CLOSE POSITION
# WILL TRY FOR LIMIT ORDERS 5 TIMES (each waiting for 10 seconds) AND THEN DO A MARKET SELL IF ALL 5 FAILED
# ASSUMES WE ARE USING A SUBACCOUNT ONLY FOR A GIVEN BOT AND SO IT CAN CLOSE THE POSITION BY SELLING ALL AVAILABLE BTC


def CLOSE_LONG_BTC():
    global t0
    global clock
    global symbol
    global exchange
    global extra_delta_bid_ask_USD

    max_limit_orders_to_try = 5

    balance = exchange.fetch_balance()
    BUSD_free = float(balance['free']['BUSD'])
    pri = float(exchange.fetch_ticker(symbol)['last'])
    BTC_amount = math.floor(0.9999*amount_BUSD/pri*100000.0)/100000.0

    params = {}
    params = {
        'type': 'limit_maker'
    }
    side = 'sell'
    typee = 'limit'
    market_sell_counter = 0
    processed = False
    while not processed:
        orderbook = exchange.fetch_order_book(symbol)
        ask = orderbook['asks'][0][0]
        bid = orderbook['bids'][0][0]
        price = ask + extra_delta_bid_ask_USD
        order = exchange.create_order(
            symbol, typee, side, BTC_amount, price, params)
        print(order)
        idd = order['id']
        t0 = time.time()
        while True:
            time.sleep(1)
            order = exchange.fetchOrder(idd, symbol, params={})
            t1 = time.time()
            clock = t1-t0
            if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                break
            if order['status'] == 'closed':
                processed = True
                break
            if (clock > max_time_order_sec):
                market_sell_counter = market_sell_counter+1
                if market_sell_counter >= max_limit_orders_to_try:
                    print("too much order failed, doing market sell")
                    try:
                        exchange.cancelOrder(idd, symbol, params={})
                        print("order has been canceled")
                    except:
                        print("order failed to be canceled")
                        pass
                    exchange.create_order(
                        symbol, 'market', side, BTC_amount, params={})
                    print("market sell done")
                    processed = True
                    break
                order = exchange.fetchOrder(idd, symbol, params={})
                if order['status'] == 'closed':
                    processed = True
                    break
                if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                    break
                try:
                    exchange.cancelOrder(idd, symbol, params={})
                    print("order has been canceled")
                except:
                    print("order failed to be canceled")
                    pass

################################################################################
# OPEN POSITION
# WILL TRY FOR LIMIT ORDERS AS MANY TIMES ARE NECESSARY


def OPEN_LONG_BTC(BTC_amount):
    global t0
    global clock
    global exchange
    global amount_BUSD
    global extra_delta_bid_ask_USD

    params = {}
    params = {
        'type': 'limit_maker'
    }
    side = 'buy'
    typee = 'limit'
    processed = False
    while not processed:
        orderbook = exchange.fetch_order_book(symbol)
        ask = orderbook['asks'][0][0]
        bid = orderbook['bids'][0][0]
        price = ask - extra_delta_bid_ask_USD
        order = exchange.create_order(
            symbol, typee, side, BTC_amount, price, params)
        print(order)
        idd = order['id']
        t0 = time.time()
        while True:
            time.sleep(1)
            order = exchange.fetchOrder(idd, symbol, params={})
            t1 = time.time()
            clock = t1-t0
            if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                break
            if order['status'] == 'closed':
                processed = True
                break
            if (clock > max_time_order_sec):
                order = exchange.fetchOrder(idd, symbol, params={})
                if order['status'] == 'closed':
                    processed = True
                    break
                if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                    break
                try:
                    exchange.cancelOrder(idd, symbol, params={})
                except:
                    pass

################################################################################
# THIS IS the entry/first function called by Google Cloud Function request through WEBHOOK
# expects to revieve a request as a JSON
#   that contains a passphrase and an "event" variable that is "open_long" or "close_long" (even if this is SPOT)
# (can be easily changed to specify a given position size, check conditions, etc...)


def gc_function_main(request):
    global tick_size_in_BTC
    global clock
    global t0
    global exchange
    global symbol
    global extra_delta_bid_ask_USD
    global PASSPHRASE

    data = request.get_json()  # contains the request JSON send by Trading View webhook

    # check if passphrase is correct (for security)
    if ("passphrase", PASSPHRASE) not in data.items():
        return {
            "msg": "error: incorrect passphrase"
        }

    if ('event' not in data):
        return {
            "msg": "request JSON should have an event field."
        }

    if (data['event'] == 'open_short' or data['event'] == 'close_short'):
        return {
            "msg": "shorts are not possible in Spot."
        }

    if not(data['event'] == 'open_long' or data['event'] == 'close_long'):
        return {
            "msg": "shorts are not possible in Spot."
        }

    chorometer0 = time.time()

    # wait a little to make sure position was closed before opening
    if data['event'] == 'open_long':
        amount_BTC = calculate_position_size_in_BTC(amount_BUSD)
        print(f"Calculated position BTC size to open: {amount_BTC}")
        OPEN_LONG_BTC(amount_BTC)
        print("openned long")

    if data['event'] == 'close_long':
        CLOSE_LONG_BTC()
        print("closed long")

    chorometer1 = time.time()

    clock = chorometer1-chorometer0

    return {
        "amount_processed_BUSD": str(amount_BUSD),
        "amount_processed_BTC": str(amount_BTC),
        "time_filled": f"{clock}",
        "BOT_ID": BOT_ID
    }
