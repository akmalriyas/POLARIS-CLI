import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, create_model

class Tool:
    """Base class for all POLARIS-CLI tools."""
    
    def __init__(self, name: str, description: str, func: Callable, args_model: Type[BaseModel]):
        self.name = name
        self.description = description
        self.func = func
        self.args_model = args_model

    def get_schema(self) -> Dict[str, Any]:
        """Return the OpenAI-compatible tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_model.model_json_schema()
            }
        }

    def run(self, **kwargs) -> str:
        """Execute the tool with the provided arguments."""
        try:
            # Validate with Pydantic
            validated_args = self.args_model(**kwargs)
            return self.func(**validated_args.model_dump())
        except Exception as e:
            return f"Error executing tool {self.name}: {str(e)}"

def tool(name: str, description: str):
    """Decorator to easily create a Tool from a function."""
    def decorator(func: Callable):
        # Automatically generate Pydantic model from function signature
        sig = inspect.signature(func)
        fields = {}
        for param_name, param in sig.parameters.items():
            if param.annotation == inspect.Parameter.empty:
                fields[param_name] = (Any, ...)
            else:
                fields[param_name] = (param.annotation, ... if param.default == inspect.Parameter.empty else param.default)
        
        args_model = create_model(f"{func.__name__}_args", **fields)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper._tool = Tool(name=name, description=description, func=func, args_model=args_model)
        return wrapper
    return decorator
