import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self):
        self.data = None
    
    def fetch_data(self, symbol, period="1y", interval="1d"):
        """
        Fetch stock data from Yahoo Finance
        
        Parameters:
        symbol (str): Stock symbol (e.g., 'AAPL', 'GOOGL')
        period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
        pd.DataFrame: Stock data with OHLCV columns
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            self.data = data
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_multiple_symbols(self, symbols, period="1y", interval="1d"):
        """
        Fetch data for multiple symbols
        
        Parameters:
        symbols (list): List of stock symbols
        period (str): Data period
        interval (str): Data interval
        
        Returns:
        dict: Dictionary with symbol as key and DataFrame as value
        """
        data_dict = {}
        for symbol in symbols:
            data_dict[symbol] = self.fetch_data(symbol, period, interval)
        return data_dict
    
    def get_info(self, symbol):
        """Get stock information"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except Exception as e:
            print(f"Error getting info for {symbol}: {e}")
            return None