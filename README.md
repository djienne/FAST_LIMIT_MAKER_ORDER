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