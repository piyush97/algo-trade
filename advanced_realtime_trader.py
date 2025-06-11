#!/usr/bin/env python3
"""
Advanced Real-Time Trading System
Complete trading system with risk management, position tracking, and smart alerts
"""

import sys
import os
import time
import signal as sig
from datetime import datetime
import argparse
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.realtime_data import RealTimeDataFetcher
from strategies.realtime_signals import RealTimeSignalGenerator
from utils.notifications import NotificationSystem
from utils.risk_management import RiskManager

class AdvancedRealTimeTrader:
    def __init__(self, symbols: List[str], update_interval: int = 60, initial_capital: float = 10000):
        self.symbols = symbols
        self.update_interval = update_interval
        
        # Initialize components
        self.data_fetcher = RealTimeDataFetcher(update_interval=update_interval)
        self.signal_generator = RealTimeSignalGenerator()
        self.notification_system = NotificationSystem()
        self.risk_manager = RiskManager()
        
        # Set initial capital
        self.risk_manager.portfolio_value = initial_capital
        self.risk_manager.daily_start_value = initial_capital
        
        # Add symbols to monitor
        for symbol in symbols:
            self.data_fetcher.add_symbol(symbol)
        
        # Set up signal handler for graceful shutdown
        sig.signal(sig.SIGINT, self._signal_handler)
        sig.signal(sig.SIGTERM, self._signal_handler)
        
        self.running = True
        self.trade_log = []
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\\n🛑 Received shutdown signal. Stopping...")
        self.running = False
        self.data_fetcher.stop_monitoring()
    
    def _on_data_update(self, symbol: str, data, latest_info):
        """Callback function for when data is updated"""
        try:
            if data.empty or not latest_info:
                return
            
            current_price = latest_info.get('price', 0)
            if current_price <= 0:
                return
            
            # Generate trading signals
            signal_data = self.signal_generator.generate_composite_signal(symbol, data)
            
            # Process trading logic
            self._process_trading_signals(symbol, current_price, signal_data)
            
            # Show current status
            self._show_current_status(symbol, latest_info, signal_data)
            
        except Exception as e:
            print(f"❌ Error processing data for {symbol}: {e}")
    
    def _process_trading_signals(self, symbol: str, current_price: float, signal_data: Dict):
        """Process trading signals and execute trades if appropriate"""
        
        # Check for position exit first
        should_exit, exit_reason = self.risk_manager.should_exit_position(symbol, current_price, signal_data)
        if should_exit:
            exit_record = self.risk_manager.exit_position(symbol, current_price, exit_reason)
            if exit_record:
                self.trade_log.append(exit_record)
                # Send exit notification
                exit_alert = self._create_exit_alert(exit_record)
                self.notification_system.send_alert(exit_alert)
        
        # Check for position entry
        else:
            should_enter, entry_reason = self.risk_manager.should_enter_position(symbol, signal_data)
            if should_enter:
                # Calculate position size
                confidence_factor = min(signal_data.get('confidence', 0) / 100, 1.0)
                position_info = self.risk_manager.calculate_position_size(symbol, current_price, confidence_factor)
                
                if position_info['shares'] > 0:
                    # Enter position
                    self.risk_manager.enter_position(symbol, position_info)
                    
                    # Send entry notification
                    entry_alert = self._create_entry_alert(position_info, signal_data)
                    self.notification_system.send_alert(entry_alert)
            
            # Send regular signal alerts for monitoring
            elif self.signal_generator.should_alert(symbol, signal_data):
                self.notification_system.send_alert(signal_data)
    
    def _create_entry_alert(self, position_info: Dict, signal_data: Dict) -> Dict:
        """Create alert for position entry"""
        return {
            'symbol': position_info['symbol'],
            'overall_signal': f"POSITION_ENTERED",
            'confidence': signal_data.get('confidence', 0),
            'timestamp': datetime.now(),
            'individual_signals': [{
                'strategy': 'Risk Management',
                'signal': 'BUY',
                'strength': 100,
                'current_price': position_info['entry_price'],
                'reason': f"Entered {position_info['shares']} shares. Stop: ${position_info['stop_loss_price']:.2f}, Target: ${position_info['take_profit_price']:.2f}"
            }],
            'position_info': position_info
        }
    
    def _create_exit_alert(self, exit_record: Dict) -> Dict:
        """Create alert for position exit"""
        return {
            'symbol': exit_record['symbol'],
            'overall_signal': f"POSITION_EXITED",
            'confidence': 100,
            'timestamp': datetime.now(),
            'individual_signals': [{
                'strategy': 'Risk Management',
                'signal': 'SELL',
                'strength': 100,
                'current_price': exit_record['exit_price'],
                'reason': f"Exited {exit_record['shares']} shares. P&L: ${exit_record['pnl']:+.2f} ({exit_record['pnl_percent']:+.1f}%). Reason: {exit_record['reason']}"
            }],
            'exit_record': exit_record
        }
    
    def _show_current_status(self, symbol: str, latest_info, signal_data):
        """Show current status for a symbol"""
        price = latest_info.get('price', 0)
        change = latest_info.get('change', 0)
        change_percent = latest_info.get('change_percent', 0)
        signal = signal_data.get('overall_signal', 'HOLD')
        confidence = signal_data.get('confidence', 0)
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Color for price change
        color = '\\033[92m' if change >= 0 else '\\033[91m'
        reset = '\\033[0m'
        
        # Position indicator
        position_indicator = ""
        if symbol in self.risk_manager.current_positions:
            position = self.risk_manager.current_positions[symbol]
            entry_price = position['entry_price']
            shares = position['shares']
            current_pnl = shares * (price - entry_price)
            pnl_percent = (current_pnl / position['position_value']) * 100
            pnl_color = '\\033[92m' if current_pnl >= 0 else '\\033[91m'
            position_indicator = f" | {pnl_color}[POS: {shares} @ ${entry_price:.2f} P&L: ${current_pnl:+.2f} ({pnl_percent:+.1f}%)]{reset}"
        
        # Signal color
        signal_colors = {
            'STRONG_BUY': '\\033[92m',
            'BUY': '\\033[92m',
            'WEAK_BUY': '\\033[93m',
            'HOLD': '\\033[94m',
            'WEAK_SELL': '\\033[93m',
            'SELL': '\\033[91m',
            'STRONG_SELL': '\\033[91m'
        }
        signal_color = signal_colors.get(signal, '\\033[0m')
        
        print(f"[{timestamp}] {symbol}: {color}${price:.2f} ({change:+.2f}, {change_percent:+.2f}%){reset} | {signal_color}{signal} ({confidence:.1f}%){reset}{position_indicator}")
    
    def _show_portfolio_update(self):
        """Show periodic portfolio update"""
        current_prices = {}
        for symbol in self.risk_manager.current_positions.keys():
            data = self.data_fetcher.get_cached_data(symbol)
            if not data.empty:
                current_prices[symbol] = data['Close'].iloc[-1]
        
        # Update daily P&L
        total_daily_pnl = self.risk_manager.update_daily_pnl(current_prices)
        
        # Get portfolio summary
        portfolio = self.risk_manager.get_portfolio_summary()
        risk_metrics = self.risk_manager.get_risk_metrics()
        
        print("\\n" + "="*80)
        print("💼 PORTFOLIO UPDATE")
        print("="*80)
        print(f"Total Value: ${portfolio['total_value']:,.2f} | Cash: ${portfolio['cash']:,.2f} | Invested: ${portfolio['invested']:,.2f}")
        print(f"Daily P&L: ${total_daily_pnl:+,.2f} ({(total_daily_pnl/self.risk_manager.daily_start_value)*100:+.2f}%)")
        print(f"Positions: {portfolio['num_positions']} | Portfolio Risk: {risk_metrics['current_portfolio_risk']:.1f}%")
        print("="*80 + "\\n")
    
    def start(self):
        """Start real-time monitoring with advanced features"""
        print("🚀 Advanced Real-Time Trading System")
        print("=" * 80)
        print(f"📊 Monitoring symbols: {', '.join(self.symbols)}")
        print(f"💰 Initial capital: ${self.risk_manager.portfolio_value:,.2f}")
        print(f"⏱️ Update interval: {self.update_interval} seconds")
        print(f"🛡️ Risk Management: ON")
        print(f"   • Max position size: {self.risk_manager.max_position_size*100:.1f}%")
        print(f"   • Stop loss: {self.risk_manager.stop_loss_percent*100:.1f}%")
        print(f"   • Take profit: {self.risk_manager.take_profit_percent*100:.1f}%")
        print(f"   • Max daily loss: {self.risk_manager.max_daily_loss*100:.1f}%")
        print("=" * 80)
        print("💡 Press Ctrl+C to stop monitoring")
        print("\\n📈 Live Data Feed:")
        
        # Add callback for data updates
        self.data_fetcher.add_callback(self._on_data_update)
        
        # Start monitoring
        self.data_fetcher.start_monitoring()
        
        last_portfolio_update = time.time()
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
                # Show portfolio update every 5 minutes
                if time.time() - last_portfolio_update > 300:  # 5 minutes
                    self._show_portfolio_update()
                    last_portfolio_update = time.time()
                
        except KeyboardInterrupt:
            print("\\n🛑 Stopping monitoring...")
        
        finally:
            self.data_fetcher.stop_monitoring()
            print("\\n📊 Final Summary:")
            self._show_final_summary()
    
    def _show_final_summary(self):
        """Show comprehensive trading summary"""
        print("\\n" + "="*80)
        print("📈 FINAL TRADING SESSION SUMMARY")
        print("="*80)
        
        # Portfolio summary
        portfolio = self.risk_manager.get_portfolio_summary()
        print(f"💼 Portfolio Value: ${portfolio['total_value']:,.2f}")
        print(f"💰 Cash: ${portfolio['cash']:,.2f}")
        print(f"📊 Invested: ${portfolio['invested']:,.2f}")
        print(f"📈 Daily P&L: ${portfolio['daily_pnl']:+,.2f} ({portfolio['daily_pnl_percent']:+.2f}%)")
        
        # Current positions
        if self.risk_manager.current_positions:
            print(f"\\n📍 Current Positions ({len(self.risk_manager.current_positions)}):")
            for symbol, position in self.risk_manager.current_positions.items():
                print(f"  {symbol}: {position['shares']} shares @ ${position['entry_price']:.2f}")
                print(f"    Stop: ${position['stop_loss_price']:.2f} | Target: ${position['take_profit_price']:.2f}")
        
        # Trade log
        if self.trade_log:
            print(f"\\n💹 Completed Trades ({len(self.trade_log)}):")
            total_pnl = sum(trade['pnl'] for trade in self.trade_log)
            winning_trades = len([t for t in self.trade_log if t['pnl'] > 0])
            
            print(f"  Total Realized P&L: ${total_pnl:+,.2f}")
            print(f"  Win Rate: {winning_trades}/{len(self.trade_log)} ({(winning_trades/len(self.trade_log)*100):.1f}%)")
            
            print("\\n  Recent trades:")
            for trade in self.trade_log[-5:]:  # Show last 5 trades
                pnl_color = '\\033[92m' if trade['pnl'] >= 0 else '\\033[91m'
                print(f"    {trade['symbol']}: ${trade['pnl']:+.2f} ({trade['pnl_percent']:+.1f}%) - {trade['reason']}")
        
        # Show alert history
        alerts = self.notification_system.get_alert_history(10)
        if alerts:
            print(f"\\n🚨 Recent Alerts ({len(alerts)}):")
            for alert in alerts[-5:]:  # Show last 5 alerts
                timestamp = alert['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                print(f"  {timestamp.strftime('%H:%M:%S')} - {alert['symbol']}: {alert['signal']} ({alert['confidence']}%)")
        
        # Save session data
        self._save_session_data()
        
        print("\\n✅ Session ended successfully")
    
    def _save_session_data(self):
        """Save session data to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save alerts
        alert_file = self.notification_system.save_alerts_to_file(f"alerts_{timestamp}.json")
        
        # Save trade log
        if self.trade_log:
            import json
            trade_file = f"trades_{timestamp}.json"
            try:
                # Convert datetime objects to strings
                trade_log_json = []
                for trade in self.trade_log:
                    trade_copy = trade.copy()
                    for key, value in trade_copy.items():
                        if isinstance(value, datetime):
                            trade_copy[key] = value.isoformat()
                    trade_log_json.append(trade_copy)
                
                with open(trade_file, 'w') as f:
                    json.dump(trade_log_json, f, indent=2)
                print(f"💾 Trade log saved to: {trade_file}")
            except Exception as e:
                print(f"❌ Failed to save trade log: {e}")

def main():
    parser = argparse.ArgumentParser(description='Advanced Real-Time Trading System')
    parser.add_argument('symbols', nargs='*', default=['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
                        help='Stock symbols to monitor (default: AAPL GOOGL MSFT TSLA)')
    parser.add_argument('--interval', '-i', type=int, default=60,
                        help='Update interval in seconds (default: 60)')
    parser.add_argument('--capital', '-c', type=float, default=10000,
                        help='Initial capital (default: 10000)')
    parser.add_argument('--test', action='store_true',
                        help='Run notification test and exit')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Testing notification system...")
        notification_system = NotificationSystem()
        notification_system.test_notifications()
        return
    
    # Validate symbols
    symbols = [symbol.upper() for symbol in args.symbols]
    
    if not symbols:
        print("❌ No symbols provided")
        return
    
    # Create and start trader
    trader = AdvancedRealTimeTrader(symbols, args.interval, args.capital)
    trader.start()

if __name__ == "__main__":
    main()