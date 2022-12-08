from calculateTechnicals import *
from datetime import datetime
from technicalsClient import *
from kucoinValues import *
from marketData import *
from telegramHelper import *

def main():
    # print(date_to_seconds(dt))
    # print(date_to_seconds('June 01, 2022'))
    # analyzeWatchlist()
    # getMarket24()
    # tti = getWholePortfolio()
    # sio = sellCoin('XLM', 20)
    # print(sio)
    # BTC, ETH, SOL, DOT, AVAX, LINK, MATIC, CRO, XLM, ATOM, UNI, HBAR, AXS, THETA
    # LONG: BTC, ETH, SOL, AVAX, DOT
    # CURRENT HOLDS: BNX, STC
    analyzeCoin('ETH')

if __name__ == '__main__':
    main()
