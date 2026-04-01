from typing import Any, Dict, List, Optional, Callable
from polaris_cli.tools.base import Tool
from polaris_cli.tools import filesystem, search, system

class ToolRegistry:
    """Registry to manage and execute POLARIS-CLI tools."""
    
    def __init__(self):
        # Register tools by name
        self.tools: Dict[str, Tool] = {}
        
        # Add filesystem tools
        self._register(filesystem.read_file._tool)
        self._register(filesystem.ls_dir._tool)
        self._register(filesystem.write_file._tool)
        
        # Add search tools
        self._register(search.search_code._tool)
        
        # Add system tools
        self._register(system.run_cmd._tool)
        self._register(system.sys_get_info._tool)

    def _register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Return the list of OpenAI-compatible schemas for all registered tools."""
        return [tool.get_schema() for tool in self.tools.values()]

    def call(self, name: str, **kwargs) -> str:
        """Call a tool by name with arguments."""
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        
        return self.tools[name].run(**kwargs)
