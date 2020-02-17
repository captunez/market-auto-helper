import sys
from utils.util import *
from lxml import etree
from lxml.etree import tostring
import time


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


if __name__ == '__main__':
    exchange_market = ["NYSE", "NASDAQ"]
    get_symbols_from_market(exchange_market)
