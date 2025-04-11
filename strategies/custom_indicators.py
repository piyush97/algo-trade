import pandas as pd
import numpy as np
from typing import Tuple

class TechnicalIndicators:
    """Custom implementation of technical indicators without external dependencies"""
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Parameters:
        prices (pd.Series): Price series (typically Close prices)
        period (int): Period for RSI calculation (default: 14)
        
        Returns:
        pd.Series: RSI values
        """
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Parameters:
        prices (pd.Series): Price series (typically Close prices)
        fast (int): Fast EMA period (default: 12)
        slow (int): Slow EMA period (default: 26)
        signal (int): Signal line EMA period (default: 9)
        
        Returns:
        tuple: (macd_line, signal_line, histogram)
        """
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Parameters:
        prices (pd.Series): Price series (typically Close prices)
        period (int): Period for moving average (default: 20)
        std_dev (float): Number of standard deviations (default: 2)
        
        Returns:
        tuple: (upper_band, middle_band, lower_band)
        """
        middle_band = prices.rolling(window=period, min_periods=1).mean()
        std = prices.rolling(window=period, min_periods=1).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def sma(prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Parameters:
        prices (pd.Series): Price series
        period (int): Period for moving average
        
        Returns:
        pd.Series: Simple moving average
        """
        return prices.rolling(window=period, min_periods=1).mean()
    
    @staticmethod
    def ema(prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Parameters:
        prices (pd.Series): Price series
        period (int): Period for moving average
        
        Returns:
        pd.Series: Exponential moving average
        """
        return prices.ewm(span=period).mean()
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Parameters:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        k_period (int): %K period (default: 14)
        d_period (int): %D period (default: 3)
        
        Returns:
        tuple: (%K, %D)
        """
        lowest_low = low.rolling(window=k_period, min_periods=1).min()
        highest_high = high.rolling(window=k_period, min_periods=1).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period, min_periods=1).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Williams %R
        
        Parameters:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        period (int): Period for calculation (default: 14)
        
        Returns:
        pd.Series: Williams %R values
        """
        highest_high = high.rolling(window=period, min_periods=1).max()
        lowest_low = low.rolling(window=period, min_periods=1).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return williams_r
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Parameters:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        period (int): Period for ATR calculation (default: 14)
        
        Returns:
        pd.Series: ATR values
        """
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period, min_periods=1).mean()
        
        return atr