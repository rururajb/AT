"""
Settings Page
-------------
TODO
 * Documentation
"""

import enums
import symbols
from decimal import Decimal as D

"""
There are three modes
 * Backtest `backtest`: Uses the `HistoricDataHandler` and the `SimulatedExecutionHandler`
 * Paper Trading `paper`: Uses the `LiveDataHandler` and the `SimulatedExecutionHandler`
 * Live Trader `live`: Uses the `LiveDataHandler` and the `ExchangeHandler`
"""
MODE = "backtest"

FEES = {enums.exchanges.BINANCE: D(0.001)}

SYMBOLS = {
    # Exchange data
    "Binance": [
        # Symbols in exchange that you want to trade
        # Symbols must have a similarily named csv file
        "BTCUSDT",
    ],
    # "Twitter": [
    #     "BTC",
    # ]
}

DATA_INTERVAL: "1m"
TRADING_INTERVAL: "1m"

# ----------------
# | Data Handler |
# ----------------
# Warmup period is how many the starting point for the data. Everything in the
# warmup period can be used as data right from the start.
DATA_WARMUP_PERIOD = 500
DATA_DIRECTORY = r"C:\Users\evanh\Projects\AT\Data"

# ------------
# | Strategy |
# ------------

# Strategy you want to use. Backtesting uses getattr to read the strategy 
# provided that their is a equivalently named strategy in the strategy folder.
STRATEGY = "UpDownTick"
PARAMETERS = {"method": "TREND"}

# ----------------
# | Risk Handler |
# ----------------
TAKE_PROFITS = False
STOP_LOSSES = False
LEVERAGE_RATIO = 1.0
# Percent of total equity
CASH_BUFFER = .2
WEIGHTING = 'long-only'
POSITION_SIZER = {"method": "Fixed Size", "size": ".1"}

# -------------
# | Portfolio |
# -------------
INITIAL_CASH = 1000

# ----------
# | Broker |
# ----------
QUIET = True

# FEE MODEL
ADJUST_QUANTITY = True
SLIPPAGE_LAG = 1

BINANCE_PUBLIC = "7jb3SlTMwlZuDahexdh798uwtrCgjNyArWOWGbCEFrgZHI3gw0zjl6w7s1CXKUty"
BINANCE_PRIVATE = "5iC9G1mWHYmXOvzunuYuCoXNPJaSkEavs7JzN1rZuMnXMkDCHEJIuouyAl8s9ANO"