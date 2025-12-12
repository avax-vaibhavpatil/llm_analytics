"""
OpenAI Provider - Implementation for OpenAI Models

Supports:
- GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- Chat completions (generate)
- Streaming responses (generate_stream)
- Embeddings (embed)

API Docs: https://platform.openai.com/docs/api-reference
"""

import os
from typing import Optional, Iterator
from openai import OpenAI, OpenAIError
from llm.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    OpenAI implementation of BaseProvider.
    
    Uses OpenAI's Chat Completions API for text generation.
    Supports all GPT models including GPT-4 and GPT-3.5.
    
    Example:
        # Basic usage
        llm = OpenAIProvider(model="gpt-4o-mini")
        response = llm.generate("What is Python?")
        
        # With custom settings
        llm = OpenAIProvider(
            model="gpt-4",
            temperature=0.2,
            max_tokens=1000
        )
        
        # Streaming
        for chunk in llm.generate_stream("Tell me a story"):
            print(chunk, end="", flush=True)
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            model: OpenAI model name (default: gpt-4o-mini)
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional OpenAI-specific parameters
        
        Raises:
            ValueError: If API key not found
        
        Example:
            # From environment variable
            llm = OpenAIProvider(model="gpt-4o-mini")
            
            # Explicit API key
            llm = OpenAIProvider(
                model="gpt-4",
                api_key="sk-proj-..."
            )
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
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Initialize OpenAI client
        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion using OpenAI.
        
        This is the MAIN method - implements the abstract method from BaseProvider.
        
        Args:
            prompt: Input text prompt
            **kwargs: Optional overrides for temperature, max_tokens, etc.
        
        Returns:
            Generated text as string
        
        Raises:
            OpenAIError: If API call fails
            Exception: For other errors
        
        Example:
            llm = OpenAIProvider(model="gpt-4o-mini")
            
            # Basic
            response = llm.generate("What is AI?")
            
            # With overrides
            response = llm.generate(
                "Explain quantum computing",
                temperature=0.0,  # Override default
                max_tokens=1000
            )
        """
        try:
            # Merge instance settings with call-time overrides
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            # Call OpenAI API
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
            return response.choices[0].message.content.strip()
        
        except OpenAIError as e:
            # Handle OpenAI-specific errors
            error_message = f"OpenAI API error: {str(e)}"
            
            # Check for common errors
            if "rate_limit" in str(e).lower():
                error_message = "Rate limit exceeded. Please try again later."
            elif "invalid_api_key" in str(e).lower():
                error_message = "Invalid API key. Please check your credentials."
            elif "model_not_found" in str(e).lower():
                error_message = f"Model '{self.model}' not found or not accessible."
            
            raise Exception(error_message) from e
        
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}") from e
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate text with streaming (yields chunks as they arrive).
        
        Useful for chat interfaces to show real-time typing effect.
        
        Args:
            prompt: Input text prompt
            **kwargs: Optional overrides for parameters
        
        Yields:
            String chunks as they're generated
        
        Example:
            llm = OpenAIProvider(model="gpt-4o-mini")
            
            # Stream response
            print("Response: ", end="")
            for chunk in llm.generate_stream("Tell me a joke"):
                print(chunk, end="", flush=True)
            print()  # New line at end
        """
        try:
            # Merge settings
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            # Call OpenAI API with stream=True
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
            
            # Yield chunks as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except OpenAIError as e:
            error_message = f"OpenAI streaming error: {str(e)}"
            raise Exception(error_message) from e
        
        except Exception as e:
            raise Exception(f"Failed to stream response: {str(e)}") from e
    
    def embed(self, text: str, model: str = "text-embedding-ada-002", **kwargs) -> list[float]:
        """
        Generate embeddings for text using OpenAI.
        
        Converts text into vector representation for semantic search, 
        similarity comparisons, etc.
        
        Args:
            text: Input text to embed
            model: Embedding model name (default: ada-002)
            **kwargs: Additional parameters
        
        Returns:
            List of floats (embedding vector)
        
        Example:
            llm = OpenAIProvider(model="gpt-4o-mini")
            
            # Generate embedding
            embedding = llm.embed("Hello world")
            print(f"Dimensions: {len(embedding)}")  # 1536
            
            # Compare similarity
            emb1 = llm.embed("cat")
            emb2 = llm.embed("dog")
            # Calculate cosine similarity...
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text,
                **kwargs
            )
            
            return response.data[0].embedding
        
        except OpenAIError as e:
            error_message = f"OpenAI embedding error: {str(e)}"
            raise Exception(error_message) from e
        
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}") from e
    
    def validate_config(self) -> bool:
        """
        Validate OpenAI provider configuration.
        
        Checks:
        - API key is set
        - Model name is valid
        - Can connect to API
        
        Returns:
            True if valid, False otherwise
        
        Example:
            llm = OpenAIProvider(model="gpt-4o-mini")
            
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
        
        # Check model name format
        if not self.model or len(self.model) < 3:
            return False
        
        # Could add: Test API connection
        # try:
        #     self.client.models.retrieve(self.model)
        #     return True
        # except:
        #     return False
        
        return True


# ══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ══════════════════════════════════════════════════════════════════

"""
Example 1: Basic usage
    
    from llm.providers.openai_provider import OpenAIProvider
    
    llm = OpenAIProvider(model="gpt-4o-mini")
    response = llm.generate("What is Python?")
    print(response)

Example 2: With custom settings

    llm = OpenAIProvider(
        model="gpt-4",
        temperature=0.2,
        max_tokens=1000
    )
    response = llm.generate("Explain quantum physics")

Example 3: Streaming

    llm = OpenAIProvider(model="gpt-4o-mini")
    
    for chunk in llm.generate_stream("Tell me a story"):
        print(chunk, end="", flush=True)

Example 4: Error handling

    try:
        llm = OpenAIProvider(model="gpt-4o-mini")
        response = llm.generate("test")
    except Exception as e:
        print(f"Error: {e}")

Example 5: Embeddings

    llm = OpenAIProvider(model="gpt-4o-mini")
    embedding = llm.embed("Hello world")
    print(f"Vector dimensions: {len(embedding)}")

Example 6: Override settings per call

    llm = OpenAIProvider(model="gpt-4o-mini", temperature=0.7)
    
    # Use instance temperature (0.7)
    response1 = llm.generate("Creative story")
    
    # Override for this call only (0.0)
    response2 = llm.generate("Factual answer", temperature=0.0)
"""

