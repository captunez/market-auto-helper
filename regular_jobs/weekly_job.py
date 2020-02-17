import os
import json
import sys
sys.path.append('../')
from utils.stock_utils import *

EXCHANGE_MARKETS = ["NYSE", "NASDAQ"]
DATA_DIR = "../data"


def update_symbol_list():
    symbol_to_name = get_symbols_from_market(EXCHANGE_MARKETS)
    parent_dir = os.path.join(DATA_DIR, "symbols")
    write_to_path = os.path.join(parent_dir, "all_symbols_" + "_".join(EXCHANGE_MARKETS) + ".txt")
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    with open(write_to_path, "w") as f:
        f.write(json.dumps(symbol_to_name))


def process():
    update_symbol_list()


if __name__ == '__main__':
    process()
