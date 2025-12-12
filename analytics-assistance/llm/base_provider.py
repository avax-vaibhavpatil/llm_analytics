"""
Base Provider - Abstract Interface for All LLM Providers

This is the CONTRACT that all LLM providers must follow.
Every provider (OpenAI, Bedrock, Groq, etc.) must implement these methods.

Why?
- Consistent interface across all providers
- Easy to switch providers without changing code
- Forces all providers to support required features

Design Pattern: Abstract Base Class (ABC)
- Python's way of creating interfaces
- Subclasses MUST implement abstract methods
- Cannot instantiate base class directly
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class BaseProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    All providers (OpenAI, Bedrock, Groq, etc.) must:
    1. Extend this class
    2. Implement all @abstractmethod methods
    3. Follow the same method signatures
    
    This ensures:
    - Any provider can replace another
    - Code using providers doesn't need to change
    - New providers are easy to add
    
    Example:
        # Define a provider
        class MyProvider(BaseProvider):
            def generate(self, prompt, **kwargs):
                return "response"
        
        # Use it
        llm = MyProvider(model="my-model")
        response = llm.generate("hello")
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ):
        """
        Initialize provider with common parameters.
        
        Args:
            model: Model name/ID (provider-specific)
            api_key: API key for authentication (optional, can use env var)
            temperature: Sampling temperature (0.0 = focused, 1.0 = creative)
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters
        
        Example:
            provider = OpenAIProvider(
                model="gpt-4",
                temperature=0.2,
                max_tokens=1000
            )
        """
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_params = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion from prompt.
        
        This is the MAIN method every provider must implement.
        Takes a prompt, returns generated text.
        
        Args:
            prompt: Input text prompt
            **kwargs: Additional generation parameters (optional)
        
        Returns:
            Generated text as string
        
        Raises:
            Exception: If generation fails
        
        Example:
            response = llm.generate("What is Python?")
            print(response)  # "Python is a programming language..."
        
        Note:
            Subclasses MUST implement this method.
            It's the core functionality of every LLM provider.
        """
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs):
        """
        Generate text with streaming (yields tokens as they arrive).
        
        Like generate() but returns chunks in real-time.
        Useful for chat interfaces to show typing effect.
        
        Args:
            prompt: Input text prompt
            **kwargs: Additional generation parameters
        
        Yields:
            String chunks as they're generated
        
        Example:
            for chunk in llm.generate_stream("Tell me a story"):
                print(chunk, end="", flush=True)
        
        Note:
            Not all providers support streaming.
            Can return NotImplementedError if unavailable.
        """
        pass
    
    def embed(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings for text (optional).
        
        Converts text into vector representation.
        Used for semantic search, similarity, etc.
        
        Args:
            text: Input text to embed
            **kwargs: Additional embedding parameters
        
        Returns:
            List of floats (embedding vector)
        
        Example:
            embedding = llm.embed("Hello world")
            print(len(embedding))  # 1536 (for OpenAI ada-002)
        
        Note:
            Optional - not all providers need to implement
            Default implementation raises NotImplementedError
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support embeddings"
        )
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name as string
        
        Example:
            print(llm.get_provider_name())  # "OpenAI"
        """
        return self.__class__.__name__.replace("Provider", "")
    
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Checks if provider is properly configured:
        - API key set
        - Model name valid
        - Required parameters present
        
        Returns:
            True if valid, False otherwise
        
        Example:
            if llm.validate_config():
                response = llm.generate(prompt)
            else:
                print("Provider not configured!")
        """
        if not self.model:
            return False
        return True
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current provider configuration.
        
        Returns:
            Dictionary of current settings
        
        Example:
            config = llm.get_config()
            print(config["model"])      # "gpt-4"
            print(config["temperature"]) # 0.7
        """
        return {
            "provider": self.get_provider_name(),
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"{self.get_provider_name()}Provider("
            f"model='{self.model}', "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens})"
        )


# ══════════════════════════════════════════════════════════════════
# EXPLANATION - Why Abstract Base Class?
# ══════════════════════════════════════════════════════════════════

"""
🎓 LEARNING: Abstract Base Class (ABC)

1. What is it?
   - A class that cannot be instantiated directly
   - Defines a CONTRACT that subclasses must follow
   - Forces subclasses to implement certain methods

2. Why use it?
   # Without ABC (BAD):
   class BaseProvider:
       def generate(self, prompt):
           pass  # Subclass forgets to implement this!
   
   # With ABC (GOOD):
   from abc import ABC, abstractmethod
   
   class BaseProvider(ABC):
       @abstractmethod
       def generate(self, prompt):
           pass  # Python FORCES subclass to implement!
   
   # If you forget to implement:
   class MyProvider(BaseProvider):
       pass  # ERROR: Can't instantiate - missing generate()

3. Real-world analogy:
   - Interface: "All vehicles must have start() and stop()"
   - Implementations: Car, Bike, Plane all implement these
   - Guarantee: Any vehicle can be used the same way

4. Benefits:
   ✅ Type safety - Python checks implementations
   ✅ Documentation - Clear what methods are required
   ✅ Consistency - All providers work the same
   ✅ Swappability - Easy to switch providers

🎯 In our case:
   - BaseProvider = Contract
   - OpenAIProvider, GroqProvider, etc. = Implementations
   - All must implement: generate(), generate_stream()
   - Result: Switch providers with zero code changes!
"""

