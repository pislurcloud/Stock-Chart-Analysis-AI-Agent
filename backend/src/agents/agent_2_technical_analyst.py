"""
Agent 2: Technical Analyst
Interprets indicators and identifies signals
No LLM required - rule-based analysis
"""

from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalyst:
    """
    Agent 2: Technical Analyst
    Analyzes calculated indicators and generates structured insights
    """
    
    def analyze(self, data_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze technical indicators and generate insights
        
        Args:
            data_package: Output from Agent 1
        
        Returns:
            Structured technical analysis
        """
        logger.info("Performing technical analysis...")
        
        indicators = data_package['indicators']
        latest_candle = data_package['latest_candle']
        
        analysis = {
            'trend_analysis': self._analyze_trend(indicators),
            'momentum_analysis': self._analyze_momentum(indicators),
            'volatility_analysis': self._analyze_volatility(indicators),
            'volume_analysis': self._analyze_volume(indicators),
            'support_resistance': self._analyze_support_resistance(indicators, latest_candle),
            'signal_confluence': self._identify_confluences(indicators),
            'overall_bias': None,  # Will be determined
            'strength_score': 0.0,  # 0-100
            'key_levels': {},
        }
        
        # Determine overall bias and strength
        analysis['overall_bias'] = self._determine_bias(analysis)
        analysis['strength_score'] = self._calculate_strength_score(analysis)
        analysis['key_levels'] = self._identify_key_levels(indicators, latest_candle)
        
        logger.info(f"Technical analysis complete: {analysis['overall_bias']} bias with {analysis['strength_score']:.0f}% strength")
        
        return analysis
    
    def _analyze_trend(self, indicators: Dict) -> Dict[str, Any]:
        """Analyze trend indicators"""
        ma = indicators.get('moving_averages', {})
        st = indicators.get('supertrend', {})
        ich = indicators.get('ichimoku', {})
        adx = indicators.get('adx', {})
        
        signals = []
        score = 0
        
        # Moving Average analysis
        if ma.get('price_vs_SMA50', 0) > 0:
            signals.append("Price above SMA 50 (bullish)")
            score += 1
        else:
            signals.append("Price below SMA 50 (bearish)")
            score -= 1
        
        if ma.get('price_vs_SMA200', 0) > 0:
            signals.append("Price above SMA 200 (long-term bullish)")
            score += 1
        else:
            signals.append("Price below SMA 200 (long-term bearish)")
            score -= 1
        
        # Golden/Death Cross
        sma50 = ma.get('SMA_50', 0)
        sma200 = ma.get('SMA_200', 0)
        if sma50 > sma200:
            signals.append("Golden Cross formation (SMA 50 > SMA 200)")
            score += 1
        elif sma50 < sma200:
            signals.append("Death Cross formation (SMA 50 < SMA 200)")
            score -= 1
        
        # SuperTrend
        if st.get('signal') == 'BULLISH':
            signals.append("SuperTrend: BULLISH")
            score += 1
        else:
            signals.append("SuperTrend: BEARISH")
            score -= 1
        
        # Ichimoku
        if ich.get('price_vs_cloud') == 'ABOVE':
            signals.append("Price above Ichimoku Cloud (bullish)")
            score += 1
        elif ich.get('price_vs_cloud') == 'BELOW':
            signals.append("Price below Ichimoku Cloud (bearish)")
            score -= 1
        
        # ADX strength
        adx_val = adx.get('value', 0)
        adx_strength = adx.get('strength', 'WEAK')
        if adx_strength in ['STRONG', 'MODERATE']:
            signals.append(f"ADX shows {adx_strength} trend (ADX: {adx_val:.1f})")
        else:
            signals.append(f"ADX shows WEAK trend (ADX: {adx_val:.1f}) - choppy market")
        
        # Determine trend
        if score >= 3:
            trend = "STRONG BULLISH"
        elif score >= 1:
            trend = "BULLISH"
        elif score <= -3:
            trend = "STRONG BEARISH"
        elif score <= -1:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"
        
        return {
            'trend': trend,
            'score': score,
            'signals': signals,
            'adx_strength': adx_strength
        }
    
    def _analyze_momentum(self, indicators: Dict) -> Dict[str, Any]:
        """Analyze momentum indicators"""
        rsi = indicators.get('rsi', {})
        macd = indicators.get('macd', {})
        stoch = indicators.get('stochastic', {})
        
        signals = []
        score = 0
        
        # RSI
        rsi_val = rsi.get('value', 50)
        rsi_cond = rsi.get('condition', 'NEUTRAL')
        
        if rsi_cond == 'OVERSOLD':
            signals.append(f"RSI oversold ({rsi_val:.1f}) - potential bounce")
            score += 1
        elif rsi_cond == 'OVERBOUGHT':
            signals.append(f"RSI overbought ({rsi_val:.1f}) - potential pullback")
            score -= 1
        elif rsi_val > 50:
            signals.append(f"RSI bullish ({rsi_val:.1f})")
            score += 0.5
        else:
            signals.append(f"RSI bearish ({rsi_val:.1f})")
            score -= 0.5
        
        # MACD
        macd_sig = macd.get('signal', 'NEUTRAL')
        macd_hist = macd.get('histogram', 0)
        
        if macd_sig == 'BULLISH':
            signals.append("MACD bullish crossover")
            score += 1
        else:
            signals.append("MACD bearish crossover")
            score -= 1
        
        if macd_hist > 0:
            signals.append("MACD histogram positive (momentum increasing)")
        else:
            signals.append("MACD histogram negative (momentum decreasing)")
        
        # Stochastic
        stoch_cond = stoch.get('condition', 'NEUTRAL')
        stoch_k = stoch.get('k', 50)
        
        if stoch_cond == 'OVERSOLD':
            signals.append(f"Stochastic oversold (%K: {stoch_k:.1f})")
            score += 0.5
        elif stoch_cond == 'OVERBOUGHT':
            signals.append(f"Stochastic overbought (%K: {stoch_k:.1f})")
            score -= 0.5
        
        # Determine momentum
        if score >= 2:
            momentum = "STRONG BULLISH"
        elif score >= 0.5:
            momentum = "BULLISH"
        elif score <= -2:
            momentum = "STRONG BEARISH"
        elif score <= -0.5:
            momentum = "BEARISH"
        else:
            momentum = "NEUTRAL"
        
        return {
            'momentum': momentum,
            'score': score,
            'signals': signals,
            'rsi_divergence': self._check_rsi_divergence(rsi_val)
        }
    
    def _analyze_volatility(self, indicators: Dict) -> Dict[str, Any]:
        """Analyze volatility indicators"""
        bb = indicators.get('bollinger_bands', {})
        atr = indicators.get('atr', {})
        
        signals = []
        
        # Bollinger Bands
        bb_pct = bb.get('percent_b', 0.5)
        bb_width = bb.get('bandwidth', 0)
        
        if bb_pct > 1:
            signals.append("Price above upper Bollinger Band (extended)")
        elif bb_pct < 0:
            signals.append("Price below lower Bollinger Band (oversold)")
        elif 0.4 < bb_pct < 0.6:
            signals.append("Price near Bollinger Band middle (consolidation)")
        
        # ATR
        atr_pct = atr.get('percentage', 0)
        
        if atr_pct > 4:
            volatility_level = "HIGH"
            signals.append(f"High volatility (ATR: {atr_pct:.2f}%)")
        elif atr_pct > 2:
            volatility_level = "MODERATE"
            signals.append(f"Moderate volatility (ATR: {atr_pct:.2f}%)")
        else:
            volatility_level = "LOW"
            signals.append(f"Low volatility (ATR: {atr_pct:.2f}%)")
        
        return {
            'volatility_level': volatility_level,
            'atr_percentage': atr_pct,
            'bollinger_position': bb_pct,
            'signals': signals
        }
    
    def _analyze_volume(self, indicators: Dict) -> Dict[str, Any]:
        """Analyze volume indicators"""
        vol = indicators.get('volume', {})
        
        signals = []
        
        rel_vol = vol.get('relative_volume', 1.0)
        
        if rel_vol > 1.5:
            volume_status = "VERY HIGH"
            signals.append(f"Very high volume ({rel_vol:.2f}x average)")
        elif rel_vol > 1.2:
            volume_status = "HIGH"
            signals.append(f"Above average volume ({rel_vol:.2f}x)")
        elif rel_vol < 0.8:
            volume_status = "LOW"
            signals.append(f"Below average volume ({rel_vol:.2f}x)")
        else:
            volume_status = "NORMAL"
            signals.append(f"Normal volume ({rel_vol:.2f}x)")
        
        return {
            'volume_status': volume_status,
            'relative_volume': rel_vol,
            'signals': signals
        }
    
    def _analyze_support_resistance(self, indicators: Dict, latest_candle: Dict) -> Dict[str, Any]:
        """Identify key support and resistance levels"""
        fib = indicators.get('fibonacci', {})
        pivot = indicators.get('pivot_points', {})
        
        current_price = latest_candle['close']
        
        # Collect all levels
        levels = {
            'resistance': [],
            'support': []
        }
        
        # Fibonacci levels
        fib_retraces = fib.get('retracements', {})
        for level, price in fib_retraces.items():
            if price > current_price:
                levels['resistance'].append(('Fibonacci ' + level, price))
            else:
                levels['support'].append(('Fibonacci ' + level, price))
        
        # Pivot points
        if pivot.get('r1', 0) > current_price:
            levels['resistance'].append(('Pivot R1', pivot.get('r1', 0)))
        if pivot.get('r2', 0) > current_price:
            levels['resistance'].append(('Pivot R2', pivot.get('r2', 0)))
        if pivot.get('s1', 0) < current_price:
            levels['support'].append(('Pivot S1', pivot.get('s1', 0)))
        if pivot.get('s2', 0) < current_price:
            levels['support'].append(('Pivot S2', pivot.get('s2', 0)))
        
        # Sort by distance from current price
        levels['resistance'].sort(key=lambda x: x[1])
        levels['support'].sort(key=lambda x: x[1], reverse=True)
        
        return {
            'current_price': current_price,
            'nearest_resistance': levels['resistance'][:3] if levels['resistance'] else [],
            'nearest_support': levels['support'][:3] if levels['support'] else [],
            'all_levels': levels
        }
    
    def _identify_confluences(self, indicators: Dict) -> List[str]:
        """Identify when multiple indicators agree"""
        confluences = []
        
        # Bullish confluences
        bullish_count = 0
        if indicators.get('supertrend', {}).get('signal') == 'BULLISH':
            bullish_count += 1
        if indicators.get('macd', {}).get('signal') == 'BULLISH':
            bullish_count += 1
        if indicators.get('moving_averages', {}).get('price_vs_SMA50', 0) > 0:
            bullish_count += 1
        if indicators.get('rsi', {}).get('condition') == 'OVERSOLD':
            bullish_count += 1
        
        if bullish_count >= 3:
            confluences.append(f"Strong bullish confluence ({bullish_count} indicators)")
        
        # Bearish confluences
        bearish_count = 0
        if indicators.get('supertrend', {}).get('signal') == 'BEARISH':
            bearish_count += 1
        if indicators.get('macd', {}).get('signal') == 'BEARISH':
            bearish_count += 1
        if indicators.get('moving_averages', {}).get('price_vs_SMA50', 0) < 0:
            bearish_count += 1
        if indicators.get('rsi', {}).get('condition') == 'OVERBOUGHT':
            bearish_count += 1
        
        if bearish_count >= 3:
            confluences.append(f"Strong bearish confluence ({bearish_count} indicators)")
        
        return confluences
    
    def _determine_bias(self, analysis: Dict) -> str:
        """Determine overall market bias"""
        trend_score = analysis['trend_analysis']['score']
        momentum_score = analysis['momentum_analysis']['score']
        
        total_score = trend_score + momentum_score
        
        if total_score >= 4:
            return "STRONG BULLISH"
        elif total_score >= 2:
            return "BULLISH"
        elif total_score <= -4:
            return "STRONG BEARISH"
        elif total_score <= -2:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_strength_score(self, analysis: Dict) -> float:
        """Calculate overall signal strength (0-100)"""
        trend_score = abs(analysis['trend_analysis']['score'])
        momentum_score = abs(analysis['momentum_analysis']['score'])
        confluence_count = len(analysis['signal_confluence'])
        
        # Normalize scores
        max_trend = 6  # Maximum possible trend score
        max_momentum = 3  # Maximum possible momentum score
        
        trend_contribution = (trend_score / max_trend) * 40
        momentum_contribution = (momentum_score / max_momentum) * 40
        confluence_contribution = min(confluence_count * 10, 20)
        
        total = trend_contribution + momentum_contribution + confluence_contribution
        
        return round(total, 2)
    
    def _identify_key_levels(self, indicators: Dict, latest_candle: Dict) -> Dict[str, float]:
        """Identify most important price levels"""
        current_price = latest_candle['close']
        
        # Get key levels
        ma = indicators.get('moving_averages', {})
        pivot = indicators.get('pivot_points', {})
        
        return {
            'current': current_price,
            'sma_50': ma.get('SMA_50', 0),
            'sma_200': ma.get('SMA_200', 0),
            'pivot': pivot.get('pivot', 0),
            'resistance_1': pivot.get('r1', 0),
            'support_1': pivot.get('s1', 0)
        }
    
    def _check_rsi_divergence(self, rsi_value: float) -> Optional[str]:
        """Check for potential RSI divergence (simplified)"""
        # This is a placeholder - full divergence detection needs price history
        if rsi_value > 70:
            return "Potential bearish divergence zone"
        elif rsi_value < 30:
            return "Potential bullish divergence zone"
        return None


# Test function
if __name__ == "__main__":
    from agent_1_orchestrator import DataOrchestrator
    
    print("="*80)
    print("Testing Agent 2: Technical Analyst")
    print("="*80)
    
    # Get data from Agent 1
    orchestrator = DataOrchestrator()
    data_package = orchestrator.orchestrate('RELIANCE', '1d')
    
    if data_package['status'] == 'success':
        # Analyze with Agent 2
        analyst = TechnicalAnalyst()
        analysis = analyst.analyze(data_package)
        
        print("\n✅ Analysis Complete!")
        print(f"\nOverall Bias: {analysis['overall_bias']}")
        print(f"Strength Score: {analysis['strength_score']}/100")
        
        print("\nTrend Analysis:")
        print(f"  Trend: {analysis['trend_analysis']['trend']}")
        for signal in analysis['trend_analysis']['signals'][:3]:
            print(f"  • {signal}")
        
        print("\nMomentum Analysis:")
        print(f"  Momentum: {analysis['momentum_analysis']['momentum']}")
        for signal in analysis['momentum_analysis']['signals'][:3]:
            print(f"  • {signal}")
        
        print("\nKey Levels:")
        levels = analysis['key_levels']
        print(f"  Current: ₹{levels['current']:.2f}")
        print(f"  SMA 50: ₹{levels['sma_50']:.2f}")
        print(f"  Resistance: ₹{levels['resistance_1']:.2f}")
        print(f"  Support: ₹{levels['support_1']:.2f}")
        
        if analysis['signal_confluence']:
            print("\nConfluences:")
            for conf in analysis['signal_confluence']:
                print(f"  • {conf}")
    
    print("\n" + "="*80)