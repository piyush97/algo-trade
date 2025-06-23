#!/usr/bin/env python3
"""
Easy startup script for the trading system
Automatically handles virtual environment and dependencies
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Real-Time Algorithmic Trading System")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('requirements.txt'):
        print("❌ Please run this script from the algo-trading directory")
        sys.exit(1)
    
    # Activate virtual environment and run the chosen script
    print("📦 Setting up environment...")
    
    # Menu
    print("\nChoose your trading mode:")
    print("1. Basic Real-Time Signals")
    print("2. Advanced Trading with Risk Management")
    print("3. Quick Demo")
    print("4. Test Notifications")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    # Prepare the command
    if choice == "1":
        command = "source venv/bin/activate && python realtime_trader.py AAPL GOOGL MSFT TSLA"
        print("🔥 Starting Basic Real-Time Trader...")
    elif choice == "2":
        command = "source venv/bin/activate && python advanced_realtime_trader.py AAPL GOOGL MSFT TSLA"
        print("🔥 Starting Advanced Real-Time Trader...")
    elif choice == "3":
        command = "source venv/bin/activate && python demo.py"
        print("🔥 Running Demo...")
    elif choice == "4":
        command = "source venv/bin/activate && python realtime_trader.py --test"
        print("🔥 Testing Notifications...")
    else:
        command = "source venv/bin/activate && python demo.py"
        print("🔥 Running Demo (default choice)...")
    
    print("\n" + "=" * 50)
    print("🚨 IMPORTANT: Press Ctrl+C to stop the trader")
    print("=" * 50)
    
    # Execute the command
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print("\n🛑 Trading session stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Session ended. Thank you for using the trading system!")

if __name__ == "__main__":
    main()