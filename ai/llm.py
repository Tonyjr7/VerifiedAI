import logging
from typing import Any, Dict, Generator, List, Optional, Union

from groq import Groq

from config.settings import Settings


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqLLM:
    """ 
    A client wrapper for the Groq Cloud API, providing convenient methods
    for text generation and streaming.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        default_model: str = Settings().model
    ):
        """
        Initialize the Groq LLM client.
        
        Args:
            api_key: The Groq API key. If not provided, it will be loaded from settings.
            default_model: The default model to use for generations.
        """
        self.api_key = api_key or Settings.groq_api_key
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Please set 'groq_api_key' in your environment or settings."
            )
        
        self.client = Groq(api_key=self.api_key)
        self.default_model = default_model
        logger.info(f"GroqLLM client initialized with model: {self.default_model}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> Union[Any, Generator[Any, None, None]]:
        """
        Generate a response for the given conversation messages.
        
        Args:
            messages: A list of message dictionaries (e.g. [{"role": "user", "content": "hello"}])
            model: Optional model name to override the default model.
            temperature: Sampling temperature (0 to 2).
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            **kwargs: Additional parameters to pass to the Groq API.
            
        Returns:
            Either a chat completion object or a generator for streaming responses.
        """
        selected_model = model or self.default_model
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Error during Groq API generation: {e}")
            raise

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """
        Helper method to generate a simple text response from a single prompt.
        
        Args:
            prompt: The user query string.
            system_prompt: Optional system prompt to instruct the model.
            model: Optional model name.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens.
            
        Returns:
            The generated response string.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            **kwargs
        )
        return response.choices[0].message.content

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> Generator[str, None, None]:
        """
        Helper method to stream responses from a single prompt.
        
        Args:
            prompt: The user query string.
            system_prompt: Optional system prompt.
            model: Optional model name.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens.
            
        Returns:
            A generator yielding chunk strings.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream_response = self.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        for chunk in stream_response:
            content = chunk.choices[0].delta.content
            if content:
                yield content


if __name__ == "__main__":
    # Example usage for testing
    import os
    
    print("Testing GroqLLM client initialization...")
    try:
        llm = GroqLLM()
        print("Initialization successful. Testing simple prompt:")
        
        test_prompt = "Say hello in exactly 3 words."
        print(f"Prompt: {test_prompt}")
        
        response = llm.generate_text(prompt=test_prompt)
        print(f"Response: {response}")
    except Exception as err:
        print(f"Error testing GroqLLM: {err}")
