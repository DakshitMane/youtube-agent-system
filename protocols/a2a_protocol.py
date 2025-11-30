import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import logging
import asyncio
from pydantic import BaseModel

class AgentMessage(BaseModel):
    """Standardized message format for Agent-to-Agent communication"""
    message_id: str
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    priority: str = "normal"
    response_to: Optional[str] = None
    metadata: Dict[str, Any] = {}

class MessageResponse(BaseModel):
    """Response to an agent message"""
    response_id: str
    original_message_id: str
    sender: str
    content: Dict[str, Any]
    success: bool
    timestamp: str
    error_message: Optional[str] = None

class A2AProtocol:
    """Agent-to-Agent communication protocol"""
    
    def __init__(self, message_broker_url: str = None):
        self.logger = logging.getLogger("a2a_protocol")
        self.registered_agents: Dict[str, Callable] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_responses: Dict[str, asyncio.Future] = {}
        
        # In production, this would connect to Redis/RabbitMQ
        # self.broker = MessageBroker(message_broker_url)
    
    def register_agent(self, agent_name: str, message_handler: Callable):
        """Register an agent to receive messages"""
        self.registered_agents[agent_name] = message_handler
        self.logger.info(f"Registered agent: {agent_name}")
    
    async def send_message(self, sender: str, receiver: str, 
                         message_type: str, content: Dict[str, Any],
                         priority: str = "normal", 
                         wait_for_response: bool = False,
                         timeout: int = 30) -> Optional[MessageResponse]:
        """Send message to another agent"""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            content=content,
            timestamp=datetime.now().isoformat(),
            priority=priority
        )
        
        self.logger.debug(f"Sending message from {sender} to {receiver}: {message_type}")
        
        if wait_for_response:
            return await self._send_and_await_response(message, timeout)
        else:
            await self._queue_message(message)
            return None
    
    async def broadcast_message(self, sender: str, message_type: str, 
                              content: Dict[str, Any], 
                              target_agents: List[str] = None):
        """Broadcast message to multiple agents"""
        receivers = target_agents or list(self.registered_agents.keys())
        
        for receiver in receivers:
            if receiver != sender:  # Don't send to self
                await self.send_message(sender, receiver, message_type, content)
        
        self.logger.info(f"Broadcast message from {sender} to {len(receivers)} agents: {message_type}")
    
    async def _send_and_await_response(self, message: AgentMessage, timeout: int) -> MessageResponse:
        """Send message and wait for response"""
        response_future = asyncio.Future()
        self.pending_responses[message.message_id] = response_future
        
        await self._queue_message(message)
        
        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout waiting for response to message {message.message_id}")
            return MessageResponse(
                response_id=str(uuid.uuid4()),
                original_message_id=message.message_id,
                sender="system",
                content={},
                success=False,
                timestamp=datetime.now().isoformat(),
                error_message="Response timeout"
            )
        finally:
            self.pending_responses.pop(message.message_id, None)
    
    async def _queue_message(self, message: AgentMessage):
        """Queue message for processing"""
        await self.message_queue.put(message)
    
    async def start_message_processor(self):
        """Start processing messages from the queue"""
        self.logger.info("Starting A2A message processor")
        
        while True:
            try:
                message = await self.message_queue.get()
                await self._process_message(message)
                self.message_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")
    
    async def _process_message(self, message: AgentMessage):
        """Process a single message"""
        try:
            if message.receiver not in self.registered_agents:
                self.logger.warning(f"Unknown agent: {message.receiver}")
                await self._send_error_response(message, f"Unknown agent: {message.receiver}")
                return
            
            handler = self.registered_agents[message.receiver]
            
            # Call the handler
            if asyncio.iscoroutinefunction(handler):
                response_content = await handler(message)
            else:
                response_content = handler(message)
            
            # Send response if requested
            if message.message_id in self.pending_responses:
                response = MessageResponse(
                    response_id=str(uuid.uuid4()),
                    original_message_id=message.message_id,
                    sender=message.receiver,
                    content=response_content,
                    success=True,
                    timestamp=datetime.now().isoformat()
                )
                
                future = self.pending_responses[message.message_id]
                future.set_result(response)
            
            self.logger.debug(f"Processed message {message.message_id} for {message.receiver}")
            
        except Exception as e:
            self.logger.error(f"Error handling message {message.message_id}: {str(e)}")
            await self._send_error_response(message, str(e))
    
    async def _send_error_response(self, message: AgentMessage, error: str):
        """Send error response for failed message processing"""
        if message.message_id in self.pending_responses:
            response = MessageResponse(
                response_id=str(uuid.uuid4()),
                original_message_id=message.message_id,
                sender="system",
                content={},
                success=False,
                timestamp=datetime.now().isoformat(),
                error_message=error
            )
            
            future = self.pending_responses[message.message_id]
            future.set_result(response)

class MessageTemplates:
    """Pre-defined message templates for common agent communications"""
    
    @staticmethod
    def research_request(topic: str, research_type: str) -> Dict[str, Any]:
        """Template for research requests"""
        return {
            "action": "research",
            "topic": topic,
            "research_type": research_type,
            "requirements": {
                "depth": "comprehensive",
                "sources": ["academic", "news", "trends"]
            }
        }
    
    @staticmethod
    def script_review_request(script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Template for script review requests"""
        return {
            "action": "review_script",
            "script_data": script_data,
            "review_aspects": ["clarity", "engagement", "accuracy", "structure"]
        }
    
    @staticmethod
    def quality_validation_request(assets: Dict[str, Any]) -> Dict[str, Any]:
        """Template for quality validation requests"""
        return {
            "action": "validate_quality",
            "assets": assets,
            "quality_standards": {
                "min_score": 0.7,
                "required_components": ["script", "audio", "visuals"]
            }
        }
    
    @staticmethod
    def production_request(script: Dict[str, Any], assets: List[str]) -> Dict[str, Any]:
        """Template for production requests"""
        return {
            "action": "produce_video",
            "script": script,
            "required_assets": assets,
            "output_format": "mp4",
            "quality_preset": "youtube_hd"
        }
    
    @staticmethod
    def success_response(result: Dict[str, Any]) -> Dict[str, Any]:
        """Template for success responses"""
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error_response(error: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Template for error responses"""
        return {
            "status": "error",
            "error": error,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }