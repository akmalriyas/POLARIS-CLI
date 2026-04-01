import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.status import Status
from rich.table import Table
from rich.theme import Theme
from rich.syntax import Syntax

# Custom Theme for Gemini-like aesthetics
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "agent": "white",
    "prompt": "bold magenta"
})

console = Console(theme=custom_theme)

# Gemini-style ASCII Art (Slant Font)
ASCII_ART = r"""[bold magenta]
        ░█████████    ░██████   ░██            ░███    ░█████████  ░██████  ░██████   
░██     ░██     ░██  ░██   ░██  ░██           ░██░██   ░██     ░██   ░██   ░██   ░██  
 ░██    ░██     ░██ ░██     ░██ ░██          ░██  ░██  ░██     ░██   ░██  ░██         
  ░██   ░█████████  ░██     ░██ ░██         ░█████████ ░█████████    ░██   ░████████  
 ░██    ░██         ░██     ░██ ░██         ░██    ░██ ░██   ░██     ░██          ░██ 
░██     ░██          ░██   ░██  ░██         ░██    ░██ ░██    ░██    ░██   ░██   ░██  
        ░██           ░██████   ░██████████ ░██    ░██ ░██     ░██ ░██████  ░██████   
[/bold magenta]"""

def print_banner():
    """Print the POLARIS-CLI banner and initial instructions."""
    console.print(ASCII_ART)
    console.print("[dim]Tips for getting started:[/dim]")
    console.print("[dim]1. Ask questions, analyze files, or run commands.[/dim]")
    console.print("[dim]2. Be specific for the best results.[/dim]")
    console.print("[dim]3. Use [bold magenta]help[/bold magenta] for more information.[/dim]\n")

def print_message(role: str, content: str):
    """Print a message with Gemini-style icons."""
    if role == "user":
        # Handled by the prompt usually, but for history:
        console.print(f"[bold magenta]> [/bold magenta]{content}")
    elif role == "agent":
        # Gemini uses a small star/diamond icon (✦)
        markdown = Markdown(content)
        console.print(Text("✦ ", style="bold magenta"), end="")
        console.print(markdown)
    else:
        console.print(content)

def print_tool_call(name: str, args: dict, result: str):
    """Print a boxed tool call with syntax highlighting, matching Gemini style."""
    arg_str = ", ".join(f"{k}={v}" for k, v in args.items())
    
    # Tool header
    console.print(f"\n[bold green]✓ {name}[/bold green] [dim]{arg_str}[/dim]")
    
    # Boxed result with syntax highlighting if it looks like code
    if result.startswith("stdout:") or result.startswith("stderr:") or "\n" in result:
        # Try to guess if it's code/output
        syntax = Syntax(result, "bash", theme="monokai", line_numbers=True, word_wrap=True)
        console.print(Panel(syntax, border_style="dim", padding=(0, 1)))
    else:
        console.print(Panel(result, border_style="dim", padding=(0, 1)))

def show_status(text: str):
    """Display a status message with a spinner."""
    return console.status(f"[italic dim]{text}...[/italic dim]", spinner="dots")

def print_error(text: str):
    """Print an error message."""
    console.print(f"[bold red]✗ Error: {text}[/bold red]")

def print_info(text: str):
    """Print an info message."""
    console.print(f"[italic dim]Responding with Groq AI...[/italic dim]")

def print_success(text: str):
    """Print a success message with the Gemini-style icon."""
    console.print(f"[bold magenta]✦ [/bold magenta][success]{text}[/success]")

def print_footer():
    """Print a footer with context info."""
    cwd = os.getcwd()
    console.print(f"\n[dim]~{cwd}[/dim]", end=" ")
