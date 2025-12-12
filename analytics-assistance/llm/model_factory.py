"""
Model Factory - Centralized Provider Creation

This is the MAIN interface for creating LLM providers.
Instead of importing individual providers, just use:

    llm = ModelProvider("groq")
    
Or from config:

    llm = ModelProvider.from_config(config)

Design Pattern: Factory Pattern
- Centralizes object creation
- Hides implementation details
- Easy to add new providers
- Configuration-driven selection

Benefits:
- ✅ One line to create any provider
- ✅ Config-based provider switching
- ✅ Automatic validation
- ✅ Easy to extend
"""

import os
import yaml
from typing import Dict, Any, Optional, Type
from pathlib import Path

from llm.base_provider import BaseProvider
from llm.providers.openai_provider import OpenAIProvider
from llm.providers.groq_provider import GroqProvider


# ══════════════════════════════════════════════════════════════════
# PROVIDER REGISTRY
# ══════════════════════════════════════════════════════════════════

# This is the CENTRAL REGISTRY of all available providers
# To add a new provider:
# 1. Create provider class (extend BaseProvider)
# 2. Add it here
# 3. That's it! No other code changes needed.

PROVIDER_REGISTRY: Dict[str, Type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    # Add more providers here:
    # "anthropic": AnthropicProvider,
    # "bedrock": BedrockProvider,
    # "gemini": GeminiProvider,
    # "mistral": MistralProvider,
}


# ══════════════════════════════════════════════════════════════════
# DEFAULT CONFIGURATIONS
# ══════════════════════════════════════════════════════════════════

# Default settings for each provider
# Used when not specified in config or parameters

DEFAULT_CONFIGS = {
    "openai": {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 500,
    },
    "groq": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 500,
    },
}


# ══════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def ModelProvider(
    provider_name: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> BaseProvider:
    """
    Create an LLM provider by name.
    
    This is the MAIN function to create providers.
    Automatically loads the right provider class and initializes it.
    
    Args:
        provider_name: Provider name ("openai", "groq", etc.)
        model: Model name (optional, uses default if not provided)
        api_key: API key (optional, reads from env if not provided)
        temperature: Sampling temperature (optional, uses default)
        max_tokens: Max tokens in response (optional, uses default)
        **kwargs: Additional provider-specific parameters
    
    Returns:
        Initialized provider instance
    
    Raises:
        ValueError: If provider not found
        Exception: If provider initialization fails
    
    Examples:
        # Minimal - uses all defaults
        llm = ModelProvider("groq")
        
        # With custom model
        llm = ModelProvider("groq", model="mixtral-8x7b-32768")
        
        # With all settings
        llm = ModelProvider(
            "openai",
            model="gpt-4",
            temperature=0.2,
            max_tokens=1000
        )
        
        # Use in your code
        response = llm.generate("What is Python?")
    """
    
    # Normalize provider name
    provider_name = provider_name.lower().strip()
    
    # Check if provider exists
    if provider_name not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unknown provider: '{provider_name}'. "
            f"Available providers: {available}"
        )
    
    # Get provider class
    provider_class = PROVIDER_REGISTRY[provider_name]
    
    # Get default config for this provider
    default_config = DEFAULT_CONFIGS.get(provider_name, {})
    
    # Merge defaults with provided parameters
    # Priority: explicit params > env vars > defaults
    final_config = {
        "model": model or os.getenv(f"{provider_name.upper()}_MODEL") or default_config.get("model"),
        "api_key": api_key or os.getenv(f"{provider_name.upper()}_API_KEY"),
        "temperature": temperature if temperature is not None else default_config.get("temperature", 0.7),
        "max_tokens": max_tokens if max_tokens is not None else default_config.get("max_tokens", 500),
        **kwargs
    }
    
    # Initialize and return provider
    try:
        return provider_class(**final_config)
    except Exception as e:
        raise Exception(
            f"Failed to initialize {provider_name} provider: {str(e)}"
        ) from e


def ModelProvider_from_config(
    config: Dict[str, Any],
    provider_key: str = "provider"
) -> BaseProvider:
    """
    Create provider from configuration dictionary.
    
    Useful when loading from YAML/JSON config files.
    
    Args:
        config: Configuration dictionary
        provider_key: Key for provider name in config (default: "provider")
    
    Returns:
        Initialized provider instance
    
    Example Config Dict:
        {
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.2,
            "max_tokens": 1000
        }
    
    Usage:
        config = {
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.2
        }
        llm = ModelProvider_from_config(config)
        response = llm.generate("test")
    """
    
    if provider_key not in config:
        raise ValueError(
            f"Config missing '{provider_key}' key. "
            f"Config must specify which provider to use."
        )
    
    provider_name = config[provider_key]
    
    # Extract all other config parameters
    provider_config = {
        k: v for k, v in config.items() 
        if k != provider_key
    }
    
    return ModelProvider(provider_name, **provider_config)


def ModelProvider_from_yaml(
    yaml_path: str,
    section: str = "llm"
) -> BaseProvider:
    """
    Create provider from YAML configuration file.
    
    This is the PRODUCTION way to configure providers!
    Change provider in YAML, no code changes needed.
    
    Args:
        yaml_path: Path to YAML config file
        section: Section in YAML containing LLM config (default: "llm")
    
    Returns:
        Initialized provider instance
    
    Example YAML (config.yaml):
        llm:
          provider: groq
          model: llama-3.3-70b-versatile
          temperature: 0.2
          max_tokens: 1000
    
    Usage:
        # Read from config.yaml
        llm = ModelProvider_from_yaml("config.yaml")
        
        # Or specify section
        llm = ModelProvider_from_yaml("config.yaml", section="llm")
        
        # Switch provider: just change YAML!
        # llm:
        #   provider: openai  ← Change this line
        #   model: gpt-4
    """
    
    # Load YAML file
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    with open(yaml_path, 'r') as f:
        full_config = yaml.safe_load(f)
    
    # Extract LLM section
    if section not in full_config:
        raise ValueError(
            f"Config file missing '{section}' section. "
            f"Available sections: {list(full_config.keys())}"
        )
    
    llm_config = full_config[section]
    
    return ModelProvider_from_config(llm_config)


# ══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def list_providers() -> list[str]:
    """
    List all available providers.
    
    Returns:
        List of provider names
    
    Example:
        providers = list_providers()
        print(f"Available: {', '.join(providers)}")
    """
    return list(PROVIDER_REGISTRY.keys())


def get_provider_class(provider_name: str) -> Type[BaseProvider]:
    """
    Get provider class by name.
    
    Useful for advanced use cases where you need the class itself.
    
    Args:
        provider_name: Provider name
    
    Returns:
        Provider class
    
    Example:
        ProviderClass = get_provider_class("groq")
        llm = ProviderClass(model="llama-3.3-70b-versatile")
    """
    provider_name = provider_name.lower().strip()
    if provider_name not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unknown provider: '{provider_name}'. "
            f"Available: {available}"
        )
    return PROVIDER_REGISTRY[provider_name]


def register_provider(name: str, provider_class: Type[BaseProvider]) -> None:
    """
    Register a new provider at runtime.
    
    Useful for plugins or dynamically loaded providers.
    
    Args:
        name: Provider name
        provider_class: Provider class (must extend BaseProvider)
    
    Example:
        # Custom provider
        class MyProvider(BaseProvider):
            def generate(self, prompt):
                return "response"
        
        # Register it
        register_provider("myprovider", MyProvider)
        
        # Use it
        llm = ModelProvider("myprovider")
    """
    if not issubclass(provider_class, BaseProvider):
        raise ValueError(
            f"Provider must extend BaseProvider. "
            f"Got: {provider_class.__name__}"
        )
    
    PROVIDER_REGISTRY[name.lower()] = provider_class
    print(f"✅ Registered provider: {name}")


# ══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ══════════════════════════════════════════════════════════════════

"""
Example 1: Simple usage

    from llm.model_factory import ModelProvider
    
    llm = ModelProvider("groq")
    response = llm.generate("What is Python?")
    print(response)

Example 2: With custom settings

    llm = ModelProvider(
        "openai",
        model="gpt-4",
        temperature=0.2,
        max_tokens=1000
    )
    response = llm.generate("Explain quantum physics")

Example 3: From config dict

    config = {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.2
    }
    llm = ModelProvider_from_config(config)

Example 4: From YAML file (PRODUCTION)

    # config.yaml:
    # llm:
    #   provider: groq
    #   model: llama-3.3-70b-versatile
    #   temperature: 0.2
    
    llm = ModelProvider_from_yaml("config.yaml")
    response = llm.generate("test")
    
    # To switch providers: just edit YAML!
    # No code changes needed!

Example 5: List providers

    from llm.model_factory import list_providers
    
    providers = list_providers()
    print(f"Available: {', '.join(providers)}")
    # Output: Available: openai, groq

Example 6: Dynamic provider switching

    def get_llm(provider_name):
        return ModelProvider(provider_name)
    
    # Use different providers
    groq_llm = get_llm("groq")
    openai_llm = get_llm("openai")
    
    # Same interface!
    groq_response = groq_llm.generate("test")
    openai_response = openai_llm.generate("test")

Example 7: With error handling

    try:
        llm = ModelProvider("groq")
        response = llm.generate("test")
    except ValueError as e:
        print(f"Invalid config: {e}")
    except Exception as e:
        print(f"Error: {e}")

Key Benefits:
1. ✅ One line to create any provider
2. ✅ Config-driven (YAML/JSON)
3. ✅ Easy to switch providers
4. ✅ Automatic validation
5. ✅ Extensible (add providers to registry)
6. ✅ Production-ready
"""

