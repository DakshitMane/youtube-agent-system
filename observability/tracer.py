import time
import uuid
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
import logging
from functools import wraps

class Span:
    """Represents a single operation in a trace"""
    
    def __init__(self, trace_id: str, span_id: str, name: str, parent_id: str = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.name = name
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.attributes: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.status: str = "started"
    
    def end(self, status: str = "completed"):
        """End the span"""
        self.end_time = time.time()
        self.status = status
    
    def add_attribute(self, key: str, value: Any):
        """Add attribute to span"""
        self.attributes[key] = value
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add event to span"""
        self.events.append({
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "attributes": attributes or {}
        })
    
    def get_duration(self) -> float:
        """Get span duration in seconds"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

class Tracer:
    """Distributed tracing for agent system"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger("tracer")
        self.current_spans: Dict[str, Span] = {}
    
    def start_span(self, name: str, parent_span_id: str = None, attributes: Dict[str, Any] = None) -> str:
        """Start a new span"""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        span = Span(trace_id, span_id, name, parent_span_id)
        
        if attributes:
            for key, value in attributes.items():
                span.add_attribute(key, value)
        
        self.current_spans[span_id] = span
        
        self.logger.debug(f"Started span: {name} (id: {span_id})")
        return span_id
    
    def end_span(self, span_id: str, status: str = "completed", attributes: Dict[str, Any] = None):
        """End a span"""
        if span_id not in self.current_spans:
            self.logger.warning(f"Attempted to end unknown span: {span_id}")
            return
        
        span = self.current_spans[span_id]
        
        if attributes:
            for key, value in attributes.items():
                span.add_attribute(key, value)
        
        span.end(status)
        
        # Log span completion
        self._log_span(span)
        
        # Remove from current spans
        del self.current_spans[span_id]
    
    def add_span_attribute(self, span_id: str, key: str, value: Any):
        """Add attribute to existing span"""
        if span_id in self.current_spans:
            self.current_spans[span_id].add_attribute(key, value)
    
    def add_span_event(self, span_id: str, event_name: str, attributes: Dict[str, Any] = None):
        """Add event to existing span"""
        if span_id in self.current_spans:
            self.current_spans[span_id].add_event(event_name, attributes)
    
    def trace_function(self, name: str = None, attributes: Dict[str, Any] = None):
        """Decorator to trace function execution"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"
                span_id = self.start_span(span_name, attributes=attributes)
                
                try:
                    result = await func(*args, **kwargs)
                    self.end_span(span_id, "completed")
                    return result
                except Exception as e:
                    self.end_span(span_id, "error", {"error": str(e)})
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"
                span_id = self.start_span(span_name, attributes=attributes)
                
                try:
                    result = func(*args, **kwargs)
                    self.end_span(span_id, "completed")
                    return result
                except Exception as e:
                    self.end_span(span_id, "error", {"error": str(e)})
                    raise
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def _log_span(self, span: Span):
        """Log span information"""
        span_data = {
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "name": span.name,
            "parent_id": span.parent_id,
            "duration_seconds": span.get_duration(),
            "status": span.status,
            "attributes": span.attributes,
            "events_count": len(span.events),
            "service": self.service_name,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Span completed: {json.dumps(span_data)}")
    
    def get_trace_tree(self, trace_id: str) -> Dict[str, Any]:
        """Get complete trace tree (simplified implementation)"""
        # In production, this would query a trace database
        spans = [span for span in self.current_spans.values() if span.trace_id == trace_id]
        
        return {
            "trace_id": trace_id,
            "spans": [
                {
                    "span_id": span.span_id,
                    "name": span.name,
                    "parent_id": span.parent_id,
                    "duration": span.get_duration(),
                    "status": span.status
                }
                for span in spans
            ],
            "total_spans": len(spans),
            "service": self.service_name
        }

# Global tracer instance
global_tracer: Optional[Tracer] = None

def setup_tracing(service_name: str) -> Tracer:
    """Setup global tracing"""
    global global_tracer
    global_tracer = Tracer(service_name)
    return global_tracer

def get_tracer() -> Tracer:
    """Get global tracer instance"""
    if global_tracer is None:
        raise RuntimeError("Tracer not initialized. Call setup_tracing first.")
    return global_tracer