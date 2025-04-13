import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class Backtester:
    def __init__(self, initial_capital=10000, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.portfolio = None
        self.trades = []
    
    def run_backtest(self, data: pd.DataFrame, strategy_signals: pd.DataFrame) -> Dict:
        """
        Run backtest with given data and strategy signals
        
        Parameters:
        data (pd.DataFrame): Stock price data
        strategy_signals (pd.DataFrame): Strategy signals
        
        Returns:
        dict: Backtest results
        """
        portfolio = pd.DataFrame(index=data.index)
        portfolio['price'] = data['Close']
        portfolio['signal'] = strategy_signals['signal']
        portfolio['positions'] = strategy_signals['positions']
        
        # Calculate holdings
        portfolio['holdings'] = 0.0
        portfolio['cash'] = self.initial_capital
        portfolio['total'] = self.initial_capital
        
        current_cash = self.initial_capital
        current_holdings = 0.0
        
        for i, (date, row) in enumerate(portfolio.iterrows()):
            if i == 0:
                continue
                
            price = row['price']
            position_change = row['positions']
            
            # Execute trades
            if position_change == 1.0:  # Buy signal
                if current_cash > 0:
                    shares_to_buy = int(current_cash / price)
                    cost = shares_to_buy * price * (1 + self.commission)
                    if cost <= current_cash:
                        current_holdings += shares_to_buy
                        current_cash -= cost
                        self.trades.append({
                            'date': date,
                            'type': 'BUY',
                            'shares': shares_to_buy,
                            'price': price,
                            'cost': cost
                        })
                        
            elif position_change == -1.0:  # Sell signal
                if current_holdings > 0:
                    proceeds = current_holdings * price * (1 - self.commission)
                    current_cash += proceeds
                    self.trades.append({
                        'date': date,
                        'type': 'SELL',
                        'shares': current_holdings,
                        'price': price,
                        'proceeds': proceeds
                    })
                    current_holdings = 0.0
            
            portfolio.loc[date, 'holdings'] = current_holdings
            portfolio.loc[date, 'cash'] = current_cash
            portfolio.loc[date, 'total'] = current_cash + current_holdings * price
        
        self.portfolio = portfolio
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if self.portfolio is None:
            return {}
        
        total_return = (self.portfolio['total'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # Calculate daily returns
        daily_returns = self.portfolio['total'].pct_change().dropna()
        
        # Calculate key metrics
        metrics = {
            'total_return': total_return,
            'annual_return': (1 + total_return) ** (252 / len(self.portfolio)) - 1,
            'volatility': daily_returns.std() * np.sqrt(252),
            'sharpe_ratio': daily_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() > 0 else 0,
            'max_drawdown': self.calculate_max_drawdown(),
            'total_trades': len(self.trades),
            'final_portfolio_value': self.portfolio['total'].iloc[-1],
            'initial_capital': self.initial_capital
        }
        
        return metrics
    
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if self.portfolio is None:
            return 0
        
        peak = self.portfolio['total'].cummax()
        drawdown = (self.portfolio['total'] - peak) / peak
        return drawdown.min()
    
    def get_trade_summary(self) -> pd.DataFrame:
        """Get summary of all trades"""
        if not self.trades:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trades)