from Portfolio.position import Position
# from .trade import Trade

import pandas as pd
import numpy as np
from decimal import Decimal as D

from enums import trade_type, asset_side

from collections import deque, defaultdict
from copy import deepcopy

import helper as h

# from decimal import Decimal

import settings as settings

import logging

# TODO: Incorporate position sizing and risk
# TODO: Move over from floats to Decimals

# TODO: Ensure that currencies like XRPBTC can be used
# For XRPBTC, the asset would still have to be measured in USD
# So XRPUSD and BTCUSD
class Portfolio:
    def __init__(self, dh):
        self.dh = dh

        self.positions = {symbol: Position(symbol) for symbol in self.dh.split_symbols}
        self.positions["Binance-USDT"].quantity = settings.INITIAL_CASH
        
        # Double Ended Queue
        self.holdings = deque()

        self.trades: dict = defaultdict(deque)
        self.closed_trades: list = deque()

        self.weights = {symbol: 0 for symbol in self.dh.split_symbols}
        self.weights["Binance-USDT"] = 100

    def update_value(self, symbols, edit=False):

        holding = {}
        for symbol in symbols:
            # type(symbol) = Symbol()
            # Loops through base and asset
            for s in symbol:

                if h.is_cash_like(s):
                    price = D(1.0)
                else:
                    price = self.dh.get_latest_data(symbol, "Close")
                
                date = self.dh.date

                holding["%s Value" % s] = self.positions[s].update_value(price, date)

        holding_array = np.array(list(holding.values()))
        holding["Assets"] = np.sum(holding_array[holding_array > 0])
        holding["Debt"] = np.sum(holding_array[holding_array < 0])
        holding["Total Equity"] = np.sum(holding_array)

        # Update weights
        for symbol in symbols:

            base = symbol.base

            self.weights['Binance-USDT'] = (holding["Binance-USDT Value"] * 100) / holding["Total Equity"]
            if self.positions[base].market_value != 0:
                self.weights[base] = (holding["%s Value" % base] * 100) / holding["Total Equity"]
            else:
                self.weights[base] = 0

        # Debt-to-Equity ratio
        holding["Leverage"] = holding["Assets"] / holding["Total Equity"]

        # edit means write over current data (I think)
        # I believe I put in there in case I wanted to preallocate an array
        if not edit:
            self.holdings.append(holding)
        else:
            self.holdings[-1] = holding


    @property
    def portfolio_df(self):
        return pd.DataFrame(
            list(map(lambda position: vars(position), self.positions.values()))
        ).set_index(["Symbol"])

    def on_fill(
        self,
        id_,
        symbol, # Symbol
        quantity,
        direction,
        price,
        fill_type,
        slippage=None,
        commission=None,
        stop_loss=None,
    ):
        
        # Buying means buying Base and selling Quote
        # Selling mean selling Base and buying the Quote

        # Buy/Long means increase `Base Asset` and decrease `Quote Asset`
        if direction == trade_type.LONG or direction == trade_type.BUY:
            self.positions[symbol.base].update_position(
                quantity=quantity,
                price=price,
                direction=direction,
                side=asset_side.BASE,
                slippage=slippage,
            )
            self.positions[symbol.quote].update_position(
                quantity=quantity,
                price=price,
                direction=direction,
                side=asset_side.QUOTE,
                slippage=slippage,
                commission=commission,
            )

        # Sell/Short means decrease `Base Asset` and increase `Quote Asset`
        else: # direction == trade_type.SHORT or direction == trade_type.SELL:
            self.positions[symbol.base].update_position(
                quantity=quantity,
                price=price,
                direction=direction,
                side=asset_side.BASE,
                slippage=slippage,
            )
            self.positions[symbol.quote].update_position(
                quantity=quantity,
                price=price,
                direction=direction,
                side=asset_side.QUOTE,
                slippage=slippage,
                commission=commission,
            )

        # if direction == trade_type.LONG or direction == enums.trade_type.SHORT:
        #     self.trades[symbol].append(
        #         Trade(
        #             symbol=symbol,
        #             id_=id_,
        #             quantity=quantity,
        #             open_date=date,
        #             price=price,
        #             slippage=slippage,
        #             commission=commission,
        #             direction=direction,
        #             stop_loss=stop_loss,
        #         )
        #     )

        # elif direction == enums.trade_type.BUY or direction == enums.trade_type.SELL:
        #     if fill_type == "SIGNAL":
        #         self._modify_trade(symbol, quantity, price, date)
        #     else:
        #         trade = h.find_id(self.trades[symbol], id_)
        #         self.trades[symbol].remove(trade)
        #         trade.close_price = price
        #         trade.close_date = date
        #         self.closed_trades.append(trade)

        self.update_value([symbol], edit=True)
        
        # TODO: Provide more info
        logging.debug("Made a trade.")

    # This is implemented stuff
#     def _modify_trade(self, symbol, desired_quantity, price, date):
#         while True:
#             # Makes sure deque isn't empty
#             if (not self.trades[symbol]) or (desired_quantity == 0):
#                 break

#             last_trade = self.trades[symbol][0]

#             # Checks if trade quantity is less than desired quantity.
#             # If so it closes the trade in question and subtracts
#             # the trade quantity from the desired quanity
#             if last_trade.quantity <= desired_quantity:

#                 desired_quantity -= last_trade.quantity
#                 last_trade.close_date = date
#                 last_trade.close_price = price

#                 self.broker.modify_order(symbol, last_trade.id_, quantity=0)

#                 self.closed_trades.append(self.trades[symbol].popleft())

#             # Checks if desired quanity is less than trade quantity.
#             # If so it subtracts the desired_quanity from the trade quantity,
#             # It also creates a copy of the trade which it then modifies and
#             # adds to the closed trades
#             else:
#                 ct = deepcopy(last_trade)
#                 ct.quantity = desired_quantity
#                 ct.close_date = date
#                 ct.close_price = price

#                 self.trades[symbol][0].quantity -= desired_quantity

#                 self.broker.modify_order(
#                     symbol, last_trade.id_, self.trades[symbol][0].quantity
#                 )

#                 self.closed_trades.append(ct)
#                 break
    
    @property
    def total_equity(self):
        return self.holdings[-1]["Total Equity"]
