import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
import os

class StructuredLogger:
    """Structured logging for agent system observability"""
    
    def __init__(self, name: str, level: str = "INFO", log_file: str = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_agent_start(self, agent_name: str, task: Dict[str, Any], session_id: str):
        """Log agent execution start"""
        self.logger.info(json.dumps({
            "event": "agent_start",
            "agent": agent_name,
            "session_id": session_id,
            "task_type": task.get("type", "unknown"),
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_agent_end(self, agent_name: str, result: Dict[str, Any], session_id: str, duration: float):
        """Log agent execution completion"""
        self.logger.info(json.dumps({
            "event": "agent_end", 
            "agent": agent_name,
            "session_id": session_id,
            "success": result.get("success", False),
            "duration_seconds": duration,
            "result_size": len(str(result)),
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_tool_usage(self, tool_name: str, parameters: Dict[str, Any], success: bool, duration: float):
        """Log tool usage"""
        self.logger.debug(json.dumps({
            "event": "tool_usage",
            "tool": tool_name,
            "parameters": parameters,
            "success": success,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_quality_check(self, session_id: str, quality_score: float, iteration: int):
        """Log quality validation results"""
        self.logger.info(json.dumps({
            "event": "quality_validation",
            "session_id": session_id,
            "quality_score": quality_score,
            "iteration": iteration,
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_error(self, component: str, error: str, context: Dict[str, Any] = None):
        """Log error with context"""
        self.logger.error(json.dumps({
            "event": "error",
            "component": component,
            "error": error,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log custom metrics"""
        self.logger.info(json.dumps({
            "event": "metrics",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }))

def setup_logging(level: str = "INFO", log_file: str = None):
    """Setup structured logging for the entire application"""
    
    # Remove default handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Basic configuration
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            *( [logging.FileHandler(log_file)] if log_file else [] )
        ]
    )