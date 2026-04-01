import json
from typing import List, Dict, Any, Optional

from polaris_cli.client import GroqClient
from polaris_cli.router import Router, TaskClassification
from polaris_cli.tools.registry import ToolRegistry
from polaris_cli.ui import console, show_status, print_message, print_info, print_error, print_success

class Agent:
    """The core POLARIS-CLI agent that coordinates reasoning and tool use."""
    
    def __init__(self, client: GroqClient):
        self.client = client
        self.router = Router(client=client)
        self.registry = ToolRegistry()
        self.history: List[Dict[str, Any]] = []

    def run(self, prompt: str, classification: Optional[TaskClassification] = None):
        """Execute a single task with autonomous tool use."""
        if not classification:
            with show_status("Classifying task"):
                classification = self.router.classify_task(prompt)
        
        print_info(f"Routing to [bold sky_blue]{classification.category}[/bold sky_blue] model ([dim]{classification.suggested_model}[/dim])")
        
        self.history.append({"role": "user", "content": prompt})
        
        # Max steps to prevent infinite loops
        max_steps = 10
        for step in range(max_steps):
            with show_status(f"Thinking (Step {step+1})"):
                response = self.client.request(
                    model=classification.suggested_model,
                    messages=self.history,
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
                
                with show_status(f"Executing [bold yellow]{name}[/bold yellow]"):
                    result = self.registry.call(name, **args)
                
                print_info(f"Tool [dim]{name}[/dim] result: [dim]{result[:100]}...[/dim]")
                
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": result
                })

    def chat(self):
        """Enter an interactive multi-turn chat session."""
        from rich.prompt import Prompt
        from rich.panel import Panel
        from rich.text import Text
        
        print_info("Entering interactive mode. Type 'exit' or 'quit' to leave.")
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]User[/bold green]")
                
                if user_input.lower() in ["exit", "quit"]:
                    print_success("Goodbye!")
                    break
                
                if not user_input.strip():
                    continue

                self.run(user_input)
                
            except KeyboardInterrupt:
                print_success("\nGoodbye!")
                break
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
