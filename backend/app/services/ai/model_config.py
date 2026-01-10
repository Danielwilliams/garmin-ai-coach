"""AI Model Configuration System - Exact replica of CLI model management.

This replicates the CLI's sophisticated model selection and configuration system
with support for multiple AI providers and automatic fallback mechanisms.
"""

import os
from enum import Enum
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from pydantic import BaseModel


class AIMode(str, Enum):
    """AI mode settings that control model selection and behavior."""
    
    DEVELOPMENT = "development"
    STANDARD = "standard" 
    COST_EFFECTIVE = "cost_effective"


class ModelProvider(str, Enum):
    """Supported AI model providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"  # Fallback provider


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    
    name: str
    provider: ModelProvider
    model_id: str
    max_tokens: int
    temperature: float
    supports_tools: bool
    supports_structured_output: bool
    cost_per_1k_tokens: float
    context_length: int
    
    
class ModelRegistry:
    """Registry of available AI models - exact CLI configuration."""
    
    MODELS = {
        # === CLAUDE MODELS ===
        "claude-4": ModelConfig(
            name="claude-4",
            provider=ModelProvider.ANTHROPIC,
            model_id="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True,
            cost_per_1k_tokens=0.015,
            context_length=200000
        ),
        
        "claude-3-sonnet": ModelConfig(
            name="claude-3-sonnet", 
            provider=ModelProvider.ANTHROPIC,
            model_id="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True,
            cost_per_1k_tokens=0.003,
            context_length=200000
        ),
        
        "claude-3-haiku": ModelConfig(
            name="claude-3-haiku",
            provider=ModelProvider.ANTHROPIC, 
            model_id="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True,
            cost_per_1k_tokens=0.00025,
            context_length=200000
        ),
        
        # === OPENAI MODELS ===
        "gpt-5": ModelConfig(
            name="gpt-5",
            provider=ModelProvider.OPENAI,
            model_id="gpt-5.1",
            max_tokens=16384,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True,
            cost_per_1k_tokens=0.06,
            context_length=128000
        ),
        
        "gpt-4o": ModelConfig(
            name="gpt-4o",
            provider=ModelProvider.OPENAI,
            model_id="gpt-4o",
            max_tokens=16384,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True, 
            cost_per_1k_tokens=0.005,
            context_length=128000
        ),
        
        "gpt-4o-mini": ModelConfig(
            name="gpt-4o-mini",
            provider=ModelProvider.OPENAI,
            model_id="gpt-4o-mini",
            max_tokens=16384,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True,
            cost_per_1k_tokens=0.00015,
            context_length=128000
        ),
        
        # === DEEPSEEK MODELS ===
        "deepseek-v3": ModelConfig(
            name="deepseek-v3",
            provider=ModelProvider.DEEPSEEK,
            model_id="deepseek-chat",
            max_tokens=8192,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True,
            cost_per_1k_tokens=0.0002,
            context_length=64000
        ),
        
        # === GEMINI MODELS ===
        "gemini-pro": ModelConfig(
            name="gemini-pro",
            provider=ModelProvider.GEMINI,
            model_id="gemini-1.5-pro-latest",
            max_tokens=8192,
            temperature=0.3,
            supports_tools=True,
            supports_structured_output=True,
            cost_per_1k_tokens=0.00125,
            context_length=1048576
        )
    }


class AISettings:
    """AI settings and model assignment for different agent roles."""
    
    # === MODE-BASED MODEL ASSIGNMENTS ===
    MODE_ASSIGNMENTS = {
        AIMode.DEVELOPMENT: {
            "primary_model": "claude-4",
            "fallback_model": "claude-3-sonnet",
            "cost_effective_model": "claude-3-haiku"
        },
        AIMode.STANDARD: {
            "primary_model": "gpt-5",
            "fallback_model": "gpt-4o", 
            "cost_effective_model": "gpt-4o-mini"
        },
        AIMode.COST_EFFECTIVE: {
            "primary_model": "claude-3-haiku",
            "fallback_model": "gpt-4o-mini",
            "cost_effective_model": "deepseek-v3"
        }
    }
    
    # === AGENT ROLE ASSIGNMENTS ===
    AGENT_MODEL_PREFERENCES = {
        # Data summarization agents - fast, cost-effective
        "metrics_summarizer": "cost_effective_model",
        "physiology_summarizer": "cost_effective_model", 
        "activity_summarizer": "cost_effective_model",
        
        # Expert analysis agents - high quality
        "metrics_expert": "primary_model",
        "physiology_expert": "primary_model",
        "activity_expert": "primary_model",
        
        # Synthesis and formatting - high quality
        "synthesis": "primary_model",
        "formatter": "fallback_model",
        
        # Planning agents - high quality
        "season_planner": "primary_model",
        "weekly_planner": "primary_model",
        "plan_formatter": "fallback_model",
        
        # Orchestration
        "orchestrator": "primary_model",
        "plot_resolution": "fallback_model"
    }


class ModelManager:
    """Manages model selection and API client creation."""
    
    def __init__(self, ai_mode: AIMode = AIMode.DEVELOPMENT):
        self.ai_mode = ai_mode
        self.model_assignments = AISettings.MODE_ASSIGNMENTS[ai_mode]
        self._validate_api_keys()
    
    def _validate_api_keys(self) -> None:
        """Validate that required API keys are available."""
        
        required_keys = {
            ModelProvider.OPENAI: "OPENAI_API_KEY",
            ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            ModelProvider.DEEPSEEK: "DEEPSEEK_API_KEY", 
            ModelProvider.GEMINI: "GOOGLE_API_KEY"
        }
        
        self.available_providers = []
        
        for provider, key_name in required_keys.items():
            if os.getenv(key_name):
                self.available_providers.append(provider)
        
        # Always have OpenRouter as fallback
        if os.getenv("OPENROUTER_API_KEY"):
            self.available_providers.append(ModelProvider.OPENROUTER)
    
    def get_model_for_agent(self, agent_role: str) -> ModelConfig:
        """Get the appropriate model for a specific agent role."""
        
        # Get model preference for this agent
        preference = AISettings.AGENT_MODEL_PREFERENCES.get(agent_role, "primary_model")
        model_name = self.model_assignments[preference]
        
        # Get model config
        model_config = ModelRegistry.MODELS.get(model_name)
        
        if not model_config:
            raise ValueError(f"Model {model_name} not found in registry")
        
        # Check if provider is available
        if model_config.provider not in self.available_providers:
            # Try fallback
            fallback_name = self.model_assignments["fallback_model"]
            fallback_config = ModelRegistry.MODELS.get(fallback_name)
            
            if fallback_config and fallback_config.provider in self.available_providers:
                return fallback_config
            
            # Last resort - find any available model
            for config in ModelRegistry.MODELS.values():
                if config.provider in self.available_providers:
                    return config
            
            raise RuntimeError("No available AI providers configured")
        
        return model_config
    
    def create_client(self, model_config: ModelConfig) -> Any:
        """Create appropriate client for the model provider."""
        
        if model_config.provider == ModelProvider.OPENAI:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_config.model_id,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        
        elif model_config.provider == ModelProvider.ANTHROPIC:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=model_config.model_id,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        
        elif model_config.provider == ModelProvider.DEEPSEEK:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_config.model_id,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
        
        elif model_config.provider == ModelProvider.GEMINI:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model_config.model_id,
                temperature=model_config.temperature,
                max_output_tokens=model_config.max_tokens,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        
        else:
            raise ValueError(f"Unsupported provider: {model_config.provider}")
    
    def get_agent_client(self, agent_role: str) -> Any:
        """Get configured client for specific agent role."""
        
        model_config = self.get_model_for_agent(agent_role)
        return self.create_client(model_config)
    
    def estimate_cost(self, agent_role: str, token_count: int) -> float:
        """Estimate cost for using specific agent with token count."""
        
        model_config = self.get_model_for_agent(agent_role)
        return (token_count / 1000) * model_config.cost_per_1k_tokens


# Global model manager instance
model_manager: Optional[ModelManager] = None


def initialize_model_manager(ai_mode: AIMode = AIMode.DEVELOPMENT) -> ModelManager:
    """Initialize global model manager."""
    
    global model_manager
    model_manager = ModelManager(ai_mode)
    return model_manager


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    
    global model_manager
    if model_manager is None:
        model_manager = ModelManager()
    return model_manager