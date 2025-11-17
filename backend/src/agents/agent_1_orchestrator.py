"""
Agent 1: Data Orchestrator
Coordinates data flow and prepares analysis package
No LLM required - pure Python
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add parent directory to path
#backend_dir = Path(__file__).parent.parent.parent
#sys.path.insert(0, str(backend_dir))
sys.path.append('/workspaces/Stock-Chart-Analysis-AI-Agent/backend')

from src.services.data_fetcher import StockDataFetcher
from src.services.technical_indicators import TechnicalIndicators
from src.services.chart_generator import ChartGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataOrchestrator:
    """
    Agent 1: Data Orchestrator
    Validates inputs, fetches data, generates charts, prepares data package
    """
    
    def __init__(self):
        self.fetcher = StockDataFetcher()
        self.chart_gen = ChartGenerator()
    
    def orchestrate(self, symbol: str, timeframe: str = '1d') -> Dict[str, Any]:
        """
        Main orchestration method
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            timeframe: Timeframe (e.g., '1d', '1h', '15m')
        
        Returns:
            Complete data package for downstream agents
        """
        logger.info(f"Orchestrating analysis for {symbol} {timeframe}")
        
        try:
            # Step 1: Validate inputs
            symbol = self._validate_symbol(symbol)
            timeframe = self._validate_timeframe(timeframe)
            
            # Step 2: Fetch stock data
            df = self.fetcher.fetch_live_data(symbol, timeframe=timeframe)
            if df is None or df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Step 3: Get stock info
            stock_info = self.fetcher.get_stock_info(symbol)
            
            # Step 4: Calculate technical indicators
            calc = TechnicalIndicators(df)
            indicators = calc.calculate_all()
            df_enriched = calc.get_enriched_dataframe()
            
            # Step 5: Generate chart image
            chart_path = self.chart_gen.generate_comprehensive_chart(
                df_enriched,
                indicators,
                symbol,
                timeframe,
                stock_info
            )
            
            # Step 6: Get latest values
            latest_data = calc.get_latest_values()
            
            # Step 7: Prepare complete data package
            data_package = {
                'metadata': {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'company_name': stock_info.get('company_name', symbol),
                    'sector': stock_info.get('sector', 'N/A'),
                    'exchange': stock_info.get('exchange', 'NSE'),
                },
                'stock_info': stock_info,
                'latest_candle': {
                    'timestamp': latest_data['timestamp'],
                    'open': latest_data['open'],
                    'high': latest_data['high'],
                    'low': latest_data['low'],
                    'close': latest_data['close'],
                    'volume': latest_data['volume'],
                },
                'indicators': indicators,
                'chart_path': chart_path,
                'data_quality': self._assess_data_quality(df, indicators),
                'status': 'success'
            }
            
            logger.info(f"Orchestration complete for {symbol}")
            return data_package
            
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'symbol': symbol,
                'timeframe': timeframe
            }
    
    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize stock symbol"""
        symbol = symbol.upper().strip()
        
        # Remove .NS suffix if present (we'll add it in fetcher)
        symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        if not symbol or len(symbol) < 2:
            raise ValueError("Invalid symbol")
        
        return symbol
    
    def _validate_timeframe(self, timeframe: str) -> str:
        """Validate timeframe"""
        valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1wk']
        
        timeframe = timeframe.lower().strip()
        
        if timeframe not in valid_timeframes:
            raise ValueError(f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}")
        
        return timeframe
    
    def _assess_data_quality(self, df, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess quality and completeness of data
        
        Returns:
            Dict with quality metrics
        """
        return {
            'candles_count': len(df),
            'indicators_count': len(indicators),
            'has_sufficient_data': len(df) >= 200,  # Need 200+ for MA200
            'data_recency': str(df.index[-1]) if not df.empty else None,
            'quality_score': self._calculate_quality_score(df, indicators)
        }
    
    def _calculate_quality_score(self, df, indicators: Dict[str, Any]) -> float:
        """
        Calculate overall data quality score (0-100)
        """
        score = 0.0
        
        # Sufficient candles (40 points)
        if len(df) >= 200:
            score += 40
        elif len(df) >= 100:
            score += 30
        elif len(df) >= 50:
            score += 20
        
        # All indicators present (30 points)
        expected_indicators = [
            'moving_averages', 'bollinger_bands', 'supertrend',
            'ichimoku', 'rsi', 'macd', 'stochastic', 'adx',
            'volume', 'fibonacci', 'atr', 'pivot_points'
        ]
        present = sum(1 for ind in expected_indicators if ind in indicators)
        score += (present / len(expected_indicators)) * 30
        
        # No missing values (20 points)
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        score += (1 - missing_ratio) * 20
        
        # Recent data (10 points)
        from datetime import datetime, timedelta
        if not df.empty:
            latest_date = df.index[-1]
            days_old = (datetime.now(latest_date.tz) - latest_date).days
            if days_old <= 1:
                score += 10
            elif days_old <= 7:
                score += 5
        
        return round(score, 2)


# Test function
if __name__ == "__main__":
    print("="*80)
    print("Testing Agent 1: Data Orchestrator")
    print("="*80)
    
    orchestrator = DataOrchestrator()
    
    # Test with RELIANCE
    result = orchestrator.orchestrate('RELIANCE', '1d')
    
    if result['status'] == 'success':
        print("\n✅ Orchestration Successful!")
        print(f"\nSymbol: {result['metadata']['symbol']}")
        print(f"Company: {result['metadata']['company_name']}")
        print(f"Sector: {result['metadata']['sector']}")
        print(f"\nLatest Close: ₹{result['latest_candle']['close']:.2f}")
        print(f"Volume: {result['latest_candle']['volume']:,}")
        print(f"\nIndicators: {result['data_quality']['indicators_count']} categories")
        print(f"Data Quality: {result['data_quality']['quality_score']}/100")
        print(f"Chart: {result['chart_path']}")
    else:
        print(f"\n❌ Orchestration Failed: {result['error']}")
    
    print("\n" + "="*80)