import numpy as np

from .trading_env import TradingEnv, Actions, Positions

#yemi-defined
from running_z_score import Running_Z_Score

class ForexEnv(TradingEnv):

    def __init__(self, df, window_size, frame_bound, unit_side='left'):
        assert len(frame_bound) == 2
        assert unit_side.lower() in ['left', 'right']

        self.frame_bound = frame_bound
        self.unit_side = unit_side.lower()
        super().__init__(df, window_size)

        self.trade_fee = 0.0003  # unit


    def _process_data(self):
        prices = self.df.loc[:, 'Close'].to_numpy()

        prices[self.frame_bound[0] - self.window_size]  # validate index (TODO: Improve validation)
        prices = prices[self.frame_bound[0]-self.window_size:self.frame_bound[1]]

        diff = np.insert(np.diff(prices), 0, 0)   #diff is used in arr to calc diference in price of prev index... kinda like %change without the%
        
        #yemi--------------------------------------------------------------------
        #print(self.df.columns)
        open = self.df.loc[:, 'Open'].to_numpy()
        high = self.df.loc[:, 'High'].to_numpy()
        low = self.df.loc[:, 'Low'].to_numpy()


        norm_close = np.empty_like(prices)
        norm_open = np.empty_like(open)
        norm_high = np.empty_like(high)
        norm_low = np.empty_like(low)

        normalize_data_close = Running_Z_Score(mode = "min-max", period = 96)
        normalize_data_open = Running_Z_Score(mode = "min-max", period = 96)
        normalize_data_high = Running_Z_Score(mode = "min-max", period = 96)
        normalize_data_low = Running_Z_Score(mode = "min-max", period = 96)

        for price, o, h, l, idx in zip(prices, open, high, low, range(prices.size)):
            norm_close[idx] = normalize_data_close.norm(price)
            norm_open[idx] = normalize_data_open.norm(o)
            norm_high[idx] = normalize_data_high.norm(h)
            norm_low[idx] = normalize_data_low.norm(l)

        #signal_features = np.stack((norm_close, diff, norm_open, norm_high, norm_low), axis=-1)
        signal_features = np.column_stack((norm_close, diff))
        
        #signal_features = np.column_stack((prices, diff))

        return prices, signal_features


    def _calculate_reward(self, action):
        step_reward = 0  # pip

        trade = False
        if ((action == Actions.Buy.value and self._position == Positions.Short) or
            (action == Actions.Sell.value and self._position == Positions.Long)):
            trade = True

        if trade:
            current_price = self.prices[self._current_tick]
            last_trade_price = self.prices[self._last_trade_tick]
            price_diff = current_price - last_trade_price

            if self._position == Positions.Short:
                step_reward += -price_diff * 10000
            elif self._position == Positions.Long:
                step_reward += price_diff * 10000

        return step_reward


    def _update_profit(self, action):
        trade = False
        if ((action == Actions.Buy.value and self._position == Positions.Short) or
            (action == Actions.Sell.value and self._position == Positions.Long)):
            trade = True

        if trade or self._done:
            current_price = self.prices[self._current_tick]
            last_trade_price = self.prices[self._last_trade_tick]

            if self.unit_side == 'left':
                if self._position == Positions.Short:
                    quantity = self._total_profit * (last_trade_price - self.trade_fee)
                    self._total_profit = quantity / current_price

            elif self.unit_side == 'right':
                if self._position == Positions.Long:
                    quantity = self._total_profit / last_trade_price
                    self._total_profit = quantity * (current_price - self.trade_fee)


    def max_possible_profit(self):
        current_tick = self._start_tick
        last_trade_tick = current_tick - 1
        profit = 1.

        while current_tick <= self._end_tick:
            position = None
            if self.prices[current_tick] < self.prices[current_tick - 1]:
                while (current_tick <= self._end_tick and
                       self.prices[current_tick] < self.prices[current_tick - 1]):
                    current_tick += 1
                position = Positions.Short
            else:
                while (current_tick <= self._end_tick and
                       self.prices[current_tick] >= self.prices[current_tick - 1]):
                    current_tick += 1
                position = Positions.Long

            current_price = self.prices[current_tick - 1]
            last_trade_price = self.prices[last_trade_tick]

            if self.unit_side == 'left':
                if position == Positions.Short:
                    quantity = profit * (last_trade_price - self.trade_fee)
                    profit = quantity / current_price

            elif self.unit_side == 'right':
                if position == Positions.Long:
                    quantity = profit / last_trade_price
                    profit = quantity * (current_price - self.trade_fee)

            last_trade_tick = current_tick - 1

        return profit
