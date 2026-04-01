from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.status import Status
from rich.table import Table
from rich.theme import Theme

# Custom Theme
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "agent": "bold blue"
})

console = Console(theme=custom_theme)

ASCII_ART = r"""
 [bold cyan]
  ____  ____  _        _    ____  ___ ____        ____ _     ___ 
 |  _ \|  _ \| |      / \  |  _ \|_ _/ ___|      / ___| |   |_ _|
 | |_) | | | | |     / _ \ | |_) || |\___ \_____| |   | |    | | 
 |  __/| |_| | |___ / ___ \|  _ < | | ___) |_____| |___| |___ | | 
 |_|   |____/|_____/_/   \_\_| \_\___|____/       \____|_____|___|
 [/bold cyan]
"""

def print_banner():
    """Print the POLARIS-CLI banner."""
    console.print(ASCII_ART)
    console.print("[dim italic center]Ultra-fast Autonomous Agent powered by Groq[/dim italic center]")

def print_message(role: str, content: str):
    """Print a message with syntax-highlighted markdown."""
    if role == "user":
        console.print(Panel(content, title="[bold green]User[/bold green]", border_style="green"))
    elif role == "agent":
        markdown = Markdown(content)
        console.print(Panel(markdown, title="[bold blue]Polaris[/bold blue]", border_style="blue"))
    else:
        console.print(content)

def show_status(text: str):
    """Display a status message with a spinner."""
    return console.status(f"[bold cyan]{text}...[/bold cyan]", spinner="dots")

def print_error(text: str):
    """Print an error message."""
    console.print(f"[bold red]✗ Error: {text}[/bold red]")

def print_info(text: str):
    """Print an info message."""
    console.print(f"[dim info]➜ {text}[/dim info]")

def print_success(text: str):
    """Print a success message."""
    console.print(f"[bold success]✓ {text}[/bold success]")
