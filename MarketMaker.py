# First iteration only with no lending spot

# Cast orders to liquidate position faster
# For each build position: sell spot at x% higher and buy future at y% lower than current price.

# Requirements:
# - Present position
# - bid prices of futures
# - ask prices of spots
# - When the pairTrader spots an opportunity, it should still be able to act to it


# Solution:
# - Get balance spot
# - Make sure the spot balance is higher than the maximumTradeValue of PairTrader, to make sure pairTrader can make a trade when it wants
# - Get ask price of spot
# - If the balance of spot is higher than 0, then cast sell orders
# --- Given a certain ask price of the spot, cast order at x% higher
#
# - Each cycle
# --- When the price changes, update the orderprice accordingly (does not count for FTX order limit per minute)
# --- When the balance changes to below the maximumTradeValue of PairTrader, cancel the order
# 


# Remarks:
# - available balance cash or spot impacted when casting orders?
# --- If this is the case, then we might not be able to build or liquidate our positions like we did without order casting
# --- Yes, there is an impact on available balance. This does have an impact on the free collateral field!
# ------ What are the implications of lower free collateral? 
#
#
# - Websocket price feed needs to be trustworthy!
#
# - When an order that is cast is filled, the balancingFunction will kick in to correct the position 