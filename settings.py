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
    "Binance": [
        # "ETHUSDT",
        "BTCUSDT",
        # "Binance-XRPUSDT",
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
DATA_WARMUP_PERIOD = 500
DATA_DIRECTORY = r"C:\Users\evanh\Projects\AT\Data"

# Strategy
STRATEGY = "UpDownTick"
PARAMETERS = {"method": "TREND"} #{"BollingerBands": ("TREND", 24), "method": "all"}

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