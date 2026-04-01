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
        try:
            if not classification:
                with show_status("Classifying task"):
                    classification = self.router.classify_task(prompt)
            
            # Gemini-style: Show which model is being used
            console.print(f"[italic dim]Responding with {classification.suggested_model}...[/italic dim]")
            
            self.history.append({"role": "user", "content": prompt})
            
            # Max steps to prevent infinite loops
            max_steps = 10
            for step in range(max_steps):
                with show_status("Thinking"):
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

                if user_input.startswith("/help"):
                    from polaris_cli.cli import show_branded_help
                    show_branded_help()
                    continue

                self.run(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[bold magenta]✦ [/bold magenta][dim]Goodbye![/dim]")
                break
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
