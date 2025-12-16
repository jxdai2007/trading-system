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
    
    def simple_momentum_strategy(self, data):
        """
        Simple strategy: Buy if price went up yesterday, sell if it went down
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals (1 = buy, -1 = sell, 0 = hold)
        """
        df = data.copy()
        
        # Calculate daily returns (today's close / yesterday's close - 1)
        df['Return'] = df['Close'].pct_change()
        
        # Generate signals: 1 if yesterday was positive, -1 if negative
        df['Signal'] = 0
        df.loc[df['Return'] > 0, 'Signal'] = 1  # Buy signal
        df.loc[df['Return'] < 0, 'Signal'] = -1  # Sell signal
        
        return df
    
    def execute_backtest(self, data_with_signals):
        """
        Execute trades based on signals
        
        Args:
            data_with_signals: DataFrame with 'Signal' column
        """
        print("\n=== Running Backtest ===\n")
        
        for i, row in data_with_signals.iterrows():
            date = row['Date']
            price = row['Close']
            signal = row['Signal']
            
            # BUY signal and we have cash
            if signal == 1 and self.cash > 0:
                shares_to_buy = int(self.cash / price)  # Buy as many shares as possible
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


# Test the backtester
if __name__ == "__main__":
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
        
        # Create backtester with $10,000
        backtester = SimpleBacktester(initial_capital=10000)
        
        # Load data
        data = backtester.load_data(csv_path)
        
        # Generate trading signals
        data_with_signals = backtester.simple_momentum_strategy(data)
        
        # Run backtest
        backtester.execute_backtest(data_with_signals)
        
        # Calculate performance
        final_price = data_with_signals.iloc[-1]['Close']
        results = backtester.calculate_performance(final_price)