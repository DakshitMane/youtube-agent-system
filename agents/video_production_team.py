from typing import Dict, Any, List
import asyncio
import logging
import os
from .sequential_agents import ScriptWriterAgent
from .parallel_agents import ResearchAgent, ParallelAgentExecutor
from .loop_agents import QualityValidatorAgent
from memory.session_manager import SessionManager
from tools.custom_tools import VoiceSynthesisTool, VideoEditorTool, ThumbnailGeneratorTool, AnimatedSlideGenerator

class VideoProductionTeam:
    """Orchestrate the entire video production workflow"""
    
    def __init__(self):
        self.logger = logging.getLogger("production_team")
        
        # Initialize agents
        self.script_writer = ScriptWriterAgent()
        self.quality_validator = QualityValidatorAgent()
        self.parallel_executor = ParallelAgentExecutor()
        
        # Initialize tools
        self.voice_tool = VoiceSynthesisTool()
        self.video_tool = VideoEditorTool()
        self.thumbnail_tool = ThumbnailGeneratorTool()
        self.animated_slides = AnimatedSlideGenerator()  # New animated slide generator
        
        # Research agents
        self.research_agents = [
            ResearchAgent("trends"),
            ResearchAgent("facts"), 
            ResearchAgent("competition")
        ]
    
    async def execute_workflow(self, session) -> Dict[str, Any]:
        """Execute complete video production workflow"""
        self.logger.info(f"Starting production workflow for session: {session.session_id}")
        
        try:
            # Phase 1: Research (Parallel)
            research_results = await self._execute_research_phase(session.topic)
            
            # Phase 2: Script Writing (Sequential) 
            script_result = await self._execute_script_phase(session.topic, research_results)
            
            # Phase 3: Production (Parallel)
            production_results = await self._execute_production_phase(script_result)
            
            # Phase 4: Quality Validation (Loop)
            final_assets = await self._execute_quality_phase(production_results)
            
            # Phase 5: Final Assembly
            final_video = await self._assemble_final_video(final_assets)
            
            return {
                "success": True,
                "video_url": final_video,
                "metadata": {
                    "title": script_result.get("final_script", {}).get("title", ""),
                    "duration": script_result.get("estimated_duration", 0),
                    "quality_score": final_assets.get("quality_score", 0.0)
                },
                "assets": final_assets
            }
            
        except Exception as e:
            self.logger.error(f"Production workflow failed: {str(e)}")
            raise
    
    async def _execute_research_phase(self, topic: str) -> Dict[str, Any]:
        """Execute parallel research phase"""
        self.logger.info("Starting research phase")
        
        research_tasks = [
            {"topic": topic, "research_type": "trends"},
            {"topic": topic, "research_type": "facts"},
            {"topic": topic, "research_type": "competition"}
        ]
        
        results = await self.parallel_executor.execute_parallel(
            self.research_agents, research_tasks
        )
        
        self.logger.info("Research phase completed")
        return results
    
    async def _execute_script_phase(self, topic: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sequential script writing phase"""
        self.logger.info("Starting script writing phase")
        
        script_task = {
            "topic": topic,
            "research_data": research_data,
            "duration": 600  # 10 minutes
        }
        
        result = await self.script_writer.execute(script_task)
        self.logger.info("Script writing phase completed")
        return result
    
    async def _execute_production_phase(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parallel production phase"""
        self.logger.info("Starting production phase")
        
        # Extract scenes for production
        scenes = script_data.get("final_script", {}).get("scenes", [])
        
        # Generate voiceover for each scene
        voiceover_tasks = []
        for scene in scenes:
            voiceover_text = scene.get("voiceover_text", "")
            if voiceover_text:
                voiceover_tasks.append(
                    self.voice_tool.synthesize_speech(voiceover_text)
                )
        
        # Generate thumbnail
        thumbnail_task = self.thumbnail_tool.generate_thumbnail(
            script_data.get("final_script", {}).get("title", "Video Title")
        )
        
        # Execute production tasks in parallel
        production_results = await asyncio.gather(
            *voiceover_tasks,
            thumbnail_task,
            return_exceptions=True
        )
        
        # Process results
        assets = {
            "voiceovers": production_results[:-1],  # All except thumbnail
            "thumbnail": production_results[-1],    # Last item is thumbnail
            "script": script_data,
            "scenes": scenes
        }
        
        self.logger.info("Production phase completed")
        return assets
    
    async def _execute_quality_phase(self, production_assets: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quality validation loop phase"""
        self.logger.info("Starting quality validation phase")
        
        quality_task = {
            "video_assets": production_assets,
            "quality_requirements": {
                "min_component_score": 0.7,
                "min_overall_score": 0.8
            }
        }
        
        quality_result = await self.quality_validator.execute(quality_task)
        
        # Combine assets with quality results
        final_assets = {
            **production_assets,
            "quality_assessment": quality_result,
            "quality_score": quality_result["final_quality_score"],
            "meets_standards": quality_result["meets_standards"]
        }
        
        self.logger.info("Quality validation phase completed")
        return final_assets
    
    async def _assemble_final_video(self, assets: Dict[str, Any]) -> str:
        """Assemble final video with animated slides and voiceover narration"""
        self.logger.info("Assembling final video with animated slides and narration")
        
        script = assets.get("script", {}).get("final_script", {})
        
        # Convert script sections into animated slides
        slides = self._convert_script_to_slides(script)
        
        # Create animated video with Gamma-like effects
        video_path = "output_videos/output_video.mp4"
        video_path = self.animated_slides.create_animated_video(
            slides,
            output_path=video_path,
            fps=30
        )
        
        # Generate voiceover narration for all slides
        voiceover_texts = []
        for slide in slides:
            narration = slide.get("title", "")
            content = slide.get("content", [])
            if isinstance(content, list):
                narration += " " + " ".join(content)
            voiceover_texts.append(narration)
        
        self.logger.info(f"🔊 Generating voiceover for {len(voiceover_texts)} slides")
        audio_files = await self.voice_tool.synthesize_multiple(voiceover_texts)
        
        if audio_files and len(audio_files) > 0:
            self.logger.info(f"✓ Generated {len(audio_files)} audio segments")
            try:
                # Try to merge audio with video using FFmpeg if available
                final_video = await self._merge_audio_video(video_path, audio_files)
                self.logger.info(f"✓ Final video with audio assembled: {final_video}")
                return final_video
            except Exception as e:
                self.logger.warning(f"Could not merge audio: {e}. Returning video without narration.")
                return video_path
        else:
            self.logger.warning("No audio files generated. Returning video without narration.")
            return video_path
    
    async def _merge_audio_video(self, video_path: str, audio_files: List[str]) -> str:
        """Merge audio narration with video (requires ffmpeg)"""
        try:
            import subprocess
            
            # Create a concat file for audio files
            audio_concat = "output_videos/audio_concat.txt"
            with open(audio_concat, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{os.path.abspath(audio_file)}'\n")
            
            # Concatenate all audio files
            combined_audio = "output_videos/combined_audio.wav"
            concat_cmd = [
                "ffmpeg", "-f", "concat", "-safe", "0", "-i", audio_concat,
                "-c", "aac", "-q:a", "9", combined_audio, "-y"
            ]
            
            # Run ffmpeg (silently)
            result = subprocess.run(concat_cmd, capture_output=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("✓ Audio files concatenated successfully")
                
                # Merge audio with video
                output_with_audio = "output_videos/output_video_with_audio.mp4"
                merge_cmd = [
                    "ffmpeg", "-i", video_path, "-i", combined_audio,
                    "-c:v", "copy", "-c:a", "aac", "-shortest",
                    output_with_audio, "-y"
                ]
                
                result = subprocess.run(merge_cmd, capture_output=True, timeout=600)
                
                if result.returncode == 0:
                    self.logger.info("✓ Audio merged with video successfully")
                    return output_with_audio
                else:
                    self.logger.warning(f"FFmpeg merge failed: {result.stderr.decode()}")
                    return video_path
            else:
                self.logger.warning(f"FFmpeg concat failed: {result.stderr.decode()}")
                return video_path
                
        except FileNotFoundError:
            self.logger.warning("FFmpeg not found. Install ffmpeg to enable audio merging.")
            return video_path
        except Exception as e:
            self.logger.warning(f"Audio-video merge failed: {e}")
            return video_path
    
    def _convert_script_to_slides(self, script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert script into animated slide objects"""
        slides = []
        
        # Title slide
        slides.append({
            "title": script.get("title", "Video"),
            "content": [script.get("tagline", "")],
            "duration": 5,
            "transition": "fade",
            "slide_number": 1
        })
        
        # Content slides from sections
        sections = script.get("sections", [])
        for idx, section in enumerate(sections):
            slide = {
                "title": section.get("heading", ""),
                "content": section.get("key_points", []),
                "duration": section.get("duration_seconds", 5),
                "transition": ["fade", "slide", "wipe"][idx % 3],  # Vary transitions
                "slide_number": idx + 2
            }
            slides.append(slide)
        
        # Conclusion slide
        slides.append({
            "title": "Key Takeaways",
            "content": script.get("conclusion", []) if isinstance(script.get("conclusion"), list) else [script.get("conclusion", "")],
            "duration": 5,
            "transition": "fade",
            "slide_number": len(slides) + 1
        })
        
        # Add total slides count to each
        total = len(slides)
        for slide in slides:
            slide["total_slides"] = total
        
        return slides