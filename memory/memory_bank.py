import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from pydantic import BaseModel

class MemoryItem(BaseModel):
    """Individual memory item"""
    id: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    accessed_at: str
    access_count: int = 0

class MemoryBank:
    """Long-term memory storage for agent system"""
    
    def __init__(self, vector_store_url: str = None):
        self.logger = logging.getLogger("memory_bank")
        self.memories: Dict[str, MemoryItem] = {}
        self.vector_store_url = vector_store_url
        
        # In production, this would connect to a vector database
        # self.vector_client = connect_to_vector_store(vector_store_url)
    
    async def store(self, key: str, content: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """Store content in memory bank"""
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        memory_item = MemoryItem(
            id=memory_id,
            content=content,
            metadata=metadata or {},
            created_at=timestamp,
            accessed_at=timestamp
        )
        
        self.memories[memory_id] = memory_item
        self.logger.debug(f"Stored memory: {memory_id}")
        
        return memory_id
    
    async def retrieve(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve specific memory by ID"""
        if memory_id not in self.memories:
            return None
        
        memory = self.memories[memory_id]
        
        # Update access information
        memory.accessed_at = datetime.now().isoformat()
        memory.access_count += 1
        
        self.logger.debug(f"Retrieved memory: {memory_id}")
        return memory
    
    async def search(self, query: Dict[str, Any], limit: int = 10) -> List[MemoryItem]:
        """Search memories based on query"""
        self.logger.debug(f"Searching memories with query: {query}")
        
        results = []
        
        for memory in self.memories.values():
            if self._matches_query(memory, query):
                results.append(memory)
            
            if len(results) >= limit:
                break
        
        # Sort by relevance (simplified - in production would use vector similarity)
        results.sort(key=lambda x: x.access_count, reverse=True)
        
        return results
    
    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing memory"""
        if memory_id not in self.memories:
            return False
        
        memory = self.memories[memory_id]
        
        # Update content and metadata
        if "content" in updates:
            memory.content.update(updates["content"])
        
        if "metadata" in updates:
            memory.metadata.update(updates["metadata"])
        
        memory.accessed_at = datetime.now().isoformat()
        
        self.logger.debug(f"Updated memory: {memory_id}")
        return True
    
    async def delete(self, memory_id: str) -> bool:
        """Delete memory by ID"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            self.logger.debug(f"Deleted memory: {memory_id}")
            return True
        return False
    
    async def get_session_memories(self, session_id: str) -> List[MemoryItem]:
        """Get all memories for a specific session"""
        return await self.search({"metadata.session_id": session_id})
    
    async def compact_context(self, session_id: str, max_tokens: int = 32000) -> Dict[str, Any]:
        """Compact context for a session to fit within token limits"""
        memories = await self.get_session_memories(session_id)
        
        if not memories:
            return {}
        
        # Sort by importance (access count + recency)
        sorted_memories = sorted(
            memories,
            key=lambda x: (
                x.access_count,
                datetime.fromisoformat(x.accessed_at).timestamp()
            ),
            reverse=True
        )
        
        # Compact memories to fit within token limits
        compacted = await self._semantic_compaction(sorted_memories, max_tokens)
        
        return compacted
    
    def _matches_query(self, memory: MemoryItem, query: Dict[str, Any]) -> bool:
        """Check if memory matches search query"""
        for key, value in query.items():
            if key.startswith("metadata."):
                # Search in metadata
                metadata_key = key[9:]  # Remove "metadata." prefix
                if memory.metadata.get(metadata_key) != value:
                    return False
            else:
                # Search in content
                if memory.content.get(key) != value:
                    return False
        
        return True
    
    async def _semantic_compaction(self, memories: List[MemoryItem], max_tokens: int) -> Dict[str, Any]:
        """Perform semantic compaction of memories"""
        # Simplified compaction - in production, use NLP to summarize/compress
        compacted = {
            "key_insights": [],
            "important_facts": [],
            "decisions_made": [],
            "remaining_tokens": max_tokens
        }
        
        token_count = 0
        
        for memory in memories:
            # Estimate token count (very simplified)
            content_str = json.dumps(memory.content)
            memory_tokens = len(content_str) // 4  # Rough estimate
            
            if token_count + memory_tokens <= max_tokens:
                # Extract key information based on memory type
                memory_type = memory.metadata.get("type", "general")
                
                if memory_type == "research":
                    compacted["key_insights"].append(memory.content.get("key_findings", []))
                elif memory_type == "decision":
                    compacted["decisions_made"].append(memory.content)
                elif memory_type == "fact":
                    compacted["important_facts"].append(memory.content)
                
                token_count += memory_tokens
            else:
                break
        
        compacted["remaining_tokens"] = max_tokens - token_count
        return compacted
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory bank statistics"""
        total_memories = len(self.memories)
        total_accesses = sum(memory.access_count for memory in self.memories.values())
        
        return {
            "total_memories": total_memories,
            "total_accesses": total_accesses,
            "average_accesses": total_accesses / max(total_memories, 1),
            "memory_types": self._get_memory_type_distribution()
        }
    
    def _get_memory_type_distribution(self) -> Dict[str, int]:
        """Get distribution of memory types"""
        distribution = {}
        for memory in self.memories.values():
            memory_type = memory.metadata.get("type", "unknown")
            distribution[memory_type] = distribution.get(memory_type, 0) + 1
        return distribution