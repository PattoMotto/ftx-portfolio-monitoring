import ccxt
import json
import pandas as pd

class ExchangeClient:
  def __init__(self, exchange):
    self.exchange = exchange

  def getSubaccounts(self):
    return self.exchange.private_get_subaccounts()['result']

  def getWalletBalance(self):
    return self.exchange.fetch_balance()
