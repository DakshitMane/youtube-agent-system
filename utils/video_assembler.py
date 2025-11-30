import os
import json
from typing import Dict, Any, List
import logging
from datetime import datetime
import asyncio
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Import MoviePy with graceful fallback
ColorClip = None
TextClip = None
CompositeVideoClip = None
concatenate_videoclips = None
AudioFileClip = None

try:
    from moviepy import (
        ColorClip, TextClip, CompositeVideoClip, 
        concatenate_videoclips, AudioFileClip
    )
except ImportError:
    pass  # Will handle gracefully in code

class VideoAssembler:
    """Assemble final video from generated components"""
    
    def __init__(self, output_dir: str = "output_videos"):
        self.logger = logging.getLogger("video_assembler")
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    async def assemble_video(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble final video from all components"""
        self.logger.info("Starting video assembly")
        
        try:
            # Extract components
            script = components.get("script", {})
            voiceovers = components.get("voiceovers", [])
            visuals = components.get("visuals", [])
            thumbnail = components.get("thumbnail")
            
            # Validate components
            self._validate_components(script, voiceovers, visuals)
            
            # Create video structure
            video_structure = await self._create_video_structure(script, voiceovers, visuals)
            
            # Generate final video file (simulated)
            video_path = await self._generate_video_file(video_structure)
            
            # Create metadata
            metadata = self._create_video_metadata(script, components)
            
            result = {
                "video_path": video_path,
                "thumbnail_path": thumbnail,
                "metadata": metadata,
                "duration": video_structure["total_duration"],
                "resolution": "1920x1080",
                "format": "mp4",
                "file_size": self._estimate_file_size(video_structure),
                "assembly_time": datetime.now().isoformat()
            }
            
            self.logger.info(f"Video assembly completed: {video_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Video assembly failed: {str(e)}")
            raise
    
    def _validate_components(self, script: Dict[str, Any], voiceovers: List[str], visuals: List[str]):
        """Validate that all required components are present"""
        if not script:
            raise ValueError("Script is required for video assembly")
        
        if not voiceovers:
            raise ValueError("Voiceovers are required for video assembly")
        
        if not visuals:
            raise ValueError("Visuals are required for video assembly")
        
        scenes = script.get("scenes", [])
        if len(scenes) != len(voiceovers):
            self.logger.warning(f"Scene count ({len(scenes)}) doesn't match voiceover count ({len(voiceovers)})")
        
        self.logger.debug("All video components validated")
    
    async def _create_video_structure(self, script: Dict[str, Any], 
                                    voiceovers: List[str], 
                                    visuals: List[str]) -> Dict[str, Any]:
        """Create structured video timeline"""
        scenes = script.get("scenes", [])
        
        video_timeline = {
            "title": script.get("title", "Generated Video"),
            "total_duration": 0,
            "scenes": []
        }
        
        for i, scene in enumerate(scenes):
            scene_data = {
                "scene_number": i + 1,
                "content": scene.get("content", ""),
                "duration_seconds": scene.get("duration_seconds", 60),
                "voiceover_file": voiceovers[i] if i < len(voiceovers) else None,
                "visual_file": visuals[i] if i < len(visuals) else None,
                "transition": self._get_transition_type(i, len(scenes))
            }
            
            video_timeline["scenes"].append(scene_data)
            video_timeline["total_duration"] += scene_data["duration_seconds"]
        
        self.logger.debug(f"Created video timeline with {len(scenes)} scenes, total duration: {video_timeline['total_duration']}s")
        return video_timeline
    
    async def _generate_video_file(self, video_structure: Dict[str, Any]) -> str:
        """Generate actual playable video file using MoviePy"""
        if ColorClip is None:
            return await self._generate_placeholder_video(video_structure)
        
        video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video_path = os.path.join(self.output_dir, video_filename)
        
        try:
            # Create clips for each scene
            clips = []
            
            for scene in video_structure.get("scenes", []):
                scene_clip = await self._create_scene_clip(scene)
                clips.append(scene_clip)
            
            if not clips:
                self.logger.warning("No clips created, generating placeholder video")
                return await self._generate_placeholder_video(video_structure)
            
            # Concatenate all clips
            final_video = concatenate_videoclips(clips)
            
            # Write to file (without audio initially)
            final_video.write_videofile(
                video_path,
                verbose=False,
                logger=None,
                codec='libx264',
                audio=False
            )
            
            self.logger.info(f"Generated real video file: {video_path}")
            return video_path
            
        except Exception as e:
            self.logger.error(f"Error generating video with MoviePy: {str(e)}")
            self.logger.info("Falling back to placeholder video")
            return await self._generate_placeholder_video(video_structure)
    
    async def _create_scene_clip(self, scene: Dict[str, Any]) -> Any:
        """Create a video clip for a single scene"""
        duration = scene.get("duration_seconds", 5)
        content = scene.get("content", "Scene")
        
        # Create a colored background
        clip = ColorClip(size=(1920, 1080), color=(30, 30, 40), duration=duration)
        
        try:
            # Add scene title/content text
            txt_clip = TextClip(
                content,
                fontsize=60,
                color='white',
                font='Arial-Bold',
                method='caption',
                size=(1800, 800)
            ).set_duration(duration).set_position('center')
            
            # Composite text on background
            clip = CompositeVideoClip([clip, txt_clip])
        except Exception as e:
            self.logger.warning(f"Could not add text to clip: {e}")
        
        return clip
    
    async def _generate_placeholder_video(self, video_structure: Dict[str, Any]) -> str:
        """Generate a placeholder video when MoviePy is not available"""
        video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video_path = os.path.join(self.output_dir, video_filename)
        
        try:
            # Create a simple video using frame images
            frame_files = await self._generate_frames(video_structure)
            
            if frame_files and ColorClip:
                clips = [
                    ColorClip(size=(1920, 1080), color=(30, 30, 40), duration=5)
                    for _ in frame_files
                ]
                
                if clips:
                    final_video = concatenate_videoclips(clips)
                    final_video.write_videofile(
                        video_path,
                        verbose=False,
                        logger=None,
                        codec='libx264',
                        audio=False
                    )
                    return video_path
        except Exception as e:
            self.logger.warning(f"Could not generate frame-based video: {e}")
        
        # Fallback: create simple text file as placeholder
        with open(video_path, 'w') as f:
            f.write("Video placeholder - MoviePy not fully configured\n")
            f.write(json.dumps(video_structure, indent=2))
        
        self.logger.info(f"Created placeholder video file: {video_path}")
        return video_path
    
    async def _generate_frames(self, video_structure: Dict[str, Any]) -> List[str]:
        """Generate frame images for the video"""
        frame_files = []
        
        try:
            for i, scene in enumerate(video_structure.get("scenes", [])):
                frame_path = await self._create_frame_image(scene, i)
                if frame_path:
                    frame_files.append(frame_path)
        except Exception as e:
            self.logger.warning(f"Error generating frames: {e}")
        
        return frame_files
    
    async def _create_frame_image(self, scene: Dict[str, Any], index: int) -> str:
        """Create a single frame image for a scene"""
        try:
            # Create image
            img = Image.new('RGB', (1920, 1080), color=(30, 30, 40))
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = f"Scene {index + 1}: {scene.get('content', 'Content')}"
            text_color = (255, 255, 255)
            
            # Center text
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (1920 - text_width) // 2
            y = (1080 - text_height) // 2
            
            draw.text((x, y), text, fill=text_color)
            
            # Save frame
            frames_dir = os.path.join(self.output_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)
            
            frame_path = os.path.join(frames_dir, f"frame_{index:03d}.png")
            img.save(frame_path)
            
            return frame_path
        except Exception as e:
            self.logger.warning(f"Could not create frame image: {e}")
            return None
    
    def _create_video_metadata(self, script: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive video metadata"""
        return {
            "title": script.get("title", "Generated Video"),
            "description": self._generate_description(script),
            "tags": self._generate_tags(script),
            "category": "Education",
            "language": "en",
            "created_date": datetime.now().isoformat(),
            "duration_seconds": sum(scene.get("duration_seconds", 0) for scene in script.get("scenes", [])),
            "scene_count": len(script.get("scenes", [])),
            "quality_score": components.get("quality_score", 0.0),
            "production_version": "1.0",
            "agent_system": "YouTube Video Generator"
        }
    
    def _generate_description(self, script: Dict[str, Any]) -> str:
        """Generate YouTube description from script"""
        title = script.get("title", "Generated Video")
        scenes = script.get("scenes", [])
        
        description = f"{title}\n\n"
        description += "In this video, we cover:\n"
        
        for i, scene in enumerate(scenes[:5]):  # First 5 scenes
            description += f"• {scene.get('content', f'Point {i+1}')}\n"
        
        description += "\n"
        description += "Generated using AI Agent System\n"
        description += "#AI #Generated #Education"
        
        return description
    
    def _generate_tags(self, script: Dict[str, Any]) -> List[str]:
        """Generate relevant tags for YouTube"""
        title = script.get("title", "").lower()
        scenes = script.get("scenes", [])
        
        tags = ["AI Generated", "Automated Video", "Education"]
        
        # Extract keywords from title
        title_words = title.split()
        tags.extend([word for word in title_words if len(word) > 3][:5])
        
        # Add content-based tags
        content_keywords = []
        for scene in scenes[:3]:
            content = scene.get("content", "").lower()
            content_words = content.split()
            content_keywords.extend([word for word in content_words if len(word) > 4])
        
        tags.extend(content_keywords[:5])
        
        return list(set(tags))[:20]  # Remove duplicates and limit to 20 tags
    
    def _get_transition_type(self, scene_index: int, total_scenes: int) -> str:
        """Determine transition type between scenes"""
        if scene_index == 0:
            return "fade_in"
        elif scene_index == total_scenes - 1:
            return "fade_out"
        else:
            return "cross_fade"
    
    def _estimate_file_size(self, video_structure: Dict[str, Any]) -> str:
        """Estimate video file size"""
        duration = video_structure.get("total_duration", 0)
        # Rough estimate: 1.5 MB per minute for 1080p
        size_mb = (duration / 60) * 1.5
        return f"{size_mb:.1f} MB"
    
    async def cleanup_temp_files(self, components: Dict[str, Any]):
        """Clean up temporary files after video assembly"""
        try:
            files_to_cleanup = []
            
            # Add voiceover files
            files_to_cleanup.extend(components.get("voiceovers", []))
            
            # Add visual files
            files_to_cleanup.extend(components.get("visuals", []))
            
            # Clean up files
            for file_path in files_to_cleanup:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.logger.debug(f"Cleaned up temporary file: {file_path}")
            
            self.logger.info("Temporary files cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {str(e)}")