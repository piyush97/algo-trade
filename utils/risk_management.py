import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class RiskManager:
    def __init__(self, 
                 max_position_size=0.1,  # 10% of portfolio per position
                 max_daily_loss=0.05,    # 5% max daily loss
                 stop_loss_percent=0.05,  # 5% stop loss
                 take_profit_percent=0.15,  # 15% take profit
                 max_portfolio_risk=0.2):   # 20% max portfolio risk
        
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.max_portfolio_risk = max_portfolio_risk
        
        self.portfolio_value = 10000  # Default starting value
        self.current_positions = {}
        self.daily_pnl = 0
        self.daily_start_value = self.portfolio_value
        
    def calculate_position_size(self, symbol: str, entry_price: float, signal_strength: float = 1.0) -> Dict:
        """
        Calculate appropriate position size based on risk management rules
        
        Parameters:
        symbol (str): Stock symbol
        entry_price (float): Proposed entry price
        signal_strength (float): Signal strength (0-1), affects position size
        
        Returns:
        dict: Position sizing information
        """
        # Base position size (percentage of portfolio)
        base_position_size = self.max_position_size * signal_strength
        
        # Calculate dollar amount
        position_value = self.portfolio_value * base_position_size
        
        # Calculate number of shares
        shares = int(position_value / entry_price)
        actual_position_value = shares * entry_price
        
        # Calculate stop loss and take profit levels
        stop_loss_price = entry_price * (1 - self.stop_loss_percent)
        take_profit_price = entry_price * (1 + self.take_profit_percent)
        
        # Calculate risk per share
        risk_per_share = entry_price - stop_loss_price
        total_risk = shares * risk_per_share
        
        # Check if position exceeds risk limits
        risk_warning = False
        if total_risk > self.portfolio_value * self.max_daily_loss:
            risk_warning = True
            # Reduce position size to meet risk limit
            max_shares = int((self.portfolio_value * self.max_daily_loss) / risk_per_share)
            shares = min(shares, max_shares)
            actual_position_value = shares * entry_price
            total_risk = shares * risk_per_share
        
        return {
            'symbol': symbol,
            'shares': shares,
            'entry_price': entry_price,
            'position_value': actual_position_value,
            'position_percent': (actual_position_value / self.portfolio_value) * 100,
            'stop_loss_price': round(stop_loss_price, 2),
            'take_profit_price': round(take_profit_price, 2),
            'risk_amount': round(total_risk, 2),
            'risk_percent': (total_risk / self.portfolio_value) * 100,
            'risk_warning': risk_warning,
            'signal_strength': signal_strength
        }
    
    def should_enter_position(self, symbol: str, signal_data: Dict) -> Tuple[bool, str]:
        """
        Determine if we should enter a position based on risk management rules
        
        Returns:
        tuple: (should_enter: bool, reason: str)
        """
        signal = signal_data.get('overall_signal', 'HOLD')
        confidence = signal_data.get('confidence', 0)
        
        # Don't enter if not a buy signal
        if signal not in ['BUY', 'STRONG_BUY']:
            return False, f"Signal is {signal}, not a buy signal"
        
        # Check if we already have a position
        if symbol in self.current_positions:
            return False, f"Already have position in {symbol}"
        
        # Check daily loss limit
        daily_loss_percent = (self.daily_pnl / self.daily_start_value) * 100
        if daily_loss_percent <= -self.max_daily_loss * 100:
            return False, f"Daily loss limit reached ({daily_loss_percent:.1f}%)"
        
        # Check portfolio risk
        current_risk = self.calculate_current_portfolio_risk()
        if current_risk >= self.max_portfolio_risk:
            return False, f"Portfolio risk limit reached ({current_risk:.1%})"
        
        # Check signal confidence
        min_confidence = 60  # Minimum confidence for entry
        if confidence < min_confidence:
            return False, f"Signal confidence too low ({confidence:.1f}% < {min_confidence}%)"
        
        return True, "All risk checks passed"
    
    def should_exit_position(self, symbol: str, current_price: float, signal_data: Dict = None) -> Tuple[bool, str]:
        """
        Determine if we should exit a position based on risk management rules
        
        Returns:
        tuple: (should_exit: bool, reason: str)
        """
        if symbol not in self.current_positions:
            return False, "No position to exit"
        
        position = self.current_positions[symbol]
        entry_price = position['entry_price']
        
        # Check stop loss
        if current_price <= position['stop_loss_price']:
            return True, f"Stop loss triggered at ${current_price:.2f} (entry: ${entry_price:.2f})"
        
        # Check take profit
        if current_price >= position['take_profit_price']:
            return True, f"Take profit triggered at ${current_price:.2f} (entry: ${entry_price:.2f})"
        
        # Check signal reversal
        if signal_data:
            signal = signal_data.get('overall_signal', 'HOLD')
            confidence = signal_data.get('confidence', 0)
            
            if signal in ['SELL', 'STRONG_SELL'] and confidence >= 70:
                return True, f"Strong sell signal: {signal} ({confidence:.1f}% confidence)"
        
        # Check time-based exit (optional - hold for max 30 days)
        entry_date = position.get('entry_date', datetime.now())
        if isinstance(entry_date, str):
            entry_date = datetime.fromisoformat(entry_date)
        
        days_held = (datetime.now() - entry_date).days
        if days_held >= 30:
            return True, f"Maximum holding period reached ({days_held} days)"
        
        return False, "No exit conditions met"
    
    def enter_position(self, symbol: str, position_info: Dict):
        """Record a new position"""
        position_info['entry_date'] = datetime.now()
        position_info['entry_time'] = datetime.now().isoformat()
        self.current_positions[symbol] = position_info
        
        # Update portfolio value
        self.portfolio_value -= position_info['position_value']
        
        print(f"✅ Entered position: {symbol} - {position_info['shares']} shares at ${position_info['entry_price']:.2f}")
        print(f"   Stop Loss: ${position_info['stop_loss_price']:.2f} | Take Profit: ${position_info['take_profit_price']:.2f}")
        print(f"   Risk: ${position_info['risk_amount']:.2f} ({position_info['risk_percent']:.1f}%)")
    
    def exit_position(self, symbol: str, exit_price: float, reason: str = "Manual exit"):
        """Exit a position and calculate P&L"""
        if symbol not in self.current_positions:
            return None
        
        position = self.current_positions[symbol]
        shares = position['shares']
        entry_price = position['entry_price']
        
        # Calculate P&L
        exit_value = shares * exit_price
        entry_value = position['position_value']
        pnl = exit_value - entry_value
        pnl_percent = (pnl / entry_value) * 100
        
        # Update portfolio value
        self.portfolio_value += exit_value
        self.daily_pnl += pnl
        
        # Create exit record
        exit_record = {
            'symbol': symbol,
            'shares': shares,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_value': entry_value,
            'exit_value': exit_value,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'reason': reason,
            'entry_date': position.get('entry_date'),
            'exit_date': datetime.now(),
            'holding_days': (datetime.now() - position.get('entry_date', datetime.now())).days
        }
        
        # Remove from current positions
        del self.current_positions[symbol]
        
        print(f"❌ Exited position: {symbol} - {shares} shares at ${exit_price:.2f}")
        print(f"   P&L: ${pnl:+.2f} ({pnl_percent:+.1f}%) | Reason: {reason}")
        
        return exit_record
    
    def calculate_current_portfolio_risk(self) -> float:
        """Calculate current portfolio risk exposure"""
        total_risk = 0
        for position in self.current_positions.values():
            total_risk += position.get('risk_amount', 0)
        
        return total_risk / self.portfolio_value if self.portfolio_value > 0 else 0
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        total_position_value = sum(pos['position_value'] for pos in self.current_positions.values())
        cash = self.portfolio_value
        total_portfolio_value = cash + total_position_value
        
        return {
            'total_value': total_portfolio_value,
            'cash': cash,
            'invested': total_position_value,
            'num_positions': len(self.current_positions),
            'daily_pnl': self.daily_pnl,
            'daily_pnl_percent': (self.daily_pnl / self.daily_start_value) * 100,
            'portfolio_risk': self.calculate_current_portfolio_risk(),
            'positions': self.current_positions
        }
    
    def update_daily_pnl(self, current_prices: Dict[str, float]):
        """Update daily P&L based on current prices"""
        unrealized_pnl = 0
        
        for symbol, position in self.current_positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                entry_price = position['entry_price']
                shares = position['shares']
                unrealized_pnl += shares * (current_price - entry_price)
        
        # Total daily P&L includes realized + unrealized
        total_daily_pnl = self.daily_pnl + unrealized_pnl
        return total_daily_pnl
    
    def reset_daily_tracking(self):
        """Reset daily tracking (call at market open)"""
        self.daily_pnl = 0
        self.daily_start_value = self.portfolio_value + sum(pos['position_value'] for pos in self.current_positions.values())
    
    def get_risk_metrics(self) -> Dict:
        """Get comprehensive risk metrics"""
        portfolio_summary = self.get_portfolio_summary()
        
        return {
            'max_position_size': self.max_position_size * 100,
            'max_daily_loss': self.max_daily_loss * 100,
            'stop_loss_percent': self.stop_loss_percent * 100,
            'take_profit_percent': self.take_profit_percent * 100,
            'max_portfolio_risk': self.max_portfolio_risk * 100,
            'current_portfolio_risk': portfolio_summary['portfolio_risk'] * 100,
            'daily_pnl_percent': portfolio_summary['daily_pnl_percent'],
            'cash_percent': (portfolio_summary['cash'] / portfolio_summary['total_value']) * 100,
            'invested_percent': (portfolio_summary['invested'] / portfolio_summary['total_value']) * 100
        }