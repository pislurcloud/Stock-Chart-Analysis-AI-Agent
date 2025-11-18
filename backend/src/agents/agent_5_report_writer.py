"""
Agent 5: Report Writer & Synthesizer
Creates comprehensive markdown and DOCX reports from all agent outputs
Uses: moonshotai/kimi-vl-a3b-thinking (default) or Claude Sonnet 4 (configurable)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

# Add parent directory to path
#backend_dir = Path(__file__).parent.parent.parent
#sys.path.insert(0, str(backend_dir))
backend_dir = Path(__file__)
sys.path.insert(0, str(backend_dir))
#sys.path.append('/workspaces/Stock-Chart-Analysis-AI-Agent/backend')

from src.utils.llm_config import LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportWriter:
    """
    Agent 5: Report Writer
    Synthesizes all analysis into professional report
    """
    
    def __init__(self):
        """Initialize with configured LLM"""
        self.config = LLMConfig.get_agent_config('report')
        logger.info(f"Report Writer initialized with {self.config['model']}")
    
    def generate_report(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive report
        
        Args:
            data_package: Output from Agent 1
            technical_analysis: Output from Agent 2
            pattern_analysis: Output from Agent 3
            risk_analysis: Output from Agent 4
        
        Returns:
            Dict with markdown report and metadata
        """
        logger.info("Generating comprehensive report...")
        
        try:
            # Create synthesis prompt
            prompt = self._create_synthesis_prompt(
                data_package,
                technical_analysis,
                pattern_analysis,
                risk_analysis
            )
            
            # Call LLM for narrative synthesis
            llm_narrative = self._call_report_llm(prompt)
            
            # Generate structured report
            markdown_report = self._build_markdown_report(
                data_package,
                technical_analysis,
                pattern_analysis,
                risk_analysis,
                llm_narrative
            )
            
            result = {
                'markdown': markdown_report,
                'summary': self._extract_summary(markdown_report),
                'recommendation': self._extract_recommendation(risk_analysis),
                'generated_at': datetime.now().isoformat(),
                'word_count': len(markdown_report.split())
            }
            
            logger.info(f"Report generated: {result['word_count']} words")
            
            return result
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return self._fallback_report(
                data_package,
                technical_analysis,
                pattern_analysis,
                risk_analysis
            )
    
    def _create_synthesis_prompt(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> str:
        """Create prompt for narrative synthesis"""
        
        metadata = data_package['metadata']
        latest = data_package['latest_candle']
        bias = technical_analysis['overall_bias']
        scenarios = risk_analysis['scenarios']
        
        prompt = f"""You are a professional market analyst writing a comprehensive stock analysis report.

**STOCK:** {metadata['company_name']} ({metadata['symbol']})
**PRICE:** ₹{latest['close']:.2f}
**TIMEFRAME:** {metadata['timeframe']}

**ANALYSIS SUMMARY:**
- Technical Bias: {bias}
- Signal Strength: {technical_analysis['strength_score']}/100
- Pattern Recognition: {pattern_analysis.get('market_structure', 'N/A')}
- Scenarios Generated: {len(scenarios)}

**YOUR TASK:**
Write a compelling, professional analysis narrative that includes:

1. **OPENING HOOK** (1-2 sentences):
   - Capture the current market situation
   - Highlight the most important insight
   
2. **MARKET STRUCTURE ANALYSIS** (2-3 paragraphs):
   - Describe the technical setup
   - Explain what the indicators are showing
   - Discuss pattern formations (if any)
   - Analyze support/resistance landscape
   
3. **RISK LANDSCAPE** (1-2 paragraphs):
   - Discuss the scenarios (bullish/bearish)
   - Explain the risk/reward setup
   - Mention key levels where the story changes
   
4. **KEY TAKEAWAY** (1 strong paragraph):
   - What's the main lesson for traders?
   - What should they watch for?
   - Timing considerations

**STYLE GUIDELINES:**
- Be specific and actionable
- Use natural, confident language
- No jargon without explanation
- Think like you're advising a professional trader
- Include actual price levels when relevant
- Be honest about uncertainties

**LENGTH:** 200-300 words total

Write the narrative now:"""

        return prompt
    
    def _call_report_llm(self, prompt: str) -> str:
        """Call LLM for report synthesis"""
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
            return self._fallback_narrative(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.config['api_key'])
        
        response = client.chat.completions.create(
            model=self.config['model'],
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional market analyst writing clear, actionable stock analysis reports."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
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
                    "content": "You are a professional market analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1500,
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
            max_tokens=1500,
            system="You are a professional market analyst writing clear, actionable reports.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return message.content[0].text
    
    def _build_markdown_report(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        llm_narrative: str
    ) -> str:
        """Build complete markdown report"""
        
        metadata = data_package['metadata']
        latest = data_package['latest_candle']
        scenarios = risk_analysis['scenarios']
        backtest = risk_analysis['backtest']
        
        # Build scenario table
        scenario_table = self._build_scenario_table(scenarios)
        
        # Build pattern section
        pattern_section = self._build_pattern_section(
            pattern_analysis,
            technical_analysis
        )
        
        # Build technical details
        technical_details = self._build_technical_details(
            data_package,
            technical_analysis
        )
        
        report = f"""# {metadata['company_name']} ({metadata['symbol']}) - {metadata['timeframe'].upper()} Technical Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M IST')}  
**Current Price:** ₹{latest['close']:.2f}  
**Volume:** {latest['volume']:,}  
**Sector:** {metadata.get('sector', 'N/A')}

---

## Summary

{llm_narrative}

---

## 🚦 Technical Setup

**Overall Bias:** {technical_analysis['overall_bias']}  
**Signal Strength:** {technical_analysis['strength_score']}/100  
**Volatility:** {technical_analysis['volatility_analysis']['volatility_level']}  
**Risk Grade:** {risk_analysis['risk_metrics']['risk_grade']}

---

## 🧭 Scenario Playbook

{scenario_table}

**Insights 🔍**
- **Optimal trade:** {self._get_optimal_trade(scenarios)}
- **Position size:** {risk_analysis['position_sizing']['recommended_position']} of capital
- **Risk/Reward:** Average R:R of {risk_analysis['risk_metrics']['average_rr_ratio']}

---

{pattern_section}

---

## 📊 Technical Indicators Summary

{technical_details}

---

## 🎓 Key Takeaway

{self._generate_key_takeaway(technical_analysis, risk_analysis)}

---

## 📈 Backtest Results

**Similar Setup Success Rate:** {backtest['estimated_success_rate']}%  
**Lookback Period:** {backtest['lookback_period']}  
**Note:** {backtest['note']}

---

## ⚠️ Risk Warnings

- Stop losses are CRITICAL - honor them always
- Position sizing matters - never overleverage
- Market conditions can change rapidly
- Past patterns don't guarantee future results
- Always do your own research

---

👉 **Want me to analyze a different timeframe for additional perspective?**

---

*This analysis is for educational purposes only. Not financial advice. Trade at your own risk.*
"""
        
        return report
    
    def _build_scenario_table(self, scenarios: list) -> str:
        """Build scenario playbook table"""
        
        table = """| Scenario | Entry | Stop | Target | R:R | Confidence | WarrenAI Take |
|----------|-------|------|--------|-----|------------|---------------|
"""
        
        for scenario in scenarios:
            entry = scenario.get('entry', 0)
            stop = scenario.get('stop', 0)
            target = scenario.get('target', 0)
            rr = scenario.get('rr_ratio', 0)
            conf = scenario.get('confidence', 'N/A')
            take = scenario.get('warreni_take', 'See analysis')
            
            table += f"| {scenario.get('scenario', 'N/A')} | ₹{entry:.2f} | ₹{stop:.2f} | ₹{target:.2f} | {rr:.2f} | {conf} | {take} |\n"
        
        return table
    
    def _build_pattern_section(
        self,
        pattern_analysis: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> str:
        """Build pattern and risk lessons section"""
        
        patterns = pattern_analysis.get('patterns', [])
        volatility = technical_analysis['volatility_analysis']
        
        pattern_list = ""
        if patterns:
            for pattern in patterns[:3]:
                pattern_list += f"- **{pattern.get('pattern', 'Unknown')}**: Identified with {pattern_analysis.get('confidence', 'moderate')} confidence\n"
        else:
            pattern_list = "- No clear chart patterns identified at this time\n"
        
        section = f"""## 🧩 Pattern & Risk Lessons

**Patterns Identified:**
{pattern_list}

**Volatility Analysis:**
- **Level:** {volatility['volatility_level']}
- **ATR:** {volatility['atr_percentage']:.2f}% of price
- **Implication:** {"Wider stops needed" if volatility['volatility_level'] == 'HIGH' else "Standard stops acceptable"}

**Volume Insight:**
- {technical_analysis['volume_analysis']['signals'][0] if technical_analysis['volume_analysis']['signals'] else 'Normal volume activity'}

**Stop Discipline:**
- Critical level: Where the technical story changes
- Don't move stops to "give it more room"
- Honor your exit strategy"""
        
        return section
    
    def _build_technical_details(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> str:
        """Build technical indicators details"""
        
        indicators = data_package['indicators']
        
        # Moving Averages
        ma = indicators.get('moving_averages', {})
        ma_text = f"""**Moving Averages:**
- SMA 20: ₹{ma.get('SMA_20', 0):.2f}
- SMA 50: ₹{ma.get('SMA_50', 0):.2f}
- SMA 200: ₹{ma.get('SMA_200', 0):.2f}
- Price vs SMA 50: {ma.get('price_vs_SMA50', 0):.2f}%"""
        
        # Momentum
        rsi = indicators.get('rsi', {})
        macd = indicators.get('macd', {})
        momentum_text = f"""**Momentum:**
- RSI: {rsi.get('value', 0):.1f} ({rsi.get('condition', 'NEUTRAL')})
- MACD: {macd.get('signal', 'NEUTRAL')}"""
        
        # Trend
        st = indicators.get('supertrend', {})
        adx = indicators.get('adx', {})
        trend_text = f"""**Trend:**
- SuperTrend: {st.get('signal', 'N/A')} at ₹{st.get('value', 0):.2f}
- ADX: {adx.get('value', 0):.1f} ({adx.get('strength', 'WEAK')} trend)"""
        
        return f"""{ma_text}

{momentum_text}

{trend_text}"""
    
    def _generate_key_takeaway(
        self,
        technical_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> str:
        """Generate key takeaway message"""
        
        bias = technical_analysis['overall_bias']
        strength = technical_analysis['strength_score']
        
        if 'STRONG BULLISH' in bias and strength > 70:
            return "**Strong bullish setup** with high conviction. Consider entering on any minor pullback to support levels. The technical stars are aligned, but always honor your stop loss."
        elif 'BULLISH' in bias:
            return "**Bullish bias present** but watch for confirmation. Don't chase - wait for better entry on dips. Patience will be rewarded with better risk/reward."
        elif 'STRONG BEARISH' in bias and strength > 70:
            return "**Strong bearish setup** suggests caution. If you must trade, use tight stops and smaller position sizes. Consider sitting this one out."
        elif 'BEARISH' in bias:
            return "**Bearish undertone** - wait for clearer setup. Sometimes the best trade is no trade. Capital preservation is key."
        else:
            return "**Neutral/choppy market** - low conviction setup. Wait for better clarity. Use smaller positions if you must trade, and keep stops extra tight."
    
    def _get_optimal_trade(self, scenarios: list) -> str:
        """Determine optimal trade from scenarios"""
        
        if not scenarios:
            return "Wait for clearer setup"
        
        # Find highest R:R with moderate+ confidence
        best_scenario = max(
            scenarios,
            key=lambda s: s.get('rr_ratio', 0) if s.get('confidence', 'Low') != 'Low' else 0
        )
        
        return f"{best_scenario.get('scenario', 'N/A')} (R:R: {best_scenario.get('rr_ratio', 0):.2f})"
    
    def _extract_summary(self, markdown: str) -> str:
        """Extract summary from markdown report"""
        lines = markdown.split('\n')
        
        # Find summary section
        in_summary = False
        summary_lines = []
        
        for line in lines:
            if '## Summary' in line:
                in_summary = True
                continue
            elif line.startswith('##') and in_summary:
                break
            elif in_summary and line.strip():
                summary_lines.append(line.strip())
        
        return ' '.join(summary_lines[:3])  # First 3 sentences
    
    def _extract_recommendation(self, risk_analysis: Dict[str, Any]) -> str:
        """Extract main recommendation"""
        scenarios = risk_analysis['scenarios']
        
        if not scenarios:
            return "WAIT - No clear setup"
        
        # Find best scenario
        best = max(scenarios, key=lambda s: s.get('rr_ratio', 0))
        
        if best.get('confidence') == 'High' and best.get('rr_ratio', 0) > 1.5:
            return f"BUY - {best.get('scenario', 'N/A')}"
        elif best.get('rr_ratio', 0) > 1.0:
            return f"WATCH - {best.get('scenario', 'N/A')}"
        else:
            return "WAIT - Low R:R ratios"
    
    def _fallback_narrative(self, prompt: str) -> str:
        """Fallback narrative when LLM fails"""
        return "Technical analysis shows mixed signals. Monitor key support and resistance levels for clearer direction. Exercise caution and proper risk management."
    
    def _fallback_report(
        self,
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback report when synthesis fails"""
        
        narrative = self._fallback_narrative("")
        
        markdown = self._build_markdown_report(
            data_package,
            technical_analysis,
            pattern_analysis,
            risk_analysis,
            narrative
        )
        
        return {
            'markdown': markdown,
            'summary': "Technical analysis complete with basic insights.",
            'recommendation': self._extract_recommendation(risk_analysis),
            'generated_at': datetime.now().isoformat(),
            'fallback_used': True
        }


# Test function
if __name__ == "__main__":
    print("="*80)
    print("Testing Agent 5: Report Writer")
    print("="*80)
    
    # Get data from all previous agents
    from agent_1_orchestrator import DataOrchestrator
    from agent_2_technical_analyst import TechnicalAnalyst
    from agent_3_vision_recognition import VisionPatternRecognition
    from agent_4_risk_analyst import RiskScenarioAnalyst
    
    orchestrator = DataOrchestrator()
    data_package = orchestrator.orchestrate('RELIANCE', '1d')
    
    if data_package['status'] == 'success':
        analyst = TechnicalAnalyst()
        technical_analysis = analyst.analyze(data_package)
        
        vision = VisionPatternRecognition()
        pattern_analysis = vision.analyze_chart(data_package, technical_analysis)
        
        risk_analyst = RiskScenarioAnalyst()
        risk_analysis = risk_analyst.analyze(
            data_package,
            technical_analysis,
            pattern_analysis
        )
        
        # Generate report
        writer = ReportWriter()
        report = writer.generate_report(
            data_package,
            technical_analysis,
            pattern_analysis,
            risk_analysis
        )
        
        print("\n✅ Report Generated!")
        print(f"\nWord Count: {report['word_count']}")
        print(f"Recommendation: {report['recommendation']}")
        
        print("\n" + "="*80)
        print("MARKDOWN REPORT:")
        print("="*80)
        print(report['markdown'])
    
    print("\n" + "="*80)