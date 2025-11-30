from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
from pydantic import BaseModel

class AgentMessage(BaseModel):
    """Standard message format for A2A communication"""
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str, config: Dict[str, Any] = None):
        self.name = name
        self.role = role
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.memory = []
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent's primary task"""
        pass
    
    def send_message(self, receiver: str, message_type: str, content: Dict[str, Any]) -> AgentMessage:
        """Send message to another agent"""
        message = AgentMessage(
            sender=self.name,
            receiver=receiver,
            message_type=message_type,
            content=content,
            timestamp=self._get_timestamp()
        )
        self.logger.debug(f"Sent message to {receiver}: {message_type}")
        return message
    
    def receive_message(self, message: AgentMessage) -> None:
        """Receive and process message from another agent"""
        self.memory.append(message)
        self.logger.debug(f"Received message from {message.sender}: {message.message_type}")
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()