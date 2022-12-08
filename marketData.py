from pycoingecko import CoinGeckoAPI
import globals


cg = CoinGeckoAPI()

# get 24 hr market change... overall market
def getMarket24():
    result = cg.get_global()
    percent = float(result["market_cap_change_percentage_24h_usd"])
    percent_rounded = round(percent, 2)
    # print(percent_rounded)
    return percent_rounded


# get top coins - top 10
def getTopTenCoins():
    coin_ids = globals.top_coins
    result = cg.get_coins_markets('usd', ids=coin_ids)
    topTenStr = ''
    for x in result:
        symbol = x['symbol'].upper()
        name = x['name']
        price = x['current_price']
        priceChange = round(x['price_change_percentage_24h'], 2)
        topTenStr += f'${symbol}: {name}\n  Price: ${price}\n  24h: {priceChange}%\n\n'

    # print(topTenStr)
    
    return topTenStr



# get Categories
def getCategoryPerformance():
    category_ids = ['gaming', 'metaverse', 'smart-contract-platform', 'decentralized-finance-defi', 'meme-tokens']
    result = cg.get_coins_categories()
    categories = {}
    for x in result:
        for y in category_ids:
            if x['id'] == y:
                percent_change = float(x['market_cap_change_24h'])
                categories[y] = round(percent_change, 2)
                # print(percent_change)
    return categories