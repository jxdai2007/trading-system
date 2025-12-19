# Algorithmic Trading System

A Python-based backtesting framework for quantitative trading strategies with comprehensive performance analysis.

## Features

- **Multi-Strategy Framework**: Modular architecture supporting multiple trading strategies
- **Three Implemented Strategies**:
  - Momentum-based trading (16.88% return, 2.79 Sharpe ratio)
  - Moving Average Crossover (15.39% return, 1.91 Sharpe ratio)  
  - RSI (Relative Strength Index)
- **Comprehensive Metrics**: Sharpe ratio, maximum drawdown, win rate, average trade return
- **Fair Backtesting**: Aligned warmup periods for accurate strategy comparison
- **Data Pipeline**: Automated fetching and storage of historical market data

## Performance Summary

Tested on AAPL (June-December 2025, 124 trading days):

| Strategy | Return | Sharpe Ratio | Max Drawdown | Win Rate | Trades |
|----------|--------|--------------|--------------|----------|--------|
| Momentum | 16.88% | 2.79 | -2.42% | 53.33% | 31 |
| MA Crossover | 15.39% | 1.91 | -5.29% | 0.00% | 2 |
| RSI | 0.00% | 0.00 | 0.00% | 0.00% | 0 |

## Tech Stack

- **Python 3.x**
- **pandas**: Time-series data manipulation
- **NumPy**: Numerical computations
- **yfinance**: Market data API

## Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/algorithmic-trading-system.git
cd algorithmic-trading-system

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Fetch Market Data
```bash
python src/data_pipeline/data_fetcher.py
```

### Run Backtest
```bash
python src/backtesting/simple_backtester.py
```

## Project Structure
```
trading-system/
├── data/
│   ├── raw/              # Historical OHLCV data
│   └── processed/        # Cleaned data (future)
├── src/
│   ├── data_pipeline/
│   │   └── data_fetcher.py    # Market data ingestion
│   └── backtesting/
│       ├── simple_backtester.py    # Backtesting engine
│       └── strategies.py           # Trading strategies
├── config/               # Configuration files
├── notebooks/            # Analysis notebooks
└── requirements.txt      # Python dependencies
```

## Strategies Explained

### Momentum Strategy
Buys when price increased yesterday, sells when price decreased. Captures short-term trends with rapid trade execution.

### Moving Average Crossover
Buys when 20-day MA crosses above 50-day MA (golden cross), sells on opposite signal. Classic trend-following approach.

### RSI Strategy  
Buys when RSI < 35 (oversold), sells when RSI > 65 (overbought). Mean-reversion strategy for range-bound markets.

## Key Metrics

- **Sharpe Ratio**: Risk-adjusted return (>1 is good, >2 is excellent)
- **Maximum Drawdown**: Worst peak-to-trough portfolio decline
- **Win Rate**: Percentage of profitable closed trades
- **Average Trade Return**: Mean return per trade

## Roadmap

- [ ] Additional technical indicators (MACD, Bollinger Bands)
- [ ] Machine learning models (LSTM, XGBoost)
- [ ] Multi-asset portfolio backtesting
- [ ] Transaction cost modeling
- [ ] Paper trading integration with broker API

## Author

Built by Jollen Dai. Hobby project :D

## License

MIT License
```