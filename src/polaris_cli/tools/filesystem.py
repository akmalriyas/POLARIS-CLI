import os
from pathlib import Path
from typing import List, Optional
from polaris_cli.tools.base import tool

@tool(
    name="read_file",
    description="Read the contents of a file at the specified path. Supports text files only."
)
def read_file(path: str) -> str:
    """Read file content safely."""
    p = Path(path)
    if not p.exists():
        return f"Error: File '{path}' does not exist."
    if not p.is_file():
        return f"Error: '{path}' is a directory, not a file. Use ls_dir instead."
    
    try:
        # Check size limit (e.g. 500KB to avoid context blowup)
        size = p.stat().st_size
        if size > 512 * 1024:
            return f"Error: File is too large ({size} bytes). Max limit is 512KB."
        
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool(
    name="ls_dir",
    description="List the contents of a directory. Shows files and subdirectories with sizes."
)
def ls_dir(path: str = ".") -> str:
    """List directory contents."""
    p = Path(path)
    if not p.exists():
        return f"Error: Directory '{path}' does not exist."
    if not p.is_dir():
        return f"Error: '{path}' is a file, not a directory. Use read_file instead."
    
    try:
        items = []
        for entry in p.iterdir():
            prefix = "📁" if entry.is_dir() else "📄"
            size_str = ""
            if entry.is_file():
                size = entry.stat().st_size
                if size < 1024:
                    size_str = f" ({size} B)"
                elif size < 1024 * 1024:
                    size_str = f" ({size/1024:.1f} KB)"
                else:
                    size_str = f" ({size/(1024*1024):.1f} MB)"
            
            items.append(f"{prefix} {entry.name}{size_str}")
        
        if not items:
            return f"Directory '{path}' is empty."
        
        return "\n".join(sorted(items))
    except Exception as e:
        return f"Error listing directory: {str(e)}"
