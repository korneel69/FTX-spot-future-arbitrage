# Subaccount to trade under
subaccount_name='XXX'

# api-keys to be generated from https://ftx.com/en/external-program-api-keys
external_api_key="2FUmI45_XVwSxyx1xxxxxxx"
external_api_secret="a_mO0kIt8xxxxxxxxxxx"

# Remember relative prices. RatioBid levels the bot builds a position at. The higher the leverage the subaccount currently uses, the higher we want the payoff to be to take on extra risk.
RatioThreshold=1.003
RatioThreshold2=1.006
RatioThreshold3=1.008
RatioThreshold4=1.015

# Leverage levels that determine the needed RatioBid levels
leverage1=4
leverage2=6
leverage3=7
leverage4=10

# RatioAsk level: when to sell
LiquidationRatio=0.999
LiquidationRatioThreshold2=0.9965

# Better execution by liquidating position at a worse price, avoids balancing when liquidation is partially successfull
PriceDiscount=1.001

# Maximum USD order value
MaxOrderValue=100
MaxLiquidationValue=100

# Minimum collateral of spot
minimumCollateral=0

# Volume requirement for spot lending
volume_requirement=1000000

