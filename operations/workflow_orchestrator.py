from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStep:
    """Represents a single step in the workflow"""
    
    def __init__(self, step_id: str, agent_name: str, task: Dict[str, Any], 
                 dependencies: List[str] = None):
        self.step_id = step_id
        self.agent_name = agent_name
        self.task = task
        self.dependencies = dependencies or []
        self.status = WorkflowStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

class WorkflowOrchestrator:
    """Orchestrate complex multi-agent workflows"""
    
    def __init__(self, session_manager, a2a_protocol):
        self.logger = logging.getLogger("workflow_orchestrator")
        self.session_manager = session_manager
        self.a2a_protocol = a2a_protocol
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
    async def create_video_production_workflow(self, session_id: str, topic: str) -> str:
        """Create a video production workflow"""
        workflow_id = f"workflow_{session_id}"
        
        workflow = {
            "workflow_id": workflow_id,
            "session_id": session_id,
            "topic": topic,
            "status": WorkflowStatus.PENDING,
            "steps": self._create_production_steps(topic),
            "created_at": datetime.now().isoformat(),
            "current_step": None,
            "results": {}
        }
        
        self.active_workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow {workflow_id} for topic: {topic}")
        
        return workflow_id
    
    def _create_production_steps(self, topic: str) -> Dict[str, WorkflowStep]:
        """Create the steps for video production workflow"""
        steps = {
            "research_trends": WorkflowStep(
                step_id="research_trends",
                agent_name="researcher_trends",
                task={"topic": topic, "research_type": "trends"}
            ),
            "research_facts": WorkflowStep(
                step_id="research_facts", 
                agent_name="researcher_facts",
                task={"topic": topic, "research_type": "facts"}
            ),
            "research_competition": WorkflowStep(
                step_id="research_competition",
                agent_name="researcher_competition", 
                task={"topic": topic, "research_type": "competition"}
            ),
            "script_writing": WorkflowStep(
                step_id="script_writing",
                agent_name="script_writer",
                task={"topic": topic},
                dependencies=["research_trends", "research_facts", "research_competition"]
            ),
            "voiceover_production": WorkflowStep(
                step_id="voiceover_production",
                agent_name="voice_synthesizer", 
                task={},
                dependencies=["script_writing"]
            ),
            "visual_production": WorkflowStep(
                step_id="visual_production",
                agent_name="video_editor",
                task={},
                dependencies=["script_writing"]
            ),
            "thumbnail_creation": WorkflowStep(
                step_id="thumbnail_creation",
                agent_name="thumbnail_generator",
                task={},
                dependencies=["script_writing"]
            ),
            "quality_validation": WorkflowStep(
                step_id="quality_validation", 
                agent_name="quality_validator",
                task={},
                dependencies=["voiceover_production", "visual_production", "thumbnail_creation"]
            ),
            "final_assembly": WorkflowStep(
                step_id="final_assembly",
                agent_name="video_assembler",
                task={},
                dependencies=["quality_validation"]
            )
        }
        
        return steps
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute the complete workflow"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = WorkflowStatus.RUNNING
        
        self.logger.info(f"Starting workflow execution: {workflow_id}")
        
        try:
            # Execute steps in dependency order
            executed_steps = set()
            total_steps = len(workflow["steps"])
            
            while len(executed_steps) < total_steps:
                # Find ready steps (all dependencies satisfied)
                ready_steps = [
                    step for step in workflow["steps"].values()
                    if (step.step_id not in executed_steps and
                        all(dep in executed_steps for dep in step.dependencies))
                ]
                
                if not ready_steps:
                    # Check for circular dependencies or deadlock
                    pending_steps = [
                        step_id for step_id in workflow["steps"]
                        if step_id not in executed_steps
                    ]
                    self.logger.warning(f"No ready steps found. Pending: {pending_steps}")
                    break
                
                # Execute ready steps in parallel
                execution_tasks = []
                for step in ready_steps:
                    task = self._execute_workflow_step(workflow_id, step)
                    execution_tasks.append(task)
                
                # Wait for all parallel steps to complete
                step_results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                
                # Process results
                for step, result in zip(ready_steps, step_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Step {step.step_id} failed: {str(result)}")
                        step.status = WorkflowStatus.FAILED
                        step.error = str(result)
                    else:
                        step.status = WorkflowStatus.COMPLETED
                        step.result = result
                        executed_steps.add(step.step_id)
                        workflow["results"][step.step_id] = result
                    
                    self.logger.info(f"Step {step.step_id} completed with status: {step.status}")
            
            # Check if all steps completed successfully
            failed_steps = [
                step_id for step_id, step in workflow["steps"].items()
                if step.status == WorkflowStatus.FAILED
            ]
            
            if failed_steps:
                workflow["status"] = WorkflowStatus.FAILED
                self.logger.error(f"Workflow failed due to steps: {failed_steps}")
            else:
                workflow["status"] = WorkflowStatus.COMPLETED
                self.logger.info(f"Workflow completed successfully: {workflow_id}")
            
            return workflow["results"]
            
        except Exception as e:
            workflow["status"] = WorkflowStatus.FAILED
            self.logger.error(f"Workflow execution failed: {str(e)}")
            raise
    
    async def _execute_workflow_step(self, workflow_id: str, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step"""
        self.logger.info(f"Executing step: {step.step_id} with agent: {step.agent_name}")
        
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.now()
        
        try:
            # Send message to the appropriate agent
            response = await self.a2a_protocol.send_message(
                sender="workflow_orchestrator",
                receiver=step.agent_name,
                message_type="execute_task",
                content=step.task,
                wait_for_response=True,
                timeout=300  # 5 minute timeout
            )
            
            if response and response.success:
                step.completed_at = datetime.now()
                return response.content
            else:
                error_msg = response.error_message if response else "No response received"
                raise Exception(f"Agent execution failed: {error_msg}")
                
        except Exception as e:
            step.completed_at = datetime.now()
            step.error = str(e)
            raise
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        if workflow["status"] == WorkflowStatus.RUNNING:
            workflow["status"] = WorkflowStatus.PAUSED
            self.logger.info(f"Workflow paused: {workflow_id}")
            return True
        
        return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        if workflow["status"] == WorkflowStatus.PAUSED:
            workflow["status"] = WorkflowStatus.RUNNING
            self.logger.info(f"Workflow resumed: {workflow_id}")
            
            # Continue execution from where we left off
            asyncio.create_task(self.execute_workflow(workflow_id))
            return True
        
        return False
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = WorkflowStatus.CANCELLED
        
        self.logger.info(f"Workflow cancelled: {workflow_id}")
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.active_workflows[workflow_id]
        
        # Calculate progress
        total_steps = len(workflow["steps"])
        completed_steps = sum(
            1 for step in workflow["steps"].values()
            if step.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]
        )
        
        progress = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"].value,
            "progress": round(progress, 2),
            "current_step": workflow.get("current_step"),
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "created_at": workflow["created_at"],
            "step_details": {
                step_id: {
                    "status": step.status.value,
                    "agent": step.agent_name,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error": step.error
                }
                for step_id, step in workflow["steps"].items()
            }
        }
    
    def get_workflow_results(self, workflow_id: str) -> Dict[str, Any]:
        """Get results from completed workflow"""
        status = self.get_workflow_status(workflow_id)
        
        if status["status"] != "completed":
            return {"error": "Workflow not completed"}
        
        workflow = self.active_workflows[workflow_id]
        return workflow["results"]