import json
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

from polaris_cli.client import GroqClient

class TaskClassification(BaseModel):
    category: Literal["flagship", "reasoning", "heavy", "smart", "vision", "light", "versatile"] = Field(..., description="Complexity and type of the task")
    explanation: str = Field(..., description="Short explanation for the classification")
    suggested_model: str = Field(..., description="ID of the model to use")

class Router:
    """Intelligently routes tasks to the most appropriate Groq model."""
    
    MODELS = {
        "flagship": "openai/gpt-oss-120b",    
        "reasoning": "qwen/qwen3-32b",          
        "heavy": "llama-3.3-70b-versatile",   
        "smart": "groq/compound",             
        "vision": "meta-llama/llama-4-scout-17b-16e-instruct", 
        "light": "llama-3.1-8b-instant",
        "versatile": "openai/gpt-oss-20b"     
    }

    def __init__(self, client: GroqClient):
        self.client = client

    def classify_task(self, prompt: str) -> TaskClassification:
        """Classify the user prompt and suggest a model using llama-3.1-8b-instant."""
        
        system_prompt = (
            "You are a task classifier for POLARIS-CLI. Your job is to analyze the user prompt and "
            "determine the best model for the task. Respond ONLY in valid JSON format matching this schema:\n"
            '{"category": "flagship" | "reasoning" | "heavy" | "smart" | "vision" | "light" | "versatile", "explanation": "...", "suggested_model": "..."}\n\n'
            "Available categories and best-fit models:\n"
            "- flagship: [openai/gpt-oss-120b] - Deep logic, system architecture, flagship reasoning.\n"
            "- reasoning: [qwen/qwen3-32b, deepseek-r1-distill-llama-70b] - Intense mathematical logic, coding algorithms.\n"
            "- heavy: [llama-3.3-70b-versatile] - Standard high-performance generation.\n"
            "- smart: [groq/compound] - Multi-step autonomous tool use (web search, etc).\n"
            "- vision: [meta-llama/llama-4-scout-17b-16e-instruct] - Image analysis, diagrams, visual context.\n"
            "- light: [llama-3.1-8b-instant] - Fast responses, simple queries, terminal commands.\n"
            "- versatile: [openai/gpt-oss-20b] - Balanced creative writing and code debugging."
        )

        try:
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
        except Exception:
            # Absolute fallback if classification fails
            data = {"category": "light", "explanation": "Auto-routed due to classification failure.", "suggested_model": "llama-3.1-8b-instant"}
        
        # Validation mapping if model ID is missing (ensure exact IDs from MODELS dict)
        category = data.get("category", "light")
        if category in self.MODELS:
            data["suggested_model"] = self.MODELS[category]
        else:
             data["suggested_model"] = self.MODELS.get("light")

        return TaskClassification(**data)
