#!/usr/bin/env python3
"""
Debug script to test the analysis endpoint and see actual errors
Run this to see what's failing in the API
"""

import sys
import os

# Add src to path
sys.path.insert(0, '/workspaces/Stock-Chart-Analysis-AI-Agent/backend/src/services')
sys.path.insert(0, '/workspaces/Stock-Chart-Analysis-AI-Agent/backend')

print("="*80)
print("DEBUG: Testing Analysis Pipeline")
print("="*80)

try:
    print("\n1. Testing imports...")
    from src.services.data_fetcher import StockDataFetcher
    from src.services.technical_indicators import TechnicalIndicators
    from src.services.chart_generator import ChartGenerator
    print("✅ All imports successful")

except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Testing data fetching...")
    fetcher = StockDataFetcher()
    df = fetcher.fetch_live_data('RELIANCE', timeframe='1d')
    
    if df is None or df.empty:
        print("❌ No data returned from Yahoo Finance")
        print("   This might be a network issue or Yahoo Finance blocking")
        sys.exit(1)
    
    print(f"✅ Data fetched: {len(df)} candles")
    print(f"   Latest close: ₹{df.iloc[-1]['Close']:.2f}")

except Exception as e:
    print(f"❌ Data fetching error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Testing technical indicators...")
    calc = TechnicalIndicators(df)
    indicators = calc.calculate_all()
    print(f"✅ Indicators calculated: {len(indicators)} categories")

except Exception as e:
    print(f"❌ Indicator calculation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n4. Testing stock info...")
    stock_info = fetcher.get_stock_info('RELIANCE')
    print(f"✅ Stock info retrieved: {stock_info.get('company_name', 'RELIANCE')}")

except Exception as e:
    print(f"❌ Stock info error: {e}")
    import traceback
    traceback.print_exc()
    # Continue anyway, this is optional

try:
    print("\n5. Testing chart generation...")
    df_enriched = calc.get_enriched_dataframe()
    chart_gen = ChartGenerator()
    chart_path = chart_gen.generate_comprehensive_chart(
        df_enriched,
        indicators,
        'RELIANCE',
        '1d',
        stock_info
    )
    
    if os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path) / 1024
        print(f"✅ Chart generated: {chart_path}")
        print(f"   Size: {file_size:.2f} KB")
    else:
        print(f"❌ Chart file not found: {chart_path}")

except Exception as e:
    print(f"❌ Chart generation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n6. Testing latest values...")
    latest_data = calc.get_latest_values()
    print(f"✅ Latest values extracted")
    print(f"   Timestamp: {latest_data['timestamp']}")
    print(f"   Close: ₹{latest_data['close']:.2f}")
    print(f"   Indicators: {len(latest_data['indicators'])} categories")

except Exception as e:
    print(f"❌ Latest values error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - Analysis pipeline is working!")
print("="*80)
print("\nIf the API still fails, the issue is likely:")
print("1. Import path issues in main.py")
print("2. Chart directory permissions")
print("3. Network restrictions for Yahoo Finance")
print("\nCheck the server logs for the actual error message.")