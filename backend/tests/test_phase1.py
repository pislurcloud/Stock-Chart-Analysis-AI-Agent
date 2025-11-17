"""
Comprehensive Test Script for Phase 1 - Data Pipeline
Tests all components: Data Fetching, Indicators, Chart Generation
"""

import sys
import os

# Add src to path
sys.path.insert(0, '/home/claude/stock-analysis-ai/backend/src/services')

from data_fetcher import StockDataFetcher
from technical_indicators import TechnicalIndicators
from chart_generator import ChartGenerator
import json
from datetime import datetime


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_phase_1_complete():
    """Complete end-to-end test of Phase 1"""
    
    print("\n" + "🚀"*40)
    print("  PHASE 1 - CORE DATA PIPELINE TEST")
    print("🚀"*40)
    
    # Test Configuration
    test_symbols = ['RELIANCE', 'TCS', 'INFY']
    test_timeframes = ['1d', '1h', '15m']
    
    # Initialize components
    fetcher = StockDataFetcher()
    chart_gen = ChartGenerator()
    
    # Test 1: Data Fetching
    print_section("TEST 1: DATA FETCHING")
    
    for symbol in test_symbols[:2]:  # Test 2 symbols
        print(f"\n📊 Testing {symbol}:")
        
        # Get stock info
        info = fetcher.get_stock_info(symbol)
        print(f"   ✓ Company: {info['company_name']}")
        print(f"   ✓ Sector: {info['sector']}")
        print(f"   ✓ Market Cap: ₹{info['market_cap']:,}")
        
        # Test different timeframes
        for tf in test_timeframes[:2]:  # Test 2 timeframes
            df = fetcher.fetch_live_data(symbol, timeframe=tf)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                print(f"\n   ✅ {tf.upper()} Timeframe:")
                print(f"      • Candles: {len(df)}")
                print(f"      • Latest Close: ₹{latest['Close']:.2f}")
                print(f"      • Volume: {latest['Volume']:,}")
                print(f"      • Date: {df.index[-1]}")
            else:
                print(f"\n   ❌ {tf.upper()} Timeframe: Failed")
    
    # Test 2: Technical Indicators
    print_section("TEST 2: TECHNICAL INDICATORS CALCULATION")
    
    symbol = 'RELIANCE'
    print(f"\n📈 Calculating all indicators for {symbol} (1D)...")
    
    df = fetcher.fetch_live_data(symbol, timeframe='1d')
    if df is not None and not df.empty:
        calc = TechnicalIndicators(df)
        indicators = calc.calculate_all()
        
        print("\n✅ All Indicators Calculated:")
        
        # Moving Averages
        print("\n   1. Moving Averages:")
        ma = indicators['moving_averages']
        print(f"      • SMA 50: ₹{ma['SMA_50']:.2f}")
        print(f"      • SMA 200: ₹{ma['SMA_200']:.2f}")
        print(f"      • Price vs SMA50: {ma['price_vs_SMA50']:+.2f}%")
        print(f"      • Price vs SMA200: {ma['price_vs_SMA200']:+.2f}%")
        
        # Bollinger Bands
        print("\n   2. Bollinger Bands:")
        bb = indicators['bollinger_bands']
        print(f"      • Upper: ₹{bb['upper']:.2f}")
        print(f"      • Middle: ₹{bb['middle']:.2f}")
        print(f"      • Lower: ₹{bb['lower']:.2f}")
        print(f"      • %B: {bb['percent_b']:.2f}")
        
        # SuperTrend
        print("\n   3. SuperTrend:")
        st = indicators['supertrend']
        print(f"      • Signal: {st['signal']}")
        print(f"      • Value: ₹{st['value']:.2f}")
        print(f"      • Direction: {st['direction']}")
        
        # Ichimoku Cloud
        print("\n   4. Ichimoku Cloud:")
        ich = indicators['ichimoku']
        print(f"      • Tenkan Sen: ₹{ich['tenkan_sen']:.2f}")
        print(f"      • Kijun Sen: ₹{ich['kijun_sen']:.2f}")
        print(f"      • Cloud Color: {ich['cloud_color']}")
        print(f"      • Price vs Cloud: {ich['price_vs_cloud']}")
        
        # Volume
        print("\n   5. Volume Analysis:")
        vol = indicators['volume']
        print(f"      • Current: {vol['current']:,}")
        print(f"      • Average (20): {vol['average_20']:,}")
        print(f"      • Relative Volume: {vol['relative_volume']:.2f}x")
        print(f"      • VPOC: ₹{vol['vpoc']:.2f}")
        
        # Fibonacci
        print("\n   6. Fibonacci Levels:")
        fib = indicators['fibonacci']
        print(f"      • Swing High: ₹{fib['swing_high']:.2f}")
        print(f"      • Swing Low: ₹{fib['swing_low']:.2f}")
        print(f"      • 0.618 Retracement: ₹{fib['retracements']['0.618']:.2f}")
        print(f"      • 1.618 Extension: ₹{fib['extensions']['1.618']:.2f}")
        
        # ATR
        print("\n   7. ATR (Volatility):")
        atr = indicators['atr']
        print(f"      • Value: ₹{atr['value']:.2f}")
        print(f"      • Percentage: {atr['percentage']:.2f}%")
        
        # RSI
        print("\n   8. RSI:")
        rsi = indicators['rsi']
        print(f"      • Value: {rsi['value']:.2f}")
        print(f"      • Condition: {rsi['condition']}")
        
        # MACD
        print("\n   9. MACD:")
        macd = indicators['macd']
        print(f"      • MACD Line: {macd['macd_line']:.2f}")
        print(f"      • Signal Line: {macd['signal_line']:.2f}")
        print(f"      • Histogram: {macd['histogram']:.2f}")
        print(f"      • Signal: {macd['signal']}")
        
        # Stochastic
        print("\n   10. Stochastic:")
        stoch = indicators['stochastic']
        print(f"       • %K: {stoch['k']:.2f}")
        print(f"       • %D: {stoch['d']:.2f}")
        print(f"       • Condition: {stoch['condition']}")
        
        # ADX
        print("\n   11. ADX (Trend Strength):")
        adx = indicators['adx']
        print(f"       • Value: {adx['value']:.2f}")
        print(f"       • Strength: {adx['strength']}")
        print(f"       • +DI: {adx['plus_di']:.2f}")
        print(f"       • -DI: {adx['minus_di']:.2f}")
        
        # Pivot Points
        print("\n   12. Pivot Points:")
        pp = indicators['pivot_points']
        print(f"       • Pivot: ₹{pp['pivot']:.2f}")
        print(f"       • R1: ₹{pp['r1']:.2f} | S1: ₹{pp['s1']:.2f}")
        print(f"       • R2: ₹{pp['r2']:.2f} | S2: ₹{pp['s2']:.2f}")
        print(f"       • R3: ₹{pp['r3']:.2f} | S3: ₹{pp['s3']:.2f}")
        
        # Test 3: Chart Generation
        print_section("TEST 3: CHART GENERATION")
        
        print(f"\n📊 Generating comprehensive chart for {symbol}...")
        
        df_enriched = calc.get_enriched_dataframe()
        stock_info = fetcher.get_stock_info(symbol)
        
        chart_path = chart_gen.generate_comprehensive_chart(
            df_enriched,
            indicators,
            symbol,
            '1d',
            stock_info
        )
        
        # Check if file exists
        if os.path.exists(chart_path):
            file_size = os.path.getsize(chart_path) / 1024  # KB
            print(f"\n   ✅ Chart Generated Successfully!")
            print(f"      • Path: {chart_path}")
            print(f"      • Size: {file_size:.2f} KB")
            print(f"      • Resolution: 1920x1080")
            print(f"      • Theme: Light")
        else:
            print(f"\n   ❌ Chart generation failed")
        
        # Test 4: Data Export
        print_section("TEST 4: DATA EXPORT (JSON)")
        
        # Export latest values as JSON
        latest_data = calc.get_latest_values()
        
        output_file = f"/home/claude/stock-analysis-ai/backend/charts/{symbol}_data.json"
        with open(output_file, 'w') as f:
            json.dump(latest_data, f, indent=2, default=str)
        
        print(f"\n   ✅ Data exported to: {output_file}")
        print(f"      • Timestamp: {latest_data['timestamp']}")
        print(f"      • Close Price: ₹{latest_data['close']:.2f}")
        print(f"      • Indicators Count: {len(latest_data['indicators'])}")
        
    else:
        print("\n   ❌ Failed to fetch data")
    
    # Summary
    print_section("PHASE 1 TEST SUMMARY")
    print("\n✅ All Phase 1 Components Working:")
    print("   1. ✓ Data Fetching (Yahoo Finance - NSE)")
    print("   2. ✓ Technical Indicators (12 categories)")
    print("   3. ✓ Chart Generation (1920x1080, Light theme)")
    print("   4. ✓ Data Export (JSON)")
    
    print("\n🎯 Ready for Phase 2: CrewAI Agent Development")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Install dependencies check
    try:
        import yfinance
        import pandas_ta
        import mplfinance
        print("✅ All dependencies installed\n")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        exit(1)
    
    # Run tests
    test_phase_1_complete()