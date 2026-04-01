import os
import re
from pathlib import Path
from typing import List, Optional
from polaris_cli.tools.base import tool

@tool(
    name="search_code",
    description="Search for a specific keyword or pattern in all files within a directory (recursive)."
)
def search_code(keyword: str, path: str = ".", include_glob: str = "*") -> str:
    """Search for code snippets recursively."""
    p = Path(path)
    if not p.exists():
        return f"Error: Path '{path}' does not exist."
    
    try:
        results = []
        pattern = re.compile(keyword, re.IGNORECASE)
        count = 0
        max_matches = 20 # Limit to avoid context blowup
        
        for file_path in p.rglob(include_glob):
            if file_path.is_file():
                # Avoid binary or common noisy files/dirs
                if any(part.startswith(".") for part in file_path.parts) or "__pycache__" in str(file_path):
                    continue
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if pattern.search(line):
                                results.append(f"📄 {file_path.relative_to(p)} (L{i}): {line.strip()[:200]}")
                                count += 1
                                if count >= max_matches:
                                    break
                except (IOError, UnicodeDecodeError):
                    continue
            
            if count >= max_matches:
                results.append(f"\n... (Max {max_matches} results reached)")
                break
        
        if not results:
            return f"No matches found for '{keyword}'."
        
        return "\n".join(results)
    except Exception as e:
        return f"Error searching code: {str(e)}"
