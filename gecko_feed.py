# Python imports
import requests, json, sys
from styles import green, yellow, blue, red, pink, bold, underline
import re

GECKO_COINS_URL = 'https://api.coingecko.com/api/v3/coins/'

""" need to get coinlist in order search for base/quote individually
gecko does not provide pairs by default. for base/quote one must be listed as ticker
and the other lsited as full name, i.e. BTCUSD is vs_currency = usd , ids = bitcoin
https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin    
"""


def print_args(*args):
    print(' '.join([str(arg) for arg in args]))

def print_usage():
    print_args("Usage: python " + sys.argv[0], yellow('[symbol]'))
    print_args("Symbol is required, for example:")
    print_args("python " + sys.argv[0], yellow('BTC/USD'))


def get_gecko_json(url): 
    r = requests.get(url)
    json_obj = r.json()
    return json_obj
    

def check_gecko_symbol_exists(coinlist, symbol):    
    try:
        symbol_name = [obj for obj in coinlist if obj['symbol']==symbol][0]['id']
        return symbol_name
    except IndexError:
        return None
    

def filter_bit_symbol(symbol):
    # if matches bitUSD or any bit prefix, strip 
    stripBit = re.match(r'bit[A-Z]{3}' , symbol) 
    sym = symbol
    if stripBit:
        sym = re.sub("bit", "", symbol)
    return sym


def get_gecko_market_price(base, quote):

    try:        
        coin_list = get_gecko_json(GECKO_COINS_URL+'list')
        quote_name = check_gecko_symbol_exists(coin_list, quote.lower())
        
        lookup_pair = "?vs_currency="+base.lower()+"&ids="+quote_name
        market_url = GECKO_COINS_URL+'markets'+lookup_pair
        print(market_url)
                
        ticker = get_gecko_json(market_url)
        print("Getting ticker current price")
       
        for entry in ticker:
            current_price = entry['current_price']
            high_24h = entry['high_24h']
            low_24h = entry['low_24h']
            total_volume = entry['total_volume']

#        print_args('current_price: ' + current_price, 'high 24h:' + high_24h)
            
        return current_price

    except TypeError:
        return None


def test_gecko_pricefeed():
    '''base currency for coin gecko is in USD,EUR,JPY, CAD, etc, 
    see entire list here: https://api.coingecko.com/api/v3/global
    
    Example of no market = BTC/USDT
    Example of working market BTC/EUR or BTC/USD
    '''
    try:
        symbol = sys.argv[1]  # get exchange id from command line arguments
        print(symbol)

        quote = symbol.split('/')[0]
        print("quote:" + quote)

        base = symbol.split('/')[1]
        print("base:" + base)

        new_base = filter_bit_symbol(base)
        print("old base", base, "new base", new_base, sep=": ")

        new_quote = filter_bit_symbol(quote)
        print("old quote", quote, "new quote", new_quote, sep=": ")

        current_price = get_gecko_market_price(new_base, new_quote)
        print(current_price)
        
        if current_price is None:
            # try inverted version
            print(" Trying pair inversion...")
            current_price = get_gecko_market_price(new_quote, new_base)
            # invert price
            print(new_base+"/"+new_quote+ ":"+ str(current_price))
            if current_price is not None:
                actual_price = 1/current_price
                print(new_quote+"/"+new_base+ ":"+ str(actual_price))

    except Exception as e:
        print(type(e).__name__, e.args, str(e))
        print_usage()



if __name__ == '__main__':
 
#    base = 'USD'
#    quote = 'BTC'    
 
    test_gecko_pricefeed()
