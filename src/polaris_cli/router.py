import json
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

from polaris_cli.client import GroqClient

class TaskClassification(BaseModel):
    category: Literal["heavy", "smart", "vision", "light", "versatile"] = Field(..., description="Complexity and type of the task")
    explanation: str = Field(..., description="Short explanation for the classification")
    suggested_model: str = Field(..., description="ID of the model to use")

class Router:
    """Intelligently routes tasks to the most appropriate Groq model."""
    
    MODELS = {
        "heavy": "llama-3.3-70b-versatile", # Or openai/gpt-oss-120b if preferred
        "smart": "groq/compound",           # Multi-step tool execution system
        "vision": "llama-3.2-11b-vision-preview",
        "light": "llama-3.1-8b-instant",
        "versatile": "mixtral-8x7b-32768"
    }

    def __init__(self, client: GroqClient):
        self.client = client

    def classify_task(self, prompt: str) -> TaskClassification:
        """Classify the user prompt and suggest a model using llama-3.1-8b-instant."""
        
        system_prompt = (
            "You are a task classifier for POLARIS-CLI. Your job is to analyze the user prompt and "
            "determine the best model for the task. Respond ONLY in valid JSON format matching this schema:\n"
            '{"category": "heavy" | "smart" | "vision" | "light" | "versatile", "explanation": "...", "suggested_model": "..."}\n\n'
            "Available models and use cases:\n"
            "- heavy: [llama-3.3-70b-versatile, openai/gpt-oss-120b] - Deep reasoning, complex logic, large context.\n"
            "- smart: [groq/compound] - Complex multi-step tool execution, web search, code execution (The most capable system).\n"
            "- vision: [llama-3.2-11b-vision-preview] - Image analysis or visual context.\n"
            "- light: [llama-3.1-8b-instant] - Fast responses, simple definitions, terminal routing.\n"
            "- versatile: [mixtral-8x7b-32768] - Good balance of speed and reasoning, excellent for coding assistance."
        )

        response = self.client.request(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Task: {prompt}"}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Ensure the suggested_model is valid or fallback to a default for that category
        category = data.get("category", "light")
        suggested = data.get("suggested_model")
        
        # Validation mapping if model ID is generic or missing
        if category == "smart":
            data["suggested_model"] = "groq/compound"
        elif category == "vision":
            data["suggested_model"] = "llama-3.2-11b-vision-preview"
        elif category == "versatile":
            data["suggested_model"] = "mixtral-8x7b-32768"
        elif not suggested or suggested not in ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]:
             data["suggested_model"] = self.MODELS.get(category, "llama-3.1-8b-instant")

        return TaskClassification(**data)
