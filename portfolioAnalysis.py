import portfolioGlobals
from kucoinValues import *


# analyze the portfolio
def analyzePortfolio():
    portfolio = getPortfolio()
    coinsVal = {}
    coinsGaming = portfolioGlobals.gamingCoins
    coinsPayment = portfolioGlobals.largePaymentCoins
    coinsPlatform = portfolioGlobals.largePlatformCoins
    coinsStable = portfolioGlobals.stableCoins
    for x in portfolio:
        usdAmt = getUSDValue(x)
        portfolioGlobals.totalVal += usdAmt
        coinsVal[x] = usdAmt

    # find value of major currencies: btc, eth 
    # should be > 50%
    btc = 'BTC'
    eth = 'ETH'
    if btc in coinsVal:
        tempVal = coinsVal['BTC']
        portfolioGlobals.majorCurrencies += tempVal
    if eth in coinsVal:
        tempVal = coinsVal['ETH']
        portfolioGlobals.majorCurrencies += tempVal

    # find value of all gaming coins
    for x in coinsGaming:
        if x in coinsVal:
            tempVal = coinsVal[x]
            portfolioGlobals.gamingVal +=  tempVal

    # find value for large cap payment coins
    for x in coinsPayment:
        if x in coinsVal:
            tempVal = coinsVal[x]
            portfolioGlobals.largePaymentVal += tempVal
    
    # find value for large cap platform coins
    for x in coinsPlatform:
        if x in coinsVal:
            tempVal = coinsVal[x]
            portfolioGlobals.largePlatformVal += tempVal

    # find value for large cap platform coins
    for x in coinsStable:
        if x in coinsVal:
            tempVal = coinsVal[x]
            portfolioGlobals.stableCoinVal += tempVal


    # set portfolio percentages btech globals
    portfolioGlobals.majorPercent = round((portfolioGlobals.majorCurrencies / portfolioGlobals.totalVal) * 100.0, 2)
    portfolioGlobals.gamingPercent = round((portfolioGlobals.gamingVal / portfolioGlobals.totalVal) * 100.0, 2)
    portfolioGlobals.paymentPercent = round((portfolioGlobals.largePaymentVal / portfolioGlobals.totalVal) * 100.0, 2)
    portfolioGlobals.platformPercent = round((portfolioGlobals.largePlatformVal / portfolioGlobals.totalVal) * 100.0, 2)
    portfolioGlobals.stablePercent = round((portfolioGlobals.stableCoinVal / portfolioGlobals.totalVal) * 100.0, 2)