import os
import time
from typing import Any, Dict, List, Optional, Generator

from groq import Groq, InternalServerError, RateLimitError, UnprocessableEntityError, AuthenticationError
from pydantic import BaseModel

class GroqClient:
    """A resilient wrapper for the Groq API with multi-key rotation and error handling."""
    
    def __init__(self, api_keys: List[str]):
        if not api_keys:
            raise ValueError("No API keys provided.")
        self.api_keys = api_keys
        self.current_key_index = 0
        self.client = Groq(api_key=self.api_keys[self.current_key_index])

    def rotate_key(self) -> bool:
        """Switch to the next available API key. Returns True if successful, False if all keys exhausted."""
        self.current_key_index += 1
        if self.current_key_index >= len(self.api_keys):
            return False
            
        self.client = Groq(api_key=self.api_keys[self.current_key_index])
        return True

    def request(self, method: str = "chat.completions.create", **kwargs) -> Any:
        """Safely execute a request to Groq with automatic retry and key rotation."""
        while True:
            try:
                if method == "chat.completions.create":
                    return self.client.chat.completions.create(**kwargs)
                else:
                    attr = getattr(self.client, method)
                    return attr(**kwargs)
            except (RateLimitError, AuthenticationError) as e:
                if isinstance(e, RateLimitError):
                    print(f"\n[yellow]! Rate limit hit on key {self.current_key_index+1}. Rotating...[/yellow]")
                else:
                    print(f"\n[red]! Invalid API key detected (index {self.current_key_index+1}). Rotating...[/red]")
                
                if not self.rotate_key():
                    raise Exception("All API keys exhausted or invalid.") from e
            except Exception as e:
                # Handle other unexpected errors
                raise e

    def stream_request(self, **kwargs) -> Generator[str, None, None]:
        """Stream chat completions from Groq."""
        while True:
            try:
                stream = self.client.chat.completions.create(stream=True, **kwargs)
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except (RateLimitError, AuthenticationError):
                if not self.rotate_key():
                    raise Exception("All API keys exhausted or invalid.")
            except Exception as e:
                raise e
