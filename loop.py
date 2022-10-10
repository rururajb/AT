from collections import deque

import pandas as pd

from data import HistoricData
import strategies
from portfolio import Portfolio
from risk import RiskHandler
from simple_risk import SimpleRiskHandler
from execution import SimulateExecutionHandler
from cMetrics import cMetrics

from datetime import *

import symbols

# TODO:
#  * Optimize
#  * Go Live! (or at least have the option of doing so)
#  * Use enums

class Backtester:
    def __init__(self, strat, initial_capital=1000):
        self.events = deque()
        self.dh = HistoricData(
            self.events,
            r"C:\Users\evanh\Projects\AT\Data",
            {"BTCUSDT": symbols.BTCUSDT},#, 'ETHUSDT': symbols.ETHUSDT, 'XRPUSDT': symbols.XRPUSDT},
            warmup_period=200,
        )
        self.portfolio = Portfolio(self.events, self.dh, initial_cash=initial_capital)
        self.rh = SimpleRiskHandler(self.dh, self.events, self.portfolio)

        # Load strategy module from string
        # strategy_ = getattr(strategies, strat)
        # self.strategy = strategy_(
        #     dh=self.dh,
        #     events=self.events,
        #     BollingerBandsStrategy=[],
        #     PredictiveStrategy=[],
        # )
        self.strategy = strategies.BollingerBandsStrategy()
        self.strategy.initialize(self.dh, self.events)
        self.broker = SimulateExecutionHandler(self.events, self.dh, verbose=True)

    def run(self):

        while True:
            self.dh.update_latest_data()

            if self.dh.continue_backtest == False:
                break

            while True:
                try:
                    event = self.events.popleft()
                except IndexError:
                    break

                if event is not None:
                    if event.type_ == "MARKET":
                        self.strategy.on_market(event)
                        self.portfolio.update_value(event.symbols)
                        self.rh.check_stop_loss(event)
                    elif event.type_ == "SIGNAL":
                        self.rh.on_signal(event)
                    elif event.type_ == "ORDER":
                        self.broker.execute_order(event)
                    elif event.type_ == "FILL":
                        self.portfolio.on_fill(event)

    def calculate_metrics(self):
        df = pd.DataFrame(self.portfolio.holdings)

        m = cMetrics(portfolio=self.portfolio, dh=self.dh)
        # m.holdings.index = self.dh.symbol_dates[self.dh.warmup_period:]
        print(m)
        # m.plot_holdings()


bt = Backtester("BuyAndHold")
bt.run()
bt.calculate_metrics()
