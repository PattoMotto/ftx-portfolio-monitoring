import ccxt
import json
import pandas as pd

class ExchangeClient:
  def __init__(self, exchange):
    self.exchange = exchange

  def getSubaccounts(self):
    return self.exchange.private_get_subaccounts()['result']

  def getAccount(self):
    account = self.exchange.private_get_account()['result']
    for k, v in account.items():
      if self.is_convertible_to_float(v):
        account[k] = float(v)
    return account

  def cancelAllOrders(self, pair=None):
    self.exchange.cancelAllOrders(symbol=pair)

  def cancelOrder(self, orderId):
    result = self.exchange.cancelOrder(id=orderId)
    return result['success'] if 'success' in result else False

  def getTicker(self, pair):
    try:
      r1 = json.dumps(self.exchange.fetch_ticker(pair))
      dataPrice = json.loads(r1)
    except ccxt.NetworkError as e:
      r1 = json.dumps(self.exchange.fetch_ticker(pair))
      dataPrice = json.loads(r1)
    except ccxt.ExchangeError as e:
      r1 = json.dumps(self.exchange.fetch_ticker(pair))
      dataPrice = json.loads(r1)
    except Exception as e:
      r1 = json.dumps(self.exchange.fetch_ticker(pair))
      dataPrice = json.loads(r1)
    return {
      'price': dataPrice['last'],
      'bid': dataPrice['bid'],
      'ask': dataPrice['ask'],
      'minOrder': float(dataPrice['info']['minProvideSize']),
    }

  def fetchOrder(self, orderId):
    return self.exchange.fetchOrder(orderId)
  
  def getOrders(self, pair, limit=None):
    return self.getOrdersDataframe(self.exchange.fetchOrders(symbol=pair, limit=limit))

  def getTrades(self, pair, limit=None):
    # "timestamp":1621870087485,
    # "datetime":"2021-05-24T15:28:07.485Z",
    # "symbol":"RAY/USD",
    # "id":"2339054923",
    # "order":"51524551360",
    # "type":"None",
    # "takerOrMaker":"maker",
    # "side":"sell",
    # "price":4.294,
    # "amount":1.0,
    # "cost":4.294,
    # "fee":{
    #     "cost":-0.0004294,
    #     "currency":"USD",
    #     "rate":-0.0001
    # }
    fields = ['timestamp', 'datetime', 'symbol', 'id', 'order', 'takerOrMaker', 'side', 'price', 'amount', 'cost', 'fee.cost', 'fee.currency', 'fee.rate']
    trades = self.exchange.fetch_my_trades(symbol=pair, limit=limit)
    tradesDf = pd.json_normalize(trades)
    if not tradesDf.empty:
      for columnName in ['price', 'amount', 'cost', 'fee.cost', 'fee.rate']:
        tradesDf[columnName] = tradesDf[columnName].astype(float)
      tradesDf['datetime'] = pd.to_datetime(tradesDf['timestamp'], unit='ms')
      return tradesDf[fields]
    return tradesDf

  def getOHLC(self, pair, timeframe, count):  # นำขั้นตอนการเรียกข้อมุล ohlc มารวมเป็น function เพื่อเรียกใช้งานได้เรื่อยๆ
    # 5m 1h 1d
    if self.exchange.has['fetchOHLCV']:
        try:  # try/except ใช้แก้ error : Connection aborted https://github.com/ccxt/ccxt/wiki/Manual#error-handling
            ohlc = self.exchange.fetch_ohlcv(pair, timeframe, limit=count)
            # print(ohlc)
        except ccxt.NetworkError as e:
            print(self.exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
            ohlc = self.exchange.fetch_ohlcv(pair, timeframe, limit=count)
            # retry or whatever

        except ccxt.ExchangeError as e:
            print(self.exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
            ohlc = self.exchange.fetch_ohlcv(pair, timeframe, limit=count)
            # retry or whatever

        except Exception as e:
            print(self.exchange.id, 'fetch_ohlcv failed with:', str(e))
            ohlc = self.exchange.fetch_ohlcv(pair, timeframe, limit=count)
            # retry or whatever

        ohlcDf = pd.DataFrame(ohlc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        ohlcDf['datetime'] = pd.to_datetime(ohlcDf['datetime'], unit='ms')
    return ohlcDf

  def getOrdersDataframe(self, orderList):
      # "id":"51868070885",
      # "clientOrderId":"None",
      # "timestamp":1621961095081,
      # "datetime":"2021-05-25T16:44:55.081Z",
      # "lastTradeTimestamp":"None",
      # "symbol":"RAY/USD",
      # "type":"limit",
      # "timeInForce":"None",
      # "postOnly":false,
      # "side":"buy",
      # "price":2.5,
      # "stopPrice":"None",
      # "amount":1.0,
      # "cost":0.0,
      # "average":"None",
      # "filled":0.0,
      # "remaining":1.0,
      # "status":"open",
      # "fee":"None",
      # "trades":"None"
    columns = ['id', 'timestamp','datetime','status','symbol','type', 'timeInForce', 'postOnly','side','price', 'stopPrice','amount','filled','average','remaining']
    pendingOrders = pd.DataFrame(orderList, columns=columns)
    pendingOrders['datetime'] = pd.to_datetime(pendingOrders['timestamp'], unit='ms')
    for columnName in ['price', 'stopPrice','amount','filled','average','remaining']:
      pendingOrders[columnName] = pendingOrders[columnName].astype(float)
    return pendingOrders

  def getPendingOrders(self, pair):
    return self.getOrdersDataframe(self.exchange.fetch_open_orders(pair))

  def getWalletBalance(self):
    return self.exchange.fetch_balance()

  def getBalance(self, tokenCode):
    balance = self.exchange.fetch_balance()
    if tokenCode in balance:
      return balance[tokenCode]['total']
    else:
      return 0.0

  def getLiquidity(self, tokenCode):
    balance = self.exchange.fetch_balance()
    if tokenCode in balance:
      return balance[tokenCode]['free']
    else:
      return 0.0

  def getFreeCollateral(self):
    account = self.getAccount()
    return account['freeCollateral']
  
  def getLongPosition(self, symbol):
    position = self.getPosition(symbol)
    if position is None:
      return 0
    elif position['side'] == 'buy':
      return position['size']
    else:
      return 0

  def getPosition(self, symbol):
    positions = self.exchange.fetch_positions(symbols=symbol)
    filteredPosition = list(filter(lambda element: element['future'] == symbol, positions))
    if len(filteredPosition) == 1:
      position = filteredPosition[0]
      for k, v in position.items():
        if self.is_convertible_to_float(v):
          position[k] = float(v)
      return position
    else:
      return None

  def sendOrder(self, pair, isLimitOrder, price, orderSize, isBuyOrder, reduceOnly = False):
    orderType = 'limit' if isLimitOrder else 'market'
    side = 'buy' if isBuyOrder else 'sell'                           # กำหนดฝั่ง BUY/SELL
    postOnly =  isLimitOrder                # วางโพซิชั่นเป็น MAKER เท่านั้น (TRUE = only MAKER, default = false)
    ioc = False                             # immidate or cancel เช่น ส่งคำสั่งไป Long 1000 market 
                                            # ถ้าไม่ได้ 1000 ก็ไม่เอา เช่นอาจจะเป็น 500 สองตัวก็ไม่เอา
    ## Send Order ##
    # print(pair, orderType , side, orderSize, price, {'postOnly': postOnly, 'reduceOnly': reduceOnly})
    # return None
    order = self.exchange.create_order(
      symbol=pair, 
      type=orderType, 
      side=side, 
      amount=orderSize, 
      price=price, 
      params={'postOnly': postOnly, 'reduceOnly': reduceOnly}
    )
    return order

  def lendAsset(self, coin, size, rate):
    self.exchange.private_post_spot_margin_offers({
      'coin': coin,
      'size': size,
      'rate': rate
    })
  
  def getLendingInfo(self):
    return self.exchange.private_get_spot_margin_lending_info()
  
  def getLendingRates(self):
    return self.exchange.private_get_spot_margin_lending_rates()

  def is_convertible_to_float(self, value):
    try:
      float(value)
      return True
    except:
      return False