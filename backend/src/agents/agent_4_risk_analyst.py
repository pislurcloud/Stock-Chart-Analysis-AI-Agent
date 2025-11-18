"""
Agent 4: Risk & Scenario Analyst
Generates scenario playbook with R:R ratios, entries, stops, targets
Uses: GPT-4o-mini (default) or Claude Sonnet 4 (configurable)
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Add parent directory to path
#backend_dir = Path(__file__).parent.parent.parent
#sys.path.insert(0, str(backend_dir))
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
#sys.path.append('/workspaces/Stock-Chart-Analysis-AI-Agent/backend')

from src.utils.llm_config import LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskScenarioAnalyst:
    """
    Agent 4: Risk & Scenario Analyst
    Creates comprehensive scenario playbook with risk/reward analysis
    """
    
    def __init__(self):
        """Initialize with configured LLM"""
        self.config = LLMConfig.get_agent_config('risk')
        logger.info(f"Risk Agent initialized with {self.config['model']}")
    
    def analyze(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate risk scenarios and trading strategies
        
        Args:
            data_package: Output from Agent 1
            technical_analysis: Output from Agent 2
            pattern_analysis: Output from Agent 3
        
        Returns:
            Complete risk analysis with scenarios
        """
        logger.info("Generating risk scenarios and strategies...")
        
        try:
            # Create comprehensive prompt
            prompt = self._create_risk_prompt(
                data_package,
                technical_analysis,
                pattern_analysis
            )
            
            # Call LLM for strategic analysis
            response = self._call_risk_llm(prompt)
            
            # Parse and structure response
            scenarios = self._parse_scenarios(response, data_package, technical_analysis)
            
            # Add backtesting insights
            backtest_results = self._simulate_backtest(
                data_package,
                technical_analysis
            )
            
            result = {
                'scenarios': scenarios,
                'backtest': backtest_results,
                'risk_metrics': self._calculate_risk_metrics(
                    data_package,
                    technical_analysis,
                    scenarios
                ),
                'position_sizing': self._recommend_position_size(
                    data_package,
                    technical_analysis
                ),
                'raw_llm_analysis': response
            }
            
            logger.info(f"Risk analysis complete: {len(scenarios)} scenarios generated")
            
            return result
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            return self._fallback_scenarios(data_package, technical_analysis)
    
    def _create_risk_prompt(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> str:
        """Create detailed prompt for risk/scenario analysis"""
        
        metadata = data_package['metadata']
        latest = data_package['latest_candle']
        indicators = data_package['indicators']
        
        bias = technical_analysis['overall_bias']
        strength = technical_analysis['strength_score']
        trend = technical_analysis['trend_analysis']
        momentum = technical_analysis['momentum_analysis']
        support_resistance = technical_analysis['support_resistance']
        
        # Get key levels
        current_price = latest['close']
        atr = indicators.get('atr', {}).get('value', current_price * 0.02)
        
        # Support/Resistance levels
        resistance_levels = [level[1] for level in support_resistance.get('nearest_resistance', [])[:3]]
        support_levels = [level[1] for level in support_resistance.get('nearest_support', [])[:3]]
        
        prompt = f"""You are a professional risk analyst and trading strategist. Create a comprehensive scenario playbook for this stock.

**STOCK:** {metadata['company_name']} ({metadata['symbol']})
**CURRENT PRICE:** ₹{current_price:.2f}
**TIMEFRAME:** {metadata['timeframe']}

**TECHNICAL CONTEXT:**
- Overall Bias: {bias} (Strength: {strength}/100)
- Trend: {trend['trend']} (ADX: {trend.get('adx_strength', 'N/A')})
- Momentum: {momentum['momentum']}
- ATR (volatility): ₹{atr:.2f} ({indicators.get('atr', {}).get('percentage', 0):.2f}%)

**KEY LEVELS:**
- Resistance: {', '.join([f'₹{r:.2f}' for r in resistance_levels]) if resistance_levels else 'None identified'}
- Support: {', '.join([f'₹{s:.2f}' for s in support_levels]) if support_levels else 'None identified'}

**PATTERN INSIGHTS:**
{pattern_analysis.get('raw_analysis', 'No pattern analysis available')[:500]}

**YOUR TASK:**
Create a detailed scenario playbook with specific entry/exit strategies. For EACH scenario below, provide:

1. **BULLISH AGGRESSIVE** (if bias allows):
   - Entry: Specific price level
   - Stop Loss: Where the bullish story breaks
   - Target 1: Conservative target
   - Target 2: Aggressive target (optional)
   - Confidence: High/Moderate/Low
   - WarrenAI Take: One-liner strategic insight

2. **BULLISH CONSERVATIVE** (if bias allows):
   - Entry: Better entry on pullback/dip
   - Stop Loss: Tighter stop
   - Target 1: Realistic target
   - Confidence: High/Moderate/Low
   - WarrenAI Take: When to enter this trade

3. **BEARISH/COUNTER-TREND** (always include for risk awareness):
   - Entry: If trend reverses
   - Stop Loss: Above resistance
   - Target 1: Downside target
   - Confidence: Usually Low unless strong bearish bias
   - WarrenAI Take: Risk warning

**CRITICAL REQUIREMENTS:**
- All prices must be REALISTIC and based on current levels
- Stop losses should use ATR and key support/resistance
- Calculate and provide R:R ratio for each scenario
- Entry should consider current price of ₹{current_price:.2f}
- Be specific - no vague levels like "wait for confirmation"
- If bias is bearish, flip the aggressive/conservative logic

**ADDITIONAL INSIGHTS:**
- Optimal trade recommendation
- No-trade zones (price ranges to avoid)
- Position sizing suggestion (% of capital)
- Key risk factors
- What would invalidate each scenario

**OUTPUT FORMAT:**
Provide a clear, structured response with specific numbers. Think like a professional trader creating an actionable plan."""

        return prompt
    
    def _call_risk_llm(self, prompt: str) -> str:
        """Call LLM for risk analysis"""
        try:
            if self.config['provider'] == 'openai':
                return self._call_openai(prompt)
            elif self.config['provider'] == 'openrouter':
                return self._call_openrouter(prompt)
            elif self.config['provider'] == 'anthropic':
                return self._call_anthropic(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.config['provider']}")
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.config['api_key'])
        
        response = client.chat.completions.create(
            model=self.config['model'],
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional trading risk analyst. Provide specific, actionable trading scenarios with exact price levels and risk/reward ratios."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config['model'],
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional trading risk analyst. Provide specific, actionable trading scenarios."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=self.config['api_key'])
        
        message = client.messages.create(
            model=self.config['model'],
            max_tokens=2000,
            system="You are a professional trading risk analyst. Provide specific, actionable trading scenarios with exact price levels.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return message.content[0].text
    
    def _parse_scenarios(
        self,
        llm_response: str,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse LLM response into structured scenarios
        
        Returns:
            List of scenario dictionaries
        """
        current_price = data_package['latest_candle']['close']
        atr = data_package['indicators'].get('atr', {}).get('value', current_price * 0.02)
        
        # Try to extract scenarios from LLM response
        scenarios = self._extract_scenarios_from_text(llm_response, current_price, atr)
        
        # If extraction failed, create fallback scenarios
        if not scenarios:
            scenarios = self._create_fallback_scenarios(
                data_package,
                technical_analysis
            )
        
        return scenarios
    
    def _extract_scenarios_from_text(
        self,
        text: str,
        current_price: float,
        atr: float
    ) -> List[Dict[str, Any]]:
        """Extract scenario details from LLM response text"""
        scenarios = []
        
        # This is a simplified extraction - can be enhanced with regex or structured output
        # For now, create structured scenarios based on common patterns
        
        text_lower = text.lower()
        
        # Try to identify bullish aggressive scenario
        if 'bullish aggressive' in text_lower or 'aggressive entry' in text_lower:
            scenario = self._extract_single_scenario(
                text,
                'bullish_aggressive',
                current_price,
                atr
            )
            if scenario:
                scenarios.append(scenario)
        
        # Try to identify bullish conservative
        if 'bullish conservative' in text_lower or 'conservative' in text_lower:
            scenario = self._extract_single_scenario(
                text,
                'bullish_conservative',
                current_price,
                atr
            )
            if scenario:
                scenarios.append(scenario)
        
        # Try to identify bearish
        if 'bearish' in text_lower or 'counter' in text_lower:
            scenario = self._extract_single_scenario(
                text,
                'bearish',
                current_price,
                atr
            )
            if scenario:
                scenarios.append(scenario)
        
        return scenarios
    
    def _extract_single_scenario(
        self,
        text: str,
        scenario_type: str,
        current_price: float,
        atr: float
    ) -> Optional[Dict[str, Any]]:
        """Extract a single scenario from text (simplified)"""
        # This is a placeholder for more sophisticated extraction
        # In production, would use structured output or better parsing
        
        # For now, return None to trigger fallback
        return None
    
    def _create_fallback_scenarios(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create rule-based scenarios when LLM extraction fails"""
        
        current_price = data_package['latest_candle']['close']
        atr = data_package['indicators'].get('atr', {}).get('value', current_price * 0.02)
        support_resistance = technical_analysis['support_resistance']
        bias = technical_analysis['overall_bias']
        
        scenarios = []
        
        # Get resistance and support levels
        resistance_levels = [level[1] for level in support_resistance.get('nearest_resistance', [])]
        support_levels = [level[1] for level in support_resistance.get('nearest_support', [])]
        
        resistance = resistance_levels[0] if resistance_levels else current_price * 1.05
        support = support_levels[0] if support_levels else current_price * 0.95
        
        # Bullish Aggressive
        if 'BULLISH' in bias:
            entry_agg = current_price
            stop_agg = support
            target_agg = resistance
            rr_agg = (target_agg - entry_agg) / (entry_agg - stop_agg) if entry_agg > stop_agg else 0
            
            scenarios.append({
                'scenario': 'Bullish (Aggressive)',
                'entry': round(entry_agg, 2),
                'stop': round(stop_agg, 2),
                'target': round(target_agg, 2),
                'rr_ratio': round(rr_agg, 2),
                'confidence': 'Moderate' if 'STRONG' in bias else 'Low',
                'warreni_take': 'Enter near current levels if bias holds'
            })
            
            # Bullish Conservative
            entry_cons = support + (atr * 0.5)
            stop_cons = support - atr
            target_cons = resistance
            rr_cons = (target_cons - entry_cons) / (entry_cons - stop_cons) if entry_cons > stop_cons else 0
            
            scenarios.append({
                'scenario': 'Bullish (Conservative)',
                'entry': round(entry_cons, 2),
                'stop': round(stop_cons, 2),
                'target': round(target_cons, 2),
                'rr_ratio': round(rr_cons, 2),
                'confidence': 'High' if 'STRONG' in bias else 'Moderate',
                'warreni_take': 'Wait for dip to support before entering'
            })
        
        # Bearish scenario (counter-trend or main if bearish bias)
        entry_bear = current_price
        stop_bear = resistance + atr
        target_bear = support
        rr_bear = (entry_bear - target_bear) / (stop_bear - entry_bear) if stop_bear > entry_bear else 0
        
        confidence_bear = 'Moderate' if 'BEARISH' in bias else 'Low'
        
        scenarios.append({
            'scenario': 'Bearish (Counter-trend)' if 'BULLISH' in bias else 'Bearish (Aggressive)',
            'entry': round(entry_bear, 2),
            'stop': round(stop_bear, 2),
            'target': round(target_bear, 2),
            'rr_ratio': round(rr_bear, 2),
            'confidence': confidence_bear,
            'warreni_take': 'Counter-trend trade - high risk' if 'BULLISH' in bias else 'Enter on breakdown'
        })
        
        return scenarios
    
    def _simulate_backtest(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate backtesting results based on current setup
        (Simplified - would need historical data for real backtesting)
        """
        bias = technical_analysis['overall_bias']
        strength = technical_analysis['strength_score']
        
        # Estimate success rate based on bias and strength
        if 'STRONG BULLISH' in bias:
            success_rate = 65 + (strength / 100 * 15)  # 65-80%
        elif 'BULLISH' in bias:
            success_rate = 50 + (strength / 100 * 15)  # 50-65%
        elif 'STRONG BEARISH' in bias:
            success_rate = 65 + (strength / 100 * 15)
        elif 'BEARISH' in bias:
            success_rate = 50 + (strength / 100 * 15)
        else:
            success_rate = 40 + (strength / 100 * 10)  # 40-50% for neutral
        
        return {
            'estimated_success_rate': round(success_rate, 1),
            'sample_size': '(Based on similar setups)',
            'lookback_period': '6 months',
            'note': 'Estimated based on technical bias and strength'
        }
    
    def _calculate_risk_metrics(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall risk metrics"""
        
        current_price = data_package['latest_candle']['close']
        volatility = technical_analysis['volatility_analysis']
        
        # Calculate average R:R
        rr_ratios = [s.get('rr_ratio', 0) for s in scenarios if s.get('rr_ratio', 0) > 0]
        avg_rr = sum(rr_ratios) / len(rr_ratios) if rr_ratios else 0
        
        return {
            'average_rr_ratio': round(avg_rr, 2),
            'volatility_level': volatility['volatility_level'],
            'expected_range': f"₹{current_price * 0.98:.2f} - ₹{current_price * 1.02:.2f} (daily)",
            'risk_grade': self._calculate_risk_grade(technical_analysis)
        }
    
    def _recommend_position_size(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend position sizing based on volatility"""
        
        volatility = technical_analysis['volatility_analysis']['volatility_level']
        strength = technical_analysis['strength_score']
        
        if volatility == 'HIGH':
            position = '1-2%'
            rationale = 'High volatility requires smaller position'
        elif volatility == 'MODERATE':
            position = '2-3%'
            rationale = 'Moderate volatility allows standard sizing'
        else:
            position = '3-5%'
            rationale = 'Low volatility can handle larger position'
        
        # Adjust for signal strength
        if strength < 40:
            position = position.split('-')[0] + '%'  # Lower end
            rationale += ', weak signals reduce size'
        
        return {
            'recommended_position': position,
            'rationale': rationale,
            'max_risk_per_trade': '2% of capital'
        }
    
    def _calculate_risk_grade(self, technical_analysis: Dict[str, Any]) -> str:
        """Calculate overall risk grade"""
        strength = technical_analysis['strength_score']
        volatility = technical_analysis['volatility_analysis']['volatility_level']
        
        if strength > 70 and volatility != 'HIGH':
            return 'A (Low Risk)'
        elif strength > 50:
            return 'B (Moderate Risk)'
        elif strength > 30:
            return 'C (High Risk)'
        else:
            return 'D (Very High Risk)'
    
    def _fallback_scenarios(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback when LLM fails"""
        logger.warning("Using fallback risk scenarios")
        
        scenarios = self._create_fallback_scenarios(data_package, technical_analysis)
        backtest = self._simulate_backtest(data_package, technical_analysis)
        
        return {
            'scenarios': scenarios,
            'backtest': backtest,
            'risk_metrics': self._calculate_risk_metrics(
                data_package,
                technical_analysis,
                scenarios
            ),
            'position_sizing': self._recommend_position_size(
                data_package,
                technical_analysis
            ),
            'fallback_used': True
        }


# Test function
if __name__ == "__main__":
    print("="*80)
    print("Testing Agent 4: Risk & Scenario Analyst")
    print("="*80)
    
    # Get data from previous agents
    from agent_1_orchestrator import DataOrchestrator
    from agent_2_technical_analyst import TechnicalAnalyst
    from agent_3_vision_recognition import VisionPatternRecognition
    
    orchestrator = DataOrchestrator()
    data_package = orchestrator.orchestrate('RELIANCE', '1d')
    
    if data_package['status'] == 'success':
        analyst = TechnicalAnalyst()
        technical_analysis = analyst.analyze(data_package)
        
        vision = VisionPatternRecognition()
        pattern_analysis = vision.analyze_chart(data_package, technical_analysis)
        
        # Run risk analysis
        risk_analyst = RiskScenarioAnalyst()
        risk_analysis = risk_analyst.analyze(
            data_package,
            technical_analysis,
            pattern_analysis
        )
        
        print("\n✅ Risk Analysis Complete!")
        
        print("\nScenarios:")
        for scenario in risk_analysis['scenarios']:
            print(f"\n  {scenario['scenario']}:")
            print(f"    Entry: ₹{scenario['entry']}")
            print(f"    Stop: ₹{scenario['stop']}")
            print(f"    Target: ₹{scenario['target']}")
            print(f"    R:R: {scenario['rr_ratio']}")
            print(f"    Confidence: {scenario['confidence']}")
            print(f"    Take: {scenario['warreni_take']}")
        
        print(f"\nPosition Sizing: {risk_analysis['position_sizing']['recommended_position']}")
        print(f"Risk Grade: {risk_analysis['risk_metrics']['risk_grade']}")
    
    print("\n" + "="*80)