from datetime import datetime
import dateparser
import pytz
from kucoin.client import Client
import kucoinSecrets
from kucoinValues import *
import pandas as pd
from stockstats import wrap
import globals

# create kucoin client
client = Client(kucoinSecrets.api_key, kucoinSecrets.api_secret, kucoinSecrets.api_passphrase)

# convert UTC date to seconds


def date_to_seconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds())

def get_historical_klines(coin, start_str, end_str=None):
    # daily interval
    week_interval = '1week'
    # create symbol
    symbol = f'{coin}-USDT'
    # store indicators are dictionary
    weekly_indicators = {}
    # convert sate to seconds
    start_time = date_to_seconds(start_str)
    # use now if end date is not passed
    if end_str is None:
        end_str = 'now UTC'
    end_time = date_to_seconds(end_str)

    # for interval of 1 week
    klines_result = client.get_kline_data(symbol, week_interval, start_time, end_time)
    # print(klines_result)

    df = pd.DataFrame(klines_result, columns=['date', 'Open', 'close', 'high', 'low', 'volume', 'amount'])
    df['date'] = pd.to_datetime(df['date'], unit='s')
    # df.set_index('Timestamp', inplace=True)
    df = df[['date','close', 'high', 'low','volume']]
    df['volume'] = df['volume'].astype('float')
    df['high'] = df['high'].astype('float')
    df['low'] = df['low'].astype('float')
    df['close'] = df['close'].astype('float')
    df = df[::-1]

    # get indicators into df
    df = wrap(df)
    df['macd'] = df.get('macd')
    df['rsi'] = df.get('rsi')
    df['boll'] = df.get('boll')
    # df['stochrsi'] = df.get('stochrsi')
    df['sma'] = df.get('high_30_sma')
    df['dma'] = df.get('dma')

    weekly_indicators['rsi'] = df['rsi'].iat[-1]
    weekly_indicators['macd'] = df['macd'].iat[-1]
    weekly_indicators['macds'] = df['macds'].iat[-1]
    weekly_indicators['bbLow'] = df['boll_lb'].iat[-1]
    weekly_indicators['bbHigh'] = df['boll_ub'].iat[-1]
    weekly_indicators['pdi'] = df['pdi'].iat[-1]
    weekly_indicators['mdi'] = df['mdi'].iat[-1]
    weekly_indicators['adx'] = df['adx'].iat[-1]

    #print(df)
    # print(weekly_indicators)

    return analyzeIndicators(coin, weekly_indicators)


    
def analyzeIndicators(coin, weekly_indicators):
    numBuyWeekly = 0
    numSellWeekly = 0
    numNeutralWeekly = 0
    price = getPrice(coin)
    daily_indicators = {}
    resultStr = ''

    # weekly first
    # rsi
    rsi = weekly_indicators['rsi']
    print(f'RSI weekly: {rsi}')
    if rsi < 30.0:
        numBuyWeekly += 1
        print('RSI weekly says buy')
    elif rsi > 70.0:
        numSellWeekly += 1
        print('RSI weekly says sell')
    else:
        numNeutralWeekly += 1
    
    # bbands
    bbLow = weekly_indicators['bbLow']
    bbHigh = weekly_indicators['bbHigh']
    if price < bbLow:
        numBuyWeekly += 1
        print('Bbands weekly say buy')
    elif price > bbHigh:
        numSellWeekly += 1
        print('Bbands weekly say sell')
    else:
        numNeutralWeekly += 1

    # MACD
    macd = weekly_indicators['macd']
    macd_signal = weekly_indicators['macds']
    if macd > macd_signal:
        numBuyWeekly += 1
        print('macd weekly say buy')
    elif macd < macd_signal:
        numSellWeekly += 1
        print('macd weekly say sell')
    else:
        numNeutralWeekly += 1


    # important signal: +DI > -DI... buy
    # +DI < -DI... sell
    # if ADX < 30... strong singal... add 2
    pdi = weekly_indicators['pdi']
    mdi = weekly_indicators['mdi']
    adx = weekly_indicators['adx']
    if pdi > mdi:
        if adx > 40.0:
            numBuyWeekly += 2
            print('adx says buy + 2')
        else:
            numBuyWeekly += 1
            print('adx says buy + 1')
    elif pdi < mdi:
        if adx > 40.0:
            numSellWeekly += 2
            print('adx says sell + 2')
        else:
            numBuyWeekly += 1
            print('adx says sell + 1')

    print(f'numSell: {numSellWeekly}, numBuy: {numBuyWeekly}')
    # confirm trade with 1day interval
    # check if we need to get interval of 1d
    if (numBuyWeekly >=3 and numSellWeekly < 2) or (numSellWeekly >= 3 and numBuyWeekly < 2) or (numBuyWeekly >= 2 and numSellWeekly < 1) or (numSellWeekly >= 2 and numBuyWeekly < 1):
        # get interval for 1day
        date = 'September 25, 2021'
        daily_start_time = date_to_seconds(date)
        symbol = f'{coin}-USDT'
        daily_interval = '1day'
        daily_klines_result = client.get_kline_data(symbol, daily_interval, daily_start_time)

        daily_df = pd.DataFrame(daily_klines_result, columns=['date', 'Open', 'close', 'high', 'low', 'volume', 'amount'])
        daily_df['date'] = pd.to_datetime(daily_df['date'], unit='s')
        daily_df = daily_df[['date','close', 'high', 'low','volume']]
        daily_df['volume'] = daily_df['volume'].astype('float')
        daily_df['high'] = daily_df['high'].astype('float')
        daily_df['low'] = daily_df['low'].astype('float')
        daily_df['close'] = daily_df['close'].astype('float')
        daily_df = daily_df[::-1]

        daily_df = wrap(daily_df)
        daily_df['macd'] = daily_df.get('macd')
        daily_df['rsi'] = daily_df.get('rsi')
        daily_df['boll'] = daily_df.get('boll')
        # daily_df['stochrsi'] = daily_df.get('stochrsi')
        daily_df['sma50'] = daily_df.get('high_50_sma')
        daily_df['sma200'] = daily_df.get('high_200_sma')

        daily_indicators['rsi'] = daily_df['rsi'].iat[-1]
        daily_indicators['macd'] = daily_df['macd'].iat[-1]
        daily_indicators['macds'] = daily_df['macds'].iat[-1]
        daily_indicators['bbLow'] = daily_df['boll_lb'].iat[-1]
        daily_indicators['bbHigh'] = daily_df['boll_ub'].iat[-1]
        daily_indicators['sma50'] = daily_df['sma50'].iat[-1]
        daily_indicators['sma200'] = daily_df['sma200'].iat[-1]

        # print(daily_indicators)

        buySignals = 0
        sellSignals = 0
        rsi_daily = daily_indicators['rsi']
        macd_daily = daily_indicators['macd']
        macd_signal_daily = daily_indicators['macds']
        bbLow_daily = daily_indicators['bbLow']
        bbHigh_daily = daily_indicators['bbHigh']
        sma50 = daily_indicators['sma50']
        sma200 = daily_indicators['sma200']

        #rsi
        print(f'rsi: {rsi_daily}')
        if rsi_daily < 30.0:
            buySignals += 1
            print('RSI says buy')
        elif rsi_daily > 70.0:
            sellSignals += 1
            print('RSI says sell')
        
        # macd 
        if macd_daily > macd_signal_daily:
            buySignals += 1
            print('MACD says buy')
        elif macd_daily < macd_signal_daily:
            sellSignals += 1
            print('MACD says sell')

        # bbands
        print(f'bblow: {bbLow}')
        if price < bbLow_daily:
            buySignals += 1
            print('BBands say buy')
        elif price > bbHigh_daily:
            sellSignals += 1
            print('Bbands say sell')

        #  sma
        if sma50 > sma200:
            buySignals += 1
            print('SMA says buy')
        elif sma50 < sma200:
            sellSignals += 1
            print('SMA says sell')

        print(f'buy num 1d: {buySignals}')
        print(f'sell num 1d: {sellSignals}')

        # buy case1
        if numBuyWeekly >= 3 and numSellWeekly == 0:
            if buySignals >= sellSignals:
                resultStr = 'buy'
                print('buy: case 1')
                if coin not in globals.buy_recommendations:
                    globals.buy_recommendations.append(coin)
                
                if coin in globals.sell_recommendations:
                    globals.sell_recommendations.remove(coin)
                return resultStr
            
        # sell case 1
        elif numSellWeekly >= 3 and numBuyWeekly == 0:
            if sellSignals >= buySignals:
                resultStr = 'sell'
                print('sell: case 1')
                if coin not in globals.sell_recommendations:
                    globals.sell_recommendations.append(coin)
                
                if coin in globals.buy_recommendations:
                    globals.buy_recommendations.remove(coin)
                return resultStr

        # buy case 2
        if (numBuyWeekly >= 3 and numSellWeekly == 1) or (numBuyWeekly >= 2 and numSellWeekly == 0):
            if buySignals > sellSignals:
                resultStr = 'buy'
                print('buy: case 2')
                if coin not in globals.buy_recommendations:
                    globals.buy_recommendations.append(coin)
                
                if coin in globals.sell_recommendations:
                    globals.sell_recommendations.remove(coin)
                return resultStr

        # sell case 2
        elif (numSellWeekly >= 3 and numBuyWeekly == 1) or (numSellWeekly >=2 and numBuyWeekly == 0):
            if sellSignals > buySignals:
                resultStr = 'sell'
                print('sell: case 2')
                if coin not in globals.sell_recommendations:
                    globals.sell_recommendations.append(coin)
                
                if coin in globals.buy_recommendations:
                    globals.buy_recommendations.remove(coin)
                return resultStr

            if buySignals >= 2:
                if coin not in globals.buy_recommendations:
                    globals.buy_recommendations.append(coin)
                    #print(f'You should buy {coin}')
                
                if coin in globals.sell_recommendations:
                    globals.sell_recommendations.remove(coin)

            else:
                if coin in globals.buy_recommendations:
                    globals.buy_recommendations.remove(coin)

                if coin in globals.sell_recommendations:
                    globals.sell_recommendations.remove(coin)
                #print('sale not confirmed')

    else:
        resultStr = 'neutral'
        if coin in globals.buy_recommendations:
            globals.buy_recommendations.remove(coin)

        if coin in globals.sell_recommendations:
            globals.sell_recommendations.remove(coin)
        #print(f'Long term is neutral for {coin}')

        return resultStr