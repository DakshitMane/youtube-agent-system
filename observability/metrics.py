import time
import json
from typing import Dict, Any, List
import logging
from datetime import datetime
import asyncio

class MetricsCollector:
    """Collect and report system metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("metrics_collector")
        self.metrics: Dict[str, Any] = {}
        self.historical_data: List[Dict[str, Any]] = []
        
    def record_agent_metrics(self, agent_name: str, duration: float, success: bool, output_size: int):
        """Record metrics for agent execution"""
        key = f"agent_{agent_name}"
        if key not in self.metrics:
            self.metrics[key] = {
                "execution_count": 0,
                "total_duration": 0,
                "success_count": 0,
                "error_count": 0,
                "total_output_size": 0,
                "last_execution": None
            }
        
        self.metrics[key]["execution_count"] += 1
        self.metrics[key]["total_duration"] += duration
        self.metrics[key]["total_output_size"] += output_size
        self.metrics[key]["last_execution"] = datetime.now().isoformat()
        
        if success:
            self.metrics[key]["success_count"] += 1
        else:
            self.metrics[key]["error_count"] += 1
    
    def record_tool_metrics(self, tool_name: str, duration: float, success: bool):
        """Record metrics for tool usage"""
        key = f"tool_{tool_name}"
        if key not in self.metrics:
            self.metrics[key] = {
                "usage_count": 0,
                "total_duration": 0,
                "success_count": 0,
                "error_count": 0,
                "last_used": None
            }
        
        self.metrics[key]["usage_count"] += 1
        self.metrics[key]["total_duration"] += duration
        self.metrics[key]["last_used"] = datetime.now().isoformat()
        
        if success:
            self.metrics[key]["success_count"] += 1
        else:
            self.metrics[key]["error_count"] += 1
    
    def record_quality_metrics(self, session_id: str, quality_score: float, iteration: int):
        """Record quality validation metrics"""
        key = f"quality_{session_id}"
        self.metrics[key] = {
            "final_quality_score": quality_score,
            "iterations_required": iteration,
            "evaluated_at": datetime.now().isoformat()
        }
    
    def record_memory_metrics(self, operation: str, duration: float, success: bool):
        """Record memory operations metrics"""
        key = f"memory_{operation}"
        if key not in self.metrics:
            self.metrics[key] = {
                "operation_count": 0,
                "total_duration": 0,
                "success_count": 0,
                "error_count": 0
            }
        
        self.metrics[key]["operation_count"] += 1
        self.metrics[key]["total_duration"] += duration
        
        if success:
            self.metrics[key]["success_count"] += 1
        else:
            self.metrics[key]["error_count"] += 1
    
    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get statistics for specific agent"""
        key = f"agent_{agent_name}"
        if key not in self.metrics:
            return {}
        
        data = self.metrics[key]
        avg_duration = data["total_duration"] / data["execution_count"]
        success_rate = data["success_count"] / data["execution_count"]
        avg_output_size = data["total_output_size"] / data["execution_count"]
        
        return {
            "agent_name": agent_name,
            "execution_count": data["execution_count"],
            "average_duration": round(avg_duration, 2),
            "success_rate": round(success_rate, 2),
            "average_output_size": round(avg_output_size, 2),
            "last_execution": data["last_execution"]
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        agent_metrics = {k: v for k, v in self.metrics.items() if k.startswith("agent_")}
        tool_metrics = {k: v for k, v in self.metrics.items() if k.startswith("tool_")}
        
        total_agent_executions = sum(m["execution_count"] for m in agent_metrics.values())
        total_tool_usages = sum(m["usage_count"] for m in tool_metrics.values())
        
        return {
            "total_agents": len(agent_metrics),
            "total_tools": len(tool_metrics),
            "total_agent_executions": total_agent_executions,
            "total_tool_usages": total_tool_usages,
            "system_uptime": self._get_uptime(),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive metrics report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.get_system_health(),
            "agent_performance": {},
            "tool_usage": {},
            "quality_metrics": {},
            "recommendations": []
        }
        
        # Agent performance
        for key in self.metrics:
            if key.startswith("agent_"):
                agent_name = key[6:]  # Remove "agent_" prefix
                report["agent_performance"][agent_name] = self.get_agent_stats(agent_name)
        
        # Tool usage
        for key in self.metrics:
            if key.startswith("tool_"):
                tool_name = key[5:]  # Remove "tool_" prefix
                report["tool_usage"][tool_name] = self.metrics[key]
        
        # Quality metrics
        for key in self.metrics:
            if key.startswith("quality_"):
                session_id = key[8:]  # Remove "quality_" prefix
                report["quality_metrics"][session_id] = self.metrics[key]
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations()
        
        # Store historical data
        self.historical_data.append(report)
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate system improvement recommendations based on metrics"""
        recommendations = []
        
        # Analyze agent performance
        for key in self.metrics:
            if key.startswith("agent_"):
                data = self.metrics[key]
                success_rate = data["success_count"] / data["execution_count"]
                
                if success_rate < 0.7:
                    agent_name = key[6:]
                    recommendations.append(f"Improve reliability of {agent_name} agent (success rate: {success_rate:.2f})")
                
                avg_duration = data["total_duration"] / data["execution_count"]
                if avg_duration > 30:  # More than 30 seconds average
                    agent_name = key[6:]
                    recommendations.append(f"Optimize performance of {agent_name} agent (avg duration: {avg_duration:.2f}s)")
        
        # Analyze tool usage
        for key in self.metrics:
            if key.startswith("tool_"):
                data = self.metrics[key]
                error_rate = data["error_count"] / data["usage_count"]
                
                if error_rate > 0.3:
                    tool_name = key[5:]
                    recommendations.append(f"Address reliability issues with {tool_name} tool (error rate: {error_rate:.2f})")
        
        return recommendations
    
    def _get_uptime(self) -> str:
        """Get system uptime (simplified)"""
        # In production, this would track actual startup time
        return "24h"  # Simplified
    
    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        report = self.generate_report()
        
        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "prometheus":
            return self._format_prometheus(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _format_prometheus(self, report: Dict[str, Any]) -> str:
        """Format metrics for Prometheus"""
        lines = []
        
        # System metrics
        health = report["system_health"]
        lines.append(f'system_agents_total {health["total_agents"]}')
        lines.append(f'system_tools_total {health["total_tools"]}')
        lines.append(f'system_agent_executions_total {health["total_agent_executions"]}')
        
        # Agent metrics
        for agent_name, stats in report["agent_performance"].items():
            lines.append(f'agent_executions_total{{agent="{agent_name}"}} {stats["execution_count"]}')
            lines.append(f'agent_success_rate{{agent="{agent_name}"}} {stats["success_rate"]}')
            lines.append(f'agent_avg_duration_seconds{{agent="{agent_name}"}} {stats["average_duration"]}')
        
        return "\n".join(lines)