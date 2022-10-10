# Algorithmic Trader

There are several modules:

* Data Handler
* Strategy
* Portfolio
* Risk Handler
* BrokerDataHandler
* Backtest

Most modules have a specific function that execute the class.

### Data Handler

Handles a bar of data for each heartbeat of the system. Can handle historical data or current data.

### Strategy

Takes the current data and runs a particular strategy on that data. Then it outputs a BUY or a SELL signal.
as 

on_data()


### Portfolio

Portfolio is responsible for managing my porfolio and assets

on_fill()


### Risk Handler

Responsible for position sizing

It takes a signal and outputs a BUY or SELL order.

on_signal()


### Broker

Executes the order to the target exchange.

Also this is where slippage would be generated (if doing a historical backtest)

on_order()


### Backtest

File that combines all of the above modules.

Essentially runs through the DataHandler.__iter__() function.

Each heartbeat/loop of datahandler results in a new bar event. The bar event is sent to portfolio to update the holdings. Then the event is sent to strategy to create decide whether to buy or not.

Strategy then executes the RiskHandler.on_signal()

The RiskHandler calls the Broker.on_order(). The Broker then executes the order.

Once the broker has executed the order it calls Portfolio.on_fill() to update the current assets.


