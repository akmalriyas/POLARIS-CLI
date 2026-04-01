import json
import base64
import os
import mimetypes
from typing import List, Dict, Any, Optional

from polaris_cli.client import GroqClient
from polaris_cli.router import Router, TaskClassification
from polaris_cli.tools.registry import ToolRegistry
from polaris_cli.ui import console, show_status, print_message, print_info, print_error, print_success

class Agent:
    """The core POLARIS-CLI agent that coordinates reasoning and tool use."""
    
    SYSTEM_PROMPT = (
        "You are POLARIS, an autonomous CLI-based AI agent. You are helpful, precise, and professional. "
        "You have access to terminal and filesystem tools.\n"
        "CRITICAL TOOL CALLING RULES:\n"
        "1. You MUST use the provided JSON tool-calling capabilities inherently. NEVER output raw XML tags (e.g., <write_file>) to call tools.\n"
        "2. If you need to create or edit a file, use the 'write_file' tool.\n"
        "3. If a task is just a general conversation, answer directly without searching for a tool.\n"
        "Do NOT mention 'functions' or 'tools' in your direct responses unless an error occurs."
    )
    
    def __init__(self, client: GroqClient):
        self.client = client
        self.router = Router(client=client)
        self.registry = ToolRegistry()
        self.history: List[Dict[str, Any]] = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

    def _extract_images_from_prompt(self, prompt: str) -> List[str]:
        words = prompt.split()
        paths = []
        for word in words:
            clean_word = word.strip("'\".,;:]!?)(")
            if clean_word.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                if os.path.isfile(clean_word):
                    paths.append(clean_word)
        return paths

    def _format_vision_content(self, prompt: str, image_paths: List[str]) -> List[Dict[str, Any]]:
        content = [{"type": "text", "text": prompt}]
        for path in image_paths:
            try:
                mime_type, _ = mimetypes.guess_type(path)
                mime_type = mime_type or "image/jpeg"
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{b64}"
                    }
                })
            except Exception as e:
                console.print(f"[dim red]Failed to load image {path}: {e}[/dim red]")
        return content

    def _sanitize_history(self, target_model: str) -> List[Dict[str, Any]]:
        """Strictly rebuild message history to prevent API errors from unexpected fields."""
        sanitized = []
        for msg in self.history:
            if hasattr(msg, "model_dump"):
                msg_dict = msg.model_dump(exclude_none=True)
            elif hasattr(msg, "dict"):
                msg_dict = msg.dict(exclude_none=True)
            elif isinstance(msg, dict):
                msg_dict = msg.copy()
            else:
                msg_dict = dict(msg)
                
            # Safely rebuild the dict with EXACTLY the keys allowed by Groq API
            safe_msg = {}
            if "role" in msg_dict:
                safe_msg["role"] = msg_dict["role"]
            if "content" in msg_dict:
                c = msg_dict["content"]
                if isinstance(c, list) and target_model != self.router.MODELS.get("vision", ""):
                    text_parts = [item.get("text", "") for item in c if isinstance(item, dict) and item.get("type", "") == "text"]
                    safe_msg["content"] = "\n".join(text_parts)
                else:
                    safe_msg["content"] = c
            if "name" in msg_dict:
                safe_msg["name"] = msg_dict["name"]
            if "tool_call_id" in msg_dict:
                safe_msg["tool_call_id"] = msg_dict["tool_call_id"]
                
            if "tool_calls" in msg_dict and msg_dict["tool_calls"]:
                safe_calls = []
                for tc in msg_dict["tool_calls"]:
                    # Handle both dictionary and object forms of tool_calls
                    tc_dict = tc if isinstance(tc, dict) else (tc.model_dump() if hasattr(tc, "model_dump") else dict(tc))
                    
                    safe_tc = {"id": tc_dict.get("id"), "type": tc_dict.get("type", "function"), "function": {}}
                    if "function" in tc_dict:
                        func_data = tc_dict["function"]
                        func_dict = func_data if isinstance(func_data, dict) else (func_data.model_dump() if hasattr(func_data, "model_dump") else dict(func_data))
                        safe_tc["function"]["name"] = func_dict.get("name")
                        safe_tc["function"]["arguments"] = func_dict.get("arguments")
                    safe_calls.append(safe_tc)
                safe_msg["tool_calls"] = safe_calls
                
            sanitized.append(safe_msg)
            
        return sanitized

    def run(self, prompt: str, classification: Optional[TaskClassification] = None):
        """Execute a single task with autonomous tool use."""
        try:
            images = self._extract_images_from_prompt(prompt)
            
            if not classification:
                with show_status("Classifying task"):
                    # Extract last 4 messages for context (excluding system prompt)
                    recent = []
                    for m in self.history:
                        role = m.get("role") if isinstance(m, dict) else getattr(m, "role", None)
                        if role != "system":
                            recent.append(m)
                    recent = recent[-4:]
                    
                    history_lines = []
                    for m in recent:
                        role = m.get("role", "unknown") if isinstance(m, dict) else getattr(m, "role", "unknown")
                        
                        c = m.get("content") if isinstance(m, dict) else getattr(m, "content", None)
                        if isinstance(c, list):
                            text_parts = [item.get("text", "") for item in c if isinstance(item, dict) and item.get("type", "") == "text"]
                            c = " ".join(text_parts)
                            
                        history_lines.append(f"{role.capitalize()}: {c or '(used tool)'}")
                        
                    history_str = "\n".join(history_lines)
                    classification = self.router.classify_task(prompt, history_str)

            if images and classification.category != "vision":
                classification.category = "vision"
                classification.suggested_model = self.router.MODELS.get("vision", "meta-llama/llama-4-scout-17b-16e-instruct")
            
            # Gemini-style: Show which category is being used
            console.print(f"[italic dim]Responding with {classification.suggested_model}...[/italic dim]")
            
            if classification.category == "vision" and images:
                content_payload = self._format_vision_content(prompt, images)
            else:
                content_payload = prompt
                
            self.history.append({"role": "user", "content": content_payload})
            
            # Max steps to prevent infinite loops
            max_steps = 10
            for step in range(max_steps):
                with show_status("Thinking"):
                    response = self.client.request(
                        model=classification.suggested_model,
                        messages=self._sanitize_history(classification.suggested_model),
                        tools=self.registry.get_schemas(),
                        tool_choice="auto"
                    )
                
                message = response.choices[0].message
                content = message.content
                tool_calls = message.tool_calls
                
                self.history.append(message)
                
                if content:
                    print_message("agent", content)
                
                if not tool_calls:
                    break
                    
                # Handle tool calls
                for tool_call in tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    with show_status(f"Using {name}"):
                        result = self.registry.call(name, **args)
                    
                    # Gemini-style boxed tool output
                    from polaris_cli.ui import print_tool_call
                    print_tool_call(name, args, result)
                    
                    self.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result
                    })
            
            # After finishing, show the footer/path
            from polaris_cli.ui import print_footer
            print_footer()

        except Exception as e:
            print_error(f"{str(e)}")
            from polaris_cli.ui import print_footer
            print_footer()

    def chat(self):
        """Enter an interactive multi-turn chat session."""
        from rich.prompt import Prompt
        from rich.text import Text
        
        # Initial Banner
        from polaris_cli.ui import print_banner, print_footer
        print_banner()
        
        while True:
            try:
                # Gemini-style prompt
                user_input = Prompt.ask("[bold magenta]> [/bold magenta]")
                
                if user_input.lower() in ["exit", "quit"]:
                    console.print("[bold magenta]✦ [/bold magenta][dim]Goodbye![/dim]")
                    break
                
                if not user_input.strip():
                    continue

                if user_input.lower() in ["help", "/help"]:
                    from polaris_cli.cli import show_branded_help
                    show_branded_help()
                    continue

                self.run(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[bold magenta]✦ [/bold magenta][dim]Goodbye![/dim]")
                break
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
