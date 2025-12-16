import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

class DataFetcher:
    """Fetches market data from Yahoo Finance"""
    
    def __init__(self, data_dir='data/raw'):
        self.data_dir = data_dir
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
    
    def fetch_stock_data(ticker, start_date, end_date):
        """
        Fetch historical stock data for a single ticker
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL', 'MSFT')
            start_date: Start date as string 'YYYY-MM-DD'
            end_date: End date as string 'YYYY-MM-DD'
            
        Returns:
            pandas DataFrame with OHLCV data
        """
        print(f"Fetching data for {ticker}...")
        
        # Download data using yfinance
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            print(f"Warning: No data found for {ticker}")
            return None
        
        # Flatten multi-level columns if they exist
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Add ticker column
        data['Ticker'] = ticker
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        print(f"✓ Downloaded {len(data)} days of data for {ticker}")
        return data
        
        
    def fetch_multiple_stocks(self, tickers, start_date, end_date):
        """
        Fetch data for multiple stocks
        
        Args:
            tickers: List of stock symbols
            start_date: Start date as string 'YYYY-MM-DD'
            end_date: End date as string 'YYYY-MM-DD'
            
        Returns:
            Dictionary of {ticker: DataFrame}
        """
        all_data = {}
        
        for ticker in tickers:
            data = self.fetch_stock_data(ticker, start_date, end_date)
            if data is not None:
                all_data[ticker] = data
        
        return all_data
    
    def save_to_csv(self, data, ticker):
        """Save data to CSV file"""
        filename = f"{self.data_dir}/{ticker}_{datetime.now().strftime('%Y%m%d')}.csv"
        data.to_csv(filename, index=False)
        print(f"✓ Saved to {filename}")
        return filename


# Test function - run this to see it work
if __name__ == "__main__":
    # Create fetcher
    fetcher = DataFetcher()
    
    # Fetch last 30 days of Apple stock data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"\n=== Fetching AAPL data from {start_date} to {end_date} ===\n")
    
    data = fetcher.fetch_stock_data('AAPL', start_date, end_date)
    
    if data is not None:
        print(f"\n=== Preview of data ===\n")
        print(data.head())
        print(f"\nColumns: {list(data.columns)}")
        
        # Save it
        fetcher.save_to_csv(data, 'AAPL')
        
        print("\n✓ SUCCESS! Check your data/raw folder for the CSV file")