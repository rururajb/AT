# Algorithmic Trader

A program that will take market data and then decide when to trade.

### NOTICE

This program currently doesn't work. I created it in 2020, and I don't have the time to figure out what each line does. That being said I've done my best to document the most important files:

* [The historical data handler](https://github.com/evanwporter/AT/blob/main/DataHandler/historic_data.py)
* [Backtester](https://github.com/evanwporter/AT/blob/main/backtest.py] (ie: the engine of the program)

There are several modules:

* Data Handler
* Strategy
* Portfolio
* Risk Handler
* Broker
* Backtest

### Backtest

There is a detailed progression to each module.

The backtester runs on heartbeats. Each heartbeat, new data is made available.

The DataHandler is responsible for retrieving and making the new data available. First it instructs the Portfolio module to update the holdings with the new data. Then it calls Strategy module. The Strategy module is responsible for deciding whether to trade based on the newly available data.

If Strategy decides it wants to trade, then it calls the RiskHandler module. RiskHandler decides how much to trade (position sizing), and then calls the Broker module. The Broker module is responsible for making the trade online and updating the holdings in the Portfolio module.

### Data

Currently there are two types of data that the DataHandler can handle, SENTIMENT and BAR data. BAR data is just asset prices.  SENTIMENT isn't completely implemented, but essentially it just scrapes twitter too see how people are feeling about an asset.
