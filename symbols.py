from datetime import datetime

DEFAULT = {
    "Columns": {
        "Open": 0,
        "High": 1,
        "Low": 2,
        "Close": 3,
        "Volume": 4,
        "Quote asset volume": 5,
        "Number of trades": 6,
        "Taker buy base asset volume": 7,
        "Taker buy quote asset volume": 8,
    },
    "Timeframe": {
        "Data Interval": "1h",
        "Trading Interval": "8h",
        "Start Date": datetime(2020, 1, 1),
        "End Date": datetime(2020, 6, 1),
    },
    "Type": "BAR"
}

symbols = {
    "Binance": {
        "ETHUSDT": DEFAULT,
        "BCHUSDT": DEFAULT,
        "BTCUSDT": DEFAULT,
        "ETHBTC": DEFAULT,
        "XRPUSDT": DEFAULT,
        "XRPBTC": DEFAULT,
    },
    "Twitter-BTC": {
        "Timeframe": {
            "Trading Interval": "1h"
        },
        "Type": "SENTIMENT",
        "Data": "TWEET"
    }
}