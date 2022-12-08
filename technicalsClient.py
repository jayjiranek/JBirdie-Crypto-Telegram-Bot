import time
import globals
from calculateTechnicals import *


# threading-- analyze coin watchlist

def analyzeWatchlist():
    watchlist = globals.coin_watchlist
    dt = 'January 10, 2022'
    i = 0
    portStr = 'Analysis Complete...\n'
    for coin in watchlist:
        if i == 0:
            resultStr = get_historical_klines(coin, dt)
        else:
            time.sleep(100)
            resultStr = get_historical_klines(coin, dt)
        i += 1

        if resultStr == 'buy':
            if coin not in globals.watchlist_buys:
                globals.watchlist_buys.append(coin)
            if coin in globals.watchlist_sells:
                globals.watchlist_sells.remove(coin)

        if resultStr == 'sell':
            if coin not in globals.watchlist_sells:
                globals.watchlist_sells.append(coin)
            if coin in globals.watchlist_buys:
                globals.watchlist_buys.remove(coin)

    

def getWatchlistAnalysis():
    watchStr = 'Here is the most recent analysis. To run a new watchlist analysis send /analyzeWatchlist.\n'
    if globals.watchlist_buys:
        watchStr += '\nYou should purchase more:'
        for coin in globals.watchlist_buys:
            watchStr += f'\n  ${coin}'
    else:
        watchStr += '\nNo purchase recommendations a this time.'

    if globals.watchlist_sells:
        watchStr += '\nYou should sell some:'
        for coin in globals.watchlist_sells:
            watchStr += f'\n  ${coin}'
    else:
        watchStr += '\nNo sell recommendations a this time.'

    return watchStr

# analyze users portfolio

def analyzePortfolioCoins():
    portfolio = getPortfolio()
    dt = 'January 10, 2022'
    i = 0
    for coin in portfolio:
        if i == 0:
            resultStr = get_historical_klines(coin, dt)
        else:
            time.sleep(100)
            resultStr = get_historical_klines(coin, dt)
        i += 1
        if resultStr == 'buy':
            if coin not in globals.portfolio_buys:
                globals.portfolio_buys.append(coin)
            if coin in globals.portfolio_buys:
                globals.portfolio_sells.remove(coin)
        elif resultStr == 'sell':
            if coin not in globals.portfolio_sells:
                globals.portfolio_buys.append(coin)
            if coin in globals.portfolio_buys:
                globals.portfolio_sells.remove(coin)

def getPortfolioAnalysisCoins():
    portStr = 'Here is the most recent analysis. To run a new portfolio analysis send /analyzePortfolio.\n'
    if globals.portfolio_buys:
        portStr += '\nYou should purchase more:'
        for coin in globals.portfolio_buys:
            portStr += f'\n  ${coin}'
    else:
        portStr += '\nNo purchase recommendations a this time.'

    if globals.portfolio_sells:
        portStr += '\nYou should sell some:'
        for coin in globals.portfolio_sells:
            portStr += f'\n  ${coin}'
    else:
        portStr += '\nNo sell recommendations a this time.'

    return portStr

def analyzeCoin(coin):
    dt = 'January 10, 2022'
    coinStr = ''
    resultStr = get_historical_klines(coin, dt)
    if resultStr == 'buy':
        coinStr += f'You should buy ${coin}'
    elif resultStr == 'sell':
        coinStr += f'You should sell ${coin}'
    else:
        coinStr += f'No recommendations for ${coin} at this time'

    return coinStr