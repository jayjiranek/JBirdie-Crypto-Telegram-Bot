from pydoc import cli
import kucoinSecrets
from kucoin.client import Client

# create kucoin client
client = Client(kucoinSecrets.api_key, kucoinSecrets.api_secret, kucoinSecrets.api_passphrase)

# get price
def getPrice(coin):
    symbol = f'{coin}-USDT'
    result = client.get_ticker(symbol)
    price = float(result['price'])
    return price


# get trade balance for a coin
def getTradeBalance(coin):
    result = client.get_accounts(coin, account_type='trade')
    amount = float(result[0]['available'])
    return amount

# get USDT amount available to trade
def getTetherBalance():
    result = client.get_accounts('USDT', account_type='trade')
    amount = float(result[0]['available'])
    return amount

# return all the coins in portfolio
def getPortfolio():
    portfolio = []
    result = client.get_accounts(account_type='trade')
    for x in result:
        balance = float(x['balance'])
        if balance > 0.05:
            portfolio.append(x['currency'])
    return portfolio


# get usd value of coin holding
def getUSDValue(coin):
    price = getPrice(coin)
    amt = getTradeBalance(coin)
    usdV = price * amt
    usdVR = round(usdV, 2)
    return usdVR

# get 24 change amount %
def get24Rate(coin):
    symbol = f'{coin}-USDT'
    result = client.get_24hr_stats(symbol=symbol)
    dayChangeRate = result["changeRate"]
    changeRate = float(dayChangeRate) * 100
    roundRate = round(changeRate, 2)
    return roundRate


# TO-DO: BUY and SELL METHODS

# buy a coin
def buyCoin(coin, amount):
    symbol = f'{coin}-USDT'
    usdtAvail = getTetherBalance()
    purchaseAmt = float(amount)
    purchaseStr = ''
    if usdtAvail > purchaseAmt:
        order = client.create_market_order(symbol=symbol, side='buy', size=purchaseAmt)
        purchaseStr += f'Purchase complete\n\n{purchaseAmt} of ${coin} has added to your wallet!'
    else:
        purchaseStr += 'You do not have enough USDT to complete this purchase...'

    return purchaseStr

# add for x USDT
def sellCoin(coin, amount):
    symbol = f'{coin}-USDT'
    # amtOwned = getTradeBalance(coin)
    sellAmt = float(amount)
    # order = client.create_market_order(symbol=symbol, side='sell', size=sellAmt)
    sellStr = f'Sale complete.\n\nSold {sellAmt} of ${coin}'

    return sellStr

    

