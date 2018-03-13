import pandas as pd
import numpy as np
import json
from pandas.io.json import json_normalize
import datetime as dt
from datetime import timedelta as td

# display full (non-truncated) dataframe information in html when converting from pandas dataframe
pd.set_option('display.width', None)

# days to look back for events
first_date = dt.date.today() - td(days=3)
last_date = dt.date.today() + td(days=14)

# lists of coins being tracked
symbols_watching = ['BCH',	'ETH',	'OMG',	'NEO',	'ARK',	'USDT',	'LTC',	'ZEC',	'WAVES',	'FUN',	'XZC',	'PAY',	'MTL',	'VTC',	'ETC',	'SC',	'VIA',	'KNC',	'UBQ',	'DASH',	'NAV',	'XMR',	'TKN',	'BAT',	'LBC',	'WTC',	'FCT',	'LSK',	'QTUM',	'DCT',	'GAME',	'KMD',	'ZRX',	'XEL',	'XRP',	'BTC',	'PTOY',	'STEEM',	'GAS',	'ANT',	'BCC',	'ENG',	'USD',	'ADX',	'ANS',	'ARDR',	'BTS',	'CFI',	'CVC',	'DCR',	'DGB',	'EOS',	'GNT',	'GUP',	'LUN',	'MAID',	'MCO',	'MUE',	'NXT',	'PIVX',	'QWARK',	'SJCX',	'SNT',	'STR',	'STRAT',	'SYS',	'XEM',	'XLM',	'XVG', 'IOTA', 'VEN','XTZ']
symbols_portfolio = ['BCH',	'BTC',	'OMG',	'NEO',	'ETH',	'XZC',	'FUN',	'SC',	'EOS',	'UBQ',	'MTL',	'WAVES',	'VIA',	'ARK',	'KNC',	'XEM',	'NAV',	'BAT',	'LTC',	'PAY',	'TKN',	'LBC',	'DASH',	'ZEC',	'VEN',	'ETC',	'USDT',	'ZRX',	'ADX',	'LSK',	'QTUM',	'XRP',	'KMD',	'FCT',	'IOT',	'XMR',	'VTC',	'GAME',	'STRAT',	'ENG',	'WTC',	'STEEM',	'VIB',	'XEL',	'BNB',	'ICX',	'ZCL',	'POE',	'ANT',	'REQ',	'TRST',	'GAS',	'REP',	'LGD']

def gen_news(url_news):
    # Retrieve news from a url and normalize the nested Json response
    df = pd.read_json(url_news)
    df_norm = json_normalize(df['results']) # df_norm['currencies'] is a Pandas series
    # Convert Pandas series to Json
    df_cur = df_norm['currencies'].to_json()

    # Convert EACH nested Json result to another dataframe
    df_out = pd.DataFrame()
    for i in range(df_norm.shape[0]):
        if df_norm['currencies'].iloc[i] is not np.nan:
            nested_jason = json.dumps(df_norm['currencies'].iloc[i]) # output 'Str'
            df_currencies = pd.read_json(nested_jason)
            currencies = []
            for j in range(df_currencies.shape[0]):
                currencies.append(df_currencies['code'][j])
            # print(df_norm[['currencies','published_at', 'title','url']].iloc[i])

            if (set(currencies) & set(symbols_portfolio)) is not None:
                df_out = df_out.append(df_norm[['currencies','published_at', 'title','url']].iloc[i])
                df_out['currencies'].iloc[-1]=currencies
    return df_out


def gen_events_coindar(url_coindar):
    # Generate EVENT Details from CoinDar
    df = pd.read_json(url_coindar)

    # Convert DataFrame column type from string to datetime
    df['public_date'] = pd.to_datetime(df['public_date'])
    df = df.sort_values(by='public_date') # This now sorts in date order

    # Filter out only coins in the portfolio
    df1 = df[df['coin_symbol'].isin(symbols_portfolio)]
    df1 = df1[['coin_symbol','coin_name','caption','public_date','proof']]
    df2 = df1[((df1['public_date']>first_date) & (df1['public_date']<last_date))]
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # print out all articles, no cutdown
        print(df2)


if __name__ == '__main__':

    # Reset portfolio symbols
    # symbols_portfolio = ['XEM']
    # Decide what to pull
    pull_events = True
    pull_news = True

    # --- EVENTS ---
    if pull_events:
        url_coindar = "https://coindar.org/api/v1/lastEvents"
        # url_coindar = "https://coindar.org/api/v1/lastEvents?limit=100"
        # url_coindar = "https://coindar.org/api/v1/coinEvents?name=btc"
        print("***** EVENTS *****")
        gen_events_coindar(url_coindar)

    # --- NEWS ---
    url_cmc = "https://api.coinmarketcap.com/v1/ticker/?convert=EUR&limit=10"
    url_news_prefix = "https://cryptopanic.com/api/posts/?auth_token=xxx&trending=true&page="
    if pull_news:
        df_out = pd.DataFrame()
        for i in range(1,11):
            url_news = url_news_prefix + str(i)
            df_out = df_out.append(gen_news(url_news))
        print("\n***** NEWS *****")

        with pd.option_context('display.max_rows', None, 'display.max_columns', None): # print out all articles, no cutdown
            print(df_out)
