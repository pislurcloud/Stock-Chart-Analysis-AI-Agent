"""
Agent 3: Vision Pattern Recognition
Analyzes chart images using Vision LLM to identify patterns
Uses: llama-4-maverick:free (default) or Claude Sonnet 4 (configurable)
"""

import os
import sys
import base64
from pathlib import Path
from typing import Dict, Any, Optional
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


class VisionPatternRecognition:
    """
    Agent 3: Vision Pattern Recognition
    Analyzes chart images to identify visual patterns
    """
    
    def __init__(self):
        """Initialize with configured LLM"""
        self.config = LLMConfig.get_agent_config('vision')
        logger.info(f"Vision Agent initialized with {self.config['model']}")
    
    def analyze_chart(
        self, 
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze chart image for visual patterns
        
        Args:
            data_package: Output from Agent 1 (contains chart_path)
            technical_analysis: Output from Agent 2 (for context)
        
        Returns:
            Pattern recognition results
        """
        logger.info("Analyzing chart with Vision LLM...")
        
        chart_path = data_package.get('chart_path')
        if not chart_path or not os.path.exists(chart_path):
            return self._fallback_analysis(data_package, technical_analysis)
        
        try:
            # Encode chart image
            image_base64 = self._encode_image(chart_path)
            
            # Create prompt
            prompt = self._create_vision_prompt(data_package, technical_analysis)
            
            # Call Vision LLM
            response = self._call_vision_llm(prompt, image_base64)
            
            # Parse response
            patterns = self._parse_vision_response(response)
            
            logger.info(f"Vision analysis complete: {len(patterns.get('patterns', []))} patterns identified")
            
            return patterns
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {str(e)}")
            return self._fallback_analysis(data_package, technical_analysis)
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _create_vision_prompt(
        self, 
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> str:
        """Create detailed prompt for vision analysis"""
        
        metadata = data_package['metadata']
        latest_candle = data_package['latest_candle']
        bias = technical_analysis['overall_bias']
        
        prompt = f"""You are an expert technical analyst specializing in chart pattern recognition. 

Analyze this stock chart for **{metadata['company_name']} ({metadata['symbol']})** on {metadata['timeframe']} timeframe.

**Context:**
- Current Price: ₹{latest_candle['close']:.2f}
- Technical Bias: {bias}
- Latest Volume: {latest_candle['volume']:,}

**Your Task:**
Identify and describe the following with HIGH confidence levels:

1. **CHART PATTERNS** (if present):
   - Head & Shoulders / Inverse H&S
   - Triangles (ascending, descending, symmetrical)
   - Flags and Pennants
   - Wedges (rising, falling)
   - Double/Triple Tops/Bottoms
   - Cup & Handle
   - Rectangles/Channels

2. **CANDLESTICK PATTERNS** (last 5-10 candles):
   - Doji, Hammer, Shooting Star
   - Engulfing patterns (bullish/bearish)
   - Morning/Evening Stars
   - Harami patterns
   - Other significant patterns

3. **TREND STRUCTURE**:
   - Clear uptrend, downtrend, or sideways?
   - Higher highs/higher lows (bullish) or lower highs/lower lows (bearish)?
   - Trend strength and quality

4. **SUPPORT & RESISTANCE**:
   - Key horizontal levels visible on chart
   - Trend lines (support/resistance)
   - Are they holding or breaking?

5. **BREAKOUT/BREAKDOWN ZONES**:
   - Is price consolidating before a potential move?
   - Recent breakouts or breakdowns visible?
   - Volume confirmation?

6. **VOLUME PATTERNS**:
   - Volume increasing or decreasing?
   - Volume spikes on specific candles?
   - Volume confirmation of price moves?

7. **MARKET STRUCTURE**:
   - Overall: Bullish, Bearish, or Neutral?
   - Quality of the structure (clean vs choppy)
   - Momentum visible in price action?

**IMPORTANT:**
- Be SPECIFIC about what you see - don't be vague
- Assign CONFIDENCE levels: High (80-100%), Moderate (50-80%), Low (<50%)
- If you don't see a pattern clearly, say so - don't force it
- Focus on the most recent price action (right side of chart)
- Consider the larger context visible in the chart

**Output Format:**
For each pattern/observation, provide:
- Pattern name
- Description (what makes you identify it)
- Location (where on chart)
- Confidence level
- Bullish/Bearish implication

Be concise but thorough. Focus on actionable insights."""

        return prompt
    
    def _call_vision_llm(self, prompt: str, image_base64: str) -> str:
        """
        Call vision-capable LLM
        
        Args:
            prompt: Text prompt
            image_base64: Base64 encoded image
        
        Returns:
            LLM response text
        """
        try:
            if self.config['provider'] == 'openrouter':
                return self._call_openrouter_vision(prompt, image_base64)
            elif self.config['provider'] == 'anthropic':
                return self._call_anthropic_vision(prompt, image_base64)
            elif self.config['provider'] == 'openai':
                return self._call_openai_vision(prompt, image_base64)
            else:
                raise ValueError(f"Unknown provider: {self.config['provider']}")
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise
    
    def _call_openrouter_vision(self, prompt: str, image_base64: str) -> str:
        """Call OpenRouter API with vision"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config['model'],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
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
    
    def _call_anthropic_vision(self, prompt: str, image_base64: str) -> str:
        """Call Anthropic API with vision"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=self.config['api_key'])
        
        message = client.messages.create(
            model=self.config['model'],
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text
    
    def _call_openai_vision(self, prompt: str, image_base64: str) -> str:
        """Call OpenAI API with vision"""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.config['api_key'])
        
        response = client.chat.completions.create(
            model=self.config['model'],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _parse_vision_response(self, response: str) -> Dict[str, Any]:
        """
        Parse vision LLM response into structured format
        
        Args:
            response: Raw LLM text response
        
        Returns:
            Structured pattern analysis
        """
        # Extract patterns and structure the response
        # This is a simplified parser - can be enhanced
        
        return {
            'raw_analysis': response,
            'patterns': self._extract_patterns(response),
            'market_structure': self._extract_market_structure(response),
            'key_observations': self._extract_key_observations(response),
            'confidence': self._extract_overall_confidence(response)
        }
    
    def _extract_patterns(self, text: str) -> list:
        """Extract identified patterns from response"""
        patterns = []
        
        # Common pattern keywords
        pattern_keywords = [
            'head and shoulders', 'triangle', 'flag', 'pennant', 
            'wedge', 'double top', 'double bottom', 'cup and handle',
            'doji', 'hammer', 'engulfing', 'harami', 'shooting star',
            'morning star', 'evening star'
        ]
        
        text_lower = text.lower()
        
        for keyword in pattern_keywords:
            if keyword in text_lower:
                # Extract context around the pattern
                patterns.append({
                    'pattern': keyword.title(),
                    'mentioned': True
                })
        
        return patterns
    
    def _extract_market_structure(self, text: str) -> str:
        """Extract overall market structure assessment"""
        text_lower = text.lower()
        
        if 'bullish' in text_lower and 'bearish' not in text_lower:
            return "BULLISH"
        elif 'bearish' in text_lower and 'bullish' not in text_lower:
            return "BEARISH"
        elif 'neutral' in text_lower or 'sideways' in text_lower:
            return "NEUTRAL"
        else:
            return "MIXED"
    
    def _extract_key_observations(self, text: str) -> list:
        """Extract key observations from response"""
        # Split into sentences and take the most informative ones
        sentences = text.split('.')
        
        key_obs = []
        for sentence in sentences[:10]:  # First 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 30 and any(word in sentence.lower() for word in 
                ['pattern', 'trend', 'support', 'resistance', 'breakout', 'volume']):
                key_obs.append(sentence)
        
        return key_obs[:5]  # Top 5 observations
    
    def _extract_overall_confidence(self, text: str) -> str:
        """Extract overall confidence from response"""
        text_lower = text.lower()
        
        high_conf = text_lower.count('high confidence') + text_lower.count('strong')
        moderate_conf = text_lower.count('moderate') + text_lower.count('likely')
        low_conf = text_lower.count('low confidence') + text_lower.count('uncertain')
        
        if high_conf > moderate_conf and high_conf > low_conf:
            return "HIGH"
        elif low_conf > moderate_conf and low_conf > high_conf:
            return "LOW"
        else:
            return "MODERATE"
    
    def _fallback_analysis(
        self, 
        data_package: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback analysis when vision LLM fails
        Uses technical analysis to infer patterns
        """
        logger.warning("Using fallback pattern analysis")
        
        # Infer patterns from technical indicators
        bias = technical_analysis['overall_bias']
        trend = technical_analysis['trend_analysis']['trend']
        
        patterns = []
        
        if 'BULLISH' in bias:
            patterns.append({
                'pattern': 'Bullish Structure',
                'mentioned': True,
                'confidence': 'MODERATE'
            })
        elif 'BEARISH' in bias:
            patterns.append({
                'pattern': 'Bearish Structure',
                'mentioned': True,
                'confidence': 'MODERATE'
            })
        
        return {
            'raw_analysis': f"Fallback analysis: Market showing {bias} bias with {trend} trend.",
            'patterns': patterns,
            'market_structure': bias.split()[0] if bias else "NEUTRAL",
            'key_observations': [
                f"Technical bias: {bias}",
                f"Trend: {trend}",
                "Vision analysis unavailable - using indicator-based inference"
            ],
            'confidence': 'MODERATE',
            'fallback_used': True
        }


# Test function
if __name__ == "__main__":
    print("="*80)
    print("Testing Agent 3: Vision Pattern Recognition")
    print("="*80)
    
    # Check if API keys are configured
    validation = LLMConfig.validate_config()
    print("\nAPI Key Status:")
    for provider, valid in validation.items():
        status = "✅" if valid else "❌"
        print(f"  {status} {provider.upper()}")
    
    if not any(validation.values()):
        print("\n⚠️  No API keys configured - will use fallback analysis")
    
    # Get data from previous agents
    from agent_1_orchestrator import DataOrchestrator
    from agent_2_technical_analyst import TechnicalAnalyst
    
    orchestrator = DataOrchestrator()
    data_package = orchestrator.orchestrate('RELIANCE', '1d')
    
    if data_package['status'] == 'success':
        analyst = TechnicalAnalyst()
        technical_analysis = analyst.analyze(data_package)
        
        # Run vision analysis
        vision = VisionPatternRecognition()
        pattern_analysis = vision.analyze_chart(data_package, technical_analysis)
        
        print("\n✅ Vision Analysis Complete!")
        print(f"\nMarket Structure: {pattern_analysis['market_structure']}")
        print(f"Confidence: {pattern_analysis['confidence']}")
        
        if pattern_analysis.get('patterns'):
            print("\nPatterns Identified:")
            for pattern in pattern_analysis['patterns'][:5]:
                print(f"  • {pattern.get('pattern', 'Unknown')}")
        
        if pattern_analysis.get('key_observations'):
            print("\nKey Observations:")
            for obs in pattern_analysis['key_observations'][:3]:
                print(f"  • {obs}")
    
    print("\n" + "="*80)