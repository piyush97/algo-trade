#!/usr/bin/env python3
"""
Real-Time Trading Signal Generator
Monitors stocks and provides live buy/sell suggestions
"""

import sys
import os
import time
import signal as sig
from datetime import datetime
import argparse
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.realtime_data import RealTimeDataFetcher
from strategies.realtime_signals import RealTimeSignalGenerator
from utils.notifications import NotificationSystem

class RealTimeTrader:
    def __init__(self, symbols: List[str], update_interval: int = 60):
        self.symbols = symbols
        self.update_interval = update_interval
        
        # Initialize components
        self.data_fetcher = RealTimeDataFetcher(update_interval=update_interval)
        self.signal_generator = RealTimeSignalGenerator()
        self.notification_system = NotificationSystem()
        
        # Add symbols to monitor
        for symbol in symbols:
            self.data_fetcher.add_symbol(symbol)
        
        # Set up signal handler for graceful shutdown
        sig.signal(sig.SIGINT, self._signal_handler)
        sig.signal(sig.SIGTERM, self._signal_handler)
        
        self.running = True
    
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
            
            # Generate trading signals
            signal_data = self.signal_generator.generate_composite_signal(symbol, data)
            
            # Check if we should send an alert
            if self.signal_generator.should_alert(symbol, signal_data):
                self.notification_system.send_alert(signal_data)
            
            # Always show current status (less verbose)
            self._show_current_status(symbol, latest_info, signal_data)
            
        except Exception as e:
            print(f"❌ Error processing data for {symbol}: {e}")
    
    def _show_current_status(self, symbol: str, latest_info, signal_data):
        """Show current status for a symbol"""
        price = latest_info.get('price', 0)
        change = latest_info.get('change', 0)
        change_percent = latest_info.get('change_percent', 0)
        signal = signal_data.get('overall_signal', 'HOLD')
        confidence = signal_data.get('confidence', 0)
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Color for price change
        color = '\\033[92m' if change >= 0 else '\\033[91m'  # Green for positive, red for negative
        reset = '\\033[0m'
        
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
        
        print(f"[{timestamp}] {symbol}: {color}${price:.2f} ({change:+.2f}, {change_percent:+.2f}%){reset} | {signal_color}{signal} ({confidence:.1f}%){reset}")
    
    def start(self):
        """Start real-time monitoring"""
        print("🚀 Starting Real-Time Trading Signal Generator")
        print("=" * 60)
        print(f"📊 Monitoring symbols: {', '.join(self.symbols)}")
        print(f"⏱️ Update interval: {self.update_interval} seconds")
        print(f"🔔 Notifications: Console ✓ Desktop ✓ Sound ✓")
        print("=" * 60)
        print("💡 Press Ctrl+C to stop monitoring")
        print("\\n📈 Live Data Feed:")
        
        # Add callback for data updates
        self.data_fetcher.add_callback(self._on_data_update)
        
        # Start monitoring
        self.data_fetcher.start_monitoring()
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\\n🛑 Stopping monitoring...")
        
        finally:
            self.data_fetcher.stop_monitoring()
            print("\\n📊 Final Summary:")
            self._show_summary()
    
    def _show_summary(self):
        """Show trading summary"""
        print("\\n" + "="*60)
        print("📈 TRADING SESSION SUMMARY")
        print("="*60)
        
        # Show alert history
        alerts = self.notification_system.get_alert_history(10)
        if alerts:
            print(f"🚨 Recent Alerts ({len(alerts)}):")
            for alert in alerts[-5:]:  # Show last 5 alerts
                timestamp = alert['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                print(f"  {timestamp.strftime('%H:%M:%S')} - {alert['symbol']}: {alert['signal']} ({alert['confidence']}%)")
        else:
            print("🚨 No alerts generated during this session")
        
        # Save alerts to file
        filename = self.notification_system.save_alerts_to_file()
        if filename:
            print(f"💾 Alert history saved to: {filename}")
        
        print("\\n✅ Session ended successfully")
    
    def add_symbol(self, symbol: str):
        """Add a new symbol to monitor"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.data_fetcher.add_symbol(symbol)
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from monitoring"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            self.data_fetcher.remove_symbol(symbol)

def main():
    parser = argparse.ArgumentParser(description='Real-Time Trading Signal Generator')
    parser.add_argument('symbols', nargs='*', default=['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
                        help='Stock symbols to monitor (default: AAPL GOOGL MSFT TSLA)')
    parser.add_argument('--interval', '-i', type=int, default=60,
                        help='Update interval in seconds (default: 60)')
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
    trader = RealTimeTrader(symbols, args.interval)
    trader.start()

if __name__ == "__main__":
    main()