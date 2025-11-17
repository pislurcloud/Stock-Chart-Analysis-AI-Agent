"""
LLM Configuration Manager
Handles flexible LLM provider configuration (OpenRouter, OpenAI, Anthropic)
Allows easy switching between models
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    """Manages LLM configuration for different agents"""
    
    # Model cost per 1M tokens (approximate)
    MODEL_COSTS = {
        # Free models
        'meta-llama/llama-4-maverick:free': {'input': 0.0, 'output': 0.0},
        
        # OpenAI models
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
        
        # Anthropic models (via OpenRouter or direct)
        'anthropic/claude-sonnet-4': {'input': 3.00, 'output': 15.00},
        'anthropic/claude-opus-4': {'input': 15.00, 'output': 75.00},
        'claude-sonnet-4-20250514': {'input': 3.00, 'output': 15.00},
        'claude-opus-4-20250514': {'input': 15.00, 'output': 75.00},
        
        # Other models
        'moonshotai/kimi-vl-a3b-thinking': {'input': 0.50, 'output': 2.00},
    }
    
    @staticmethod
    def get_agent_config(agent_name: str) -> Dict[str, Any]:
        """
        Get LLM configuration for a specific agent
        
        Args:
            agent_name: 'vision', 'risk', or 'report'
        
        Returns:
            Dict with model, provider, and API key
        """
        config_map = {
            'vision': {
                'model': os.getenv('VISION_MODEL', 'meta-llama/llama-4-maverick:free'),
                'provider': os.getenv('VISION_PROVIDER', 'openrouter'),
            },
            'risk': {
                'model': os.getenv('RISK_MODEL', 'gpt-4o-mini'),
                'provider': os.getenv('RISK_PROVIDER', 'openai'),
            },
            'report': {
                'model': os.getenv('REPORT_MODEL', 'moonshotai/kimi-vl-a3b-thinking'),
                'provider': os.getenv('REPORT_PROVIDER', 'openrouter'),
            }
        }
        
        if agent_name not in config_map:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        config = config_map[agent_name]
        
        # Add API key based on provider
        if config['provider'] == 'openrouter':
            config['api_key'] = os.getenv('OPENROUTER_API_KEY')
            config['base_url'] = 'https://openrouter.ai/api/v1'
        elif config['provider'] == 'openai':
            config['api_key'] = os.getenv('OPENAI_API_KEY')
            config['base_url'] = 'https://api.openai.com/v1'
        elif config['provider'] == 'anthropic':
            config['api_key'] = os.getenv('ANTHROPIC_API_KEY')
            config['base_url'] = 'https://api.anthropic.com/v1'
        else:
            raise ValueError(f"Unknown provider: {config['provider']}")
        
        return config
    
    @staticmethod
    def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a model call
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Estimated cost in USD
        """
        if model not in LLMConfig.MODEL_COSTS:
            return 0.0  # Unknown model, assume free or use default
        
        costs = LLMConfig.MODEL_COSTS[model]
        input_cost = (input_tokens / 1_000_000) * costs['input']
        output_cost = (output_tokens / 1_000_000) * costs['output']
        
        return input_cost + output_cost
    
    @staticmethod
    def get_llm_instance(agent_name: str):
        """
        Get configured LLM instance for an agent
        
        Args:
            agent_name: 'vision', 'risk', or 'report'
        
        Returns:
            Configured LLM instance (LangChain format)
        """
        from langchain_openai import ChatOpenAI
        
        config = LLMConfig.get_agent_config(agent_name)
        
        # All providers can use ChatOpenAI with custom base_url
        llm = ChatOpenAI(
            model=config['model'],
            openai_api_key=config['api_key'],
            openai_api_base=config['base_url'],
            temperature=0.7,
            max_tokens=4000,
        )
        
        return llm
    
    @staticmethod
    def validate_config() -> Dict[str, bool]:
        """
        Validate that all required API keys are present
        
        Returns:
            Dict with validation status for each provider
        """
        results = {}
        
        # Check which providers are being used
        vision_provider = os.getenv('VISION_PROVIDER', 'openrouter')
        risk_provider = os.getenv('RISK_PROVIDER', 'openai')
        report_provider = os.getenv('REPORT_PROVIDER', 'openrouter')
        
        providers_needed = {vision_provider, risk_provider, report_provider}
        
        # Validate each provider
        for provider in providers_needed:
            if provider == 'openrouter':
                results['openrouter'] = bool(os.getenv('OPENROUTER_API_KEY'))
            elif provider == 'openai':
                results['openai'] = bool(os.getenv('OPENAI_API_KEY'))
            elif provider == 'anthropic':
                results['anthropic'] = bool(os.getenv('ANTHROPIC_API_KEY'))
        
        return results
    
    @staticmethod
    def get_current_setup() -> Dict[str, Any]:
        """
        Get current model setup for all agents
        
        Returns:
            Dict showing which models are configured for each agent
        """
        return {
            'vision': {
                'model': os.getenv('VISION_MODEL', 'meta-llama/llama-4-maverick:free'),
                'provider': os.getenv('VISION_PROVIDER', 'openrouter'),
                'cost_per_1m_tokens': LLMConfig.MODEL_COSTS.get(
                    os.getenv('VISION_MODEL', 'meta-llama/llama-4-maverick:free'),
                    {'input': 0, 'output': 0}
                )
            },
            'risk': {
                'model': os.getenv('RISK_MODEL', 'gpt-4o-mini'),
                'provider': os.getenv('RISK_PROVIDER', 'openai'),
                'cost_per_1m_tokens': LLMConfig.MODEL_COSTS.get(
                    os.getenv('RISK_MODEL', 'gpt-4o-mini'),
                    {'input': 0, 'output': 0}
                )
            },
            'report': {
                'model': os.getenv('REPORT_MODEL', 'moonshotai/kimi-vl-a3b-thinking'),
                'provider': os.getenv('REPORT_PROVIDER', 'openrouter'),
                'cost_per_1m_tokens': LLMConfig.MODEL_COSTS.get(
                    os.getenv('REPORT_MODEL', 'moonshotai/kimi-vl-a3b-thinking'),
                    {'input': 0, 'output': 0}
                )
            }
        }


# Test function
if __name__ == "__main__":
    print("="*80)
    print("LLM Configuration Test")
    print("="*80)
    
    # Show current setup
    setup = LLMConfig.get_current_setup()
    print("\nCurrent Model Setup:")
    for agent, config in setup.items():
        print(f"\n{agent.upper()} Agent:")
        print(f"  Model: {config['model']}")
        print(f"  Provider: {config['provider']}")
        print(f"  Cost (per 1M tokens): Input ${config['cost_per_1m_tokens']['input']}, Output ${config['cost_per_1m_tokens']['output']}")
    
    # Validate configuration
    print("\n" + "="*80)
    print("API Key Validation:")
    validation = LLMConfig.validate_config()
    for provider, valid in validation.items():
        status = "✅" if valid else "❌"
        print(f"  {status} {provider.upper()}: {'Configured' if valid else 'Missing API key'}")
    
    print("\n" + "="*80)