import pandas as pd
import numpy as np

from decimal import Decimal as D

from collections import OrderedDict, defaultdict

import pystore
import json

from .event import *
from .dh import DataHandler
from .symbol import Symbol

import helper as h

import exceptions
import settings
from symbols import symbols as syms

from datetime import timedelta

# TODO: Add support for slicing data
class HistoricDataHandler(DataHandler):
    def __init__(self):

        store = pystore.store(settings.DATA_DIRECTORY)

        with open(r"C:\Users\evanh\Projects\AT\AT\symbol_info.json") as info:
            self.symbol_info = json.load(info)

        # PRIVATE
        self.symbol_data = {}
        self.trade_data = {}
        self.total_data = {}

        self.symbols = {
            Symbol(*self._split_symbol(symbol, source)): syms[source][symbol]
            for source, symbols in settings.SYMBOLS.items()
            for symbol in symbols
        }

        self.split_symbols = set(
            s
            for symbol in self.symbols
            for s in symbol
        )

        # PUBLIC
        self.latest_symbol_data = {symbol: None for symbol in self.symbols}

        self.warmup_period = settings.DATA_WARMUP_PERIOD

        self._parse_pystore(store)

    def _split_symbol(self, symbol, source=None):
        if source is None:
            source, symbol = h.split_symbol(symbol)
        base = self.symbol_info[symbol]["baseAsset"]
        quote = self.symbol_info[symbol]["quoteAsset"]

        return source, base, quote

    def _parse_pystore(self, store):
        self.dates = pd.Index([])
        market_data = {}

        nested_symbols = {
            data_source: list(symbol for symbol in symbols)
            for data_source, symbols in settings.SYMBOLS.items()
        }
        print(nested_symbols)
        for data_source, symbols in nested_symbols.items():
            source = store.collection(data_source)
            for symbol in symbols:

                data = source.item(str(symbol)).to_pandas()
                symbol = h.key(source=data_source, symbol=symbol)
                print(self.symbols)
                parameters = self.symbols[symbol]

                data_interval = parameters["Timeframe"]["Data Interval"]
                trading_interval = parameters["Timeframe"]["Trading Interval"]

                if type(data_interval) is str:
                    data_interval = np.timedelta64(
                        data_interval[:-1], data_interval[-1]
                    ).astype(timedelta)
                    parameters["Timeframe"]["Data Interval"] = data_interval
                if type(trading_interval) is str:
                    trading_interval = np.timedelta64(
                        trading_interval[:-1], trading_interval[-1]
                    ).astype(timedelta)
                    parameters["Timeframe"]["Trading Interval"] = trading_interval

                # Convert to decimal for extra precision
                data[["Open", "High", "Low", "Close"]] = (
                    data[["Open", "High", "Low", "Close"]].astype(str).applymap(D)
                )

                OHLC = (
                    data.resample(rule=data_interval)
                    .agg(
                        OrderedDict(
                            (
                                ("Open", "first"),
                                ("High", "max"),
                                ("Low", "min"),
                                ("Close", "last"),
                            )
                        )
                    )
                    .ffill()
                )
                V = (
                    data.drop(columns=["Open", "High", "Low", "Close"])
                    .resample(rule=data_interval)
                    .sum()
                )

                OHLCV = pd.concat((OHLC, V), axis=1)

                # Creates packages of sorts that contain data
                self.symbol_data[symbol] = (
                    df.to_numpy() for _, df, in OHLCV.resample(rule=trading_interval)
                )

                market_data[symbol] = OHLCV.asfreq(trading_interval)

                self.dates = self.dates.union(market_data[symbol].index)

        for symbol in self.symbols:

            # Creating trading index that
            # tells how often to trade
            # and when to load the data from
            # a package
            self.trade_data[symbol] = (
                market_data[symbol]
                .reindex(self.dates)
                .notnull()
                .all(axis=1)
                .to_numpy(dtype=bool)
            )

        # for symbol, parameters in self.symbols.items():

        # if h.split_symbol(symbol)[0] == "Twitter":
        #     trading_interval = trading_interval
        #     data.date = pd.to_datetime(
        #         data.date, format="%Y-%m-%d %H:%M:%S+00:00", utc=True
        #     )
        #     data.set_index("date", inplace=True)
        #     self.symbol_data[symbol] = [
        #         df for date, df in data.resample(rule=trading_interval)
        #     ]
        #     self.market_data[symbol] = pd.DataFrame(
        #         {"date": date, "empty": np.nan if df.empty else 0}
        #         for date, df in data.resample(rule=trading_interval)
        #     ).set_index("date")

    def __iter__(self):

        for self.size in range(len(self.dates)):
            bar = BarEvent(self.date)
            sentiment = SentimentEvent(self.date)
            for symbol in self.symbols:
                if self.trade_data[symbol][self.size]:
                    # if h.split_symbol(symbol)[0] == "Twitter":
                    #     self.latest_symbol_data[symbol] = self.symbol_data[symbol][
                    #         self.size
                    #     ]
                    #     sentiment.symbols[symbol] = self.sp.split_symbol(symbol, include_source=True)
                    # else:
                    if self.latest_symbol_data[symbol] is None:
                        self.latest_symbol_data[symbol] = next(self.symbol_data[symbol])
                    else:
                        self.latest_symbol_data[symbol] = np.concatenate(
                            (
                                self.latest_symbol_data[symbol],
                                next(self.symbol_data[symbol]),
                            )
                        )
                    bar.symbols.append(symbol)

            if self.size >= self.warmup_period:
                yield [bar]  # , sentiment]
