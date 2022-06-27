# requirements :
# ccxt == 1.58.70
# The file LIB_fast_limit_maker_order.py must be in the same folder
# FOR BINANCE AND FTX
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

# The idea behind having something that can be easily used as a Google Cloud function is that in Google Cloud you can pick up a server close to Binance or FTX
# servers (reduce the latency) and so the order should have more chance to be executed faster.
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

def gc_function_main(request):

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

    chorometer0 = time.time()

    if data['event'] == 'open_long':
        amount_BTC = handler.calculate_position_size_in_BTC(handler.amount_BUSD)
        print(f"Calculated position {handler.COIN} size to open: {amount_BTC}")
        handler.OPEN_LONG_BTC(amount_BTC)
        print("LONG OPENNED")

    if data['event'] == 'close_long':
        amount_BTC = handler.CLOSE_LONG_BTC()
        print("LONG CLOSED")

    chorometer1 = time.time()

    clock = chorometer1-chorometer0

    if data['event'] == 'open_long' or data['event'] == 'close_long':
        return {
            "amount_processed_BUSD": str(handler.amount_BUSD),
            "amount_processed_BTC": str(amount_BTC),
            "time_filled": f"{clock}"
        }

################################################################################
############################### MAIN ###########################################
# below is just to test
# comment below if you want to use in a Google Cloud Function
if __name__ == "__main__":
    
    request1 = '{"event":"open_long","passphrase":"myPassphrase"}'
    gc_function_main(request1)
    print("waiting 10 seconds...")
    time.sleep(10)
    request2 = '{"event":"close_long","passphrase":"myPassphrase"}'
    gc_function_main(request2)
    
    
