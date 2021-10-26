# API information: https://docs.ftx.com/
# Licence: "dont copy please" @2021
import ftx
import datetime
import json
import time
from multiprocessing import Process, Array, Manager,Pool
import multiprocessing
from client import FtxWebsocketClient
import threading
from PairTrader import PairTrader
from FTXclient import *


# HoofdTrader is a trader that queries all markets on ftx and aims to find tradable pairs based on conditions:
# - Availability of both future perp and spot market
# - Spot can be used as collateral for future perp positions
# 
# When pairs have been identified, HoofdTrader class is used to spin up instances of PairTrader class


class HoofdTrader:
    def __init__(self):
        pass

    def fetch_data(self):
        self._future_markets_data=client.get_futures()
        self._funding_markets_data=client.get_funding_rates()
        self._spot_markets_data=client.get_markets()

    #Match Future to Spot market: create pair 
    def find_future_symbols(self):
        symbol_list=[]
        for symbol in self._future_markets_data:
            symbol_list.append(symbol['name'])
        self._future_symbol_list=symbol_list
        return self._future_symbol_list

    def find_spot_symbols(self):
        symbol_list=[]
        for symbol in self._spot_markets_data:
            symbol_list.append(symbol['name'])
        self._spot_symbol_list=symbol_list
        return self._spot_symbol_list
    
    #loopup table based on future namme
    def make_spot_usd(self):                            
        spot_usd=[]
        for symbol in self._future_symbol_list:
            symbol_usd=symbol.split('-')[0]+'/USD'
            spot_usd.append(symbol_usd)
        self._spot_usd_list=spot_usd
        return self._spot_usd_list

    def match_spot_future(self):
        match_list=dict(zip(self._future_symbol_list,self._spot_usd_list))
        self._match_list=match_list
        return self._match_list
        
    def allocate_pairs(self):
        trader_list=[]
        for future in self._match_list.keys():
            spot=self._match_list[future]
            g=[future,spot]
            trader_list.append(g)
        self.trader_list=trader_list

# HoofdTrader spins up child processes to handle each pair
if __name__=='__main__':

    jef=HoofdTrader()
    jef.__init__()
    jef.fetch_data()
    jef.find_future_symbols()
    jef.find_spot_symbols()
    jef.make_spot_usd()
    jef.match_spot_future()
    jef.allocate_pairs()
    traders_list=[]
    active_traders=[]
    processes=[]

    # Make a traders_list based on the trader_list of HoofdTrader instance
    # Filters out all futures that are no PERPetual futures
    for pair in jef.trader_list:
        try:
            if pair[0].split('-')[1]=='PERP':
                trader=PairTrader(pair[0],pair[1])
                traders_list.append(trader)
        except Exception:
            pass
    
    # Test for pairs with perpetual future and spot market
    for trader in traders_list:
        try:
            trader.test_trade()
            active_traders.append(trader)
        except Exception:
            print(trader._future, 'No spot market, thus excepted!')
            pass
    
    for i in active_traders:
        processes.append(multiprocessing.Process(target=i.go_trade))
    for p in processes:
        time.sleep(0.25)
        p.start()
        


