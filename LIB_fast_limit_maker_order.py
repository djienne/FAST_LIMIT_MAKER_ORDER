# requirements :
# ccxt == 1.58.70
# The file LIB_fast_limit_maker_order.py must be in the same folder
# FOR BINANCE OR FTX
# For SPOT ONLY.
# Tuned for BTC/BUSD (or BTC/USD), some changes may have to be done for other pairs
# USER MUST PUT HIS OWN API KEYS in the settings.json file
# AS IT IS SET NOW (EASY TO CHANGE):
# - opens position of size amount_BUSD BUSD (or USD on FTX)
# - closes position by selling all the available BTC
# (make sure this runs on a specific sub-account or update the code accordingly if you want somehting else)
# !!!!! WARNINGS: !!!!!
#   - PROBABLY STILL SOME BUGS
#   - MAY NOT WORK AS EXPECTED FOR LARGE ORDERS (>1000 BUSD) OR FOR LOW LIQUIDITY COINS
from distutils.log import error
import math
import json
import ccxt
import time
import os

class fast_limit_maker_order:

    def __init__(self):

        with open('settings.json', 'r') as f:
            json_obj = json.load(f)

        # to be changed with your API and API secret keys
        self.API_KEY = json_obj['API_KEY']
        self.API_SECRET = json_obj['API_SECRET']
        self.PASSPHRASE = json_obj['PASSPHRASE']
        self.exchange_name = json_obj['exchange_name']

        # WILL DO A 20 BUSD BUY, can be changed here or code can be updated to get this information otherwise
        self.amount_BUSD = 20.0
        # (for example coming from TradingView with the webhook)

        if self.exchange_name.lower() == "binance":
            self.exchange = ccxt.binance({
                'apiKey': self.API_KEY,
                'secret': self.API_SECRET,
                # here enableRateLimit is important to be able to send orders as quickly as possible
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                },
            })
            self.isFTX=False
            self.isBinance=True
        elif self.exchange_name.lower() == "ftx":
            self.exchange = ccxt.ftx({
                'apiKey': self.API_KEY,
                'secret': self.API_SECRET,
                # here enableRateLimit is important to be able to send orders as quickly as possible
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                },
                'headers': {
                    'FTX-SUBACCOUNT': json_obj['FTX-SUBACCOUNT']
                }
            })
            self.isFTX=True
            self.isBinance=False
        else:
            raise Exception("exchange_name must be binance or ftx")

        self.PAIR = json_obj['PAIR']
        self.COIN = self.PAIR.split('/')[0]
        self.QUOTE = self.PAIR.split('/')[1]

        if self.isFTX and self.QUOTE=='BUSD':
            raise error('cannot have a BUSD pair on FTX.')

        self.exchange.verbose = False  # debug output

        self.markets = self.exchange.load_markets()
        self.market = self.exchange.market(self.PAIR)

        # time to wait (in seconds) before canceling limit order and trying again
        self.max_time_order_sec = 10.0

    ################################################################################
    # assumes a minimal possible buy amount of 10.1 BUSD of BTC

    def calculate_min_amount(self):
        pri = float(self.exchange.fetch_ticker(self.PAIR)['last'])
        min_amount = float(self.exchange.amount_to_precision(self.PAIR, 10.1/pri))
        return min_amount

    def calculate_position_size_in_BTC(self, amount_BUSD):

        min_amount = self.calculate_min_amount()

        # not used: getting available BUSD (e.g. for makign a percent based order)
        #balance = self.exchange.fetch_balance()
        #BUSD_free = float(balance['free']['BUSD'])
        #BUSD_total = float(balance['total']['BUSD'])

        pri = float(self.exchange.fetch_ticker(self.PAIR)['last'])

        output_value = float(self.exchange.amount_to_precision(self.PAIR, amount_BUSD/pri))

        if output_value < min_amount:
            output_value = min_amount

        print(f"position size to open ({self.COIN}): {output_value}")

        return output_value

    ##################################################################################################################
    # CLOSE POSITION
    # WILL TRY FOR LIMIT ORDERS 10 TIMES (each waiting for 10 seconds) AND THEN DO A MARKET SELL IF ALL 10 FAILED
    # that's increased to 20 times on FTX
    # ASSUMES WE ARE USING A SUBACCOUNT ONLY FOR A GIVEN BOT AND SO IT CAN CLOSE THE POSITION BY SELLING ALL AVAILABLE BTC

    def CLOSE_LONG_BTC(self,amount_COIN=-1):
        if self.isBinance:
            max_limit_orders_to_try = 10
        else:
            max_limit_orders_to_try = 20

        balance = self.exchange.fetch_balance()
        if amount_COIN == -1:
            BTC_amount = float(balance['free'][self.COIN])
        else:
            BTC_amount = amount_COIN

        params = {}
        if self.isBinance:
            params = {
                'type': 'limit_maker'
            }
        else:
            params = {
                'postOnly': True
            }
        side = 'sell'
        typee = 'limit'
        market_sell_counter = 0
        processed = False
        while not processed:
            orderbook = self.exchange.fetch_order_book(self.PAIR)
            ask = orderbook['asks'][0][0]
            bid = orderbook['bids'][0][0]
            price = max(ask, bid)
            order = self.exchange.create_order(self.PAIR, typee, side, BTC_amount, price, params)
            print(order)
            idd = order['id']
            t0 = time.time()
            while True:
                time.sleep(0.1)
                order = self.exchange.fetchOrder(idd, self.PAIR, params={})
                t1 = time.time()
                clock = t1-t0
                if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                    break
                if order['status'] == 'closed':
                    processed = True
                    break
                if (clock > self.max_time_order_sec):
                    market_sell_counter = market_sell_counter+1
                    if market_sell_counter >= max_limit_orders_to_try:
                        print("too much order failed, doing market sell")
                        try:
                            self.exchange.cancelOrder(idd, self.PAIR, params={})
                            print("order has been canceled")
                        except:
                            print("order failed to be canceled")
                            pass
                        self.exchange.create_order(self.PAIR, 'market', side, BTC_amount, params={})
                        print("market sell done")
                        processed = True
                        break
                    order = self.exchange.fetchOrder(idd, self.PAIR, params={})
                    if order['status'] == 'closed':
                        processed = True
                        break
                    if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                        break
                    try:
                        self.exchange.cancelOrder(idd, self.PAIR, params={})
                        print("order has been canceled")
                    except:
                        print("order failed to be canceled")
                        pass
        return BTC_amount, price

    ################################################################################
    # OPEN POSITION
    # WILL TRY FOR LIMIT ORDERS AS MANY TIMES ARE NECESSARY

    def OPEN_LONG_BTC(self, BTC_amount):

        if self.isBinance:
            max_limit_orders_to_try = 12
        else:
            max_limit_orders_to_try = 22

        params = {}
        if self.isBinance:
            params = {
                'type': 'limit_maker'
            }
        else:
            params = {
                'postOnly': True
            }
        side = 'buy'
        typee = 'limit'
        market_buy_counter = 0
        processed = False
        while not processed:
            orderbook = self.exchange.fetch_order_book(self.PAIR)
            ask = orderbook['asks'][0][0]
            bid = orderbook['bids'][0][0]
            price = min(ask, bid)
            order = self.exchange.create_order(self.PAIR, typee, side, BTC_amount, price, params)
            print(order)
            idd = order['id']
            t0 = time.time()
            while True:
                time.sleep(0.1)
                order = self.exchange.fetchOrder(idd, self.PAIR, params={})
                t1 = time.time()
                clock = t1-t0
                if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                    break
                if order['status'] == 'closed':
                    processed = True
                    break
                if (clock > self.max_time_order_sec):
                    market_buy_counter = market_buy_counter+1
                    if market_buy_counter >= max_limit_orders_to_try:
                        print("too much order failed, doing market buy")
                        try:
                            self.exchange.cancelOrder(idd, self.PAIR, params={})
                            print("order has been canceled")
                        except:
                            print("order failed to be canceled")
                            pass
                        self.exchange.create_order(self.PAIR, 'market', side, BTC_amount, params={})
                        print("market buy done")
                        processed = True
                        break
                    order = self.exchange.fetchOrder(idd, self.PAIR, params={})
                    if order['status'] == 'closed':
                        processed = True
                        break
                    if order['status'] == 'canceled' or order['status'] == 'expired' or order['status'] == 'EXPIRED':
                        break
                    try:
                        self.exchange.cancelOrder(idd, self.PAIR, params={})
                        print("order has been canceled")
                    except:
                        print("order failed to be canceled")
                        pass
        return BTC_amount, price
