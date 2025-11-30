import asyncio
from typing import Dict, Any, List, Callable
import logging
from datetime import datetime

class LongRunningOperation:
    """Manage long-running video production operations"""
    
    def __init__(self, operation_id: str, operation_type: str):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.logger = logging.getLogger(f"operation.{operation_id}")
        
        self.state = "initialized"
        self.progress = 0.0
        self.checkpoints: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
    async def execute(self, tasks: List[Callable]) -> Dict[str, Any]:
        """Execute long-running operation with pause/resume capability"""
        self.state = "running"
        self.logger.info(f"Starting operation: {self.operation_type}")
        
        results = {}
        
        for i, task in enumerate(tasks):
            if self.state == "paused":
                self.logger.info("Operation paused, waiting for resume...")
                while self.state == "paused":
                    await asyncio.sleep(1)
            
            if self.state == "cancelled":
                self.logger.info("Operation cancelled")
                break
            
            try:
                # Execute task
                result = await task()
                results[f"task_{i}"] = result
                
                # Update progress
                self.progress = (i + 1) / len(tasks)
                
                # Create checkpoint
                await self._create_checkpoint(f"task_{i}_completed", result)
                
                self.logger.debug(f"Completed task {i+1}/{len(tasks)}")
                
            except Exception as e:
                self.logger.error(f"Task {i} failed: {str(e)}")
                results[f"task_{i}"] = {"error": str(e)}
        
        self.state = "completed"
        self.progress = 1.0
        
        self.logger.info(f"Operation completed: {self.operation_type}")
        return results
    
    async def pause(self) -> bool:
        """Pause the operation"""
        if self.state == "running":
            self.state = "paused"
            await self._create_checkpoint("paused", {})
            self.logger.info("Operation paused")
            return True
        return False
    
    async def resume(self) -> bool:
        """Resume the operation"""
        if self.state == "paused":
            self.state = "running"
            await self._create_checkpoint("resumed", {})
            self.logger.info("Operation resumed")
            return True
        return False
    
    async def cancel(self) -> bool:
        """Cancel the operation"""
        self.state = "cancelled"
        self.logger.info("Operation cancelled")
        return True
    
    async def _create_checkpoint(self, checkpoint_type: str, data: Dict[str, Any]) -> None:
        """Create operation checkpoint"""
        checkpoint = {
            "type": checkpoint_type,
            "timestamp": datetime.now().isoformat(),
            "progress": self.progress,
            "state": self.state,
            "data": data
        }
        self.checkpoints.append(checkpoint)
    
    def get_status(self) -> Dict[str, Any]:
        """Get operation status"""
        return {
            "operation_id": self.operation_id,
            "type": self.operation_type,
            "state": self.state,
            "progress": self.progress,
            "checkpoints": len(self.checkpoints),
            "duration": (datetime.now() - self.start_time).total_seconds()
        }