import pandas as pd

class MovingAverageCrossover:
    """
    Moving Average Crossover Strategy
    
    Buy when short-term MA is above long-term MA
    Sell when short-term MA is below long-term MA
    """
    
    def __init__(self, short_window=20, long_window=50):
        """
        Args:
            short_window: Period for short moving average (default 20 days)
            long_window: Period for long moving average (default 50 days)
        """
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data):
        """
        Generate buy/sell signals based on MA crossover
        
        Args:
            data: DataFrame with 'Close' column
            
        Returns:
            DataFrame with added columns: Short_MA, Long_MA, Signal
        """
        df = data.copy()
        
        # Calculate moving averages
        df['Short_MA'] = df['Close'].rolling(window=self.short_window).mean()
        df['Long_MA'] = df['Close'].rolling(window=self.long_window).mean()
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Generate signals based on MA relationship
        # Buy when short MA is above long MA (uptrend)
        df.loc[df['Short_MA'] > df['Long_MA'], 'Signal'] = 1
        
        # Sell when short MA is below long MA (downtrend)
        df.loc[df['Short_MA'] < df['Long_MA'], 'Signal'] = -1
        
        return df

class RSIStrategy:
    """
    Relative Strength Index (RSI) Strategy
    
    Buy when RSI < oversold threshold
    Sell when RSI > overbought threshold
    """
    
    def __init__(self, period=14, oversold=35, overbought=65):
        """
        Args:
            period: RSI calculation period (default 14 days)
            oversold: RSI level considered oversold (default 40 - less strict)
            overbought: RSI level considered overbought (default 60 - less strict)
        """
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data):
        """
        Generate buy/sell signals based on RSI
        
        Args:
            data: DataFrame with 'Close' column
            
        Returns:
            DataFrame with added columns: RSI, Signal
        """
        df = data.copy()
        
        # Calculate price changes
        delta = df['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        # Calculate RS (Relative Strength)
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['RSI'] < self.oversold, 'Signal'] = 1   # Oversold - buy
        df.loc[df['RSI'] > self.overbought, 'Signal'] = -1 # Overbought - sell
        
        return df

class MomentumStrategy:
    """
    Simple Momentum Strategy (your original strategy)
    
    Buy when price went up yesterday
    Sell when price went down yesterday
    """
    
    def generate_signals(self, data):
        """
        Generate buy/sell signals based on daily returns
        
        Args:
            data: DataFrame with 'Close' column
            
        Returns:
            DataFrame with added columns: Return, Signal
        """
        df = data.copy()
        
        # Calculate daily returns
        df['Return'] = df['Close'].pct_change()
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['Return'] > 0, 'Signal'] = 1   # Buy signal
        df.loc[df['Return'] < 0, 'Signal'] = -1  # Sell signal
        
        return df