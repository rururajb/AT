import numpy as np
from decimal import Decimal as D

import helper as h

import talib

import enums

import settings
import logging

from Broker.Fees import PercentFeeModel

# TODO:
#  * Reincoporate hrp allocation
#  * Add more position size techniques
#     * Kelly Criterion
#     * Van Tharp CPR


class SimpleRiskHandler:
    def __init__(
        self, dh, portfolio, broker, weighting="long only",
    ):
        self.dh = dh

        self.portfolio = portfolio
        self.holdings = self.portfolio.holdings
        self.positions = self.portfolio.positions

        self.broker = broker
        self.fee_model = PercentFeeModel()

        self.sls = settings.STOP_LOSSES
        self.tps = settings.TAKE_PROFITS

        # Maximum Leverage Ratio
        self.MLR = settings.LEVERAGE_RATIO
        if self.MLR is not type(D):
            self.MLR = D(self.MLR)

        # Cash Buffer
        self.CB = D(settings.CASH_BUFFER) * D(settings.INITIAL_CASH)
        if self.CB == D("0"):
            logging.warning(
                "Cash buffer is 0. The recommended cash buffer is at least .05"
            )

        cash_buffer = int(settings.CASH_BUFFER * 100)

        self.weight_bounds = {"Binance-BTC": (0, 100 - cash_buffer)}
        self.weight_bounds["Binance-USDT"] = (cash_buffer, 100)

        self.weights = self.portfolio.weights

        self.weighting = settings.WEIGHTING

    # def _allocate_cash_buffer(self):
    #     cash_buffer = self.CB * self.total_equity
    #     available_cash = self.portfolio.cash.quantity - cash_buffer
    #     for order in self.broker.orders:
    #         commission

    def _bet_size(self, price):
        # name = settings.POSITION_SIZER["method"]

        # # if name == r"Fixed % TE":
        # #     quantity = (settings.POSITION_SIZER["size"] * self.TE) / price

        # # if name == "Fixed Size":
        # #     quantity = settings.POSITION_SIZER["size"]

        # # if quantity is not type(D):
        # #     quantity = D(quantity)

        return D(".05")

    def _calculate_direction(self, symbol, quantity, direct):
        """There are two kinds of orders orders that increase a position
        (Long and Short orders) and orders that decrease a position (Buy
        and Sell).

        Parameters
        ----------
        symbol : str
        """

        current_position = self.positions[symbol].quantity
        if direct == "LONG":
            if quantity + current_position > 0:
                direction = "LONG"
            else:  # quantity + self.positions[event.symbol].quantity <= 0:
                # Buy orders happen only if a position is negative
                # Meaning its been shorted
                direction = "BUY"
        else:
            # Been shorted
            if -quantity + current_position < 0:
                direction = "SHORT"
            else:  # quantity + self.positions[event.symbol].quantity >= 0:
                direction = "SELL"

        return direction

    def _adjust_for_commission(self, quantity, price):
        return ((quantity * price) / (1 + settings.FEES["Binance"])) / price

    def _check_leverage(self, price, direction, symbol):
        current_holdings = self.holdings[-1]

        if direction == "SHORT" or direction == "SELL":
            quantity = -self.quantity

        # Maximum Asset Value
        MAV = self.MLR * self.TE

        # Usable Asset Value
        # TODO: Implement some algorithm for calculating the way back
        UAV = MAV - (
            current_holdings["Assets"]
            - ((current_holdings["Cash"] * D(".999")))
            - self.CB
        )

        # Maximum Quantity
        MQ = UAV / price

        if self.quantity > MQ:
            self.quantity = MQ

        # mock_holding = self.holdings[-1].copy()

        # # Market Value
        # MV = price * self.quantity

        # try:
        #     mock_holding["%s Value" % symbol] += MV
        # except KeyError:
        #     mock_holding["%s Value" % symbol] = MV

        # mock_holding["Cash"] -= MV * .999
        # mock_holding_array = np.array(list(mock_holding.values())[:-4])

        # # Potential Asset Value
        # PAV = np.sum(mock_holding_array[mock_holding_array > 0])

        # TE = np.sum(mock_holding_array)

        # # Potential Leverage Ratio
        # PLR = PAV / TE

        # if self.MLR < PLR:
        #     self.quantity = 0

        # PLR = self.MLR

        # # Adjusted AV
        # AAV = PLR * TE

        # market_value = AAV - self.holdings[-1]["Assets"]

        # self.quantity = round(
        #     market_value / price, 8
        # )

    def _set_stop_loss(self, symbol, price, direction, date, id_):
        data = self.dh.get_latest_data(
            symbol, columns=["Close", "High", "Low"], N=0, dtype=np.float64
        )
        volatility = D((3 * talib.ATR(*data))[-1])

        if direction == enums.trade_type.LONG:
            stop_loss = price - volatility
        elif enums.trade_type.SHORT:
            stop_loss = price + volatility

        self.broker.on_order(
            date=date,
            id_=id_,
            symbol=symbol,
            stop_loss=stop_loss,
            order_type="TRAILING STOP",
            quantity=self.quantity,
            direction=direction,
        )

        return stop_loss

    def _set_take_profit(self, symbol, price, direction, date, id_):
        data = self.dh.get_latest_data(
            symbol, columns=["Close", "High", "Low"], N=0, dtype=np.float64
        )
        volatility = D((0.5 * talib.ATR(*data))[-1])

        if direction == enums.trade_type.LONG:
            profit_point = price + volatility
        elif enums.trade_type.SHORT:
            profit_point = price - volatility

        self.broker.on_order(
            date=date,
            id_=id_,
            symbol=symbol,
            profit_point=profit_point,
            order_type="TAKE PROFIT",
            quantity=self.quantity,
            direction=direction,
        )

        return profit_point

    def _check_weights(
        self, base, quote, weight_adjustment, price, direction, debug=False
    ):
        weight_adjustment = weight_adjustment * 100

        base_weight = self.weights[base]
        base_min_weight, base_max_weight = self.weight_bounds[base]

        quote_weight = self.weights[quote]
        quote_min_weight, quote_max_weight = self.weight_bounds[quote]

        if direction == "LONG":
            distance = min(
                # Quote distance                    Base distance
                quote_weight - quote_min_weight, base_max_weight - base_weight
            )
            if distance < weight_adjustment:
                # Scales quanity down
                weight_adjustment = distance
        elif direction == "SHORT":
            quote_distance = quote_max_weight - quote_weight
            base_distance = base_weight - base_min_weight
            distance = min(quote_distance, base_distance)
            if distance < weight_adjustment:
                weight_adjustment = distance

        # Turn the weight adjustment into a hard quantity
        quantity = (self.TE * weight_adjustment) / (price * 100)

        return self._adjust_for_commission(quantity=quantity, price=price).quantize(
            D(enums.places.EIGHT)
        )

    def on_signal(self, price, symbol, direction):
        base = symbol.base
        quote = symbol.quote

        self.TE = self.portfolio.total_equity

        weight_adjustment = self._bet_size(price)
        quantity = self._check_weights(
            base=base,
            quote=quote,
            weight_adjustment=weight_adjustment,
            price=price,
            direction=direction,
        )
        direction = self._calculate_direction(base, quantity, direction)

        # if direction == "SHORT":
        #     weight = self.weights["Binance-BTC"]
        #     self._check_weights(
        #         base=base,
        #         quote=quote,
        #         weight_adjustment=weight_adjustment,
        #         price=price,
        #         direction=direction,
        #         debug=True,
        #     )
        if quantity > 0:
            id_ = h.generate_unique_id()

            if direction == "LONG" or direction == "SHORT":
                stop_loss = (
                    self._set_stop_loss(symbol, price, direction, date, id_)
                    if self.sls
                    else None
                )
                profit_point = (
                    self._set_take_profit(symbol, price, direction, date, id_)
                    if self.tps
                    else None
                )
            else:
                stop_loss = None
                profit_point = None

            self.broker.on_order(
                id_=id_,
                symbol=symbol,
                price=price,
                order_type="MARKET",
                quantity=quantity,
                direction=direction,
                stop_loss=stop_loss,
                profit_point=profit_point,
            )

