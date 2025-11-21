"""
Data Fetching Service for Indian NSE Stocks
Fetches live and historical OHLCV data using Yahoo Finance
WITH RATE LIMIT PROTECTION AND CACHING
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import time
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetches stock data for NSE/BSE stocks from Yahoo Finance with caching and rate limit protection"""
    
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
    
    # Cache durations (in seconds)
    CACHE_DURATION = {
        "1m": 60,       # 1 minute cache for 1m data
        "5m": 300,      # 5 minute cache for 5m data
        "15m": 900,     # 15 minute cache for 15m data
        "1h": 3600,     # 1 hour cache for 1h data
        "4h": 7200,     # 2 hour cache for 4h data
        "1d": 14400,    # 4 hour cache for daily data
        "1wk": 86400,   # 24 hour cache for weekly data
    }
    
    def __init__(self):
        self.cache = {}
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def _get_cache_key(self, symbol: str, timeframe: str, period: str) -> str:
        """Generate cache key"""
        return f"{symbol}_{timeframe}_{period}"
    
    def _is_cache_valid(self, cache_entry: Dict, timeframe: str) -> bool:
        """Check if cache entry is still valid"""
        if 'timestamp' not in cache_entry or 'data' not in cache_entry:
            return False
        
        cache_age = time.time() - cache_entry['timestamp']
        max_age = self.CACHE_DURATION.get(timeframe, 3600)
        
        return cache_age < max_age
    
    def _rate_limit_wait(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            logger.info(f"⏳ Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def get_nse_symbol(self, symbol: str) -> str:
        """Convert symbol to Yahoo Finance NSE format"""
        # Remove any existing suffix
        base_symbol = symbol.upper().replace('.NS', '').replace('.BO', '')
        return f"{base_symbol}.NS"
    
    def fetch_live_data(
        self, 
        symbol: str, 
        timeframe: str = "1d",
        period: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetch live stock data from Yahoo Finance with caching and rate limit protection
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS', 'EICHERMOT')
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d', '1wk')
            period: Data period (auto-selected if None)
            use_cache: Whether to use cached data
        
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            # Convert to NSE format
            ticker_symbol = self.get_nse_symbol(symbol)
            
            # Map timeframe and period
            interval = self.TIMEFRAME_MAPPING.get(timeframe, "1d")
            if period is None:
                period = self.PERIOD_MAPPING.get(timeframe, "1y")
            
            # Check cache first
            cache_key = self._get_cache_key(symbol, timeframe, period)
            if use_cache and cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if self._is_cache_valid(cache_entry, timeframe):
                    logger.info(f"✅ Using cached data for {ticker_symbol}")
                    return cache_entry['data'].copy()
            
            # Fetch from Yahoo Finance with retries
            df = None
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"📊 Fetching data for {ticker_symbol}, timeframe: {timeframe} (attempt {attempt + 1}/{self.max_retries})")
                    
                    # Rate limit protection
                    self._rate_limit_wait()
                    
                    # Get ticker object
                    ticker = yf.Ticker(ticker_symbol)
                    
                    # Fetch historical data
                    df = ticker.history(period=period, interval=interval)
                    
                    if not df.empty:
                        break  # Success!
                    
                    logger.warning(f"Empty dataframe returned for {ticker_symbol}")
                    
                except Exception as e:
                    error_msg = str(e)
                    
                    # Check if it's a rate limit error
                    if "rate limit" in error_msg.lower() or "too many requests" in error_msg.lower():
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)  # Exponential backoff
                            logger.warning(f"⚠️ Rate limited. Waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                            continue
                        else:
                            logger.error(f"❌ Rate limit exceeded after {self.max_retries} attempts")
                            raise Exception(
                                f"Yahoo Finance rate limit reached. Please try again in a few minutes. "
                                f"If this persists, the service may be experiencing high load."
                            )
                    else:
                        # Other error, re-raise
                        raise
            
            if df is None or df.empty:
                logger.error(f"No data returned for {ticker_symbol}")
                raise Exception(f"No data available for {symbol}. Please verify the symbol is correct.")
            
            # Resample for 4h if needed
            if timeframe == "4h":
                df = self._resample_to_4h(df)
            
            # Clean and prepare data
            df = self._clean_data(df)
            
            if df.empty:
                raise Exception(f"No valid data available for {symbol} after cleaning.")
            
            # Add metadata
            df.attrs['symbol'] = symbol
            df.attrs['timeframe'] = timeframe
            df.attrs['ticker_symbol'] = ticker_symbol
            
            # Cache the result
            if use_cache:
                self.cache[cache_key] = {
                    'data': df.copy(),
                    'timestamp': time.time()
                }
                logger.info(f"💾 Cached data for {ticker_symbol}")
            
            logger.info(f"✅ Successfully fetched {len(df)} candles for {ticker_symbol}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching data for {symbol}: {str(e)}")
            raise  # Re-raise to let caller handle it
    
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
        """Get additional stock information with caching"""
        try:
            # Check cache
            cache_key = f"info_{symbol}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                cache_age = time.time() - cache_entry['timestamp']
                if cache_age < 3600:  # Cache for 1 hour
                    logger.info(f"✅ Using cached info for {symbol}")
                    return cache_entry['data']
            
            # Rate limit protection
            self._rate_limit_wait()
            
            ticker_symbol = self.get_nse_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            result = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'INR'),
                'exchange': info.get('exchange', 'NSE'),
            }
            
            # Cache the result
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching stock info: {str(e)}")
            return {'symbol': symbol, 'company_name': symbol}
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
        logger.info("🧹 Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'cache_keys': list(self.cache.keys())
        }


# Test function
def test_data_fetcher():
    """Test the data fetcher with NSE stocks"""
    fetcher = StockDataFetcher()
    
    # Test with popular NSE stocks including EICHERMOT
    test_symbols = ['RELIANCE', 'TCS', 'EICHERMOT']
    timeframes = ['1d']
    
    print("\n" + "="*80)
    print("TESTING NSE STOCK DATA FETCHER WITH RATE LIMIT PROTECTION")
    print("="*80)
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        
        try:
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
                    
                    # Test cache
                    print(f"   🔄 Testing cache...")
                    df_cached = fetcher.fetch_live_data(symbol, timeframe=tf)
                    print(f"   ✅ Cache working!")
                else:
                    print(f"\n   ❌ {tf} timeframe: Failed to fetch")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Wait between stocks to avoid rate limiting
        time.sleep(2)
    
    print("\n" + "="*80)
    print(f"Cache stats: {fetcher.get_cache_stats()}")
    print("="*80)


if __name__ == "__main__":
    test_data_fetcher()