# Algorithmic Trader

There are several modules:

* Data Handler
* Strategy
* Portfolio
* Risk Handler
* BrokerDataHandler
* Backtest

### Backtest

File that combines all of the above modules.

Essentially runs through the DataHandler.__iter__() function. The DataHandler.__iter__() function, takes next(data), (In other words the next row/bar of data) and cocatenates it to the currect data. Backtester then updates the portfolio and executes the Strategy.on_data() which decides whether to buy or sell.

If Strategy wants to buy or sell something, it executes the RiskHandler.on_signal().

The RiskHandler decides how much to buy or sell (position sizing) and then calls the Broker.on_order(). The Broker then executes the order.

Once the broker has executed the order it calls Portfolio.on_fill() to update the current assets.

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

### Events 

Events are the signals that given to the backtester to let it know that new data has been added.

There are two event types which can trigger. SENTIMENT and BAR. SENTIMENT isn't completely implemented, but essentially it just scrapes twiiter too see how people are feeling about an asset.

Most modules have a specific function that execute the class.

