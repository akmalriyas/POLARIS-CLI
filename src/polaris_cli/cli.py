import argparse
import sys
import os
import shutil
from typing import List, Optional

from rich.table import Table
from rich.panel import Panel

from polaris_cli.config import get_api_keys, add_key_interactively, KEYS_FILE, CONFIG_DIR, load_keys, save_keys
from polaris_cli.client import GroqClient
from polaris_cli.agent import Agent
from polaris_cli.ui import console, print_banner, print_info, print_error, print_success, print_message, show_status

def show_branded_help():
    """Display a premium branded help screen."""
    from polaris_cli.ui import print_banner
    print_banner()
    
    table = Table(box=None, padding=(0, 2))
    table.add_column("Command", style="bold magenta")
    table.add_column("Description", style="dim")
    
    table.add_row("chat", "Enter interactive session.")
    table.add_row("keys", "Manage Groq keys.")
    table.add_row("setup", "Run setup wizard.")
    table.add_row("reset", "Clear all data.")
    table.add_row("help", "Show this message.")
    
    console.print(table)
    console.print("\n[dim]Developed by [bold]akmalriyas[/bold].[/dim]")

def manage_keys_cli():
    """Handle the 'keys' subcommand."""
    keys = load_keys()
    
    table = Table(title="[bold cyan]🔑 Managed Groq API Keys[/bold cyan]")
    table.add_column("Index", style="dim")
    table.add_column("Key (Masked)", style="green")
    
    for i, key in enumerate(keys, 1):
        masked = f"{key[:8]}...{key[-4:]}"
        table.add_row(str(i), masked)
    
    console.print(table)
    
    action = console.input("\n[bold]Choose action (add/remove/back): [/bold]").lower()
    
    if action == "add":
        add_key_interactively()
    elif action == "remove":
        idx = console.input("[bold]Enter index to remove: [/bold]")
        try:
            k_idx = int(idx) - 1
            if 0 <= k_idx < len(keys):
                removed = keys.pop(k_idx)
                save_keys(keys)
                print_success(f"Key {idx} removed.")
            else:
                print_error("Invalid index.")
        except ValueError:
            print_error("Please enter a number.")
    elif action == "back" or not action:
        return
    else:
        print_error("Unknown action.")

def reset_app():
    """Reset the application state (clear config and keys)."""
    confirm = console.input("[bold red]⚠ This will delete all your config and keys. Are you sure? (y/N): [/bold red]").lower()
    if confirm == 'y':
        try:
            if CONFIG_DIR.exists():
                shutil.rmtree(CONFIG_DIR)
                print_success("Application reset successfully.")
            else:
                print_info("No configuration found to reset.")
        except Exception as e:
            print_error(f"Failed to reset: {str(e)}")
    else:
        print_info("Reset cancelled.")

def main():
    parser = argparse.ArgumentParser(
        description="🌌 POLARIS-CLI: Ultra-fast Autonomous AI Agent powered by Groq.",
        add_help=False
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Single prompt
    # subparsers.add_parser("prompt", help="Run a single task") # We'll handle this manually for legacy support
    
    # Chat
    subparsers.add_parser("chat", help="Start interactive mode")
    
    # Keys
    subparsers.add_parser("keys", help="Manage API keys")
    
    # Setup
    subparsers.add_parser("setup", help="Run setup wizard")
    
    # Reset
    subparsers.add_parser("reset", help="Clear all config")
    
    # Help
    subparsers.add_parser("help", help="Show help screen")
    
    parser.add_argument("prompt", nargs="?", help="A single prompt to execute")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("-h", "--help", action="store_true", help="Show help")
    
    # Robust argument handling for Windows .exe wrappers
    argv = sys.argv[1:]
    if argv and ("polaris-cli" in argv[0].lower() or "polaris_cli" in argv[0].lower()) and argv[0].endswith(".exe"):
        argv = argv[1:]

    args, unknown = parser.parse_known_args(argv)

    if args.version:
        from polaris_cli import __version__
        console.print(f"POLARIS-CLI v{__version__}")
        return

    if args.help or args.command == "help":
        show_branded_help()
        return

    # Subcommand routing
    if args.command == "setup":
        from polaris_cli.config import setup_wizard
        setup_wizard()
        return
    
    if args.command == "keys":
        manage_keys_cli()
        return
    
    if args.command == "reset":
        reset_app()
        return

    # Load keys for other operations
    keys = get_api_keys()
    if not keys:
        sys.exit(1)
        
    client = GroqClient(api_keys=keys)
    agent = Agent(client=client)

    if args.command == "chat":
        agent.chat()
        return

    # Handle single prompt (legacy or explicit)
    user_prompt = args.prompt or (unknown[0] if unknown else None)
    
    if user_prompt:
        print_banner()
        agent.run(user_prompt)
    else:
        # guide the user
        show_branded_help()

if __name__ == "__main__":
    main()
