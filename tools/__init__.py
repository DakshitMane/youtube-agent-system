"""Tools module for YouTube Agent System."""

from .custom_tools import (
    VoiceSynthesisTool,
    VideoEditorTool, 
    ThumbnailGeneratorTool
)
from .builtin_tools import (
    GoogleSearchTool,
    CodeExecutionTool,
    TextToSpeechTool,
    ImageGenerationTool
)
from .mcp_tools import (
    MCPClient,
    ContentResearchTool,
    ScriptAnalysisTool,
    TrendPredictionTool
)
from .openapi_tools import (
    YouTubeAPITool,
    PexelsAPITool,
    ElevenLabsAPITool
)

__all__ = [
    # Custom tools
    'VoiceSynthesisTool',
    'VideoEditorTool',
    'ThumbnailGeneratorTool',
    # Built-in tools
    'GoogleSearchTool',
    'CodeExecutionTool',
    'TextToSpeechTool',
    'ImageGenerationTool',
    # MCP tools
    'MCPClient',
    'ContentResearchTool',
    'ScriptAnalysisTool',
    'TrendPredictionTool',
    # OpenAPI tools
    'YouTubeAPITool',
    'PexelsAPITool',
    'ElevenLabsAPITool'
]