import json
from typing import Dict, Any, List
import logging
from pydantic import BaseModel

try:
    import aiohttp
except ImportError:
    aiohttp = None

class MCPTool(BaseModel):
    """Model Context Protocol Tool Base"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str]

class MCPClient:
    """MCP Client for standardized tool communication"""
    
    def __init__(self, server_url: str = "http://localhost:3000"):
        self.server_url = server_url
        self.logger = logging.getLogger("mcp_client")
        self.available_tools: List[MCPTool] = []
    
    async def initialize(self):
        """Initialize MCP connection and discover available tools"""
        if aiohttp is None:
            self.logger.warning("aiohttp not installed. Install with: pip install aiohttp")
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/tools") as response:
                    if response.status == 200:
                        tools_data = await response.json()
                        self.available_tools = [MCPTool(**tool) for tool in tools_data]
                        self.logger.info(f"Discovered {len(self.available_tools)} MCP tools")
                    else:
                        self.logger.error(f"Failed to discover tools: {response.status}")
        except Exception as e:
            self.logger.warning(f"MCP server not available: {str(e)}")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        if aiohttp is None:
            return {"error": "aiohttp not installed. Install with: pip install aiohttp"}
            
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "tool": tool_name,
                    "parameters": parameters
                }
                
                async with session.post(
                    f"{self.server_url}/call",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        self.logger.debug(f"MCP tool {tool_name} executed successfully")
                        return result
                    else:
                        error_msg = f"MCP tool {tool_name} failed: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg}
                        
        except Exception as e:
            error_msg = f"MCP tool {tool_name} error: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

class ContentResearchTool:
    """MCP Tool for content research"""
    
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
        self.tool_name = "content_research"
    
    async def research_topic(self, topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
        """Research a topic using MCP"""
        parameters = {
            "topic": topic,
            "depth": depth,
            "sources": ["academic", "news", "trending"],
            "max_results": 10
        }
        
        return await self.client.call_tool(self.tool_name, parameters)

class ScriptAnalysisTool:
    """MCP Tool for script analysis"""
    
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
        self.tool_name = "script_analysis"
    
    async def analyze_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze script quality and engagement"""
        parameters = {
            "script": script,
            "analysis_types": ["readability", "engagement", "structure", "seo"]
        }
        
        return await self.client.call_tool(self.tool_name, parameters)

class TrendPredictionTool:
    """MCP Tool for trend prediction"""
    
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
        self.tool_name = "trend_prediction"
    
    async def predict_trends(self, topic: str, timeframe: str = "1month") -> Dict[str, Any]:
        """Predict trends for a topic"""
        parameters = {
            "topic": topic,
            "timeframe": timeframe,
            "platform": "youtube",
            "confidence_threshold": 0.7
        }
        
        return await self.client.call_tool(self.tool_name, parameters)