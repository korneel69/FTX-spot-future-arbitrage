**Spot-Future arbitrage on FTX exchange**

This is an automated trading bot. First and for most, use at your own risk.
The bot makes use of a popular trading strategy: spot-future arbitrage.
In this case the bot will trade the difference in price between a spot and perpetual future pair. e.g. BTC/USD and BTC-PERP/USD
Relative pricing is key here. Keep it in mind when configuring the buy and sell parameters.

1. If the price of a futures contract is higher than the price of spot, the bot will proceed to sell the future and buy the spot.
2. If the price of a futures contract is lower than the price of spot, the bot will proceed to buy the future and sell the spot. (only if spot is available)

This makes it so that a profit can be generated from 1) the price difference between the perpetual future contract and the spot and 2) the funding payments.
This article explains it better than me: https://medium.com/coinmonks/spot-futures-arbitrage-strategy-earn-15-50-apr-with-extremely-low-risk-3b230949f103

The bot executes this strategy for each available spot-(perpetual)future pair. It takes into account:
- spread
- volume
- collateral
- balance
- leverage used

Risks involved:
1. Possible bug in program (read it through before using)
2. Execution risk: The bot attempts to buy and sell at the same time. If one doesn't get filled, your net-position will be inbalanced. This will expose you to market risk. In addition, the bot will self-correct likely at unfavorable prices.
3. Fash parity loss: Flash crashes are nothing new. These events can occur at any time irrespective of market or exchange. Consider the case where the bot has entered a position with relative value 1.02. You are betting the relative value will revert to 1. What happens when this suddenly increases to 2 due to a flash crash? You could get liquidated as your overall subaccount colleteral suddenly (1.00) isn't sufficient to cover your short position (2.00). The more leverage (x2) you use, the lowever the relative value (1.5) needs to be before liquidation will take place. Mitigation of this risk is simple taking on not too much leverage. FTX liquidation mechanism reduces the liquidation severity. However, liquidation will remain painfull. (**Section to be reworked**)
4. Tax man
5. ...

Usage:
1. pip install -r requirements.txt
2. generate an external api key with external program 'deltazerotrades' from FTX (https://ftx.com/en/external-program-api-keys)
3. make a dedicated subaccount for the bot on FTX
4. config the config file (config as-is should be profitable)
5. set leverage on the dedicated subaccount equal or greater than the max leverage in the config file)
6. start trading
7. restart every 24h

tips-and-tricks:
1. make use of colocation (AWS Asia Pacific (Tokyo) Region)
2. automated restart based on CPU usage (if high, the websockets are down)



