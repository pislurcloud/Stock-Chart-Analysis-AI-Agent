"""
Technical Indicators Calculator
Calculates ALL required technical indicators for stock analysis
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculates comprehensive technical indicators"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLCV dataframe
        
        Args:
            df: DataFrame with columns [Open, High, Low, Close, Volume]
        """
        self.df = df.copy()
        self.indicators = {}
    
    def calculate_all(self) -> Dict[str, Any]:
        """Calculate all technical indicators"""
        logger.info("Calculating all technical indicators...")
        
        # Moving Averages
        self._calculate_moving_averages()
        
        # Bollinger Bands
        self._calculate_bollinger_bands()
        
        # SuperTrend
        self._calculate_supertrend()
        
        # Ichimoku Cloud
        self._calculate_ichimoku()
        
        # Volume Indicators
        self._calculate_volume_indicators()
        
        # Fibonacci Levels
        self._calculate_fibonacci()
        
        # Volatility Indicators
        self._calculate_atr()
        
        # Momentum Indicators
        self._calculate_rsi()
        self._calculate_macd()
        self._calculate_stochastic()
        
        # Trend Indicators
        self._calculate_adx()
        
        # Support & Resistance
        self._calculate_support_resistance()
        
        logger.info("All indicators calculated successfully")
        return self.indicators
    
    def _calculate_moving_averages(self):
        """Calculate Simple and Exponential Moving Averages"""
        periods = [20, 50, 100, 200]
        
        for period in periods:
            # SMA
            self.df[f'SMA_{period}'] = ta.sma(self.df['Close'], length=period)
            # EMA
            self.df[f'EMA_{period}'] = ta.ema(self.df['Close'], length=period)
        
        latest = self.df.iloc[-1]
        self.indicators['moving_averages'] = {
            'SMA_20': float(latest.get('SMA_20', 0)),
            'SMA_50': float(latest.get('SMA_50', 0)),
            'SMA_100': float(latest.get('SMA_100', 0)),
            'SMA_200': float(latest.get('SMA_200', 0)),
            'EMA_20': float(latest.get('EMA_20', 0)),
            'EMA_50': float(latest.get('EMA_50', 0)),
            'price_vs_SMA50': ((latest['Close'] / latest.get('SMA_50', latest['Close']) - 1) * 100) if latest.get('SMA_50') else 0,
            'price_vs_SMA200': ((latest['Close'] / latest.get('SMA_200', latest['Close']) - 1) * 100) if latest.get('SMA_200') else 0,
        }
    
    def _calculate_bollinger_bands(self):
        """Calculate Bollinger Bands"""
        bbands = ta.bbands(self.df['Close'], length=20, std=2)
        if bbands is not None and not bbands.empty:
            self.df = pd.concat([self.df, bbands], axis=1)
            
            latest = self.df.iloc[-1]
            
            # Get column names (they may vary in format)
            bb_cols = [col for col in self.df.columns if 'BB' in col]
            
            self.indicators['bollinger_bands'] = {
                'upper': float(latest.get([c for c in bb_cols if 'BBU' in c][0], 0)) if any('BBU' in c for c in bb_cols) else 0,
                'middle': float(latest.get([c for c in bb_cols if 'BBM' in c][0], 0)) if any('BBM' in c for c in bb_cols) else 0,
                'lower': float(latest.get([c for c in bb_cols if 'BBL' in c][0], 0)) if any('BBL' in c for c in bb_cols) else 0,
                'bandwidth': float(latest.get([c for c in bb_cols if 'BBB' in c][0], 0)) if any('BBB' in c for c in bb_cols) else 0,
                'percent_b': float(latest.get([c for c in bb_cols if 'BBP' in c][0], 0)) if any('BBP' in c for c in bb_cols) else 0,
            }
        else:
            # Fallback values
            self.indicators['bollinger_bands'] = {
                'upper': 0, 'middle': 0, 'lower': 0, 'bandwidth': 0, 'percent_b': 0
            }
    
    def _calculate_supertrend(self):
        """Calculate SuperTrend indicator"""
        supertrend = ta.supertrend(
            self.df['High'], 
            self.df['Low'], 
            self.df['Close'],
            length=10,
            multiplier=3
        )
        
        if supertrend is not None and not supertrend.empty:
            self.df = pd.concat([self.df, supertrend], axis=1)
            
            latest = self.df.iloc[-1]
            st_cols = [col for col in self.df.columns if 'SUPER' in col]
            
            st_val_col = [c for c in st_cols if 'SUPERTd' not in c and 'SUPERT' in c]
            st_dir_col = [c for c in st_cols if 'SUPERTd' in c]
            
            st_value = float(latest.get(st_val_col[0], 0)) if st_val_col else 0
            st_direction = int(latest.get(st_dir_col[0], 0)) if st_dir_col else 0
            
            self.indicators['supertrend'] = {
                'value': st_value,
                'direction': st_direction,
                'signal': 'BULLISH' if st_direction == 1 else 'BEARISH',
            }
        else:
            self.indicators['supertrend'] = {
                'value': 0, 'direction': 0, 'signal': 'NEUTRAL'
            }
    
    def _calculate_ichimoku(self):
        """Calculate Ichimoku Cloud"""
        try:
            ichimoku = ta.ichimoku(
                self.df['High'],
                self.df['Low'],
                self.df['Close']
            )
            
            if ichimoku is not None and len(ichimoku) > 0:
                self.df = pd.concat([self.df, ichimoku[0]], axis=1)
                
                latest = self.df.iloc[-1]
                ich_cols = [col for col in self.df.columns if 'I' in col and '_' in col]
                
                # Try to find columns
                its = [c for c in ich_cols if 'ITS' in c]
                iks = [c for c in ich_cols if 'IKS' in c]
                isa = [c for c in ich_cols if 'ISA' in c]
                isb = [c for c in ich_cols if 'ISB' in c]
                ics = [c for c in ich_cols if 'ICS' in c]
                
                its_val = float(latest.get(its[0], 0)) if its else 0
                iks_val = float(latest.get(iks[0], 0)) if iks else 0
                isa_val = float(latest.get(isa[0], 0)) if isa else 0
                isb_val = float(latest.get(isb[0], 0)) if isb else 0
                ics_val = float(latest.get(ics[0], 0)) if ics else 0
                
                self.indicators['ichimoku'] = {
                    'tenkan_sen': its_val,
                    'kijun_sen': iks_val,
                    'senkou_span_a': isa_val,
                    'senkou_span_b': isb_val,
                    'chikou_span': ics_val,
                    'cloud_color': 'GREEN' if isa_val > isb_val else 'RED',
                    'price_vs_cloud': 'ABOVE' if latest['Close'] > max(isa_val, isb_val) else 'BELOW',
                }
            else:
                raise ValueError("Ichimoku calculation returned None")
        except:
            self.indicators['ichimoku'] = {
                'tenkan_sen': 0, 'kijun_sen': 0, 'senkou_span_a': 0,
                'senkou_span_b': 0, 'chikou_span': 0,
                'cloud_color': 'NEUTRAL', 'price_vs_cloud': 'NEUTRAL'
            }
    
    def _calculate_volume_indicators(self):
        """Calculate Volume Profile and Volume indicators"""
        # On-Balance Volume
        obv = ta.obv(self.df['Close'], self.df['Volume'])
        if obv is not None:
            self.df['OBV'] = obv
        
        # Volume-Weighted Average Price (VWAP)
        vwap = ta.vwap(self.df['High'], self.df['Low'], self.df['Close'], self.df['Volume'])
        if vwap is not None:
            self.df['VWAP'] = vwap
        
        # Simple Volume Profile (VPOC - Volume Point of Control)
        price_ranges = pd.cut(self.df['Close'], bins=50)
        volume_profile = self.df.groupby(price_ranges)['Volume'].sum()
        vpoc_price = volume_profile.idxmax().mid if not volume_profile.empty else self.df['Close'].mean()
        
        latest = self.df.iloc[-1]
        avg_volume = self.df['Volume'].tail(20).mean()
        
        self.indicators['volume'] = {
            'current': int(latest['Volume']),
            'average_20': int(avg_volume),
            'relative_volume': float(latest['Volume'] / avg_volume) if avg_volume > 0 else 1.0,
            'obv': float(latest.get('OBV', 0)),
            'vwap': float(latest.get('VWAP', 0)),
            'vpoc': float(vpoc_price),
        }
    
    def _calculate_fibonacci(self):
        """Calculate Fibonacci Retracement and Extension levels"""
        # Get swing high and low from recent data
        recent_data = self.df.tail(100)
        swing_high = recent_data['High'].max()
        swing_low = recent_data['Low'].min()
        diff = swing_high - swing_low
        
        # Fibonacci retracement levels
        fib_levels = {
            '0.0': swing_high,
            '0.236': swing_high - (diff * 0.236),
            '0.382': swing_high - (diff * 0.382),
            '0.5': swing_high - (diff * 0.5),
            '0.618': swing_high - (diff * 0.618),
            '0.786': swing_high - (diff * 0.786),
            '1.0': swing_low,
        }
        
        # Fibonacci extension levels
        fib_extensions = {
            '1.272': swing_high + (diff * 0.272),
            '1.414': swing_high + (diff * 0.414),
            '1.618': swing_high + (diff * 0.618),
            '2.0': swing_high + diff,
        }
        
        self.indicators['fibonacci'] = {
            'swing_high': float(swing_high),
            'swing_low': float(swing_low),
            'retracements': {k: float(v) for k, v in fib_levels.items()},
            'extensions': {k: float(v) for k, v in fib_extensions.items()},
        }
    
    def _calculate_atr(self):
        """Calculate Average True Range (ATR)"""
        atr = ta.atr(self.df['High'], self.df['Low'], self.df['Close'], length=14)
        if atr is not None:
            self.df['ATR'] = atr
            
            latest = self.df.iloc[-1]
            atr_value = latest.get('ATR', 0)
            atr_percent = (atr_value / latest['Close'] * 100) if latest['Close'] > 0 else 0
            
            self.indicators['atr'] = {
                'value': float(atr_value),
                'percentage': float(atr_percent),
            }
    
    def _calculate_rsi(self):
        """Calculate Relative Strength Index"""
        rsi = ta.rsi(self.df['Close'], length=14)
        if rsi is not None:
            self.df['RSI'] = rsi
            
            latest = self.df.iloc[-1]
            rsi_value = latest.get('RSI', 50)
            
            # Determine condition
            if rsi_value > 70:
                condition = 'OVERBOUGHT'
            elif rsi_value < 30:
                condition = 'OVERSOLD'
            else:
                condition = 'NEUTRAL'
            
            self.indicators['rsi'] = {
                'value': float(rsi_value),
                'condition': condition,
            }
    
    def _calculate_macd(self):
        """Calculate MACD"""
        try:
            macd = ta.macd(self.df['Close'], fast=12, slow=26, signal=9)
            if macd is not None and not macd.empty:
                self.df = pd.concat([self.df, macd], axis=1)
                
                latest = self.df.iloc[-1]
                macd_cols = [c for c in self.df.columns if 'MACD' in c]
                
                macd_line_col = [c for c in macd_cols if 'MACDh' not in c and 'MACDs' not in c]
                signal_col = [c for c in macd_cols if 'MACDs' in c]
                hist_col = [c for c in macd_cols if 'MACDh' in c]
                
                macd_line = float(latest.get(macd_line_col[0], 0)) if macd_line_col else 0
                signal_line = float(latest.get(signal_col[0], 0)) if signal_col else 0
                histogram = float(latest.get(hist_col[0], 0)) if hist_col else 0
                
                self.indicators['macd'] = {
                    'macd_line': macd_line,
                    'signal_line': signal_line,
                    'histogram': histogram,
                    'signal': 'BULLISH' if macd_line > signal_line else 'BEARISH',
                }
            else:
                raise ValueError("MACD calculation failed")
        except:
            self.indicators['macd'] = {
                'macd_line': 0, 'signal_line': 0, 'histogram': 0, 'signal': 'NEUTRAL'
            }
    
    def _calculate_stochastic(self):
        """Calculate Stochastic Oscillator"""
        try:
            stoch = ta.stoch(self.df['High'], self.df['Low'], self.df['Close'])
            if stoch is not None and not stoch.empty:
                self.df = pd.concat([self.df, stoch], axis=1)
                
                latest = self.df.iloc[-1]
                stoch_cols = [c for c in self.df.columns if 'STOCH' in c]
                
                k_col = [c for c in stoch_cols if 'STOCHk' in c]
                d_col = [c for c in stoch_cols if 'STOCHd' in c]
                
                k_value = float(latest.get(k_col[0], 50)) if k_col else 50
                d_value = float(latest.get(d_col[0], 50)) if d_col else 50
                
                # Determine condition
                if k_value > 80:
                    condition = 'OVERBOUGHT'
                elif k_value < 20:
                    condition = 'OVERSOLD'
                else:
                    condition = 'NEUTRAL'
                
                self.indicators['stochastic'] = {
                    'k': k_value,
                    'd': d_value,
                    'condition': condition,
                }
            else:
                raise ValueError("Stochastic calculation failed")
        except:
            self.indicators['stochastic'] = {
                'k': 50, 'd': 50, 'condition': 'NEUTRAL'
            }
    
    def _calculate_adx(self):
        """Calculate Average Directional Index"""
        try:
            adx = ta.adx(self.df['High'], self.df['Low'], self.df['Close'], length=14)
            if adx is not None and not adx.empty:
                self.df = pd.concat([self.df, adx], axis=1)
                
                latest = self.df.iloc[-1]
                adx_cols = [c for c in self.df.columns if 'ADX' in c or 'DM' in c]
                
                adx_col = [c for c in adx_cols if 'ADX' in c and 'DM' not in c]
                plus_di_col = [c for c in adx_cols if 'DMP' in c]
                minus_di_col = [c for c in adx_cols if 'DMN' in c]
                
                adx_value = float(latest.get(adx_col[0], 0)) if adx_col else 0
                plus_di = float(latest.get(plus_di_col[0], 0)) if plus_di_col else 0
                minus_di = float(latest.get(minus_di_col[0], 0)) if minus_di_col else 0
                
                # Trend strength
                if adx_value > 25:
                    strength = 'STRONG'
                elif adx_value > 20:
                    strength = 'MODERATE'
                else:
                    strength = 'WEAK'
                
                self.indicators['adx'] = {
                    'value': adx_value,
                    'strength': strength,
                    'plus_di': plus_di,
                    'minus_di': minus_di,
                }
            else:
                raise ValueError("ADX calculation failed")
        except:
            self.indicators['adx'] = {
                'value': 0, 'strength': 'WEAK', 'plus_di': 0, 'minus_di': 0
            }
    
    def _calculate_support_resistance(self):
        """Calculate support and resistance levels using pivot points"""
        latest = self.df.iloc[-1]
        prev = self.df.iloc[-2] if len(self.df) > 1 else latest
        
        # Classic Pivot Points
        pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
        r1 = 2 * pivot - prev['Low']
        r2 = pivot + (prev['High'] - prev['Low'])
        r3 = r1 + (prev['High'] - prev['Low'])
        s1 = 2 * pivot - prev['High']
        s2 = pivot - (prev['High'] - prev['Low'])
        s3 = s1 - (prev['High'] - prev['Low'])
        
        self.indicators['pivot_points'] = {
            'pivot': float(pivot),
            'r1': float(r1),
            'r2': float(r2),
            'r3': float(r3),
            's1': float(s1),
            's2': float(s2),
            's3': float(s3),
        }
    
    def get_enriched_dataframe(self) -> pd.DataFrame:
        """Return dataframe with all calculated indicators"""
        return self.df
    
    def get_latest_values(self) -> Dict[str, Any]:
        """Get latest candle with all indicator values"""
        latest = self.df.iloc[-1]
        return {
            'timestamp': str(latest.name),
            'open': float(latest['Open']),
            'high': float(latest['High']),
            'low': float(latest['Low']),
            'close': float(latest['Close']),
            'volume': int(latest['Volume']),
            'indicators': self.indicators,
        }


# Test function
def test_indicators():
    """Test technical indicators calculation"""
    from data_fetcher import StockDataFetcher
    
    print("\n" + "="*80)
    print("TESTING TECHNICAL INDICATORS")
    print("="*80)
    
    fetcher = StockDataFetcher()
    df = fetcher.fetch_live_data('RELIANCE', timeframe='1d')
    
    if df is not None and not df.empty:
        calc = TechnicalIndicators(df)
        indicators = calc.calculate_all()
        
        print("\n📊 Calculated Indicators:")
        print(f"\n1. Moving Averages:")
        print(f"   SMA 50: ₹{indicators['moving_averages']['SMA_50']:.2f}")
        print(f"   SMA 200: ₹{indicators['moving_averages']['SMA_200']:.2f}")
        print(f"   Price vs SMA50: {indicators['moving_averages']['price_vs_SMA50']:.2f}%")
        
        print(f"\n2. Bollinger Bands:")
        print(f"   Upper: ₹{indicators['bollinger_bands']['upper']:.2f}")
        print(f"   Middle: ₹{indicators['bollinger_bands']['middle']:.2f}")
        print(f"   Lower: ₹{indicators['bollinger_bands']['lower']:.2f}")
        
        print(f"\n3. SuperTrend:")
        print(f"   Signal: {indicators['supertrend']['signal']}")
        print(f"   Value: ₹{indicators['supertrend']['value']:.2f}")
        
        print(f"\n4. RSI:")
        print(f"   Value: {indicators['rsi']['value']:.2f}")
        print(f"   Condition: {indicators['rsi']['condition']}")
        
        print(f"\n5. MACD:")
        print(f"   Signal: {indicators['macd']['signal']}")
        print(f"   Histogram: {indicators['macd']['histogram']:.2f}")
        
        print("\n✅ All indicators calculated successfully!")
    else:
        print("❌ Failed to fetch data")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_indicators()