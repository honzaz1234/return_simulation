import numpy as np
import pandas as pd
import yfinance as yf
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from scipy.stats import t, norm

class  Instrument(ABC):

    def __init__(self, name, type_, reality):
        self.name = name
        self.type = type_
        self.reality = reality

    @abstractmethod
    def execute_time_period(self):
        pass


class Index(Instrument):

    def __init__(
            self, name, reality, type_='index'):
        super().__init__(name, type_, reality)
        self.price_ts = None
        self.current_price = None
        self.returns_ts = None
        self.returns_degf = None
        self.returns_scale = None
        self.returns_mean = None

    def index_set_up(self):
        self.get_data()
        self.calculate_returns()
        self.set_mean_sd()
        self.set_current_price()
        
    def get_data(self, n_years=30):
        date_to = datetime.now()
        date_from = date_to - timedelta(days=365.25 * n_years)
        date_from = date_from.date()
        date_to= date_to.date()
        stock_data = yf.download(
            self.name, start=date_from, end=date_to, interval="1mo")
        self.price_ts = list(stock_data['Close'])

    def calculate_returns(self):
        self.returns_ts = pd.DataFrame(self.price_ts).pct_change().dropna()

    def set_current_price(self):
        self.current_price = self.price_ts[-1]

    def set_mean_sd(self):
        loc, scale = norm.fit(np.array(self.returns_ts, dtype=float))
        #self.returns_degf = df
        self.returns_mean = loc
        self.returns_scale = scale

    def calculate_current_price(self):
        curr_return = norm.rvs( 
                            loc=self.returns_mean, 
                            scale=self.returns_scale, 
                            size=1)[0]
        print('cur_returns:')
        print(curr_return)
        self.current_price = (1 + curr_return) * self.current_price
        print('Current Price: ')
        print(self.current_price)

    def ts_calc(self, mma_length):
        if len(self.price_ts) < mma_length:
            print('We need at least ' 
                  + str(mma_length) 
                  + " previous observations")
            return
        current_price = ((sum(self.price_ts[len(self.price_ts) - (mma_length): ]))  / (mma_length))
        return current_price
            
    def execute_time_period(self, t):
        self.calculate_current_price()

class Bond(Instrument):


    def __init__(
            self, name, reality, type_='bond'):
        super().__init__(name, type_, reality)
        self.current_price = None
        

