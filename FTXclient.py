import ftx
from client import FtxWebsocketClient
from Config import *
import time

client = ftx.FtxClient(api_key=external_api_key, api_secret=external_api_secret,subaccount_name=subaccount_name)
client_socket=FtxWebsocketClient()
client_socket.connect()