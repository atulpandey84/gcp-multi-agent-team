import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

class ToolPermissionManager:
    """
    Manages tool permissions based on the tools.yaml configuration.
    Ensures that only authorized agents can invoke specific tools.
    """
    def __init__(self, config_path: str = "config/tools.yaml"):
        self.config_path = config_path
        self.tools_config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('tools', {})
        except Exception as e:
            print(f"Error loading tools config: {e}")
            return {}

    def is_authorized(self, agent_id: str, tool_id: str) -> bool:
        """
        Check if an agent is authorized to use a specific tool.
        
        Args:
            agent_id: The ID of the agent (e.g., 'platform_architect')
            tool_id: The ID of the tool (e.g., 'architecture.resource_design_validation')
            
        Returns:
            bool: True if authorized, False otherwise.
        """
        tool = self.tools_config.get(tool_id)
        if not tool:
            return False
        
        allowed_agents = tool.get('agents', [])
        return agent_id in allowed_agents

# Singleton instance for the API
permission_manager = ToolPermissionManager()
