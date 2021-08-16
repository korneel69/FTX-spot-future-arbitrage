from FTXclient import *

# Balancing helper functions
def balance_order_buy_spot(self,multiplier):
    size=self.spot_increment
    order2=client.place_order(self.spot_name,side='buy',price=self.spot_ask, size=size*multiplier,type='limit',ioc=True)
    print('Balancing: buy spot',self._future,'| balance future vs spot: ',self._futureBalance,self._spotBalance,'| price: ',self.spot_ask,'| size: ',size)

def balance_order_buy_future(self,multiplier):
    size=self.sizeIncrement
    order2=client.place_order(self._future,side='buy',price=self.future_ask, size=size*multiplier,type='limit',ioc=True)
    print('Balancing: buy future',self._future,'| balance future vs spot: ',self._futureBalance,self._spotBalance,'| price: ',self.future_ask,'| size: ',size)

def balance_order_sell_spot(self,multiplier):
    size=self.spot_increment
    order2=client.place_order(self.spot_name,side='sell',price=self.spot_bid, size=size*multiplier,type='limit',ioc=True)
    print('Balancing: sell spot',self._future,'| balance future vs spot: ',self._futureBalance,self._spotBalance,'| price: ',self.spot_bid,'| size: ',size)

def balance_order_sell_future(self,multiplier):
    size=self.sizeIncrement
    order2=client.place_order(self._future,side='sell',price=self.future_bid, size=size*multiplier,type='limit',ioc=True)
    print('Balancing: sell future',self._future,'| balance future vs spot: ',self._futureBalance,self._spotBalance,'| price: ',self.future_bid,'| size: ',size)

# If _balanceDifference is negative, there are more futures sold than spot bought
# If _balanceDifference is positive, there are less futures sold than spot bought
# We balance based on the price that is the most affordable
# Three different order sizes can be used (multiplier1 -> 3)
def make_balancing_order(self):
        multiplier1=100
        multiplier2=10
        multiplier3=1
        if self._balanceDifference<=-1*self.sizeIncrement:
            if self.spot_ask<self.future_bid:
                try:
                    if self._balanceDifference<=-multiplier1*self.spot_increment:
                        balance_order_buy_spot(self, multiplier=multiplier1)
                    elif self._balanceDifference<=-multiplier2*self.spot_increment:
                        balance_order_buy_spot(self, multiplier=multiplier2)
                    elif self._balanceDifference<=-multiplier3*self.spot_increment:
                        balance_order_buy_spot(self, multiplier=multiplier3)
                except Exception:
                    print('spot exception')
            elif self.spot_ask>=self.future_bid:
                try:                
                    if self._balanceDifference<=-multiplier1*self.sizeIncrement:
                        balance_order_buy_future(self,multiplier=multiplier1)
                    elif self._balanceDifference<=-multiplier2*self.sizeIncrement:
                        balance_order_buy_future(self,multiplier=multiplier2)
                    elif self._balanceDifference<=-multiplier3*self.sizeIncrement:
                        balance_order_buy_future(self,multiplier=multiplier3)
                except Exception:
                    print('future exception')        
                    
        elif self._balanceDifference>1*self.spot_increment:
            if self.spot_bid<self.future_ask:
                try:    
                    if self._balanceDifference>=multiplier1*self.spot_increment:
                        balance_order_sell_spot(self, multiplier=multiplier1)
                    elif self._balanceDifference>=multiplier2*self.spot_increment:
                        balance_order_sell_spot(self, multiplier=multiplier2)
                    elif self._balanceDifference>=multiplier3*self.spot_increment:
                        balance_order_sell_spot(self, multiplier=multiplier3)
                except Exception:
                    print('spot exception')
            elif self.spot_bid>=self.future_ask:
                try:                
                    if self._balanceDifference>=multiplier1*self.sizeIncrement:
                        balance_order_sell_future(self,multiplier=multiplier1)
                    elif self._balanceDifference>=multiplier2*self.sizeIncrement:
                        balance_order_sell_future(self,multiplier=multiplier2)
                    elif self._balanceDifference>=multiplier3*self.sizeIncrement:
                        balance_order_sell_future(self,multiplier=multiplier3)
                except Exception:
                    print('future exception')  

        # Liquidates spot balance if it is lower than the min amount tradable via over-the-counter trade
        if self._futureBalance==0 and 0<self._spotBalance<self.spot_increment:
            print(self._future, 'Balancing error. Future balance=', self._futureBalance, ' and Spotbalance=', self._spotBalance)
            if self._spotBalance<self.spot_increment and self._futureBalance==0:
                try:
                    b=client.request_quote(self.spot_name.split('/')[0], 'USD', self._spotBalance)
                    time.sleep(1.5)
                    a=client.accept_quote(b['quoteId'])
                    print('Quote Accepted', a)
                    pass
                except Exception:
                    pass
