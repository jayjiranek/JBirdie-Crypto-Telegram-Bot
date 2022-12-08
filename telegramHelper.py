from kucoinValues import *
from marketData import *
import portfolioGlobals
from portfolioAnalysis import *
from technicalsClient import *
# return first string that will be sent to user
def getIntroStr():
    introStr = 'The market is'
    change_percent = getMarket24()
    if change_percent > 0.0:
        introStr += f' up {change_percent}% in the last 24h\n'
    else:
        introStr += f' down {change_percent}% in the last 24h\n'
    introStr += '\nSend /analyzeWatchlist to get my recommendations on your watchlist.\n'
    introStr += '\nSend /analyzePortfolio to get my recommendations on your portfolio.\n'
    return introStr

# market section....

# category performance
# TO-DO: IMPROVE THIS SECTION
def categoryOverview():
    overviewStr = ''
    category_score = getCategoryPerformance()
    for x, y in category_score.items():
        overviewStr += x + ': ' + str(y) + '%\n'
    # print(overviewStr)
    return overviewStr

# Market top ten coins
def getMarketTopCoins():
    coinStr = getTopTenCoins()
    return coinStr

# return a coin that was searched
def getCoin(coin):
    price = getPrice(coin)
    dayChange = get24Rate(coin)
    balance = getTradeBalance(coin)
    if price > 0:
        coinStr = f'${coin}\n  24hr change: +{dayChange}%\n  Current Price: ${price}\n'
    else:
        coinStr = f'${coin}\n  24hr change: {dayChange}%\n  Current Price: ${price}\n'

    if balance > 0.005:
        coinStr += f'  Balance: {balance}'
    else:
        coinStr += f'  Balance: None'
    return coinStr

# PORTFOLIO SECTION 

# get entire portfolio
def getWholePortfolio():
    portfolio = getPortfolio()
    portStr = "\n\nHere is your breakdown of your portfolio..."
    numCoins = len(portfolio)
    totalVal = 0.0
    total24 = 0.0
    for x in portfolio:
        price = getPrice(x)
        dayChange = get24Rate(x)
        coinAmt = getTradeBalance(x)
        coinR = round(coinAmt, 2)
        totalWorth = getUSDValue(x)
        totalVal += totalWorth
        total24 += dayChange
        if totalWorth < .50:
            continue
        portStr += f'\n${x}\n  24hr change: {dayChange}%\n  Current Price: ${price}\n  Balance: {coinR}\n  Total USD Value: ${totalWorth}'

    dailyPerformance = total24 / numCoins
    dailyPerformance = round(dailyPerformance, 2)
    totalVal = round(totalVal, 2)
    finalStr = 'Your portfolio is '
    if dailyPerformance > 0:
        finalStr += f'up {dailyPerformance}% over the last 24h\nUSD value of portfolio: ${totalVal}'
    else:
        finalStr += f'down {dailyPerformance}% over the last 24h\nUSD value of portfolio: ${totalVal}'
    
    finalStr += portStr

    return finalStr

# get performance of top 5 holdings

def getTopTen():
    portfolio = getPortfolio()
    portStr = "Here our your top ten crypto holdings..."
    i = 0
    for x in portfolio:
        if i > 5:
            break
        price = getPrice(x)
        dayChange = get24Rate(x)
        coinAmt = getTradeBalance(x)
        coinR = round(coinAmt, 2)
        totalWorth = getUSDValue(x)
        portStr += f'\n${x}\n  24hr change: {dayChange}%\n  Current Price: ${price}\n  Balance: {coinR}\n  Total USD Value: ${totalWorth}'
        i += 1

    return portStr

# analyze portfolio... based on diversifying
# TO-DO: improve/add to analysis
def getPortfolioAnalysis():
    analyzePortfolio()
    analyisStr = 'Here is our advice to help diversify your portfolio\n'
    if portfolioGlobals.majorPercent < 50.0:
        analyisStr += '\nLower your risk... allocate more to $BTC and $ETH\n'

    if portfolioGlobals.stablePercent < 7.0:
        analyisStr += '\nAdd more $USDT... Always be ready to buy when an opportunity presents itself\n'
    
    if portfolioGlobals.paymentPercent < 12.0:
        analyisStr += '\nDiversify your portfolio by adding more large cap payment coins.\n'

    if portfolioGlobals.platformPercent < 12.0:
        analyisStr += '\nAdd more large platform coins. My favorites are...\n'

    if portfolioGlobals.gamingPercent < 7.0:
        analyisStr += '\nGaming tokens have a lot of potential... you should consider adding some to your portfolio\n'

    analyisStr += 'To get recommendation on portfolio coins, please visit the analysis section.'

    # print(analyisStr)
    return analyisStr


# return watchlist
# TO-DO: ADD ANALYSIS
def getWatchlist():
    watchlist = globals.coin_watchlist
    watchlistStr = ''
    for x in watchlist:
        price = getPrice(x)
        dayChange = get24Rate(x)
        watchlistStr += f'\n${x}\n  Current Price: ${price}\n  24h change: {dayChange}%'
    
    watchlistStr += '\n\nPlease use the buttons below if you want to add/remove a coin.'
    return watchlistStr

# Add a coin to your watchlist
def addToWatchlist(coin):
    addStr = ''
    if coin in globals.coin_watchlist:
        addStr += f'${coin} is already on your watchlist.'
    else:
        globals.coin_watchlist.append(coin)
        addStr += f'${coin} has been added to your watchlist.'
    return addStr

# remove a coin from your watchlist
def removeFromWatchlist(coin):
    removeStr = ''
    if coin in globals.coin_watchlist:
        globals.coin_watchlist.remove(coin)
        removeStr += f'${coin} was removed from your watchlist.'
    else:
        removeStr += f'${coin} is not on your watchlist.'
    return removeStr


# get recommendations str
def getRecommendations():
    recommendationsStr = ''
    if globals.analysis_complete:
        if not globals.buy_recommendations:
            recommendationsStr += 'No buy reccomendations at this time.\n'
        else:
            recommendationsStr += 'You should consider buying... \n'
            for x in globals.buy_recommendations:
                recommendationsStr += f'  ${x}\n'

        if not globals.sell_recommendations:
            recommendationsStr += '\nNo sell reccomendations at this time.'
        else:
            recommendationsStr += '\nYou should consider selling... \n'
            for x in globals.sell_recommendations:
                recommendationsStr += f'  ${x}\n'
    else:
        recommendationsStr = 'We are still analyzing your watchlist. Please check back in a few minutes'

    return recommendationsStr


# execute the buy
# work on it....
def executePurchase(coin, amount):
    purchaseStr = ''
    purchaseAmt = float(amount)
    if globals.trades_enabled:
        purchaseStr = buyCoin(coin, amount)
    else:
        purchaseStr = f'Purchase complete\n\n{purchaseAmt} of ${coin} has added to your wallet!'

    return purchaseStr


# execute the sell
# work on it....
def executeSale(coin, amount):
    sellStr = ''
    sellAmt = float(amount)
    if globals.trades_enabled:
        sellStr = sellCoin(coin, amount)
    else:
        sellStr = f'Sale complete\n\n{sellAmt} of ${coin} has sold for $USDT!'

    return sellStr