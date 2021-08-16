**Spot-Future arbitrage on FTX exchange**

This is an automated trading bot. First and for most, use at your own risk.
The bot makes use of a popular trading strategy: spot-future arbitrage.
In this case the bot will trade the difference in price between a spot and perpetual future pair. e.g. BTC/USD and BTC-PERP/USD
Relative pricing is key here. Keep it in mind when configuring the buy and sell parameters.

1. If the price of a futures contract is higher than the price of spot, the bot will proceed to sell the future and buy the spot.
2. If the price of a futures contract is lower than the price of spot, the bot will proceed to buy the future and sell the spot. (only if spot is available)

This makes it so that a profit can be generated from 1. the price difference between the perpetual future contract and the spot and the funding payments.
This article explains it better than me: https://medium.com/coinmonks/spot-futures-arbitrage-strategy-earn-15-50-apr-with-extremely-low-risk-3b230949f103

The bot executes this strategy for each available spot-(perpetual)future pair. It takes into account:
- spread
- volume
- collateral
- balance
- leverage used

Usage:
1. pip install -r requirements.txt
2. generate an external api key with external program 'deltazerotrades' from FTX (https://ftx.com/en/external-program-api-keys)
3. make a dedicated subaccount for the bot on FTX
4. config the config file (config as-is should be profitable)
5. set leverage on the dedicated subaccount equal or greater than the max leverage in the config file)
6. start trading
7. restart every 24h

tips-and-tricks:
1. make use of colocation
2. automated restart based on CPU usage (if high, the websockets are down)



