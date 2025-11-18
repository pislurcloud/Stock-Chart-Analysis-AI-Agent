"""
Agents Module - Phase 2
All AI agents for stock analysis
"""
import sys
from pathlib import Path
#sys.path.append('/workspaces/Stock-Chart-Analysis-AI-Agent/backend/src/agents')
backend_dir = Path(__file__)
sys.path.insert(0, str(backend_dir))

#from .agent_1_orchestrator import DataOrchestrator
#from .agent_2_technical_analyst import TechnicalAnalyst
#from .agent_3_vision_recognition import VisionPatternRecognition
#from .agent_4_risk_analyst import RiskScenarioAnalyst
#from .agent_5_report_writer import ReportWriter

from agent_1_orchestrator import DataOrchestrator
from agent_2_technical_analyst import TechnicalAnalyst
from agent_3_vision_recognition import VisionPatternRecognition
from agent_4_risk_analyst import RiskScenarioAnalyst
from agent_5_report_writer import ReportWriter

__all__ = [
    'DataOrchestrator',
    'TechnicalAnalyst',
    'VisionPatternRecognition',
    'RiskScenarioAnalyst',
    'ReportWriter',
]