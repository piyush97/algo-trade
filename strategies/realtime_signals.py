import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .custom_indicators import TechnicalIndicators

class RealTimeSignalGenerator:
    def __init__(self):
        self.signals_history = {}
        self.last_signals = {}
        
    def calculate_sma_signals(self, data: pd.DataFrame, short_window=20, long_window=50) -> Dict:
        """Calculate Simple Moving Average signals"""
        if len(data) < long_window:
            return {'signal': 'HOLD', 'strength': 0, 'reason': 'Insufficient data'}
        
        # Calculate moving averages
        data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
        data['SMA_long'] = data['Close'].rolling(window=long_window).mean()
        
        # Get latest values
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        current_price = latest['Close']
        short_ma = latest['SMA_short']
        long_ma = latest['SMA_long']
        prev_short_ma = previous['SMA_short']
        prev_long_ma = previous['SMA_long']
        
        # Determine signal
        signal = 'HOLD'
        strength = 0
        reason = ''
        
        # Check for crossover
        if short_ma > long_ma and prev_short_ma <= prev_long_ma:
            signal = 'BUY'
            strength = min(((short_ma - long_ma) / long_ma) * 100, 100)
            reason = f'SMA crossover: {short_window}-day MA crossed above {long_window}-day MA'
        elif short_ma < long_ma and prev_short_ma >= prev_long_ma:
            signal = 'SELL'
            strength = min(((long_ma - short_ma) / long_ma) * 100, 100)
            reason = f'SMA crossover: {short_window}-day MA crossed below {long_window}-day MA'
        elif short_ma > long_ma:
            signal = 'HOLD_BULLISH'
            strength = min(((short_ma - long_ma) / long_ma) * 100, 100)
            reason = f'Bullish trend: {short_window}-day MA above {long_window}-day MA'
        else:
            signal = 'HOLD_BEARISH'
            strength = min(((long_ma - short_ma) / long_ma) * 100, 100)
            reason = f'Bearish trend: {short_window}-day MA below {long_window}-day MA'
        
        return {
            'signal': signal,
            'strength': round(strength, 2),
            'reason': reason,
            'current_price': current_price,
            'short_ma': round(short_ma, 2),
            'long_ma': round(long_ma, 2),
            'strategy': 'SMA'
        }
    
    def calculate_rsi_signals(self, data: pd.DataFrame, period=14, oversold=30, overbought=70) -> Dict:
        """Calculate RSI signals"""
        if len(data) < period + 1:
            return {'signal': 'HOLD', 'strength': 0, 'reason': 'Insufficient data'}
        
        # Calculate RSI
        data['RSI'] = TechnicalIndicators.rsi(data['Close'], period=period)
        
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        current_rsi = latest['RSI']
        prev_rsi = previous['RSI']
        current_price = latest['Close']
        
        signal = 'HOLD'
        strength = 0
        reason = ''
        
        if current_rsi <= oversold and prev_rsi > oversold:
            signal = 'BUY'
            strength = (oversold - current_rsi) / oversold * 100
            reason = f'RSI oversold: {current_rsi:.1f} (threshold: {oversold})'
        elif current_rsi >= overbought and prev_rsi < overbought:
            signal = 'SELL'
            strength = (current_rsi - overbought) / (100 - overbought) * 100
            reason = f'RSI overbought: {current_rsi:.1f} (threshold: {overbought})'
        elif current_rsi <= oversold:
            signal = 'HOLD_OVERSOLD'
            strength = (oversold - current_rsi) / oversold * 100
            reason = f'RSI oversold territory: {current_rsi:.1f}'
        elif current_rsi >= overbought:
            signal = 'HOLD_OVERBOUGHT'
            strength = (current_rsi - overbought) / (100 - overbought) * 100
            reason = f'RSI overbought territory: {current_rsi:.1f}'
        else:
            signal = 'HOLD_NEUTRAL'
            strength = 0
            reason = f'RSI neutral: {current_rsi:.1f}'
        
        return {
            'signal': signal,
            'strength': round(strength, 2),
            'reason': reason,
            'current_price': current_price,
            'rsi': round(current_rsi, 2),
            'strategy': 'RSI'
        }
    
    def calculate_macd_signals(self, data: pd.DataFrame, fast=12, slow=26, signal_period=9) -> Dict:
        """Calculate MACD signals"""
        if len(data) < slow + signal_period:
            return {'signal': 'HOLD', 'strength': 0, 'reason': 'Insufficient data'}
        
        # Calculate MACD
        macd_line, signal_line, histogram = TechnicalIndicators.macd(data['Close'], fast=fast, slow=slow, signal=signal_period)
        data['MACD'] = macd_line
        data['MACD_signal'] = signal_line
        data['MACD_histogram'] = histogram
        
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        current_macd = latest['MACD']
        current_signal = latest['MACD_signal']
        current_histogram = latest['MACD_histogram']
        prev_macd = previous['MACD']
        prev_signal = previous['MACD_signal']
        current_price = latest['Close']
        
        signal = 'HOLD'
        strength = 0
        reason = ''
        
        # Check for signal line crossover
        if current_macd > current_signal and prev_macd <= prev_signal:
            signal = 'BUY'
            strength = min(abs(current_macd - current_signal) * 100, 100)
            reason = 'MACD bullish crossover: MACD line crossed above signal line'
        elif current_macd < current_signal and prev_macd >= prev_signal:
            signal = 'SELL'
            strength = min(abs(current_macd - current_signal) * 100, 100)
            reason = 'MACD bearish crossover: MACD line crossed below signal line'
        elif current_macd > current_signal:
            signal = 'HOLD_BULLISH'
            strength = min(abs(current_macd - current_signal) * 100, 100)
            reason = 'MACD bullish: MACD line above signal line'
        else:
            signal = 'HOLD_BEARISH'
            strength = min(abs(current_macd - current_signal) * 100, 100)
            reason = 'MACD bearish: MACD line below signal line'
        
        return {
            'signal': signal,
            'strength': round(strength, 2),
            'reason': reason,
            'current_price': current_price,
            'macd': round(current_macd, 4),
            'macd_signal': round(current_signal, 4),
            'macd_histogram': round(current_histogram, 4),
            'strategy': 'MACD'
        }
    
    def calculate_bollinger_bands_signals(self, data: pd.DataFrame, period=20, std_dev=2) -> Dict:
        """Calculate Bollinger Bands signals"""
        if len(data) < period:
            return {'signal': 'HOLD', 'strength': 0, 'reason': 'Insufficient data'}
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(data['Close'], period=period, std_dev=std_dev)
        data['BB_upper'] = bb_upper
        data['BB_middle'] = bb_middle
        data['BB_lower'] = bb_lower
        
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        current_price = latest['Close']
        prev_price = previous['Close']
        bb_upper = latest['BB_upper']
        bb_middle = latest['BB_middle']
        bb_lower = latest['BB_lower']
        
        signal = 'HOLD'
        strength = 0
        reason = ''
        
        # Check for bounces off bands
        if current_price <= bb_lower and prev_price > bb_lower:
            signal = 'BUY'
            strength = ((bb_lower - current_price) / bb_lower) * 100
            reason = f'Bollinger Bands: Price touched lower band at {bb_lower:.2f}'
        elif current_price >= bb_upper and prev_price < bb_upper:
            signal = 'SELL'
            strength = ((current_price - bb_upper) / bb_upper) * 100
            reason = f'Bollinger Bands: Price touched upper band at {bb_upper:.2f}'
        elif current_price <= bb_lower:
            signal = 'HOLD_OVERSOLD'
            strength = ((bb_lower - current_price) / bb_lower) * 100
            reason = f'Bollinger Bands: Price below lower band (oversold)'
        elif current_price >= bb_upper:
            signal = 'HOLD_OVERBOUGHT'
            strength = ((current_price - bb_upper) / bb_upper) * 100
            reason = f'Bollinger Bands: Price above upper band (overbought)'
        else:
            signal = 'HOLD_NEUTRAL'
            strength = 0
            reason = f'Bollinger Bands: Price between bands'
        
        return {
            'signal': signal,
            'strength': round(strength, 2),
            'reason': reason,
            'current_price': current_price,
            'bb_upper': round(bb_upper, 2),
            'bb_middle': round(bb_middle, 2),
            'bb_lower': round(bb_lower, 2),
            'strategy': 'Bollinger Bands'
        }
    
    def generate_composite_signal(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Generate composite signal from multiple strategies"""
        signals = []
        
        # Get signals from all strategies
        sma_signal = self.calculate_sma_signals(data)
        rsi_signal = self.calculate_rsi_signals(data)
        macd_signal = self.calculate_macd_signals(data)
        bb_signal = self.calculate_bollinger_bands_signals(data)
        
        signals.extend([sma_signal, rsi_signal, macd_signal, bb_signal])
        
        # Calculate composite signal
        buy_votes = sum(1 for s in signals if s['signal'] in ['BUY'])
        sell_votes = sum(1 for s in signals if s['signal'] in ['SELL'])
        bullish_votes = sum(1 for s in signals if s['signal'] in ['BUY', 'HOLD_BULLISH'])
        bearish_votes = sum(1 for s in signals if s['signal'] in ['SELL', 'HOLD_BEARISH'])
        
        # Determine overall signal
        overall_signal = 'HOLD'
        confidence = 0
        
        if buy_votes >= 2:
            overall_signal = 'STRONG_BUY'
            confidence = (buy_votes / len(signals)) * 100
        elif buy_votes >= 1 and bullish_votes >= 3:
            overall_signal = 'BUY'
            confidence = (bullish_votes / len(signals)) * 100
        elif sell_votes >= 2:
            overall_signal = 'STRONG_SELL'
            confidence = (sell_votes / len(signals)) * 100
        elif sell_votes >= 1 and bearish_votes >= 3:
            overall_signal = 'SELL'
            confidence = (bearish_votes / len(signals)) * 100
        elif bullish_votes > bearish_votes:
            overall_signal = 'WEAK_BUY'
            confidence = 30
        elif bearish_votes > bullish_votes:
            overall_signal = 'WEAK_SELL'
            confidence = 30
        
        return {
            'symbol': symbol,
            'overall_signal': overall_signal,
            'confidence': round(confidence, 1),
            'timestamp': datetime.now(),
            'individual_signals': signals,
            'buy_votes': buy_votes,
            'sell_votes': sell_votes,
            'bullish_votes': bullish_votes,
            'bearish_votes': bearish_votes
        }
    
    def should_alert(self, symbol: str, new_signal: Dict) -> bool:
        """Check if we should send an alert for this signal"""
        if symbol not in self.last_signals:
            self.last_signals[symbol] = new_signal
            return True
        
        last_signal = self.last_signals[symbol]
        
        # Alert if signal changed
        if last_signal['overall_signal'] != new_signal['overall_signal']:
            self.last_signals[symbol] = new_signal
            return True
        
        # Alert if confidence changed significantly
        if abs(last_signal['confidence'] - new_signal['confidence']) >= 20:
            self.last_signals[symbol] = new_signal
            return True
        
        return False