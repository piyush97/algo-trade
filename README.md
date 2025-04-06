# Algorithmic Trading Setup

A complete Python-based algorithmic trading framework with **REAL-TIME TRADING SIGNALS** for live market analysis.

## 🚀 Features

- **Real-Time Data**: Live market data fetching and monitoring
- **Smart Trading Signals**: Multiple strategy analysis (SMA, RSI, MACD, Bollinger Bands)
- **Live Alerts**: Desktop notifications, sound alerts, and console alerts
- **Risk Management**: Position sizing, stop-loss, take-profit, portfolio risk controls
- **Automated Trading Logic**: Entry/exit decisions with confidence scoring
- **Historical Backtesting**: Comprehensive backtesting with performance metrics
- **Jupyter Notebooks**: Educational examples and analysis

## 📁 Project Structure

```
algo-trading/
├── data/               # Data storage
├── strategies/         # Trading strategies
├── backtesting/        # Backtesting framework
├── utils/             # Utility functions
├── notebooks/         # Jupyter notebooks
├── main.py           # Main demo script
└── requirements.txt  # Dependencies
```

## 🛠️ Installation

1. **Clone/Navigate to the project directory**
2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # On macOS/Linux
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Quick Start

### Real-Time Trading Signals (RECOMMENDED)

**Option 1: Easy Startup (Recommended)**
```bash
python run_trader.py
```

**Option 2: Manual Commands**
```bash
# First activate the virtual environment
source venv/bin/activate

# Then run your chosen trader
python realtime_trader.py                    # Basic signals
python advanced_realtime_trader.py           # With risk management
python demo.py                               # Quick demo
python realtime_trader.py --test             # Test notifications

# Custom stocks and intervals
python realtime_trader.py AAPL TSLA NVDA --interval 30
```

### Historical Backtesting
```bash
python main.py
```

### Interactive Analysis
```bash
jupyter notebook notebooks/example_analysis.ipynb
```

## 📊 Real-Time Trading Strategies

### 1. Simple Moving Average (SMA)
- **Signal**: Crossover of 20-day and 50-day moving averages
- **Use**: Trend following and momentum detection

### 2. RSI (Relative Strength Index)
- **Signal**: Oversold (<30) and overbought (>70) conditions
- **Use**: Mean reversion and momentum divergence

### 3. MACD (Moving Average Convergence Divergence)
- **Signal**: MACD line crossing signal line
- **Use**: Trend changes and momentum shifts

### 4. Bollinger Bands
- **Signal**: Price touching upper/lower bands
- **Use**: Volatility breakouts and mean reversion

### 5. Composite Signal
- **Combines all strategies** with confidence scoring
- **Smart alerts** only when multiple indicators agree

## 🔧 Real-Time Usage Examples

### Start Live Monitoring
```python
from utils.realtime_data import RealTimeDataFetcher
from strategies.realtime_signals import RealTimeSignalGenerator
from utils.notifications import NotificationSystem

# Set up components
data_fetcher = RealTimeDataFetcher(update_interval=60)
signal_generator = RealTimeSignalGenerator()
notifications = NotificationSystem()

# Add stocks to monitor
data_fetcher.add_symbol('AAPL')
data_fetcher.add_symbol('TSLA')

# Start monitoring
data_fetcher.start_monitoring()
```

### Get Trading Signals
```python
# Generate comprehensive signals
signal_data = signal_generator.generate_composite_signal('AAPL', data)

print(f"Signal: {signal_data['overall_signal']}")
print(f"Confidence: {signal_data['confidence']}%")

# Individual strategy signals
for signal in signal_data['individual_signals']:
    print(f"{signal['strategy']}: {signal['signal']} ({signal['strength']}%)")
```

### Risk Management
```python
from utils.risk_management import RiskManager

risk_manager = RiskManager(initial_capital=10000)

# Calculate position size
position_info = risk_manager.calculate_position_size('AAPL', 150.00, confidence_factor=0.8)

# Check if should enter position
should_enter, reason = risk_manager.should_enter_position('AAPL', signal_data)
```

## 📈 Real-Time Features

### Live Alerts & Notifications
- **Desktop Notifications**: Native OS notifications for trading signals
- **Sound Alerts**: Different tones for buy/sell/hold signals
- **Console Alerts**: Color-coded terminal output with detailed analysis
- **Smart Filtering**: Only alerts when confidence thresholds are met

### Risk Management
- **Position Sizing**: Automatic calculation based on portfolio percentage
- **Stop Loss**: Configurable stop-loss levels (default: 5%)
- **Take Profit**: Automatic profit-taking targets (default: 15%)
- **Daily Loss Limits**: Maximum daily loss protection
- **Portfolio Risk**: Overall portfolio risk monitoring

### Performance Tracking
- **Real-Time P&L**: Live profit/loss tracking for open positions
- **Trade Logging**: Detailed trade history with entry/exit reasons
- **Portfolio Summary**: Live portfolio value and allocation updates
- **Session Statistics**: Win rate, total trades, performance metrics

## 🎓 Learning Resources

### Notebooks
- `example_analysis.ipynb`: Complete walkthrough with multiple stocks
- Interactive visualizations and strategy comparisons

### Key Concepts Covered
1. **Data Collection**: APIs, data cleaning, storage
2. **Technical Analysis**: Moving averages, indicators
3. **Strategy Development**: Signal generation, position sizing
4. **Risk Management**: Drawdown, volatility analysis
5. **Performance Evaluation**: Metrics, benchmarking

## 🔮 Next Steps

### Expand Strategies
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Mean Reversion
- Momentum strategies

### Advanced Features
- Real-time data feeds
- Paper trading integration
- Portfolio optimization
- Machine learning models
- Alternative data sources

### Risk Management
- Stop-loss orders
- Position sizing algorithms
- Portfolio diversification
- Risk-adjusted metrics

## ⚠️ Disclaimer

This is an educational project for learning algorithmic trading concepts. **Do not use this for actual trading without proper testing and risk management.** Always consult with financial professionals before making investment decisions.

## 🤝 Contributing

Feel free to add new strategies, improve the backtesting engine, or enhance visualizations!

## 📚 Resources

- [Yahoo Finance API Documentation](https://pypi.org/project/yfinance/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Matplotlib Documentation](https://matplotlib.org/)
- [Quantitative Trading Books](https://www.quantstart.com/reading-list/)

Happy Trading! 📈