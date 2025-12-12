"""
Groq Provider - Implementation for Groq Models

Groq provides the fastest LLM inference in the world with generous free tier.

Supports:
- Llama 3.1 (70B, 8B)
- Mixtral 8x7B
- Gemma 2
- Chat completions with streaming
- FREE tier: 30 requests/min, 6000 requests/day

API Docs: https://console.groq.com/docs
Get API Key: https://console.groq.com/ (FREE!)
"""

import os
from typing import Optional, Iterator
from groq import Groq
from llm.base_provider import BaseProvider


class GroqProvider(BaseProvider):
    """
    Groq implementation of BaseProvider.
    
    Uses Groq's Chat Completions API for ultra-fast text generation.
    Supports open-source models like Llama 3.1 and Mixtral.
    
    Why Groq?
    - ✅ Completely FREE (30 req/min, 6000/day)
    - ✅ Super FAST (fastest inference)
    - ✅ Powerful models (Llama 3.1 70B)
    - ✅ Same interface as OpenAI
    
    Example:
        # Basic usage
        llm = GroqProvider(model="llama-3.1-70b-versatile")
        response = llm.generate("What is Python?")
        
        # With custom settings
        llm = GroqProvider(
            model="mixtral-8x7b-32768",
            temperature=0.2,
            max_tokens=1000
        )
        
        # Streaming
        for chunk in llm.generate_stream("Tell me a story"):
            print(chunk, end="", flush=True)
    """
    
    # Available models (as of Dec 2024 - updated)
    AVAILABLE_MODELS = [
        "llama-3.3-70b-versatile",  # Best general purpose (NEW)
        "llama-3.1-8b-instant",     # Fastest
        "mixtral-8x7b-32768",       # Great for code
        "gemma2-9b-it",             # Google's Gemma
    ]
    
    def __init__(
        self,
        model: str = "llama-3.1-70b-versatile",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ):
        """
        Initialize Groq provider.
        
        Args:
            model: Groq model name (default: llama-3.1-70b-versatile)
            api_key: Groq API key (if None, reads from GROQ_API_KEY env var)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional Groq-specific parameters
        
        Raises:
            ValueError: If API key not found
        
        Example:
            # From environment variable
            llm = GroqProvider(model="llama-3.1-70b-versatile")
            
            # Explicit API key
            llm = GroqProvider(
                model="mixtral-8x7b-32768",
                api_key="gsk_..."
            )
        
        Note:
            Get free API key at: https://console.groq.com/
        """
        # Call parent constructor
        super().__init__(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. "
                "Set GROQ_API_KEY environment variable or pass api_key parameter. "
                "Get free key at: https://console.groq.com/"
            )
        
        # Initialize Groq client
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Groq client: {e}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion using Groq.
        
        This is the MAIN method - implements BaseProvider's abstract method.
        
        Args:
            prompt: Input text prompt
            **kwargs: Optional overrides for temperature, max_tokens, etc.
        
        Returns:
            Generated text as string
        
        Raises:
            Exception: If API call fails
        
        Example:
            llm = GroqProvider(model="llama-3.1-70b-versatile")
            
            # Basic
            response = llm.generate("What is AI?")
            
            # With overrides
            response = llm.generate(
                "Explain quantum computing",
                temperature=0.0,
                max_tokens=1000
            )
        
        Performance:
            Groq is typically 10-20x faster than OpenAI!
        """
        try:
            # Merge instance settings with call-time overrides
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            # Call Groq API
            # NOTE: API is similar to OpenAI but uses Groq client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **{k: v for k, v in kwargs.items() 
                   if k not in ['temperature', 'max_tokens']}
            )
            
            # Extract and return text
            # Same structure as OpenAI!
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Groq API error: {str(e)}"
            
            # Check for common errors
            error_str = str(e).lower()
            if "rate_limit" in error_str or "429" in error_str:
                error_message = (
                    "Groq rate limit exceeded (30 req/min or 6000/day). "
                    "Please wait a moment."
                )
            elif "invalid" in error_str and "key" in error_str:
                error_message = (
                    "Invalid Groq API key. "
                    "Get a free key at: https://console.groq.com/"
                )
            elif "model" in error_str and "not found" in error_str:
                available = ", ".join(self.AVAILABLE_MODELS)
                error_message = (
                    f"Model '{self.model}' not found. "
                    f"Available models: {available}"
                )
            
            raise Exception(error_message) from e
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate text with streaming (yields chunks as they arrive).
        
        Groq's streaming is EXTREMELY fast - you'll see tokens almost instantly!
        
        Args:
            prompt: Input text prompt
            **kwargs: Optional overrides for parameters
        
        Yields:
            String chunks as they're generated
        
        Example:
            llm = GroqProvider(model="llama-3.1-70b-versatile")
            
            # Stream response (very fast!)
            print("Response: ", end="")
            for chunk in llm.generate_stream("Tell me a joke"):
                print(chunk, end="", flush=True)
            print()  # New line at end
        
        Note:
            Groq streaming is significantly faster than OpenAI.
            You'll see the difference immediately!
        """
        try:
            # Merge settings
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            # Call Groq API with stream=True
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,  # Enable streaming
                **{k: v for k, v in kwargs.items() 
                   if k not in ['temperature', 'max_tokens']}
            )
            
            # Yield chunks as they arrive (very fast!)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            error_message = f"Groq streaming error: {str(e)}"
            raise Exception(error_message) from e
    
    def embed(self, text: str, **kwargs) -> list[float]:
        """
        Generate embeddings (NOT SUPPORTED by Groq).
        
        Groq currently doesn't provide embedding models.
        Use OpenAI or other providers for embeddings.
        
        Raises:
            NotImplementedError: Always (Groq doesn't support embeddings)
        
        Example:
            llm = GroqProvider(model="llama-3.1-70b-versatile")
            
            try:
                embedding = llm.embed("test")
            except NotImplementedError:
                print("Groq doesn't support embeddings")
                # Use OpenAI for embeddings instead
        """
        raise NotImplementedError(
            "Groq does not support embeddings. "
            "Use OpenAI's embed() method for embeddings."
        )
    
    def validate_config(self) -> bool:
        """
        Validate Groq provider configuration.
        
        Checks:
        - API key is set
        - Model name is valid
        - Model is in available models list
        
        Returns:
            True if valid, False otherwise
        
        Example:
            llm = GroqProvider(model="llama-3.1-70b-versatile")
            
            if llm.validate_config():
                response = llm.generate("test")
            else:
                print("Invalid configuration!")
        """
        # Check basic config
        if not super().validate_config():
            return False
        
        # Check API key
        if not self.api_key:
            return False
        
        # Check if model is in available models
        # (This is informational - Groq will reject if invalid)
        if self.model not in self.AVAILABLE_MODELS:
            print(f"Warning: '{self.model}' not in known models list")
            print(f"Available: {', '.join(self.AVAILABLE_MODELS)}")
        
        return True
    
    @classmethod
    def list_models(cls) -> list[str]:
        """
        List available Groq models.
        
        Returns:
            List of model names
        
        Example:
            models = GroqProvider.list_models()
            for model in models:
                print(f"- {model}")
        """
        return cls.AVAILABLE_MODELS.copy()


# ══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ══════════════════════════════════════════════════════════════════

"""
Example 1: Basic usage (FASTEST!)

    from llm.providers.groq_provider import GroqProvider
    
    llm = GroqProvider(model="llama-3.1-70b-versatile")
    response = llm.generate("What is Python?")
    print(response)
    # Response arrives in ~1 second (vs 3-5 sec with OpenAI)

Example 2: With custom settings

    llm = GroqProvider(
        model="mixtral-8x7b-32768",
        temperature=0.2,
        max_tokens=1000
    )
    response = llm.generate("Explain quantum physics")

Example 3: Streaming (VERY FAST!)

    llm = GroqProvider(model="llama-3.1-70b-versatile")
    
    for chunk in llm.generate_stream("Tell me a story"):
        print(chunk, end="", flush=True)
    # Tokens appear almost instantly!

Example 4: List available models

    models = GroqProvider.list_models()
    print("Available Groq models:")
    for model in models:
        print(f"  - {model}")

Example 5: Switch between models

    # Use fast model for quick responses
    fast = GroqProvider(model="llama-3.1-8b-instant")
    quick_answer = fast.generate("Quick question")
    
    # Use powerful model for complex tasks
    powerful = GroqProvider(model="llama-3.1-70b-versatile")
    detailed_answer = powerful.generate("Complex question")

Example 6: Error handling

    try:
        llm = GroqProvider(model="llama-3.1-70b-versatile")
        response = llm.generate("test")
    except Exception as e:
        print(f"Error: {e}")
        # User-friendly error messages!

Example 7: Compare with OpenAI

    # SAME INTERFACE - just swap the provider!
    from llm.providers.openai_provider import OpenAIProvider
    from llm.providers.groq_provider import GroqProvider
    
    # OpenAI
    openai_llm = OpenAIProvider(model="gpt-4o-mini")
    openai_response = openai_llm.generate("test")
    
    # Groq (same method!)
    groq_llm = GroqProvider(model="llama-3.1-70b-versatile")
    groq_response = groq_llm.generate("test")
    
    # Code using llm.generate() works with BOTH!

Key Differences from OpenAI:
1. ✅ FREE (no credit card needed)
2. ✅ FASTER (10-20x faster)
3. ✅ Different models (Llama, Mixtral vs GPT)
4. ❌ No embeddings (use OpenAI for that)
5. ✅ Same interface (fully compatible!)
"""

