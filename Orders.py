from Config import *
from FTXclient import *
import threading


# Called by build_position_perp function
# Sell Future, Buy Spot
def sellFuture(self):
    increment=self.increment
    size=self.increment
    decimals=self.decimals
    priceIncrement=self.priceIncrement

    # Look at orderbook, determine Max possible size of trade (logging purpose)
    sizeMAX=min(self.future_bidSize, self.spot_askSize)

    # Look at orderbook, determine the size the bot will trade
    # Taking into account the MaxOrderValue
    sizeMin=min(self.future_bidSize, self.spot_askSize,round(MaxOrderValue/self.future_bid,decimals))
    size=(sizeMin//increment)*increment

    # Sanity check: trade size positive and higher or equal to increment
    if size<self.increment:
        size=self.increment

    # Sanity check 2: bid and size on markets higher or equal to increment 
    if self.future_bidSize>=increment and self.spot_askSize>=increment:
        t0=time.time()
        try:
            # Multithreading: sending out two orders at once
            # discountedPrice: get better executing by selling/buying at a worse price. This does not mean that the order always sells at a worse price. The order hits the orderbook and the order gets filled at the most favourable price. 
            # IOC: instant or cancel = true
            # reduce only order= false
            order1=threading.Thread(target=client.place_order, args=(self._future,'sell',self.discountedPrice(price=self.future_bid), size,'limit',False, True))
            order1.start()
            order2=threading.Thread(target=client.place_order, args=(self.spot_name,'buy',self.premiumPrice(price=self.spot_ask), size,'limit',False, True))
            order2.start()
            order1.join()
            order2.join()
        except Exception:
            print(self._future,'Position building failed')
        t1=time.time()
        print('Building',self._future,'| balance future vs spot: ',self._futureBalance,self._spotBalance,'| ratioBid: ' ,self.ratioBid,'| order size vs max size:' ,size,'/' ,sizeMAX,'| order price future vs spot ',  self.discountedPrice(price=self.future_bid), self.premiumPrice(price=self.spot_ask),'| Excecution time: ',t1-t0)
        return True

def buyFuture(self):
    #Determine size of bet!!!!!!!
    increment=self.increment
    size=self.increment
    decimals=self.decimals
    priceIncrement=self.priceIncrement

    # Look at orderbook, determine Max possible size of trade (logging purpose)
    sizeMAX=min(self.future_askSize, self.spot_bidSize)

    # Look at orderbook, determine the size the bot will trade
    # Taking into account the MaxOrderValue                
    sizeMin=min(self.future_askSize, self.spot_bidSize,round(MaxLiquidationValue/self.future_ask,decimals))
    size=(sizeMin//increment)*increment

    # Sanity check: if the trade size is higher than the future position we have, reduce size to future position
    if sizeMin>abs(self._futureBalance):
        size=abs(self._futureBalance)

    # Sanity check 2: size should be positive
    if size<self.increment:
        size=self.increment

    # Sanity check 3: future ask and spot bid size on markets higher or equal to increment, not lower
    if self.future_askSize>=increment and self.spot_bidSize>=increment:
        try:
            # Multithreading: sending out two orders at once
            # discountedPrice: get better executing by selling/buying at a worse price. This does not mean that the order always sells/buys at a worse price. The order hits the orderbook and the order gets filled at the most favourable price. 
            # IOC: instant or cancel = true
            # reduce only order= True (False for spot since not an option in spot markets)
            t0=time.time()
            order1=threading.Thread(target=client.place_order, args=(self.spot_name,'sell',self.discountedPrice(price=self.spot_bid), size,'limit',False,True))
            order1.start()
            order2=threading.Thread(target=client.place_order, args=(self._future,'buy',self.premiumPrice(price=self.future_ask), size,'limit',True, True))
            order2.start()
            order1.join()
            order2.join()
            t1=time.time()          
            print('Liquidating',self._future,'| balance future vs spot: ',self._futureBalance,self._spotBalance,'| ratioAsk: ', self.ratioAsk,'| order size vs max size:' ,size,'/',sizeMAX, '| order price future vs spot ', self.discountedPrice(price=self.future_ask), self.premiumPrice(price=self.spot_bid),'| Excecution time: ',t1-t0)
            print('-------------------------------------------------------------------------')
        except Exception:
            print(self._future, 'Liquidation error')
    return True