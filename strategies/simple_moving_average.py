import pandas as pd
import numpy as np
from typing import Tuple, Dict

class SimpleMovingAverageStrategy:
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window
        self.positions = None
        self.signals = None
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on moving average crossover
        
        Parameters:
        data (pd.DataFrame): Stock data with 'Close' column
        
        Returns:
        pd.DataFrame: DataFrame with signals and positions
        """
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        
        # Calculate moving averages
        signals['short_mavg'] = data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_mavg'] = data['Close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Generate signals
        signals['signal'] = 0.0
        signals['signal'][self.short_window:] = np.where(
            signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:], 
            1.0, 0.0
        )
        
        # Generate positions
        signals['positions'] = signals['signal'].diff()
        
        self.signals = signals
        return signals
    
    def get_trades(self) -> Dict:
        """
        Get buy/sell trade points
        
        Returns:
        dict: Dictionary with buy and sell signals
        """
        if self.signals is None:
            return {"buy": [], "sell": []}
        
        buy_signals = self.signals[self.signals['positions'] == 1.0]
        sell_signals = self.signals[self.signals['positions'] == -1.0]
        
        return {
            "buy": buy_signals.index.tolist(),
            "sell": sell_signals.index.tolist()
        }
    
    def calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate strategy returns
        
        Parameters:
        data (pd.DataFrame): Stock data with signals
        
        Returns:
        pd.DataFrame: DataFrame with returns
        """
        if self.signals is None:
            self.generate_signals(data)
        
        returns = pd.DataFrame(index=data.index)
        returns['stock_returns'] = data['Close'].pct_change()
        returns['strategy_returns'] = returns['stock_returns'] * self.signals['signal'].shift(1)
        returns['cumulative_stock_returns'] = (1 + returns['stock_returns']).cumprod()
        returns['cumulative_strategy_returns'] = (1 + returns['strategy_returns']).cumprod()
        
        return returns