from FTXclient import *
from Config import *
from BalancingFunctions import *
from Orders import *
from MarketMaker import *
import time
import threading


# PairTrader takes a spot-future pair and performs the strategy
# A seperate process is used for each pair (except rebase coins e.g. AMPL)


class PairTrader():
    # Initialization of variables to 0. Get changed after calling checkBalance function
    def __init__(self,future,spot_usd):
        self._future=future
        self._spot_usd=spot_usd
        self.spot_name=self._spot_usd

        self._futureBalance=0
        self._spotBalance=0
        self._balanceDifference=0
        self.excludePairs()

    # Exclusion of pairs the bot should not trade
    # It raises an error and the process is stopped indefinitly
    def excludePairs(self):
        if self._future.split('-')[0]=='AMPL':
            print('Ampleforth Exception')
            raise Exception('Ampleforth Exception')
        elif self._future.split('-')[1]!='PERP':
            print('PERP error')
            raise Exception('PERP error')
        if self._future.split('-')[0]=='OKB':
            print('OKB Exception')
            raise Exception('OKB exception')

    # Checks balances (spot) and positions (future) and calculates the difference (_balanceDifference)
    # This is used in the make_balancing_order function and can inhibit further positions to be build
    def check_balance(self):
        try:
            self._futureBalance=client.get_position(self._future)['netSize']
            spotBalances=client.get_balances()
            for x in spotBalances:
                try:
                    if x['coin']==self._future.split('-')[0]:
                        self._spotBalance=x['total']
                        break
                except Exception:
                    pass
                    print('failed at check_balance')

        except Exception:
            pass
        self._balanceDifference=self._futureBalance+self._spotBalance


    # Only fetched once!
    # Determines sizeIncrement, priceIncrement, future_Type,
    def fetch_data(self):
        self.future_data=client.get_future(self._future)
        self.spot_data=client.get_market(self._spot_usd)

        # Size increments futures and spots
        self.sizeIncrement=self.future_data['sizeIncrement']
        self.sizeIncrement_decimals=len(str(self.sizeIncrement).split('.')[0])
        self.spot_increment=self.spot_data['sizeIncrement']
        self.spot_size_increment_decimals=len(str(self.spot_increment).split('.')[0])
        

        # Price increments futures and spots
        self.price_increment=self.future_data['priceIncrement']
        self.price_increment_decimals=len(str(self.price_increment).split('.')[0])
        self.spot_price_increment=self.spot_data['priceIncrement']
        self.spot_price_increment_decimals=len(str(self.spot_price_increment).split('.')[0])

        # Use increment that can be used in both markets
        self.increment=max(self.sizeIncrement,self.spot_increment)
        self.priceIncrement=max(self.price_increment,self.spot_price_increment)

        # Gather decimals, usefull for rounding
        self.decimals=max(self.spot_size_increment_decimals,self.sizeIncrement_decimals)
        
        # Type of future (should always be 'PERP')
        self.future_type=self._future.split('-')[1]

        # Extra variables, might be usefull one day
        self.ratio=self.future_data['mark']/self.future_data['index'] 
        self.volumeUsd24h=self.future_data['volumeUsd24h']
        

        
        coins=client.get_coins()
        for x in coins:
            if x['id']==self._future.split('-')[0]:
                self.collateralWeight=x['collateralWeight'] 
                if self.collateralWeight<minimumCollateral:
                    print(self._future,'Collateral Weight is not sufficient')
                    raise Exception('No data')

    #Starting both sockets and datastream
    def web_socket_start(self):
        time.sleep(0.5)
        self.future_stream=self.client_socket.get_ticker(self._future)
        self.spot_stream=self.client_socket.get_ticker(self.spot_name)
        time.sleep(1)
        self.spot_stream=self.client_socket.get_ticker(self.spot_name)
        self.future_stream=self.client_socket.get_ticker(self._future)
        time.sleep(1)

    def web_socket_ready(self):
        self.spot_stream=self.client_socket.get_ticker(self.spot_name)
        self.future_stream=self.client_socket.get_ticker(self._future)


    def calculate_potential(self):
        self.future_ask=self.future_stream['ask']
        self.future_askSize=self.future_stream['askSize']
        self.future_bid=self.future_stream['bid']
        self.future_bidSize=self.future_stream['bidSize']
        self.future_time=self.future_stream['time']

        self.spot_ask=self.spot_stream['ask']
        self.spot_askSize=self.spot_stream['askSize']
        self.spot_bid=self.spot_stream['bid']
        self.spot_bidSize=self.spot_stream['bidSize']
        self.spot_time=self.spot_stream['time']

        #Sell high future price, buy low spot price
        self.ratioBid=self.future_bid/self.spot_ask

        #Buy Low Future, sell high spot
        self.ratioAsk=self.future_ask/self.spot_bid

    
    # Sell at a worse price, for better excecution
    def discountedPrice(self, price):
        multiplier=1/self.price_increment
        if self.price_increment<0:
            count=len(str(self.price_increment).split('.')[0])
            p=round(multiplier*price/PriceDiscount,count)/multiplier
        else:
            count=0
            p=round(multiplier*price/PriceDiscount,count)/multiplier
        return p

    # Buy at a worse price, for better excecution
    def premiumPrice(self, price):
        multiplier=1/self.price_increment
        if self.price_increment<0:
            count=len(str(self.price_increment).split('.')[0])
            p=round(multiplier*price*PriceDiscount,count)/multiplier
        else:
            count=0
            p=round(multiplier*price*PriceDiscount,count)/multiplier
        return p

    def Build_position_perp(self,RatioThreshold=RatioThreshold, RatioThreshold2=RatioThreshold2, RatioThreshold3=RatioThreshold3,RatioThreshold4=RatioThreshold4):
        # Not wasting resources on pairs that are not that tradable:
        if self.ratioBid<0.99 and self.ratioAsk>1.02:
            time.sleep(60)

        # We want to make sure the difference of the spot balance and future position is close to zero before building additional postion
        if self.future_type=='PERP' and self._balanceDifference>=-self.increment*10 and self._balanceDifference<=self.spot_increment*10 :
            
            # Calculating ratioBid again but taking into account the value of the collateral. The less collateral the more punishment.
            self.ratioBidWeight=1+(self.ratioBid-1)*((1+self.collateralWeight)/2)

            # Calculating ratioBid again but taking into account the current spread between the ratioBid and the ratioAsk. RatioBid is where we enter the trade and ratioAsk, where we exit. 
            # Previously it took out cases I did not want to trade 
            # (Would be better to use historical spread data)
            spread=(1+self.ratioAsk-self.ratioBid)
            self.ratioBidWeight=self.ratioBidWeight/spread

            if self.leverage<leverage1 and self.ratioBidWeight>RatioThreshold:
                sellFuture(self)

            elif leverage2>self.leverage>=leverage1 and self.ratioBidWeight>RatioThreshold2:
                sellFuture(self)

            elif leverage3>self.leverage>=leverage2 and self.ratioBidWeight>RatioThreshold3:
                sellFuture(self)
            
            elif leverage4>self.leverage>=leverage3 and self.ratioBidWeight>RatioThreshold4:
                sellFuture(self)
            
    def Liquidate_position_perp(self,RatioThreshold=LiquidationRatio):
        # We make sure there are futures (<0) to liquidate
        # Need to add condition for spot as well !!
        if self.future_type=='PERP' and self._futureBalance<0:
            if self.ratioAsk<RatioThreshold:
                buyFuture(self)

    # Test if tradable, if not, exception and process is stopped
    def test_trade(self):
        self.fetch_data()
        self.test_result=True


    def go_trade(self):
        self.client_socket=FtxWebsocketClient()
        self.client_socket.connect()


        self.fetch_data()

        # Check leverage of account
        info=client.get_account_info()
        self.accountValue=info['totalAccountValue']
        self.positionSize=info['totalPositionSize']
        self.leverage=self.positionSize/self.accountValue
        self.leverage=self.positionSize/self.accountValue


        self.web_socket_start()
        print('Started datastream')
        while True:
            try:
                # Keep websocket alive? Might be redundant
                self.web_socket_ready()

                # Calculates potential 
                self.calculate_potential()
                
                # Check datastream timestamps for up-to-date data
                previous_time_future=self.future_time
                previous_time_spot=self.spot_time
                while self.future_time==previous_time_future or self.spot_time==previous_time_spot:
                    self.web_socket_ready()
                    self.calculate_potential()
                    time.sleep(0.000001)

                # Building and liquidation function
                self.Build_position_perp()
                self.Liquidate_position_perp() 

                #Leave some time for FTX to update balances after a possible trade
                time.sleep(0.05)       
                self.check_balance()
                self.web_socket_ready()
                self.calculate_potential()
                make_balancing_order(self)

                # Make Market Maker move
                

                try:
                    # Update leverage again
                    info=client.get_account_info()
                    self.accountValue=info['totalAccountValue']
                    self.positionSize=info['totalPositionSize']
                    self.leverage=self.positionSize/self.accountValue
                except Exception:
                    pass
            except Exception as e:
                print(self._future, 'Failed at main function')
                print(e)
                pass
