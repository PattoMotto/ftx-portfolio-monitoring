import pandas as pd
import gsheetHelper as gsheet
from exchangeClient import ExchangeClient
import ccxt
import time, os, sys
from datetime import datetime

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
summarySheetName = 'summary'
historySheetName = 'history'

class PortfolioMonitoringBot:
    def __init__(self, apiKey, secret, gSheetName):
        self.apiKey = apiKey
        self.secret = secret
        self.gSheetName = gSheetName
        self.initialize()

    def initialize(self):
        self.mainExchangeClient = self.getExchangeClient(
            apiKey=self.apiKey,
            secret=self.secret
        )
        subaccounts = self.mainExchangeClient.getSubaccounts()
        nicknames = []
        for subaccount in subaccounts:
            nicknames.append(subaccount['nickname'])
        self.subaccounts = nicknames

    def loop(self):
        try:
            clearConsole()
            wallets = {'main': self.getWalletData(self.mainExchangeClient)}
            for subaccount in self.subaccounts:
                exchangeClient = self.getExchangeClient(
                    apiKey=self.apiKey, 
                    secret=self.secret, 
                    subaccount=subaccount
                )
                wallets[subaccount] = self.getWalletData(exchangeClient)
                time.sleep(0.1)
            toBeRemoved = []
            for subaccount in wallets.keys():
                if len(wallets[subaccount]) == 0:
                    toBeRemoved.append(subaccount)
            for subaccount in toBeRemoved:
                del wallets[subaccount]
            summary = []
            history = {}
            for subaccount in wallets.keys():
                walletTotalUSD = 0
                coins = wallets[subaccount]
                dataframe = pd.DataFrame(coins)
                print(dataframe)
                self.writeRecord(subaccount, dataframe)
                for index in range(0, len(coins)):
                    coins[index]['subaccount'] = subaccount
                    walletTotalUSD += float(coins[index]['usdValue'])
                summary += coins
                history[subaccount] = walletTotalUSD
                time.sleep(0.1)
            now = datetime.now()
            history['time'] = now.isoformat()
            self.writeRecord(summarySheetName, pd.DataFrame(summary))
            self.addHistory(historySheetName, history)
        except Exception as e:
            exc_type, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)

    def getWalletData(self, exchangeClient):
        wallet = exchangeClient.getWalletBalance()['info']['result']
        return list(filter(self.nonZeroValue, wallet))

    def nonZeroValue(self, data):
        return float(data['total']) != 0

    def getExchangeClient(self, apiKey, secret, subaccount = None):
        # Exchange Detail
        exchange = ccxt.ftx({ 'apiKey': apiKey ,'secret': secret ,'enableRateLimit': True })

        # Sub Account Check
        if subaccount is not None:
            exchange.headers = { 'FTX-SUBACCOUNT': subaccount }

        return ExchangeClient(exchange)

    def addHistory(self, worksheetName, history):
        dataframe = gsheet.readWorksheet(fileName=self.gSheetName, worksheetName=worksheetName)
        if dataframe.empty:
            dataframe = pd.DataFrame([history])
        else:
            dataframe = gsheet.setFirstRowAsColumn(dataframe)
            dataframe = dataframe.append(history, ignore_index=True)
        gsheet.writeDataFrame(dataframe, fileName=self.gSheetName, worksheetName=worksheetName)

    def writeRecord(self, worksheetName, dataframe):
        gsheet.writeDataFrame(dataframe, fileName=self.gSheetName, worksheetName=worksheetName)
