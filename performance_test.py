# requirements :
# ccxt == 1.58.70
# The file LIB_fast_limit_maker_order.py must be in the same folder
# FOR BINANCE OR FTX
# For SPOT ONLY.
# Tuned for BTC/BUSD (or BTC/USD on FTX), some changes may have to be done for other pairs

import json
import math
import ccxt
import time
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
from LIB_fast_limit_maker_order import fast_limit_maker_order

handler = fast_limit_maker_order()

################################################################################
# THIS IS the entry/first function called by Google Cloud Function request through WEBHOOK
# expects to get a request as a JSON that contains a "passphrase" and an "event" variable that is "open_long" or "close_long" (even if this is SPOT)
# (can be easily changed to specify a given position size, check conditions, etc...)

def test_function(request):

    #data = request.get_json()  # use this one instead (uncomment) when using in a google cloud function to catch the request (from webhook like TradingView)
    data = json.loads(request)  # comment when using in a google cloud function

    if ("passphrase", handler.PASSPHRASE) not in data.items(): # check if there is a passphrase and if it is correct (for security)
        return {
            "msg": "error: incorrect passphrase"
        }

    if ('event' not in data):
        return {
            "msg": "request JSON should have an event field."
        }

    if not(data['event'] == 'open_long' or data['event'] == 'close_long'):
        return {
            "msg": "event must be open_long or close_long."
        }

    last_price = float(handler.exchange.fetch_ticker(handler.PAIR)['last'])

    chorometer0 = time.time()

    if data['event'] == 'open_long':
        amount_BTC = handler.calculate_position_size_in_BTC(handler.amount_BUSD)
        print(f"Calculated position BTC size to open: {amount_BTC}")
        amount_BTC, executed_price = handler.OPEN_LONG_BTC(amount_BTC)
        print("LONG OPENNED")

    if data['event'] == 'close_long':
        amount_BTC, executed_price = handler.CLOSE_LONG_BTC()
        print("LONG CLOSED")

    chorometer1 = time.time()

    clock = chorometer1-chorometer0

    if data['event'] == 'open_long' or data['event'] == 'close_long':
        return clock, amount_BTC, executed_price, last_price

################################################################################

def log_to_file(input_str):
    with open("performance_log.txt","a") as ff:
        ff.write(input_str + ' \n')

################################################################################
############################### MAIN ###########################################

if __name__ == "__main__":

    nb_tries = 10

    for _ in range(nb_tries):

        handler.amount_BUSD = 15
    
        request1 = '{"event":"open_long","passphrase":"myPassphrase"}'
        clock, amount_BTC, executed_price, last_price = test_function(request1)
        spread = (executed_price-last_price)/last_price*100.0
        txt = f"{handler.exchange_name}: Time taken: {clock:.2f} s, spread (~effective fees) = {spread:.6f} %"
        print(txt)
        log_to_file(txt)
        print("waiting 30 seconds...")
        time.sleep(30)
        request2 = '{"event":"close_long","passphrase":"myPassphrase"}'
        clock, amount_BTC, executed_price, last_price = test_function(request2)
        spread = (last_price-executed_price)/last_price*100.0
        txt = f"{handler.exchange_name}: Time taken: {clock:.2f} s, spread (~effective fees) = {spread:.6f} %"
        print(txt)
        log_to_file(txt)
        print("waiting 1 minute...")
        time.sleep(60)
    
    
