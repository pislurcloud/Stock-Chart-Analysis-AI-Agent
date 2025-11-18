"""
CrewAI Orchestrator - Phase 2
Coordinates all 5 agents in sequential workflow
"""

import sys
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

# Add parent directory to path
backend_dir = Path(__file__)
sys.path.insert(0, str(backend_dir))
#sys.path.append('/workspaces/Stock-Chart-Analysis-AI-Agent/backend')

from src.agents.agent_1_orchestrator import DataOrchestrator
from src.agents.agent_2_technical_analyst import TechnicalAnalyst
from src.agents.agent_3_vision_recognition import VisionPatternRecognition
from src.agents.agent_4_risk_analyst import RiskScenarioAnalyst
from src.agents.agent_5_report_writer import ReportWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalysisCrew:
    """
    Main orchestrator for AI-powered analysis
    Runs all 5 agents in sequence
    """
    
    def __init__(self):
        """Initialize all agents"""
        logger.info("Initializing AI Analysis Crew...")
        
        self.agent_1 = DataOrchestrator()
        self.agent_2 = TechnicalAnalyst()
        self.agent_3 = VisionPatternRecognition()
        self.agent_4 = RiskScenarioAnalyst()
        self.agent_5 = ReportWriter()
        
        logger.info("All agents initialized successfully")
    
    def run_analysis(self, symbol: str, timeframe: str = '1d') -> Dict[str, Any]:
        """
        Run complete AI-powered analysis
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            timeframe: Timeframe (e.g., '1d', '1h', '15m')
        
        Returns:
            Complete analysis package with report
        """
        start_time = datetime.now()
        logger.info(f"Starting AI analysis for {symbol} {timeframe}")
        
        try:
            # Agent 1: Data Orchestration
            logger.info("Running Agent 1: Data Orchestrator...")
            data_package = self.agent_1.orchestrate(symbol, timeframe)
            
            if data_package['status'] != 'success':
                return {
                    'status': 'error',
                    'error': data_package.get('error', 'Data orchestration failed'),
                    'symbol': symbol,
                    'timeframe': timeframe
                }
            
            # Agent 2: Technical Analysis
            logger.info("Running Agent 2: Technical Analyst...")
            technical_analysis = self.agent_2.analyze(data_package)
            
            # Agent 3: Vision Pattern Recognition
            logger.info("Running Agent 3: Vision Pattern Recognition...")
            pattern_analysis = self.agent_3.analyze_chart(
                data_package,
                technical_analysis
            )
            
            # Agent 4: Risk & Scenario Analysis
            logger.info("Running Agent 4: Risk & Scenario Analyst...")
            risk_analysis = self.agent_4.analyze(
                data_package,
                technical_analysis,
                pattern_analysis
            )
            
            # Agent 5: Report Generation
            logger.info("Running Agent 5: Report Writer...")
            report = self.agent_5.generate_report(
                data_package,
                technical_analysis,
                pattern_analysis,
                risk_analysis
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Compile complete result
            result = {
                'status': 'success',
                'symbol': symbol,
                'timeframe': timeframe,
                'execution_time': execution_time,
                
                # Core data
                'stock_info': data_package['stock_info'],
                'latest_candle': data_package['latest_candle'],
                'chart_path': data_package['chart_path'],
                
                # Analysis outputs
                'technical_analysis': {
                    'overall_bias': technical_analysis['overall_bias'],
                    'strength_score': technical_analysis['strength_score'],
                    'trend': technical_analysis['trend_analysis']['trend'],
                    'momentum': technical_analysis['momentum_analysis']['momentum'],
                    'key_levels': technical_analysis['key_levels'],
                },
                
                'pattern_analysis': {
                    'market_structure': pattern_analysis['market_structure'],
                    'patterns': pattern_analysis['patterns'],
                    'confidence': pattern_analysis['confidence'],
                },
                
                'risk_analysis': {
                    'scenarios': risk_analysis['scenarios'],
                    'backtest': risk_analysis['backtest'],
                    'risk_metrics': risk_analysis['risk_metrics'],
                    'position_sizing': risk_analysis['position_sizing'],
                },
                
                # Final report
                'report': {
                    'markdown': report['markdown'],
                    'summary': report['summary'],
                    'recommendation': report['recommendation'],
                },
                
                # Metadata
                'generated_at': report['generated_at'],
                'agents_used': 5,
                'data_quality': data_package['data_quality'],
            }
            
            logger.info(f"Analysis complete in {execution_time:.2f}s")
            logger.info(f"Recommendation: {report['recommendation']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            import traceback
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'symbol': symbol,
                'timeframe': timeframe
            }
    
    def get_agent_status(self) -> Dict[str, bool]:
        """Check status of all agents"""
        return {
            'agent_1_orchestrator': self.agent_1 is not None,
            'agent_2_technical': self.agent_2 is not None,
            'agent_3_vision': self.agent_3 is not None,
            'agent_4_risk': self.agent_4 is not None,
            'agent_5_report': self.agent_5 is not None,
        }


# Test function
if __name__ == "__main__":
    print("="*80)
    print("Testing Complete AI Analysis Crew")
    print("="*80)
    
    crew = AIAnalysisCrew()
    
    # Check agent status
    status = crew.get_agent_status()
    print("\nAgent Status:")
    for agent, ready in status.items():
        icon = "✅" if ready else "❌"
        print(f"  {icon} {agent}")
    
    # Run full analysis
    print("\nRunning full analysis on RELIANCE...")
    result = crew.run_analysis('RELIANCE', '1d')
    
    if result['status'] == 'success':
        print("\n" + "="*80)
        print("✅ ANALYSIS SUCCESSFUL!")
        print("="*80)
        
        print(f"\nSymbol: {result['symbol']}")
        print(f"Execution Time: {result['execution_time']:.2f}s")
        print(f"Recommendation: {result['report']['recommendation']}")
        
        print(f"\nTechnical Bias: {result['technical_analysis']['overall_bias']}")
        print(f"Strength: {result['technical_analysis']['strength_score']}/100")
        
        print(f"\nScenarios Generated: {len(result['risk_analysis']['scenarios'])}")
        for scenario in result['risk_analysis']['scenarios']:
            print(f"  • {scenario['scenario']}: R:R = {scenario['rr_ratio']}")
        
        print(f"\nData Quality: {result['data_quality']['quality_score']}/100")
        
        print("\n" + "="*80)
        print("REPORT PREVIEW:")
        print("="*80)
        print(result['report']['markdown'][:500] + "...")
        
    else:
        print(f"\n❌ Analysis failed: {result['error']}")
    
    print("\n" + "="*80)