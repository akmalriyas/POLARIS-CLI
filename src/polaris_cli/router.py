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

    def classify_task(self, prompt: str, recent_history: str = "") -> TaskClassification:
        """Classify the user prompt based on context and suggest a model using llama-3.1-8b-instant."""
        
        system_prompt = (
            "You are an intelligent task router for POLARIS-CLI. Analyze the user prompt and conversation history, and select the BEST model category. Respond ONLY in valid JSON matching this schema:\n"
            '{"category": "flagship" | "reasoning" | "heavy" | "smart" | "vision" | "light" | "versatile", "explanation": "Short reasoning", "suggested_model": "..."}\n\n'
            "RULES FOR CHOOSING CATEGORIES:\n"
            "- reasoning: MUST BE USED for ANY code generation, debugging, writing files, or complex math logic. (E.g., 'write a python script', 'fix this bug').\n"
            "- flagship: Use only for high-level system architecture, multi-file code planning, or deep repository structural analysis.\n"
            "- heavy: Use for large text generation, long-form content, or standard advanced questions.\n"
            "- smart: Use when the user explicitly asks to search the web or run multi-step autonomous pipelines.\n"
            "- vision: Use ONLY for image analysis tasks (e.g. prompt contains .png or .jpg).\n"
            "- versatile: Use for balanced creative writing or general questions.\n"
            "- light: MUST ONLY BE USED for simple greetings ('hello'), quick single terminal commands ('run ls'), or trivial questions."
        )

        user_content = f"Task: {prompt}"
        if recent_history:
            user_content = f"Recent History:\n{recent_history}\n\nCurrent Task: {prompt}"

        try:
            response = self.client.request(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
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
