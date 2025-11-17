"""
Chart Generation Module
Generates professional trading charts with all technical indicators
Resolution: 1920x1080, Light theme, Volume profile included
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates professional stock charts with technical indicators"""
    
    def __init__(self, output_dir: str = "/workspaces/Stock-Chart-Analysis-AI-Agent/backend/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Light theme style
        self.style = mpf.make_mpf_style(
            base_mpf_style='yahoo',
            marketcolors=mpf.make_marketcolors(
                up='#26A69A',
                down='#EF5350',
                edge='inherit',
                wick='inherit',
                volume='in',
                alpha=0.9,
            ),
            gridcolor='#E0E0E0',
            gridstyle='--',
            y_on_right=False,
            rc={
                'font.size': 10,
                'axes.labelsize': 11,
                'axes.titlesize': 13,
                'xtick.labelsize': 9,
                'ytick.labelsize': 9,
                'legend.fontsize': 9,
            }
        )
    
    def generate_comprehensive_chart(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, Any],
        symbol: str,
        timeframe: str,
        stock_info: Optional[Dict] = None
    ) -> str:
        """
        Generate comprehensive chart with all indicators
        
        Args:
            df: DataFrame with OHLCV and calculated indicators
            indicators: Dictionary of all calculated indicators
            symbol: Stock symbol
            timeframe: Timeframe (1d, 1h, etc.)
            stock_info: Additional stock information
        
        Returns:
            Path to saved chart image
        """
        try:
            logger.info(f"Generating comprehensive chart for {symbol} {timeframe}")
            
            # Prepare plots
            additional_plots = self._prepare_indicator_plots(df, indicators)
            
            # Create figure with subplots
            fig, axes = mpf.plot(
                df,
                type='candle',
                style=self.style,
                volume=True,
                addplot=additional_plots,
                figsize=(19.2, 10.8),  # 1920x1080 pixels at 100 DPI
                panel_ratios=(6, 2, 2, 2),  # Main chart larger than subplots
                returnfig=True,
                warn_too_much_data=500,
            )
            
            # Add title and annotations
            self._add_chart_annotations(fig, axes, df, indicators, symbol, timeframe, stock_info)
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{timeframe}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            fig.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            logger.info(f"Chart saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            raise
    
    def _prepare_indicator_plots(self, df: pd.DataFrame, indicators: Dict) -> list:
        """Prepare all indicator overlays for the chart"""
        plots = []
        
        # Get all column names
        cols = df.columns.tolist()
        
        # Moving Averages on main chart (panel 0)
        if 'SMA_50' in cols:
            plots.append(mpf.make_addplot(df['SMA_50'], panel=0, color='#2196F3', width=1.5, label='SMA 50'))
        if 'SMA_200' in cols:
            plots.append(mpf.make_addplot(df['SMA_200'], panel=0, color='#FF9800', width=1.5, label='SMA 200'))
        if 'EMA_20' in cols:
            plots.append(mpf.make_addplot(df['EMA_20'], panel=0, color='#9C27B0', width=1.0, linestyle='--', label='EMA 20'))
        
        # Bollinger Bands on main chart
        bb_upper = [c for c in cols if 'BBU' in c]
        bb_lower = [c for c in cols if 'BBL' in c]
        if bb_upper and bb_lower:
            plots.append(mpf.make_addplot(df[bb_upper[0]], panel=0, color='#B0BEC5', width=1.0, linestyle='--', alpha=0.5))
            plots.append(mpf.make_addplot(df[bb_lower[0]], panel=0, color='#B0BEC5', width=1.0, linestyle='--', alpha=0.5))
        
        # SuperTrend on main chart
        st_col = [c for c in cols if 'SUPERT' in c and 'SUPERTd' not in c]
        if st_col:
            plots.append(mpf.make_addplot(df[st_col[0]], panel=0, type='scatter', markersize=2, color='#673AB7', alpha=0.3))
        
        # Ichimoku Cloud components on main chart
        its_col = [c for c in cols if 'ITS' in c]
        iks_col = [c for c in cols if 'IKS' in c]
        if its_col:
            plots.append(mpf.make_addplot(df[its_col[0]], panel=0, color='#00BCD4', width=0.8, alpha=0.6))
        if iks_col:
            plots.append(mpf.make_addplot(df[iks_col[0]], panel=0, color='#FF5722', width=0.8, alpha=0.6))
        
        # RSI on panel 1
        if 'RSI' in cols:
            plots.append(mpf.make_addplot(df['RSI'], panel=1, color='#9C27B0', width=1.5, ylabel='RSI'))
            # Add overbought/oversold lines
            plots.append(mpf.make_addplot([70]*len(df), panel=1, color='#EF5350', width=0.5, linestyle='--', alpha=0.5))
            plots.append(mpf.make_addplot([30]*len(df), panel=1, color='#26A69A', width=0.5, linestyle='--', alpha=0.5))
        
        # MACD on panel 2
        macd_line = [c for c in cols if 'MACD' in c and 'MACDh' not in c and 'MACDs' not in c]
        macd_signal = [c for c in cols if 'MACDs' in c]
        macd_hist = [c for c in cols if 'MACDh' in c]
        
        if macd_line:
            plots.append(mpf.make_addplot(df[macd_line[0]], panel=2, color='#2196F3', width=1.5, ylabel='MACD'))
        if macd_signal:
            plots.append(mpf.make_addplot(df[macd_signal[0]], panel=2, color='#FF9800', width=1.0))
        if macd_hist:
            colors = ['#26A69A' if h >= 0 else '#EF5350' for h in df[macd_hist[0]]]
            plots.append(mpf.make_addplot(df[macd_hist[0]], panel=2, type='bar', color=colors, alpha=0.3))
        
        # Stochastic on panel 3
        stoch_k = [c for c in cols if 'STOCHk' in c]
        stoch_d = [c for c in cols if 'STOCHd' in c]
        
        if stoch_k:
            plots.append(mpf.make_addplot(df[stoch_k[0]], panel=3, color='#2196F3', width=1.5, ylabel='Stochastic'))
        if stoch_d:
            plots.append(mpf.make_addplot(df[stoch_d[0]], panel=3, color='#FF9800', width=1.0))
        if stoch_k:  # Add overbought/oversold lines
            plots.append(mpf.make_addplot([80]*len(df), panel=3, color='#EF5350', width=0.5, linestyle='--', alpha=0.5))
            plots.append(mpf.make_addplot([20]*len(df), panel=3, color='#26A69A', width=0.5, linestyle='--', alpha=0.5))
        
        return plots
    
    def _add_chart_annotations(
        self,
        fig,
        axes,
        df: pd.DataFrame,
        indicators: Dict,
        symbol: str,
        timeframe: str,
        stock_info: Optional[Dict]
    ):
        """Add title, labels, and indicator values to the chart"""
        try:
            # Main title
            company_name = stock_info.get('company_name', symbol) if stock_info else symbol
            latest = df.iloc[-1]
            
            title = f"{company_name} ({symbol}.NS) - {timeframe.upper()} Chart"
            subtitle = f"Close: ₹{latest['Close']:.2f} | Volume: {latest['Volume']:,}"
            
            fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
            axes[0].text(0.01, 0.98, subtitle, transform=axes[0].transAxes,
                        fontsize=11, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
            
            # Add indicator summary box
            indicator_text = self._create_indicator_summary(indicators, latest)
            axes[0].text(0.99, 0.98, indicator_text, transform=axes[0].transAxes,
                        fontsize=9, verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3),
                        family='monospace')
            
            # Add Fibonacci levels as horizontal lines (if available)
            if 'fibonacci' in indicators:
                fib_levels = indicators['fibonacci']['retracements']
                for level, price in fib_levels.items():
                    if level in ['0.382', '0.5', '0.618']:  # Only show key levels
                        axes[0].axhline(y=price, color='gray', linestyle=':', alpha=0.3, linewidth=0.8)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fig.text(0.99, 0.01, f"Generated: {timestamp}", ha='right', va='bottom', fontsize=8, color='gray')
            
        except Exception as e:
            logger.error(f"Error adding annotations: {str(e)}")
    
    def _create_indicator_summary(self, indicators: Dict, latest_candle: pd.Series) -> str:
        """Create a text summary of key indicators"""
        lines = []
        
        # Price info
        lines.append(f"O: {latest_candle['Open']:.2f}")
        lines.append(f"H: {latest_candle['High']:.2f}")
        lines.append(f"L: {latest_candle['Low']:.2f}")
        lines.append(f"C: {latest_candle['Close']:.2f}")
        lines.append("")
        
        # Key indicators
        if 'moving_averages' in indicators:
            ma = indicators['moving_averages']
            lines.append(f"SMA50: {ma['SMA_50']:.2f}")
            lines.append(f"Price vs MA: {ma['price_vs_SMA50']:+.2f}%")
        
        if 'rsi' in indicators:
            lines.append(f"RSI: {indicators['rsi']['value']:.1f}")
        
        if 'supertrend' in indicators:
            lines.append(f"ST: {indicators['supertrend']['signal']}")
        
        if 'atr' in indicators:
            lines.append(f"ATR: {indicators['atr']['percentage']:.2f}%")
        
        return "\n".join(lines)
    
    def generate_simple_chart(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str
    ) -> str:
        """Generate a simple candlestick chart without indicators (for quick previews)"""
        try:
            fig, axes = mpf.plot(
                df,
                type='candle',
                style=self.style,
                volume=True,
                figsize=(19.2, 10.8),
                title=f"{symbol} - {timeframe}",
                returnfig=True,
            )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{timeframe}_simple_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            fig.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating simple chart: {str(e)}")
            raise


# Test function
def test_chart_generation():
    """Test chart generation with NSE stock"""
    import sys
    sys.path.append('/workspaces/Stock-Chart-Analysis-AI-Agent/backend/src/services')
    from data_fetcher import StockDataFetcher
    from technical_indicators import TechnicalIndicators
    
    print("\n" + "="*80)
    print("TESTING CHART GENERATION")
    print("="*80)
    
    # Fetch data
    fetcher = StockDataFetcher()
    symbol = 'RELIANCE'
    df = fetcher.fetch_live_data(symbol, timeframe='1d')
    
    if df is not None and not df.empty:
        # Calculate indicators
        calc = TechnicalIndicators(df)
        indicators = calc.calculate_all()
        df_enriched = calc.get_enriched_dataframe()
        
        # Get stock info
        stock_info = fetcher.get_stock_info(symbol)
        
        # Generate chart
        generator = ChartGenerator()
        chart_path = generator.generate_comprehensive_chart(
            df_enriched,
            indicators,
            symbol,
            '1d',
            stock_info
        )
        
        print(f"\n✅ Chart generated successfully!")
        print(f"📊 Chart saved at: {chart_path}")
        
        # Check file size
        import os
        file_size = os.path.getsize(chart_path) / 1024  # KB
        print(f"📦 File size: {file_size:.2f} KB")
        
    else:
        print("❌ Failed to fetch data")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_chart_generation()