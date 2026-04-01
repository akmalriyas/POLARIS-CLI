import os
import platform
import subprocess
import shutil
from typing import Dict, Any, Optional
from polaris_cli.tools.base import tool

@tool(
    name="run_cmd",
    description="Execute a shell command. Captures output and handles errors."
)
def run_cmd(command: str, timeout: int = 30) -> str:
    """Execute a terminal command safely."""
    try:
        # Use shell=True for standard execution (caution, but necessary for CLI tools)
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        
        output = []
        if result.stdout:
            output.append(f"stdout:\n{result.stdout.strip()}")
        if result.stderr:
            output.append(f"stderr:\n{result.stderr.strip()}")
        if result.returncode != 0:
            output.append(f"Return code: {result.returncode}")
            
        if not output:
            return "Command executed successfully with no output."
        
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

@tool(
    name="sys_get_info",
    description="Retrieve essential system information: OS, CPU, Memory, and current user context."
)
def sys_get_info() -> str:
    """Gather system metadata."""
    try:
        info = []
        info.append(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
        info.append(f"CPU: {platform.machine()} ({platform.processor()})")
        
        # Memory info (if psutil was available, but let's stick to standard libs)
        # shutil.disk_usage for disk info
        total, used, free = shutil.disk_usage("/")
        info.append(f"Disk (root): {used//(2**30)}GB used / {total//(2**30)}GB total")
        
        info.append(f"Current Directory: {os.getcwd()}")
        info.append(f"User: {os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'unknown')}")
        info.append(f"Python Version: {platform.python_version()}")
        
        return "\n".join(info)
    except Exception as e:
        return f"Error gathering system info: {str(e)}"
