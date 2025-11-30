from .base_agent import BaseAgent
from typing import Dict, Any, List
import asyncio
import logging

class ResearchAgent(BaseAgent):
    """Parallel agent for content research"""
    
    def __init__(self, research_type: str):
        super().__init__(f"researcher_{research_type}", f"Research {research_type}")
        self.research_type = research_type
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        topic = task.get("topic", "")
        
        self.logger.info(f"Researching {self.research_type} for: {topic}")
        
        # Simulate different research types
        if self.research_type == "trends":
            return await self._research_trends(topic)
        elif self.research_type == "facts":
            return await self._research_facts(topic)
        elif self.research_type == "competition":
            return await self._research_competition(topic)
        else:
            return {"error": f"Unknown research type: {self.research_type}"}
    
    async def _research_trends(self, topic: str) -> Dict[str, Any]:
        await asyncio.sleep(2)  # Simulate API call
        return {
            "trending_angles": [
                f"Latest developments in {topic}",
                f"Future of {topic}",
                f"Controversial aspects of {topic}"
            ],
            "search_volume": "High",
            "competition_level": "Medium"
        }
    
    async def _research_facts(self, topic: str) -> Dict[str, Any]:
        await asyncio.sleep(1.5)
        return {
            "key_facts": [
                f"Fact 1 about {topic}",
                f"Fact 2 about {topic}",
                f"Fact 3 about {topic}"
            ],
            "sources": ["Source A", "Source B", "Source C"],
            "statistics": {"relevance_score": 0.85}
        }
    
    async def _research_competition(self, topic: str) -> Dict[str, Any]:
        await asyncio.sleep(2.5)
        return {
            "top_videos": [
                {"title": f"Video 1 about {topic}", "views": "100K"},
                {"title": f"Video 2 about {topic}", "views": "150K"},
                {"title": f"Video 3 about {topic}", "views": "80K"}
            ],
            "gaps_identified": ["Missing practical examples", "No recent updates"],
            "success_factors": ["Good storytelling", "Clear explanations"]
        }

class ParallelAgentExecutor:
    """Execute multiple agents in parallel"""
    
    def __init__(self):
        self.logger = logging.getLogger("parallel_executor")
    
    async def execute_parallel(self, agents: List[BaseAgent], tasks: List[Dict]) -> Dict[str, Any]:
        """Execute multiple agents in parallel"""
        self.logger.info(f"Executing {len(agents)} agents in parallel")
        
        # Create tasks for all agents
        agent_tasks = [
            agent.execute(task) for agent, task in zip(agents, tasks)
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Process results
        processed_results = {}
        for i, (agent, result) in enumerate(zip(agents, results)):
            if isinstance(result, Exception):
                self.logger.error(f"Agent {agent.name} failed: {str(result)}")
                processed_results[agent.name] = {"error": str(result)}
            else:
                processed_results[agent.name] = result
        
        return processed_results