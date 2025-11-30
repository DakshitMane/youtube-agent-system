from typing import Dict, Any, List
import logging
import json

class ContextManager:
    """Manage and engineer context for AI agents"""
    
    def __init__(self, max_tokens: int = 32000, compaction_strategy: str = "semantic"):
        self.logger = logging.getLogger("context_manager")
        self.max_tokens = max_tokens
        self.compaction_strategy = compaction_strategy
        
    async def prepare_agent_context(self, session_data: Dict[str, Any], 
                                  agent_role: str, 
                                  current_task: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare optimized context for an agent"""
        self.logger.debug(f"Preparing context for {agent_role}")
        
        # Get relevant memories
        relevant_memories = await self._get_relevant_memories(session_data, agent_role)
        
        # Compact context if needed
        compacted_context = await self._compact_context(
            relevant_memories, 
            current_task, 
            agent_role
        )
        
        # Structure context for the agent
        structured_context = self._structure_context(
            compacted_context, agent_role, current_task
        )
        
        return structured_context
    
    async def _get_relevant_memories(self, session_data: Dict[str, Any], agent_role: str) -> List[Dict[str, Any]]:
        """Get memories relevant to the agent's role"""
        memories = session_data.get("memories", [])
        relevant_memories = []
        
        for memory in memories:
            if self._is_relevant_to_agent(memory, agent_role):
                relevant_memories.append(memory)
        
        return relevant_memories
    
    def _is_relevant_to_agent(self, memory: Dict[str, Any], agent_role: str) -> bool:
        """Check if memory is relevant to agent's role"""
        memory_type = memory.get("metadata", {}).get("type", "")
        
        relevance_map = {
            "script_writer": ["research", "outline", "content"],
            "quality_validator": ["script", "production", "feedback"],
            "research_agent": ["topic", "requirements", "previous_research"]
        }
        
        relevant_types = relevance_map.get(agent_role, [])
        return memory_type in relevant_types
    
    async def _compact_context(self, memories: List[Dict[str, Any]], 
                             current_task: Dict[str, Any], 
                             agent_role: str) -> Dict[str, Any]:
        """Compact context using specified strategy"""
        if self.compaction_strategy == "semantic":
            return await self._semantic_compaction(memories, current_task, agent_role)
        elif self.compaction_strategy == "priority":
            return await self._priority_compaction(memories, current_task, agent_role)
        else:
            return await self._basic_compaction(memories)
    
    async def _semantic_compaction(self, memories: List[Dict[str, Any]], 
                                 current_task: Dict[str, Any], 
                                 agent_role: str) -> Dict[str, Any]:
        """Semantic compaction focusing on task-relevant information"""
        compacted = {
            "task_objective": current_task.get("objective", ""),
            "key_information": [],
            "constraints": current_task.get("constraints", {}),
            "previous_work": [],
            "next_steps": []
        }
        
        for memory in memories:
            memory_content = memory.get("content", {})
            
            # Extract semantically important information
            if self._is_high_priority(memory, agent_role):
                compacted["key_information"].append({
                    "type": memory.get("metadata", {}).get("type", ""),
                    "content": self._extract_key_points(memory_content),
                    "relevance": "high"
                })
            else:
                compacted["previous_work"].append({
                    "type": memory.get("metadata", {}).get("type", ""),
                    "summary": self._summarize_memory(memory_content)
                })
        
        return compacted
    
    async def _priority_compaction(self, memories: List[Dict[str, Any]], 
                                current_task: Dict[str, Any], 
                                agent_role: str) -> Dict[str, Any]:
        """Priority-based compaction"""
        # Sort memories by priority
        prioritized_memories = sorted(
            memories,
            key=lambda x: self._calculate_priority(x, agent_role),
            reverse=True
        )
        
        compacted = {}
        token_count = 0
        
        for memory in prioritized_memories:
            memory_tokens = self._estimate_tokens(memory)
            
            if token_count + memory_tokens <= self.max_tokens:
                memory_type = memory.get("metadata", {}).get("type", "general")
                if memory_type not in compacted:
                    compacted[memory_type] = []
                
                compacted[memory_type].append(memory.get("content", {}))
                token_count += memory_tokens
            else:
                break
        
        return compacted
    
    async def _basic_compaction(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Basic compaction - limit number of memories"""
        max_memories = self.max_tokens // 1000  # Rough estimate
        return memories[:max_memories]
    
    def _structure_context(self, compacted_context: Dict[str, Any], 
                         agent_role: str, current_task: Dict[str, Any]) -> Dict[str, Any]:
        """Structure context for agent consumption"""
        return {
            "agent_role": agent_role,
            "current_task": current_task,
            "background_information": compacted_context.get("key_information", []),
            "constraints_and_requirements": compacted_context.get("constraints", {}),
            "relevant_previous_work": compacted_context.get("previous_work", []),
            "expected_output_format": current_task.get("output_format", "json")
        }
    
    def _is_high_priority(self, memory: Dict[str, Any], agent_role: str) -> bool:
        """Determine if memory is high priority"""
        priority_indicators = [
            memory.get("metadata", {}).get("access_count", 0) > 5,
            memory.get("metadata", {}).get("importance", "normal") == "high",
            memory.get("metadata", {}).get("recently_updated", False)
        ]
        
        return any(priority_indicators)
    
    def _extract_key_points(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key points from memory content"""
        # Simplified extraction - in production, use NLP
        key_points = {}
        
        for key, value in content.items():
            if isinstance(value, (str, int, float, bool)):
                key_points[key] = value
            elif isinstance(value, list) and len(value) > 0:
                key_points[key] = value[:3]  # First 3 items
        
        return key_points
    
    def _summarize_memory(self, content: Dict[str, Any]) -> str:
        """Create a summary of memory content"""
        # Simplified summary - in production, use text summarization
        content_str = json.dumps(content)
        if len(content_str) > 200:
            return content_str[:200] + "..."
        return content_str
    
    def _calculate_priority(self, memory: Dict[str, Any], agent_role: str) -> float:
        """Calculate priority score for memory"""
        metadata = memory.get("metadata", {})
        
        score = 0.0
        score += metadata.get("access_count", 0) * 0.1
        score += 0.3 if metadata.get("importance") == "high" else 0.0
        score += 0.2 if metadata.get("recently_updated", False) else 0.0
        
        # Role-specific boosts
        if agent_role in metadata.get("relevant_agents", []):
            score += 0.5
        
        return score
    
    def _estimate_tokens(self, memory: Dict[str, Any]) -> int:
        """Estimate token count for memory"""
        content_str = json.dumps(memory)
        return len(content_str) // 4  # Rough estimate