"""
Main script demonstrating algorithmic trading setup
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_fetcher import DataFetcher
from strategies.simple_moving_average import SimpleMovingAverageStrategy
from backtesting.backtester import Backtester
import matplotlib.pyplot as plt
import pandas as pd

def main():
    print("🚀 Algorithmic Trading Setup Demo")
    print("=" * 50)
    
    # Initialize components
    data_fetcher = DataFetcher()
    strategy = SimpleMovingAverageStrategy(short_window=20, long_window=50)
    backtester = Backtester(initial_capital=10000)
    
    # Example: Fetch Apple stock data
    symbol = "AAPL"
    print(f"📊 Fetching data for {symbol}...")
    data = data_fetcher.fetch_data(symbol, period="1y", interval="1d")
    
    if data is not None:
        print(f"✅ Data fetched successfully! Shape: {data.shape}")
        print(f"📈 Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
        
        # Generate trading signals
        print("\n🔍 Generating trading signals...")
        signals = strategy.generate_signals(data)
        
        # Get trade points
        trades = strategy.get_trades()
        print(f"📝 Generated {len(trades['buy'])} buy signals and {len(trades['sell'])} sell signals")
        
        # Run backtest
        print("\n🧪 Running backtest...")
        metrics = backtester.run_backtest(data, signals)
        
        # Print results
        print("\n📊 Backtest Results:")
        print(f"Initial Capital: ${metrics['initial_capital']:,.2f}")
        print(f"Final Portfolio Value: ${metrics['final_portfolio_value']:,.2f}")
        print(f"Total Return: {metrics['total_return']:.2%}")
        print(f"Annual Return: {metrics['annual_return']:.2%}")
        print(f"Volatility: {metrics['volatility']:.2%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
        print(f"Total Trades: {metrics['total_trades']}")
        
        # Create visualization
        print("\n📈 Creating visualization...")
        plt.figure(figsize=(12, 8))
        
        # Plot price and moving averages
        plt.subplot(2, 1, 1)
        plt.plot(data.index, data['Close'], label='Close Price', alpha=0.7)
        plt.plot(signals.index, signals['short_mavg'], label=f'SMA {strategy.short_window}', alpha=0.8)
        plt.plot(signals.index, signals['long_mavg'], label=f'SMA {strategy.long_window}', alpha=0.8)
        
        # Mark buy/sell points
        buy_points = signals[signals['positions'] == 1.0]
        sell_points = signals[signals['positions'] == -1.0]
        
        plt.scatter(buy_points.index, buy_points['price'], color='green', marker='^', s=100, label='Buy Signal')
        plt.scatter(sell_points.index, sell_points['price'], color='red', marker='v', s=100, label='Sell Signal')
        
        plt.title(f'{symbol} - Moving Average Strategy')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot portfolio value
        plt.subplot(2, 1, 2)
        plt.plot(backtester.portfolio.index, backtester.portfolio['total'], label='Portfolio Value', color='purple')
        plt.title('Portfolio Value Over Time')
        plt.ylabel('Portfolio Value ($)')
        plt.xlabel('Date')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Save trade summary
        trade_summary = backtester.get_trade_summary()
        if not trade_summary.empty:
            print(f"\n💾 Trade summary saved to data/trade_summary.csv")
            os.makedirs('data', exist_ok=True)
            trade_summary.to_csv('data/trade_summary.csv', index=False)
        
        print("\n🎉 Setup complete! You can now:")
        print("1. Modify strategies in the 'strategies' folder")
        print("2. Test with different stocks and parameters")
        print("3. Add more technical indicators")
        print("4. Explore Jupyter notebooks for analysis")
        
    else:
        print("❌ Failed to fetch data. Please check your internet connection.")

if __name__ == "__main__":
    main()