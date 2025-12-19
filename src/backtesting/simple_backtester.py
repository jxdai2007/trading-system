import pandas as pd
import os

class SimpleBacktester:
    """A simple backtesting engine for testing trading strategies"""
    
    def __init__(self, initial_capital=10000):
        """
        Initialize backtester
        
        Args:
            iniztial_capital: Starting cash amount (default $10,000)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.shares = 0
        self.trades = []
    
    def load_data(self, csv_path):
        """Load stock data from CSV file"""
        print(f"Loading data from {csv_path}...")
        
        # Read CSV, skipping the second header row
        data = pd.read_csv(csv_path, skiprows=[1])
        
        # Convert price columns to numeric
        price_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in price_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        print(f"✓ Loaded {len(data)} days of data")

        return data
    
    def apply_strategy(self, data, strategy):
        """
        Apply a trading strategy to generate signals
        
        Args:
            data: DataFrame with OHLCV data
            strategy: Strategy object with generate_signals() method
            
        Returns:
            DataFrame with signals
        """
        return strategy.generate_signals(data)
        
    
    def execute_backtest(self, data_with_signals, warmup_period=50):
        """
        Execute trades based on signals
        
        Args:
            data_with_signals: DataFrame with 'Signal' column
            warmup_period: Number of days to skip at start (for indicator calculation)
        """
        print("\n=== Running Backtest ===\n")
        
        # Skip warmup period to ensure fair comparison
        for i, row in data_with_signals.iloc[warmup_period:].iterrows():
            date = row['Date']
            price = row['Close']
            signal = row['Signal']
            
            # BUY signal and we have cash
            if signal == 1 and self.cash > 0:
                shares_to_buy = int(self.cash / price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    self.cash -= cost
                    self.shares += shares_to_buy
                    
                    self.trades.append({
                        'Date': date,
                        'Action': 'BUY',
                        'Price': price,
                        'Shares': shares_to_buy,
                        'Cash': self.cash,
                        'Portfolio Value': self.cash + (self.shares * price)
                    })
                    print(f"{date}: BUY {shares_to_buy} shares at ${price:.2f} | Cash: ${self.cash:.2f}")
            
            # SELL signal and we have shares
            elif signal == -1 and self.shares > 0:
                revenue = self.shares * price
                self.cash += revenue
                
                self.trades.append({
                    'Date': date,
                    'Action': 'SELL',
                    'Price': price,
                    'Shares': self.shares,
                    'Cash': self.cash,
                    'Portfolio Value': self.cash
                })
                print(f"{date}: SELL {self.shares} shares at ${price:.2f} | Cash: ${self.cash:.2f}")
                
                self.shares = 0
    
    def calculate_performance(self, final_price, data_with_signals):
        """Calculate comprehensive performance metrics"""
        import numpy as np
        
        # Final portfolio value
        final_value = self.cash + (self.shares * final_price)
        
        # Total return
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        # Profit/Loss
        profit_loss = final_value - self.initial_capital
        
        # Calculate daily returns for Sharpe ratio and drawdown
        if len(self.trades) > 0:
            # Build portfolio value series
            portfolio_values = []
            cash = self.initial_capital
            shares = 0
            
            # Create a dictionary of trades by date for efficient lookup
            trades_by_date = {}
            for trade in self.trades:
                date = trade['Date']
                if date not in trades_by_date:
                    trades_by_date[date] = []
                trades_by_date[date].append(trade)
            
            for _, row in data_with_signals.iterrows():
                price = row['Close']
                date = row['Date']
                
                # Check if we made a trade this day
                if date in trades_by_date:
                    # Process all trades on this day in order
                    for trade in trades_by_date[date]:
                        if trade['Action'] == 'BUY':
                            # trade['Shares'] is shares bought in this trade, so add to cumulative
                            shares += trade['Shares']
                            cash = trade['Cash']
                        elif trade['Action'] == 'SELL':
                            # After sell, shares go to 0
                            shares = 0
                            cash = trade['Cash']
                
                # Portfolio value = cash + (shares held * current price)
                portfolio_value = cash + (shares * price)
                portfolio_values.append(portfolio_value)
            
            # Calculate daily returns
            portfolio_series = pd.Series(portfolio_values)
            daily_returns = portfolio_series.pct_change().dropna()
            
            # Sharpe Ratio (annualized, assuming 252 trading days)
            if len(daily_returns) > 0 and daily_returns.std() > 0:
                sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
            else:
                sharpe_ratio = 0
            
            # Maximum Drawdown (calculated from portfolio values, not returns)
            portfolio_series = pd.Series(portfolio_values)
            running_max = portfolio_series.expanding().max()
            drawdown = (portfolio_series - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            
            # Win Rate and Average Trade Return
            winning_trades = 0
            losing_trades = 0
            trade_returns = []
            
            # Pair up buy/sell trades properly
            # Track open positions: each BUY adds shares at a price, each SELL closes all shares
            # We'll use weighted average cost basis for simplicity
            total_shares = 0
            total_cost = 0.0  # Total cost basis for all shares held
            
            for trade in self.trades:
                if trade['Action'] == 'BUY':
                    # Add shares to our position
                    shares_bought = trade['Shares']
                    buy_price = trade['Price']
                    total_cost += shares_bought * buy_price
                    total_shares += shares_bought
                elif trade['Action'] == 'SELL':
                    # Close all positions - calculate return based on average cost basis
                    if total_shares > 0:
                        avg_buy_price = total_cost / total_shares
                        sell_price = trade['Price']
                        trade_return = ((sell_price - avg_buy_price) / avg_buy_price) * 100
                        trade_returns.append(trade_return)
                        
                        if trade_return > 0:
                            winning_trades += 1
                        else:
                            losing_trades += 1
                        
                        # Reset position tracking after selling all shares
                        total_shares = 0
                        total_cost = 0.0
            
            # Note: If total_shares > 0 at end, we have an open position (not counted in win rate)
            
            total_closed_trades = winning_trades + losing_trades
            win_rate = (winning_trades / total_closed_trades * 100) if total_closed_trades > 0 else 0
            avg_trade_return = np.mean(trade_returns) if trade_returns else 0
            
        else:
            sharpe_ratio = 0
            max_drawdown = 0
            win_rate = 0
            avg_trade_return = 0
        
        print("\n=== Backtest Results ===")
        print(f"Initial Capital: ${self.initial_capital:.2f}")
        print(f"Final Value: ${final_value:.2f}")
        print(f"Profit/Loss: ${profit_loss:.2f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Number of Trades: {len(self.trades)}")
        print(f"\n=== Risk Metrics ===")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Maximum Drawdown: {max_drawdown:.2f}%")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Avg Trade Return: {avg_trade_return:.2f}%")
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'profit_loss': profit_loss,
            'total_return': total_return,
            'num_trades': len(self.trades),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_trade_return': avg_trade_return
        }



# Test the backtester with multiple strategies
if __name__ == "__main__":
    import os
    from strategies import MovingAverageCrossover, RSIStrategy, MomentumStrategy
    
    # Find the most recent CSV file in data/raw
    data_dir = 'data/raw'
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("Error: No CSV files found in data/raw/")
        print("Run data_fetcher.py first to download data!")
    else:
        # Use the most recent file
        latest_file = max(csv_files)
        csv_path = os.path.join(data_dir, latest_file)
        
        print(f"Using data file: {latest_file}\n")
        print("=" * 70)
        
        # Test all three strategies
        strategies = {
            'Momentum': MomentumStrategy(),
            'Moving Average Crossover': MovingAverageCrossover(short_window=20, long_window=50),
            'RSI': RSIStrategy(period=14, oversold=30, overbought=70)
        }
        
        results = {}
        
        for strategy_name, strategy in strategies.items():
            print(f"\n{'=' * 70}")
            print(f"TESTING STRATEGY: {strategy_name}")
            print('=' * 70)
            
            # Create fresh backtester for each strategy
            backtester = SimpleBacktester(initial_capital=10000)
            
            # Load data
            data = backtester.load_data(csv_path)
            
            # Generate trading signals using the strategy
            # Generate trading signals using the strategy
            data_with_signals = backtester.apply_strategy(data, strategy)

            # Run backtest
            backtester.execute_backtest(data_with_signals)
            
            # Calculate performance
            final_price = data_with_signals.iloc[-1]['Close']
            result = backtester.calculate_performance(final_price, data_with_signals)
            
            results[strategy_name] = result
        
        # Summary comparison
        print("\n" + "=" * 100)
        print("STRATEGY COMPARISON")
        print("=" * 100)
        print(f"{'Strategy':<30} {'Return':<12} {'Sharpe':<10} {'Max DD':<12} {'Win Rate':<12} {'Trades':<10}")
        print("-" * 100)
        
        for strategy_name, result in results.items():
            print(f"{strategy_name:<30} "
                  f"{result['total_return']:>8.2f}% "
                  f"{result['sharpe_ratio']:>8.2f} "
                  f"{result['max_drawdown']:>9.2f}% "
                  f"{result['win_rate']:>9.2f}% "
                  f"{result['num_trades']:>8}")
        
        print("\n" + "=" * 100)
        print("METRICS EXPLAINED:")
        print("  Return: Total percentage gain/loss")
        print("  Sharpe: Risk-adjusted return (higher is better, >1 is good, >2 is excellent)")
        print("  Max DD: Worst peak-to-trough decline (lower is better)")
        print("  Win Rate: Percentage of profitable trades")
        print("=" * 100)