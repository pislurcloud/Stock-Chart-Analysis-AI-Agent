"""
Data Fetching Service for Indian NSE Stocks
Fetches live and historical OHLCV data using Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetches stock data for NSE/BSE stocks from Yahoo Finance"""
    
    TIMEFRAME_MAPPING = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "1h": "1h",
        "4h": "1h",  # Yahoo doesn't have 4h, we'll resample
        "1d": "1d",
        "1wk": "1wk",
    }
    
    PERIOD_MAPPING = {
        "1m": "7d",      # 1 min data available for last 7 days
        "5m": "60d",     # 5 min data
        "15m": "60d",    # 15 min data
        "1h": "730d",    # 1 hour data
        "4h": "730d",    # Will resample from 1h
        "1d": "5y",      # Daily data
        "1wk": "10y",    # Weekly data
    }
    
    def __init__(self):
        self.cache = {}
    
    def get_nse_symbol(self, symbol: str) -> str:
        """Convert symbol to Yahoo Finance NSE format"""
        # Remove any existing suffix
        base_symbol = symbol.upper().replace('.NS', '').replace('.BO', '')
        return f"{base_symbol}.NS"
    
    def fetch_live_data(
        self, 
        symbol: str, 
        timeframe: str = "1d",
        period: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch live stock data from Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d', '1wk')
            period: Data period (auto-selected if None)
        
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            # Convert to NSE format
            ticker_symbol = self.get_nse_symbol(symbol)
            logger.info(f"Fetching data for {ticker_symbol}, timeframe: {timeframe}")
            
            # Get ticker object
            ticker = yf.Ticker(ticker_symbol)
            
            # Map timeframe
            interval = self.TIMEFRAME_MAPPING.get(timeframe, "1d")
            if period is None:
                period = self.PERIOD_MAPPING.get(timeframe, "1y")
            
            # Fetch historical data
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.error(f"No data returned for {ticker_symbol}")
                return None
            
            # Resample for 4h if needed
            if timeframe == "4h":
                df = self._resample_to_4h(df)
            
            # Clean and prepare data
            df = self._clean_data(df)
            
            # Add metadata
            df.attrs['symbol'] = symbol
            df.attrs['timeframe'] = timeframe
            df.attrs['ticker_symbol'] = ticker_symbol
            
            logger.info(f"Successfully fetched {len(df)} candles for {ticker_symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def _resample_to_4h(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resample 1h data to 4h candles"""
        try:
            resampled = df.resample('4H').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })
            # Remove rows with NaN
            resampled = resampled.dropna()
            return resampled
        except Exception as e:
            logger.error(f"Error resampling to 4h: {str(e)}")
            return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the dataframe"""
        # Remove any NaN rows
        df = df.dropna()
        
        # Ensure we have required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return pd.DataFrame()
        
        # Round to 2 decimal places for prices
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].round(2)
        
        # Convert volume to integer
        df['Volume'] = df['Volume'].astype(int)
        
        return df
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get additional stock information"""
        try:
            ticker_symbol = self.get_nse_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'INR'),
                'exchange': info.get('exchange', 'NSE'),
            }
        except Exception as e:
            logger.error(f"Error fetching stock info: {str(e)}")
            return {'symbol': symbol, 'company_name': symbol}


# Test function
def test_data_fetcher():
    """Test the data fetcher with NSE stocks"""
    fetcher = StockDataFetcher()
    
    # Test with popular NSE stocks
    test_symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
    timeframes = ['1d', '1h', '15m']
    
    print("\n" + "="*80)
    print("TESTING NSE STOCK DATA FETCHER")
    print("="*80)
    
    for symbol in test_symbols[:1]:  # Test with first symbol
        print(f"\n📊 Testing {symbol}:")
        
        # Get stock info
        info = fetcher.get_stock_info(symbol)
        print(f"   Company: {info['company_name']}")
        print(f"   Sector: {info['sector']}")
        
        # Test different timeframes
        for tf in timeframes:
            df = fetcher.fetch_live_data(symbol, timeframe=tf)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                print(f"\n   ✅ {tf} timeframe: {len(df)} candles")
                print(f"      Latest Close: ₹{latest['Close']:.2f}")
                print(f"      Date: {df.index[-1]}")
            else:
                print(f"\n   ❌ {tf} timeframe: Failed to fetch")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_data_fetcher()