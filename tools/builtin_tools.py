import os
import subprocess
import asyncio
from typing import Dict, Any, List
import logging

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = None

class GoogleSearchTool:
    """Built-in Google Search tool"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.logger = logging.getLogger("tool.google_search")
        if build is None:
            self.logger.warning("googleapiclient not installed. Install with: pip install google-api-python-client")
            self.service = None
        else:
            self.service = build("customsearch", "v1", developerKey=api_key)
    
    async def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform Google search"""
        if self.service is None:
            return {"error": "Google Search API not available. Install googleapiclient: pip install google-api-python-client"}
            
        try:
            self.logger.info(f"Searching Google for: {query}")
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.service.cse().list(
                    q=query,
                    cx=self.search_engine_id,
                    num=num_results
                ).execute()
            )
            
            items = result.get('items', [])
            search_results = []
            
            for item in items:
                search_results.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'snippet': item.get('snippet'),
                    'displayLink': item.get('displayLink')
                })
            
            self.logger.debug(f"Found {len(search_results)} search results")
            return {
                "query": query,
                "total_results": result.get('searchInformation', {}).get('totalResults', 0),
                "results": search_results
            }
            
        except Exception as e:
            if HttpError and isinstance(e, HttpError):
                self.logger.error(f"Google Search API error: {str(e)}")
                return {"error": f"Search API error: {str(e)}"}
            self.logger.error(f"Google Search failed: {str(e)}")
            return {"error": f"Search failed: {str(e)}"}

class CodeExecutionTool:
    """Built-in code execution tool"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.logger = logging.getLogger("tool.code_execution")
    
    async def execute_python(self, code: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Python code safely"""
        try:
            self.logger.info("Executing Python code")
            
            # Create a safe execution environment
            exec_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip
                }
            }
            
            if inputs:
                exec_globals.update(inputs)
            
            # Execute the code
            try:
                exec(code, exec_globals)
                output = exec_globals.get('result', 'Execution completed')
                
                return {
                    "success": True,
                    "output": str(output),
                    "error": None
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "output": None,
                    "error": f"Execution error: {str(e)}"
                }
                
        except Exception as e:
            self.logger.error(f"Code execution failed: {str(e)}")
            return {
                "success": False,
                "output": None,
                "error": f"Execution failed: {str(e)}"
            }
    
    async def execute_shell(self, command: str, working_dir: str = None) -> Dict[str, Any]:
        """Execute shell command"""
        try:
            self.logger.info(f"Executing shell command: {command}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8') if stdout else "",
                "stderr": stderr.decode('utf-8') if stderr else ""
            }
            
        except asyncio.TimeoutError:
            self.logger.error("Command execution timed out")
            return {
                "success": False,
                "error": "Command execution timed out"
            }
        except Exception as e:
            self.logger.error(f"Command execution failed: {str(e)}")
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}"
            }

class TextToSpeechTool:
    """Built-in Text-to-Speech tool"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool.text_to_speech")
    
    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> Dict[str, Any]:
        """Synthesize speech from text"""
        try:
            self.logger.info(f"Synthesizing speech for {len(text)} characters")
            
            # This would integrate with a TTS service
            # For now, simulate the process
            await asyncio.sleep(1)  # Simulate processing time
            
            # Generate a simulated audio file
            filename = f"tts_{hash(text) % 10000}.wav"
            
            # In production, this would generate actual audio
            with open(filename, 'w') as f:
                f.write(f"Simulated TTS audio for: {text[:100]}...")
            
            return {
                "success": True,
                "audio_file": filename,
                "duration_seconds": len(text) / 15,  # Rough estimate
                "voice_used": voice
            }
            
        except Exception as e:
            self.logger.error(f"TTS synthesis failed: {str(e)}")
            return {
                "success": False,
                "error": f"TTS failed: {str(e)}"
            }

class ImageGenerationTool:
    """Built-in Image Generation tool"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool.image_generation")
    
    async def generate_image(self, prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
        """Generate image from text prompt"""
        try:
            self.logger.info(f"Generating image for prompt: {prompt[:100]}...")
            
            # This would integrate with an image generation API
            # For now, simulate the process
            await asyncio.sleep(2)  # Simulate processing time
            
            # Generate a simulated image file
            filename = f"image_{hash(prompt) % 10000}.png"
            
            # In production, this would generate actual image
            with open(filename, 'w') as f:
                f.write(f"Simulated image for: {prompt}")
            
            return {
                "success": True,
                "image_file": filename,
                "size": size,
                "prompt_used": prompt
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Image generation failed: {str(e)}"
            }