from utils.util import *
import time
from datetime import datetime


def get_symbols_from_market(exchange_market):
    # eoddata supports different exchange markets symbol search
    symbol_to_name = {}
    for market in exchange_market:
        current_pre = 'A'
        while True:
            url_str = "http://eoddata.com/stocklist/{market}/{pre}.htm".format(market = market, pre=current_pre)
            status, content = get_web_content(url_str)
            if status == 200:
                symbols_to_append = get_symbols_by_prefix_page(str(content))
                symbol_to_name = {**symbol_to_name, **symbols_to_append}
                print("%d symbols have been collected." %len(symbol_to_name))
            if current_pre == 'Z':
                break
            current_pre = chr(ord(current_pre) + 1)
            time.sleep(1)
    return symbol_to_name


def get_symbols_by_prefix_page(content_str):
    """
    :param content_str: the web content of the symbols with the starting character
    :return:
    """
    symbol_blocks = content_str.split("Display Quote")
    symbol_to_name = dict()
    for block in symbol_blocks[1:]:
        symbol = block.split('">')[1].split("<")[0]
        name = block.split("<td>")[1].split("</td>")[0]
        symbol_to_name[symbol] = name
    return symbol_to_name


def get_single_stock_all_info_from_yahoo(symbol, start_date, end_date):
    """
    This the first version of getting critical information for a stock from yahoo
    without re-grouping the features into valuation, finance and so on
    :param symbol: symbol name i.e., WMT
    :return: A dictionary containing all the key features of the symbol
    """
    feature_to_value = dict()
    features_from_summary = get_features_from_yahoo_summary(symbol)
    feature_to_value = {**feature_to_value, **features_from_summary}
    features_from_statistics = get_features_from_yahoo_statistics(symbol)
    feature_to_value = {**feature_to_value, **features_from_statistics}
    features_from_analysis = get_features_from_yahoo_analysis(symbol)
    feature_to_value = {**feature_to_value, **features_from_analysis}
    features_from_holder = get_features_from_yahoo_holder(symbol)
    feature_to_value = {**feature_to_value, **features_from_holder}
    features_from_history = get_features_from_yahoo_history(symbol, start_date, end_date)
    feature_to_value = {**feature_to_value, **features_from_history}
    return feature_to_value


def get_features_from_yahoo_history(symbol, start_date, end_date):
    url_str = "https://finance.yahoo.com/quote/{symbol}/history".format(symbol=symbol)
    status, content = get_web_content(url_str)
    #  Feb 21, 2020, Oct 21, 2019
    features_to_update = {}
    if status == 200:
        with open("../data/sample_history.txt", "w") as f:
            f.write(str(content))
    content = str(content)
    latest_close = float(content.split(start_date)[1].split("</span>")[4].split(">")[-1])
    close_months_ago = float(content.split(end_date)[1].split("</span>")[4].split(">")[-1])
    feature_to_value = dict()
    feature_to_value['close_months_ago'] = close_months_ago
    feature_to_value['close_change_pct'] = 1.0 * (latest_close - close_months_ago) / close_months_ago
    return feature_to_value



def get_features_from_yahoo_holder(symbol):
    url_str = "https://finance.yahoo.com/quote/{symbol}/holders".format(symbol=symbol)
    status, content = get_web_content(url_str)
    features_to_update = {}
    if status == 200:
        with open("../data/sample_holder.txt", "w") as f:
            f.write(str(content))
    holder_features = ["institutionsCount"]
    content = str(content)
    for feature in holder_features:
        content = content.split(feature)[1]
        value = content.split('"raw":')[1].split(",")[0]
        features_to_update[feature] = value
    return features_to_update

def get_features_from_yahoo_analysis(symbol):
    url_str = "https://finance.yahoo.com/quote/{symbol}/analysis".format(symbol=symbol)
    status, content = get_web_content(url_str)
    features_to_update = {}
    if status == 200:
        content = str(content)
        feature_to_lookup = {"No. of Analysts": "No. of Analysts</span>"}
        with open("../data/sample_analysis.txt", "w") as f:
            f.write(content)
        analysis_features = ["No. of Analysts"]
        for feature in analysis_features:
            lookup = feature
            if feature in feature_to_lookup:
                lookup = feature_to_lookup[feature]
            content = content.split(lookup)[-1]
            value = content.split("</span")[0].split(">")[-1]
    return features_to_update


def get_features_from_yahoo_statistics(symbol):
    url_str = "https://finance.yahoo.com/quote/{symbol}/key-statistics".format(symbol=symbol)
    status, content = get_web_content(url_str)
    features_to_update = {}
    if status == 200:
        content = str(content)
        feature_to_lookup = {"Market Cap": ">Market Cap", "Enterprise Value": "Enterprise Value<",
                             "Book Value Per Share": "Book Value Per Share<"}
        statistics_feature = ["Market Cap", "Enterprise Value", "Trailing P/E", "Forward P/E",
                              "PEG Ratio", "Price/Sales", "Price/Book", "Enterprise Value/Revenue",
                              "Enterprise Value/EBITDA", "% Held by Insiders",
                              "% Held by Institutions", "Short % of Shares Outstanding",
                              "Trailing Annual Dividend Yield", "Payout Ratio",
                              "Profit Margin", "Operating Margin",
                              "Return on Assets", "Return on Equity",
                              "Quarterly Revenue Growth", "Quarterly Earnings Growth",
                              "Total Cash Per Share", "Total Debt/Equity",
                              "Current Ratio", "Book Value Per Share"]
        for stats in statistics_feature:
            lookup = stats
            if stats in feature_to_lookup:
                lookup = feature_to_lookup[stats]
            content = content.split(lookup)[1]
            value = content.split("</td></tr>")[0].split(">")[-1]
            features_to_update[stats] = value
    return features_to_update


def get_features_from_yahoo_summary(symbol, only_close_price = False):
    url_str = "https://finance.yahoo.com/quote/{symbol}".format(symbol = symbol)
    status, content = get_web_content(url_str)
    features_to_update = {}
    if status == 200:
        content = str(content)
        content = content.split("quote-header-info")[1]
        current_close = content.split("</span")[1].split(">")[-1]
        if only_close_price:
            return current_close
        features_to_update['current_close'] = float(current_close)
        content = content.split("1y Target Est</span>")[1]
        target_price = content.split("</span>")[0].split(">")[-1]
        features_to_update['target_price'] = target_price
    return features_to_update




# //*[@id="rsrch-insghts"]/div/div[1]/div[2]/span
#//*[@id="quote-header-info"]/div[3]/div[1]/div/span[1]

if __name__ == '__main__':
    start_date, end_date = "Feb 21, 2020", "Oct 21, 2019"
    print(get_single_stock_all_info_from_yahoo("WMT", start_date, end_date))

