import json
import os
import stat
from pathlib import Path
from typing import List, Optional

import questionary
from platformdirs import user_config_dir

# Constants
APP_NAME = "polaris-cli"
APP_AUTHOR = "akmalriyas"
CONFIG_DIR = Path(user_config_dir(APP_NAME, APP_AUTHOR))
KEYS_FILE = CONFIG_DIR / "keys.json"

def ensure_config_dir():
    """Ensure the configuration directory exists."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # Set directory permissions to 700 (owner only)
        try:
            os.chmod(CONFIG_DIR, stat.S_IRWXU)
        except OSError:
            pass # Permissions may not be fully supported on all systems (e.g. some Windows builds)

def load_keys() -> List[str]:
    """Load API keys from the keys file."""
    if not KEYS_FILE.exists():
        return []
    
    try:
        with open(KEYS_FILE, "r") as f:
            data = json.load(f)
            return data.get("keys", [])
    except (json.JSONDecodeError, IOError):
        return []

def save_keys(keys: List[str]):
    """Save API keys to the keys file with secure permissions."""
    ensure_config_dir()
    
    with open(KEYS_FILE, "w") as f:
        json.dump({"keys": keys}, f, indent=4)
    
    # Set file permissions to 600 (owner read/write only)
    try:
        os.chmod(KEYS_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

def setup_wizard():
    """Interactive first-time setup to collect the Groq API key."""
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]🌌 Welcome to POLARIS-CLI![/bold cyan]\n"
        "Let's get you set up with your Groq API keys.",
        border_style="cyan"
    ))
    
    key = questionary.password(
        "Enter your Groq API Key:",
        instruction="Get one at https://console.groq.com/keys"
    ).ask()
    
    if key:
        save_keys([key])
        console.print("[bold green]✓ API Key saved successfully![/bold green]")
        return [key]
    else:
        console.print("[bold red]✗ Setup cancelled. You need an API key to use POLARIS-CLI.[/bold red]")
        return []

def add_key_interactively():
    """Add another API key to the existing list."""
    keys = load_keys()
    
    new_key = questionary.password(
        "Enter additional Groq API Key:"
    ).ask()
    
    if new_key and new_key not in keys:
        keys.append(new_key)
        save_keys(keys)
        print("✓ API Key added.")
    elif new_key in keys:
        print("! This key is already in your list.")
    else:
        print("✗ Cancelled.")

def get_api_keys() -> List[str]:
    """Get the current list of API keys, running setup if none exist."""
    keys = load_keys()
    if not keys:
        keys = setup_wizard()
    return keys
