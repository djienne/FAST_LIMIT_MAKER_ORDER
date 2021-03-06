# General :
* Requires ccxt == 1.58.70
* FOR BINANCE OR FTX, SPOT ONLY.
* USER MUST PUT HIS OWN API KEYS in `settings.json`
* The pair to use is set in `settings.json`
* Tuned for BTC/BUSD (or BTC/USD on FTX), some changes may have to be done for other pairs.

* As it is set now ("easy" to change):
  * opens position of size `amount_BUSD` BUSD (or USD on FTX)
  * closes position by selling all the available BTC
  * (make sure this runs on a specific sub-account or update the code accordingly if you want somehting else)

* source files description:
  * `LIB_fast_limit_maker_order.py` : library including the class definition to handle fast limit maker orders
  * `GC_function_fast_limit_maker_order.py` : example usage of the above class to do a 20 BUSD buy in BTC, wait 10 seconds and sell every BTC available
  * `performance_test.py` : script to evaluate the performace of the library. Executes 10 buy+sell orders, giving the execution times and the spread between the last price and the average executed price (that is equivalent to fees ~ "effective fees").

# !! WARNINGS: !!
* PROBABLY STILL SOME BUGS
* MAY NOT WORK AS EXPECTED FOR LARGE ORDERS (>1000 BUSD) OR FOR LOW LIQUIDITY COINS
* Running the code "as it is" will attempt to sell all free BTC on the (sub-)account.

# Example trades Binance:
<img src="example_trade_results_binance.jpg" alt="drawing" width="300"/>

# Example trades FTX:
<img src="example_trade_results_FTX.jpg" alt="drawing" width="300"/>

# Performance tests:
```
Binance: Time taken: 6.17 s, spread (~effective fees) = 0.000000 % 
Binance: Time taken: 7.73 s, spread (~effective fees) = -0.002775 % 
Binance: Time taken: 16.68 s, spread (~effective fees) = 0.022926 % 
Binance: Time taken: 18.23 s, spread (~effective fees) = -0.017413 % 
Binance: Time taken: 3.98 s, spread (~effective fees) = -0.000051 % 
Binance: Time taken: 6.29 s, spread (~effective fees) = 0.000051 % 
Binance: Time taken: 3.25 s, spread (~effective fees) = -0.000051 % 
Binance: Time taken: 30.28 s, spread (~effective fees) = -0.012636 % 
Binance: Time taken: 19.58 s, spread (~effective fees) = 0.086372 % 
Binance: Time taken: 1.79 s, spread (~effective fees) = 0.001537 % 
Binance: Time taken: 1.74 s, spread (~effective fees) = 0.000000 % 
Binance: Time taken: 1.76 s, spread (~effective fees) = 0.000874 % 
Binance: Time taken: 16.66 s, spread (~effective fees) = 0.044029 % 
Binance: Time taken: 17.51 s, spread (~effective fees) = 0.051477 % 
Binance: Time taken: 1.74 s, spread (~effective fees) = 0.000000 % 
Binance: Time taken: 29.66 s, spread (~effective fees) = 0.097692 % 
Binance: Time taken: 3.25 s, spread (~effective fees) = 0.008322 % 
Binance: Time taken: 16.92 s, spread (~effective fees) = -0.040252 % 
Binance: Time taken: 2.49 s, spread (~effective fees) = 0.005361 % 
Binance: Time taken: 32.00 s, spread (~effective fees) = -0.039957 % 
Binance: Time taken: 1.75 s, spread (~effective fees) = -0.021385 % 
Binance: Time taken: 1.78 s, spread (~effective fees) = 0.006668 % 
Binance: Time taken: 1.74 s, spread (~effective fees) = -0.008754 % 
Binance: Time taken: 1.80 s, spread (~effective fees) = 0.000050 % 
Binance: Average Time taken to fill order : 10.20 sec // Average spread (~effective fees) : 0.0076 %
FTX: Time taken: 123.22 s, spread (~effective fees) = 0.005052 % 
FTX: Time taken: 59.77 s, spread (~effective fees) = 0.000000 % 
FTX: Time taken: 112.07 s, spread (~effective fees) = 0.035371 % 
FTX: Time taken: 61.98 s, spread (~effective fees) = -0.005053 % 
FTX: Time taken: 65.06 s, spread (~effective fees) = 0.009865 % 
FTX: Time taken: 3.11 s, spread (~effective fees) = 0.000000 % 
FTX: Time taken: 34.21 s, spread (~effective fees) = 0.000000 % 
FTX: Time taken: 62.96 s, spread (~effective fees) = 0.004930 % 
FTX: Time taken: 56.85 s, spread (~effective fees) = 0.014790 % 
FTX: Time taken: 35.88 s, spread (~effective fees) = -0.004928 % 
FTX: Time taken: 55.41 s, spread (~effective fees) = 0.014778 % 
FTX: Time taken: 2.56 s, spread (~effective fees) = 0.000000 % 
FTX: Time taken: 119.19 s, spread (~effective fees) = 0.088779 % 
FTX: Time taken: 11.44 s, spread (~effective fees) = -0.004931 % 
FTX: Time taken: 2.46 s, spread (~effective fees) = 0.019670 % 
FTX: Time taken: 3.69 s, spread (~effective fees) = -0.014755 % 
FTX: Time taken: 11.05 s, spread (~effective fees) = 0.010007 % 
FTX: Time taken: 14.66 s, spread (~effective fees) = -0.005003 % 
FTX: Time taken: 2.94 s, spread (~effective fees) = -0.005009 % 
FTX: Time taken: 3.53 s, spread (~effective fees) = -0.015079 % 
FTX: Time taken: 4.87 s, spread (~effective fees) = -0.010055 % 
FTX: Time taken: 3.17 s, spread (~effective fees) = -0.005031 % 
FTX: Time taken: 9.60 s, spread (~effective fees) = 0.000000 % 
FTX: Time taken: 7.53 s, spread (~effective fees) = 0.000000 % 
FTX: Time taken: 10.64 s, spread (~effective fees) = -0.005029 % 
FTX: Time taken: 28.44 s, spread (~effective fees) = 0.060326 % 
FTX: Time taken: 4.95 s, spread (~effective fees) = -0.005031 % 
FTX: Time taken: 10.08 s, spread (~effective fees) = 0.000000 % 
FTX: Time taken: 21.81 s, spread (~effective fees) = 0.020145 % 
FTX: Time taken: 1.83 s, spread (~effective fees) = -0.010068 % 
FTX: Time taken: 3.43 s, spread (~effective fees) = 0.045322 % 
FTX: Time taken: 6.22 s, spread (~effective fees) = -0.010069 % 
FTX: Time taken: 6.50 s, spread (~effective fees) = -0.010079 % 
FTX: Time taken: 4.38 s, spread (~effective fees) = -0.020150 % 
FTX: Time taken: 2.03 s, spread (~effective fees) = 0.010082 % 
FTX: Time taken: 1.97 s, spread (~effective fees) = -0.055525 % 
FTX: Average Time taken to fill order : 26.93 sec // Average spread (~effective fees) : 0.0043 %
```
