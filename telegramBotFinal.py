from asyncore import dispatcher
from kucoinValues import *
from telegramHelper import *
import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
    JobQueue
)

# State definitions for top level conversation
SELECTING_ACTION, PORTFOLIO, MARKET, TRADE = map(chr, range(4))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_CONFIRMED = map(chr, range(4, 6))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Meta states
STOPPING, SHOWING = map(chr, range(8, 10))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(
    ANALYSIS,
    ANALYZE_PORTFOLIO,
    ANALYZE_WL,
    ANALYZE_A_COIN,
    SELECTING_TRADE,
    TRADE_SELL,
    TRADE_BUY,
    TYPING_BUY_AMT,
    TYPING_SELL_AMOUNT,
    CONFIRM_BUY,
    BUY_CONFIRMED,
    SELECTING_SELL_CONFIRMED,
    SALE_CONFIRMED,
    MAIN_MENU,
    PORTFOLIO_OVERVIEW,
    PORTFOLIO_ANALYSIS,
    PORTFOLIO_WATCHLIST,
    START_OVER,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
    SEARCH,
    MARKET_CATEGORIES,
    MARKET_TOPCOINS,
    SELECTING_WATCHLIST,
    TYPING_ADD_TO_WL,
    ADD_COIN_WL,
    REMOVE_COIN_WL,
    TYPING_REMOVE_FROM_WL,
    GO_BACK,
) = map(chr, range(10, 39))


# run_async function for analyzing user watchlist
def analyze_user_watchlist(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('I am now analyzing the coins on your watchlist. Be paitent, I will let you know when I finish.')
    if not globals.analysis_in_progress:
        globals.analysis_in_progress = True
        globals.analysis_complete = False
        analyzeWatchlist()
        globals.analysis_complete = True
        globals.analysis_in_progress = False
        text = 'Watchlist analysis complete. You will see my recommendations in the analysis section. How else can I help you?'
    else:
        text = 'Analysis already in progress...'
    buttons = [
        [
            InlineKeyboardButton(text='Trade', callback_data=str(TRADE)),
            InlineKeyboardButton(text='Analysis', callback_data=str(ANALYSIS)),
        ],
        [
            InlineKeyboardButton(text='Portfolio', callback_data=str(PORTFOLIO)),
            InlineKeyboardButton(text='Market Data', callback_data=str(MARKET)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text=text, reply_markup=keyboard)
    return SHOWING


# run_async function for analyzing user watchlist
def analyze_user_portfolio(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('I am now analyzing the coins on your portfolio. Be paitent, I will let you know when I finish.')
    if not globals.analysis_in_progress:
        globals.analysis_in_progress = True
        globals.analysis_complete = False
        analyzePortfolioCoins()
        globals.analysis_complete = True
        globals.analysis_in_progress = False
        text = 'Portfolio analysis complete. You will see my recommendations in the analysis section. How else can I help you?'
    else:
        text = 'Analysis already in progress...'
    buttons = [
        [
            InlineKeyboardButton(text='Trade', callback_data=str(TRADE)),
            InlineKeyboardButton(text='Analysis', callback_data=str(ANALYSIS)),
        ],
        [
            InlineKeyboardButton(text='Portfolio', callback_data=str(PORTFOLIO)),
            InlineKeyboardButton(text='Market Data', callback_data=str(MARKET)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text=text, reply_markup=keyboard)
    return SHOWING


# Top level conversation callbacks... main menu
def start(update: Update, context: CallbackContext) -> str:
    """Select an action: Adding parent/child or show data."""
    text = getIntroStr()
    buttons = [
        [
            InlineKeyboardButton(text='Trade', callback_data=str(TRADE)),
            InlineKeyboardButton(text='Analysis', callback_data=str(ANALYSIS)),
        ],
        [
            InlineKeyboardButton(text='Portfolio', callback_data=str(PORTFOLIO)),
            InlineKeyboardButton(text='Market Data', callback_data=str(MARKET)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need to send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION

################ ANALYSIS SECTION #####################
# analysis is selected from main menu...
# analysis menu
def analysis_select(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    text = 'Okay, what should I run technical analysis on? Please keep in mind analyzing portfolio and watchlists can take time. I will notify you when I finish!!'
    context.user_data[CURRENT_LEVEL] = ANALYSIS
    buttons = [
        [
            InlineKeyboardButton(text='Portfolio Analysis', callback_data=str(ANALYZE_PORTFOLIO)),
            InlineKeyboardButton(text='Watchlist Analysis', callback_data=str(ANALYZE_WL)),
        ],
        [
            InlineKeyboardButton(text='Analyze a coin', callback_data=str(ANALYZE_A_COIN)),
            InlineKeyboardButton(text='Back', callback_data=str(MAIN_MENU)),
        ]

    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_LEVEL


# analyze a users portfolio
def watchlist_analysis(update: Update, context: CallbackContext) -> str:
    # update.message.reply_text("Okay, I'm analyzing your portfolio. This could take a while...")
    user_data = context.user_data
    text = getWatchlistAnalysis()
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True
    return SHOWING

# analyze a users portfolio
def portfolio_analysis(update: Update, context: CallbackContext) -> str:
    # update.message.reply_text("Okay, I'm analyzing your portfolio. This could take a while...")
    user_data = context.user_data
    text = getPortfolioAnalysisCoins()
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True
    return SHOWING

# search for coin is selected from market menu...
def analyze_provide_coin(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Please type the symbol of the coin you want me to analyze...'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return TYPING
    
# user after providing coin they would like to search for
def analyze_for_coin(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    input_text = update.message.text
    context.user_data['coin'] = input_text.upper()
    coin = context.user_data['coin']
    text = analyzeCoin(coin)
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING

################ TRADE SECTION #####################

# trade selected from main menu ask user to provide coin they want to trade
def provide_coin_selection(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Please type the symbol of the coin you want to trade'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return TYPING

# coin provided.. ask if they want to buy or sell the coin
def trade_select(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    input_text = update.message.text
    context.user_data['coin'] = input_text.upper()
    coin = context.user_data['coin']
    price = getPrice(input_text.upper())
    amountOwned = getTradeBalance(coin)
    # if amountOwned > 5.0:
    context.user_data['price'] = price
    context.user_data['amountOwned'] = amountOwned
    text = f'${coin}?\n  Price: {price}'
    if amountOwned > 0.0:
        text += f'\n  Amount owned: {amountOwned}'
    else:
        text += '\n  Anount ownded: None'
    buttons = [
        [
            InlineKeyboardButton(text='Buy', callback_data=str(TRADE_BUY)),
            InlineKeyboardButton(text='Sell', callback_data=str(TRADE_SELL)),
        ],
        [
            InlineKeyboardButton(text='Back', callback_data=str(END)),
        ]

    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text, reply_markup=keyboard)

    return SELECTING_TRADE

# buy selected from menu
# ask for amount in USDT
def provide_purchase_amount(update: Update, context: CallbackContext) -> str:
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    coin = context.user_data['coin']
    text = 'Please type the USD amount you want to purchase'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return TYPING_BUY_AMT


# sell selected from trade menu
# ask for percentage of coin they want to sell
def provide_sell_amount(update: Update, context: CallbackContext) -> str:
    amountOwned = context.user_data['amountOwned']
    coin = context.user_data['coin']
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    if amountOwned > 5.0:
        text = f'Please type the percentage of your ${coin} you want to sell...'
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)
        return TYPING_SELL_AMOUNT
    else:
        buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
        keyboard = InlineKeyboardMarkup(buttons)
        text = f'You do not own enough ${coin} for me to process a sale.'
        context.user_data[START_OVER] = True
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        return SHOWING

# buy amount provided
# confirm the purchase
def confirm_buy(update: Update, context: CallbackContext) -> str:
    inputText = update.message.text
    context.user_data['amountUSD'] = float(inputText)
    amount = context.user_data['amountUSD']
    coin = context.user_data['coin']
    price = context.user_data['price']
    volume = amount / price
    context.user_data['volume'] = volume
    buttons = [
        [
            InlineKeyboardButton(text='Confirm Buy', callback_data=str(BUY_CONFIRMED)),
            InlineKeyboardButton(text='Cancel', callback_data=str(END)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    text= f'Please confirm you want to buy {volume} ${coin} for ${amount}'
    update.message.reply_text(text, reply_markup=keyboard)

    return SELECTING_CONFIRMED

# sell amount provided....
# confirm the sale
def confirm_sale(update: Update, context: CallbackContext) -> str:
    inputText = update.message.text
    coin = context.user_data['coin']
    price = context.user_data['price']
    sellPercent = float(inputText) / 100
    context.user_data['sellPercent'] = float(inputText)
    amountOwned = context.user_data['amountOwned']
    sellAmount = amountOwned * sellPercent
    context.user_data['sellAmount'] = sellAmount
    usdSaleValue = sellAmount * price
    buttons = [
        [
            InlineKeyboardButton(text='Confirm Sale', callback_data=str(SALE_CONFIRMED)),
            InlineKeyboardButton(text='Cancel', callback_data=str(END)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    text= f'Please confirm you want to sell {sellAmount} ${coin} for ${usdSaleValue}'
    update.message.reply_text(text, reply_markup=keyboard)

    return SELECTING_SELL_CONFIRMED

# buy is confirmed, execute the purchase
def execute_buy(update: Update, context: CallbackContext) -> str:
    coin = context.user_data['coin']
    volume = context.user_data['volume']
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    text= executePurchase(coin, volume)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING

# sale is confirmed, execute the sale
def execute_sale(update: Update, context: CallbackContext) -> str:
    coin = context.user_data['coin']
    sellAmount = context.user_data['sellAmount']
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    text= executeSale(coin, sellAmount)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING

################ PORTFOLIO SECTION #####################

# portfolio is selected from main menu
# show portfolio menu
def portfolio_select(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    text = 'Okay, what portfolio information do you need?'
    context.user_data[CURRENT_LEVEL] = PORTFOLIO
    buttons = [
        [
            InlineKeyboardButton(text='Portfolio Overview', callback_data=str(PORTFOLIO_OVERVIEW)),
            InlineKeyboardButton(text='Coin Watchlist', callback_data=str(PORTFOLIO_WATCHLIST)),
        ],
        [
            InlineKeyboardButton(text='Portfolio Analysis', callback_data=str(PORTFOLIO_ANALYSIS)),
            InlineKeyboardButton(text='Back', callback_data=str(END)),
        ]

    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_LEVEL

# portfolio overview is selected from portfolio menu...
def portfolio_overview_choice(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    user_data = context.user_data
    text = getWholePortfolio()
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SHOWING

# portfolio analysis is selected from portfolio menu...
def portfolio_analysis_choice(update: Update, context: CallbackContext) -> str:
    user_data = context.user_data
    text = getPortfolioAnalysis()
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SHOWING

# portfolio watchlist is selected from menu...
# display watchlist and see if they want to add to watchlist
def portfolio_watchlist_choice(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    text = getWatchlist()
    buttons = [
            [
            InlineKeyboardButton(text='Add Coin', callback_data=str(ADD_COIN_WL)),
            InlineKeyboardButton(text='Remove Coin', callback_data=str(REMOVE_COIN_WL)),
        ],
        [
            InlineKeyboardButton(text='Back', callback_data=str(GO_BACK)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_WATCHLIST

# user wants to add coin to watchlist
# ask user to type symbol of coin to add to WL
def provide_watchlist_coin_add(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Please type the symbol of the coin you wish to add to your watchlist...'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return TYPING_ADD_TO_WL

# add coin to watchlist
def add_to_watchlist(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    input_text = update.message.text
    context.user_data['coin'] = input_text.upper()
    coin = context.user_data['coin']
    text = addToWatchlist(coin)
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING

# user wants to remove coin to watchlist
# ask user to type symbol of coin to remove to WL
def provide_watchlist_coin_remove(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Please type the symbol of the coin you wish to remove from your watchlist...'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return TYPING_REMOVE_FROM_WL


# remove the coin from the watchlist
def remove_from_watchlist(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    input_text = update.message.text
    context.user_data['coin'] = input_text.upper()
    coin = context.user_data['coin']
    text = removeFromWatchlist(coin)
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING

################ MARKET SECTION #####################

# market is selected from main menu...
# market menu
def market_select(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    text = 'Okay, what market information do you need?'
    context.user_data[CURRENT_LEVEL] = MARKET
    buttons = [
        [
            InlineKeyboardButton(text='Categories', callback_data=str(MARKET_CATEGORIES)),
            InlineKeyboardButton(text='Top Coins', callback_data=str(MARKET_TOPCOINS)),
        ],
        [
            InlineKeyboardButton(text='Search for coin', callback_data=str(SEARCH)),
            InlineKeyboardButton(text='Back', callback_data=str(END)),
        ]

    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_LEVEL

# market categories is selected from market menu...
def market_category_choice(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    user_data = context.user_data
    text = categoryOverview()
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SHOWING

# top coins is selected from market menu...
def market_topCoin_choice(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    user_data = context.user_data
    text = getMarketTopCoins()
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SHOWING

# search for coin is selected from market menu...
def market_search_choice(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Please type the symbol of the coin you are looking for'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return TYPING

# user after providing coin they would like to search for
def search_for_coin(update: Update, context: CallbackContext) -> str:
    """See information on the crypto market."""
    input_text = update.message.text
    context.user_data['coin'] = input_text.upper()
    coin = context.user_data['coin']
    text = getCoin(coin)
    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING

def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return END

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("5339628139:AAGITcRzQpwyewFoCvFNaELAQgaiBHz0OLY")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Set up ConversationHandler for analysis 
    analysis_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(analysis_select, pattern='^' + str(ANALYSIS) + '$')],
        states={
            SELECTING_LEVEL: [
                CallbackQueryHandler(portfolio_analysis, pattern='^' + str(ANALYZE_PORTFOLIO) + '$'),
                CallbackQueryHandler(watchlist_analysis, pattern='^' + str(ANALYZE_WL) + '$'),
                CallbackQueryHandler(analyze_provide_coin, pattern='^' + str(ANALYZE_A_COIN) + '$'),
            ],
            TYPING: [MessageHandler(Filters.text & ~Filters.command, analyze_for_coin)],
        },
        fallbacks=[
            CallbackQueryHandler(stop, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop),
        ],
        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
    )

    # Set up ConversationHandler for trading
    trade_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(provide_coin_selection, pattern='^' + str(TRADE) + '$')],
        states={
            SELECTING_TRADE: [
                CallbackQueryHandler(provide_purchase_amount, pattern='^' + str(TRADE_BUY) + '$'),
                CallbackQueryHandler(provide_sell_amount, pattern='^' + str(TRADE_SELL) + '$'),
            ],
            SELECTING_CONFIRMED: [CallbackQueryHandler(execute_buy, pattern='^' + str(BUY_CONFIRMED) + '$')],
            SELECTING_SELL_CONFIRMED: [CallbackQueryHandler(execute_sale, pattern='^' + str(SALE_CONFIRMED) + '$')],
            TYPING: [MessageHandler(Filters.text & ~Filters.command, trade_select)],
            TYPING_BUY_AMT: [MessageHandler(Filters.text & ~Filters.command, confirm_buy)],
            TYPING_SELL_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, confirm_sale)],

        },
        fallbacks=[
            CallbackQueryHandler(stop, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop),
        ],
        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
    )

    # Set up ConversationHandler for Portfolio
    portfolio_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(portfolio_select, pattern='^' + str(PORTFOLIO) + '$')],
        states={
            SELECTING_LEVEL: [
                CallbackQueryHandler(portfolio_overview_choice, pattern='^' + str(PORTFOLIO_OVERVIEW) + '$'),
                CallbackQueryHandler(portfolio_analysis_choice, pattern='^' + str(PORTFOLIO_ANALYSIS) + '$'),
                CallbackQueryHandler(portfolio_watchlist_choice, pattern='^' + str(PORTFOLIO_WATCHLIST) + '$')
            ],
            SELECTING_WATCHLIST:[
                CallbackQueryHandler(provide_watchlist_coin_add, pattern='^' + str(ADD_COIN_WL) + '$'),
                CallbackQueryHandler(provide_watchlist_coin_remove, pattern='^' + str(REMOVE_COIN_WL) + '$'),
                CallbackQueryHandler(portfolio_select, pattern='^' + str(GO_BACK) + '$'),
            ],
            TYPING_ADD_TO_WL: [MessageHandler(Filters.text & ~Filters.command, add_to_watchlist)],
            TYPING_REMOVE_FROM_WL: [MessageHandler(Filters.text & ~Filters.command, remove_from_watchlist)]
        },
        fallbacks=[
            CallbackQueryHandler(stop, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop),
        ],
        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
    )

    # Set up ConversationHandler for market 
    market_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(market_select, pattern='^' + str(MARKET) + '$')],
        states={
            SELECTING_LEVEL: [
                CallbackQueryHandler(market_category_choice, pattern='^' + str(MARKET_CATEGORIES) + '$'),
                CallbackQueryHandler(market_topCoin_choice, pattern='^' + str(MARKET_TOPCOINS) + '$'),
                CallbackQueryHandler(market_search_choice, pattern='^' + str(SEARCH) + '$'),
            ],
            TYPING: [MessageHandler(Filters.text & ~Filters.command, search_for_coin)],
        },
        fallbacks=[
            CallbackQueryHandler(stop, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop),
        ],
        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
    )

    selection_handlers = [
        analysis_conv,
        trade_conv,
        portfolio_conv,
        market_conv,
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SHOWING: [CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            # DESCRIBING_SELF: [description_conv],
            STOPPING: [CommandHandler('start', start)],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('analyzeWatchlist', analyze_user_watchlist, run_async=True))
    dispatcher.add_handler(CommandHandler('analyzePortfolio', analyze_user_portfolio, run_async=True))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()