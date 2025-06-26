#!/usr/bin/env python3
"""
Quick Demo of Real-Time Trading Signals
Shows how the system analyzes stocks and generates signals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.realtime_data import RealTimeDataFetcher
from strategies.realtime_signals import RealTimeSignalGenerator
from utils.notifications import NotificationSystem

def demo():
    print("🚀 Real-Time Trading Signal Demo")
    print("=" * 50)
    
    # Initialize components
    data_fetcher = RealTimeDataFetcher()
    signal_generator = RealTimeSignalGenerator()
    notification_system = NotificationSystem()
    
    # Demo with Apple stock
    symbol = "AAPL"
    print(f"📊 Analyzing {symbol}...")
    
    # Get recent data
    data = data_fetcher.get_current_data(symbol, period="5d", interval="1m")
    
    if data.empty:
        print("❌ No data available. Please check your internet connection.")
        return
    
    print(f"✅ Retrieved {len(data)} data points")
    
    # Get latest price info
    latest_info = data_fetcher.get_latest_price(symbol)
    if latest_info:
        price = latest_info['price']
        change = latest_info['change']
        change_percent = latest_info['change_percent']
        print(f"💰 Current Price: ${price:.2f} ({change:+.2f}, {change_percent:+.2f}%)")
    
    # Generate comprehensive signals
    print("\\n🔍 Generating trading signals...")
    signal_data = signal_generator.generate_composite_signal(symbol, data)
    
    # Display results
    print("\\n📊 SIGNAL ANALYSIS RESULTS:")
    print("=" * 50)
    print(f"🎯 Overall Signal: {signal_data['overall_signal']}")
    print(f"🔥 Confidence: {signal_data['confidence']:.1f}%")
    print(f"📈 Buy Votes: {signal_data['buy_votes']}")
    print(f"📉 Sell Votes: {signal_data['sell_votes']}")
    
    print("\\n📋 Individual Strategy Analysis:")
    print("-" * 50)
    
    for signal in signal_data['individual_signals']:
        strategy = signal['strategy']
        signal_type = signal['signal']
        strength = signal['strength']
        reason = signal['reason']
        
        # Color coding
        if 'BUY' in signal_type:
            color = '\\033[92m'  # Green
        elif 'SELL' in signal_type:
            color = '\\033[91m'  # Red
        else:
            color = '\\033[93m'  # Yellow
        
        print(f"{color}{strategy}:{' ' * (15-len(strategy))} {signal_type} ({strength:.1f}%)\\033[0m")
        print(f"   Reason: {reason}")
        print()
    
    # Trading recommendation
    print("💡 TRADING RECOMMENDATION:")
    print("=" * 50)
    
    overall_signal = signal_data['overall_signal']
    confidence = signal_data['confidence']
    
    if overall_signal in ['STRONG_BUY', 'BUY']:
        print(f"🟢 RECOMMENDATION: Consider BUYING {symbol}")
        print(f"   Confidence: {confidence:.1f}%")
        if confidence >= 70:
            print("   ✅ High confidence signal - Strong buy opportunity")
        else:
            print("   ⚠️ Moderate confidence - Consider waiting for stronger signal")
    
    elif overall_signal in ['STRONG_SELL', 'SELL']:
        print(f"🔴 RECOMMENDATION: Consider SELLING {symbol}")
        print(f"   Confidence: {confidence:.1f}%")
        if confidence >= 70:
            print("   ✅ High confidence signal - Strong sell opportunity")
        else:
            print("   ⚠️ Moderate confidence - Consider waiting for stronger signal")
    
    else:
        print(f"🟡 RECOMMENDATION: HOLD position in {symbol}")
        print(f"   Current signal: {overall_signal}")
        print("   ⏳ Wait for clearer buy/sell signals")
    
    # Risk considerations
    print("\\n⚠️ RISK CONSIDERATIONS:")
    print("-" * 30)
    print("• This is a demo using recent market data")
    print("• Always use proper risk management")
    print("• Consider position sizing and stop losses")
    print("• Past performance doesn't guarantee future results")
    print("• Consult financial advisors for investment decisions")
    
    # Show how to start real-time monitoring
    print("\\n🚀 TO START REAL-TIME MONITORING:")
    print("-" * 40)
    print("python realtime_trader.py")
    print("python advanced_realtime_trader.py")
    print("python realtime_trader.py AAPL TSLA GOOGL --interval 60")
    
    print("\\n✅ Demo completed!")

if __name__ == "__main__":
    demo()