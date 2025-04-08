import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, List, Callable, Optional

class RealTimeDataFetcher:
    def __init__(self, update_interval=60):
        self.update_interval = update_interval  # seconds
        self.symbols = []
        self.data_cache = {}
        self.callbacks = []
        self.is_running = False
        self.thread = None
        self.last_update = {}
        
    def add_symbol(self, symbol: str):
        """Add a symbol to monitor"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.data_cache[symbol] = pd.DataFrame()
            print(f"📊 Added {symbol} to monitoring list")
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from monitoring"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            del self.data_cache[symbol]
            print(f"❌ Removed {symbol} from monitoring list")
    
    def add_callback(self, callback: Callable):
        """Add a callback function to be called when data is updated"""
        self.callbacks.append(callback)
    
    def get_current_data(self, symbol: str, period="5d", interval="1m") -> pd.DataFrame:
        """Get current data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_latest_price(self, symbol: str) -> Dict:
        """Get the latest price and basic info for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get latest price data
            data = ticker.history(period="1d", interval="1m")
            if data.empty:
                return {}
            
            latest = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else latest
            
            return {
                'symbol': symbol,
                'price': latest['Close'],
                'change': latest['Close'] - previous['Close'],
                'change_percent': ((latest['Close'] - previous['Close']) / previous['Close']) * 100,
                'volume': latest['Volume'],
                'timestamp': latest.name,
                'high': latest['High'],
                'low': latest['Low'],
                'open': latest['Open']
            }
        except Exception as e:
            print(f"❌ Error getting latest price for {symbol}: {e}")
            return {}
    
    def update_data(self):
        """Update data for all monitored symbols"""
        for symbol in self.symbols:
            try:
                # Get recent data
                data = self.get_current_data(symbol, period="5d", interval="1m")
                if not data.empty:
                    self.data_cache[symbol] = data
                    self.last_update[symbol] = datetime.now()
                    
                    # Get latest price info
                    latest_info = self.get_latest_price(symbol)
                    
                    # Call all callbacks with updated data
                    for callback in self.callbacks:
                        try:
                            callback(symbol, data, latest_info)
                        except Exception as e:
                            print(f"❌ Error in callback for {symbol}: {e}")
                            
            except Exception as e:
                print(f"❌ Error updating data for {symbol}: {e}")
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_running:
            print("⚠️ Monitoring already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"🚀 Started real-time monitoring for {len(self.symbols)} symbols")
        print(f"📍 Update interval: {self.update_interval} seconds")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        print("⏹️ Stopped real-time monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                print(f"🔄 Updating data at {datetime.now().strftime('%H:%M:%S')}")
                self.update_data()
                time.sleep(self.update_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def get_cached_data(self, symbol: str) -> pd.DataFrame:
        """Get cached data for a symbol"""
        return self.data_cache.get(symbol, pd.DataFrame())
    
    def get_status(self) -> Dict:
        """Get monitoring status"""
        return {
            'is_running': self.is_running,
            'symbols': self.symbols,
            'update_interval': self.update_interval,
            'last_updates': self.last_update
        }