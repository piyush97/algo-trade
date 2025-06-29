#!/bin/bash

# Real-Time Algorithmic Trading Startup Script

echo "🚀 Starting Real-Time Algorithmic Trading System"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
python -c "import yfinance, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Required packages not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "✅ Environment ready!"
echo ""
echo "Choose your trading mode:"
echo "1. Basic Real-Time Signals (realtime_trader.py)"
echo "2. Advanced Trading with Risk Management (advanced_realtime_trader.py)"
echo "3. Quick Demo (demo.py)"
echo "4. Test Notifications"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🔥 Starting Basic Real-Time Trader..."
        python realtime_trader.py AAPL GOOGL MSFT TSLA
        ;;
    2)
        echo "🔥 Starting Advanced Real-Time Trader..."
        python advanced_realtime_trader.py AAPL GOOGL MSFT TSLA
        ;;
    3)
        echo "🔥 Running Demo..."
        python demo.py
        ;;
    4)
        echo "🔥 Testing Notifications..."
        python realtime_trader.py --test
        ;;
    *)
        echo "❌ Invalid choice. Starting basic trader..."
        python realtime_trader.py AAPL GOOGL MSFT TSLA
        ;;
esac