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
    
    def calculate_performance(self, final_price):
        """Calculate final performance metrics"""
        # Final portfolio value
        final_value = self.cash + (self.shares * final_price)
        
        # Total return
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        # Profit/Loss
        profit_loss = final_value - self.initial_capital
        
        print("\n=== Backtest Results ===")
        print(f"Initial Capital: ${self.initial_capital:.2f}")
        print(f"Final Value: ${final_value:.2f}")
        print(f"Profit/Loss: ${profit_loss:.2f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Number of Trades: {len(self.trades)}")
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'profit_loss': profit_loss,
            'total_return': total_return,
            'num_trades': len(self.trades)
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

            # DEBUG: Show what signals were generated
            print(f"\nDEBUG: Signal counts for {strategy_name}:")
            print(f"  Buy signals (1): {(data_with_signals['Signal'] == 1).sum()}")
            print(f"  Sell signals (-1): {(data_with_signals['Signal'] == -1).sum()}")
            print(f"  Hold signals (0): {(data_with_signals['Signal'] == 0).sum()}")
            if strategy_name == 'Moving Average Crossover':
                print(f"  Short MA values (non-null): {data_with_signals['Short_MA'].notna().sum()}")
                print(f"  Long MA values (non-null): {data_with_signals['Long_MA'].notna().sum()}")
            if strategy_name == 'RSI':
                print(f"  RSI values (non-null): {data_with_signals['RSI'].notna().sum()}")
                print(f"  RSI min: {data_with_signals['RSI'].min():.2f}")
                print(f"  RSI max: {data_with_signals['RSI'].max():.2f}")
            print()
            # Run backtest
            backtester.execute_backtest(data_with_signals)
            
            # Calculate performance
            final_price = data_with_signals.iloc[-1]['Close']
            result = backtester.calculate_performance(final_price)
            
            results[strategy_name] = result
        
        # Summary comparison
        print("\n" + "=" * 70)
        print("STRATEGY COMPARISON")
        print("=" * 70)
        print(f"{'Strategy':<30} {'Return':<15} {'Final Value':<15} {'Trades':<10}")
        print("-" * 70)
        
        for strategy_name, result in results.items():
            print(f"{strategy_name:<30} {result['total_return']:>6.2f}% {result['final_value']:>12.2f} {result['num_trades']:>8}")