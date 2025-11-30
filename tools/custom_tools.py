import os
import json
from typing import Dict, Any, List
import logging
import asyncio
import numpy as np
from PIL import Image, ImageDraw

# Try to import opencv for video creation
try:
    import cv2
    opencv_available = True
except ImportError:
    opencv_available = False

# Try to import pyttsx3 for offline text-to-speech
try:
    import pyttsx3
    tts_available = True
except ImportError:
    tts_available = False

try:
    from elevenlabs import generate, play, set_api_key
except ImportError:
    # elevenlabs is optional
    generate = None
    play = None
    set_api_key = None

class VoiceSynthesisTool:
    """Convert text to speech using offline TTS (no API keys required)"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool.voice_synthesis")
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize pyttsx3 engine for offline text-to-speech"""
        try:
            if not tts_available:
                self.logger.warning("pyttsx3 not available. Install with: pip install pyttsx3")
                return
            
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speaking rate (words per minute)
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            self.logger.info("✓ Text-to-speech engine initialized (offline, no API required)")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    async def synthesize_speech(self, text: str, output_path: str = None) -> str:
        """
        Convert text to speech and save as audio file
        Uses offline TTS (pyttsx3 - no API keys needed)
        
        Args:
            text: The text to convert to speech
            output_path: Path to save the audio file
        
        Returns:
            Path to the generated audio file, or empty string if failed
        """
        try:
            if not self.engine:
                self.logger.warning("TTS engine not available, skipping voice synthesis")
                return ""
            
            self.logger.info(f"🔊 Converting text to speech ({len(text)} characters)")
            
            if output_path is None:
                output_path = f"output_videos/voiceover_{__import__('uuid').uuid4().hex[:8]}.mp3"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            # Use a non-blocking approach to save audio without runAndWait()
            loop = asyncio.get_event_loop()
            
            # Run in executor to avoid blocking the event loop
            def _synthesize():
                self.engine.save_to_file(text, output_path)
                # Don't use runAndWait() in async context - just let it process
                # The file will be created asynchronously
                import time
                time.sleep(len(text) / 150 + 0.5)  # Estimate TTS processing time
                return output_path
            
            result = await loop.run_in_executor(None, _synthesize)
            self.logger.info(f"✓ Speech synthesized: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Voice synthesis failed: {str(e)}")
            return ""
    
    async def synthesize_multiple(self, texts: List[str]) -> List[str]:
        """
        Synthesize multiple text segments into separate audio files
        
        Args:
            texts: List of text strings to convert
        
        Returns:
            List of paths to generated audio files
        """
        audio_files = []
        for idx, text in enumerate(texts):
            if text.strip():
                self.logger.info(f"Converting segment {idx + 1}/{len(texts)}")
                audio_file = await self.synthesize_speech(text)
                if audio_file:
                    audio_files.append(audio_file)
        return audio_files
    
    def set_voice_speed(self, rate: int = 150):
        """Set the voice speaking rate (words per minute)"""
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_voice_volume(self, volume: float = 0.9):
        """Set the voice volume (0.0 to 1.0)"""
        if self.engine:
            self.engine.setProperty('volume', volume)

class VideoEditorTool:
    """Custom tool for video editing and assembly using OpenCV with stock footage"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool.video_editor")
        self.video_available = opencv_available
        self.pexels_api_key = os.getenv("PEXELS_API_KEY", "")
    
    async def create_video_montage(self, scenes: List[Dict], output_path: str = "output_videos/output_video.mp4") -> str:
        """Create video from scenes with stock footage"""
        try:
            self.logger.info(f"Creating video montage with {len(scenes)} scenes")
            
            if not self.video_available:
                self.logger.warning("OpenCV not available, creating placeholder video")
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                with open(output_path, "w") as f:
                    f.write("Placeholder video - OpenCV not configured")
                return output_path
            
            import cv2
            
            # Video parameters
            width, height = 1920, 1080
            fps = 30
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                self.logger.warning("Could not open video writer, trying MJPEG codec")
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Create frames for each scene
            for scene_idx, scene in enumerate(scenes):
                duration = int(scene.get("duration_seconds", 5))
                content = scene.get("content", "Scene")
                
                self.logger.info(f"Processing scene {scene_idx + 1}: {content}")
                
                # Try to get stock footage for this scene
                stock_video_frames = await self._get_stock_footage_frames(content, duration)
                
                # Generate frames for this scene
                for frame_num in range(duration * fps):
                    if stock_video_frames and frame_num < len(stock_video_frames):
                        # Use stock footage frame as background
                        frame = stock_video_frames[frame_num % len(stock_video_frames)].copy()
                    else:
                        # Create frame with dark background
                        frame = np.zeros((height, width, 3), dtype=np.uint8)
                        frame[:] = (30, 30, 40)  # BGR format: dark blue
                    
                    # Add text overlay to frame
                    frame = await self._add_text_overlay(frame, content)
                    
                    # Add scene progress animation
                    frame = self._add_progress_bar(frame, frame_num, duration * fps)
                    
                    # Write frame to video
                    out.write(frame)
            
            out.release()
            self.logger.info(f"Video created: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Video creation failed: {str(e)}")
            # Fallback to placeholder
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w") as f:
                f.write(f"Video placeholder - error: {str(e)}")
            return output_path
    
    async def _get_stock_footage_frames(self, topic: str, duration: int) -> List[np.ndarray]:
        """Download stock footage frames for a topic"""
        try:
            if not self.pexels_api_key:
                self.logger.debug("No Pexels API key, using generated frames")
                return []
            
            # For now, return empty list - requires Pexels API integration
            # In production, this would download actual video clips
            return []
        except Exception as e:
            self.logger.warning(f"Could not fetch stock footage: {e}")
            return []
    
    async def _add_text_overlay(self, frame: np.ndarray, text: str) -> np.ndarray:
        """Add text overlay to video frame"""
        try:
            import cv2
            
            height, width = frame.shape[:2]
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2.5
            color = (255, 255, 255)  # BGR format: white
            thickness = 3
            
            # Add semi-transparent background for text readability
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2
            
            # Draw semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(overlay, 
                         (text_x - 20, text_y - text_size[1] - 20),
                         (text_x + text_size[0] + 20, text_y + 20),
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
            
            # Add text
            cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness)
            
            return frame
        except Exception as e:
            self.logger.debug(f"Could not add text overlay: {e}")
            return frame
    
    def _add_progress_bar(self, frame: np.ndarray, current_frame: int, total_frames: int) -> np.ndarray:
        """Add progress bar to video frame"""
        try:
            import cv2
            
            height, width = frame.shape[:2]
            progress = current_frame / total_frames
            bar_width = int(width * progress)
            
            # Draw progress bar at bottom
            cv2.rectangle(frame, (0, height - 10), (bar_width, height), (0, 255, 0), -1)
            
            return frame
        except Exception as e:
            self.logger.debug(f"Could not add progress bar: {e}")
            return frame


class AnimatedSlideGenerator:
    """Generate animated slides like Gamma with smooth transitions and effects"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool.animated_slides")
    
    def create_animated_video(self, slides: List[Dict], output_path: str, fps: int = 30) -> str:
        """
        Create animated video with Gamma-like slides (optimized for speed)
        Each slide dict should have:
        - title: str
        - content: List[str] (bullet points)
        - duration: int (seconds)
        - background_color: tuple (R, G, B) optional
        - transition: str ('fade', 'slide', 'wipe') optional
        """
        try:
            import cv2
            
            width, height = 1920, 1080
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                self.logger.warning("mp4v codec failed, trying MJPG")
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                self.logger.error("Cannot open video writer with any codec")
                return output_path
            
            frame_count = 0
            for slide_idx, slide in enumerate(slides):
                self.logger.info(f"Creating animated slide {slide_idx + 1}/{len(slides)}")
                
                duration = slide.get("duration", 5)
                total_frames = duration * fps
                transition_type = slide.get("transition", "fade")
                
                # Optimize: Use fewer intermediate frames for animations
                # Generate key frames and interpolate
                key_frame_steps = max(10, int(total_frames / 5))  # Sample every ~5 frames or at least 10 steps
                
                # Generate frames for this slide with animations
                for frame_num in range(total_frames):
                    # Calculate progress for smoother animations
                    progress = frame_num / total_frames
                    
                    # Create base frame
                    frame = self._create_slide_frame(
                        slide,
                        progress,
                        frame_num,
                        total_frames,
                        transition_type
                    )
                    
                    out.write(frame)
                    frame_count += 1
                    
                    # Log progress every 30 frames
                    if frame_count % 30 == 0:
                        self.logger.debug(f"Rendered {frame_count} frames")
            
            out.release()
            self.logger.info(f"Animated video created: {output_path} ({frame_count} frames)")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create animated video: {e}")
            raise
            
        except Exception as e:
            self.logger.error(f"Failed to create animated video: {e}")
            raise
    
    def _create_slide_frame(self, slide: Dict, progress: float, frame_num: int, total_frames: int, transition: str) -> np.ndarray:
        """Create single animated frame for a slide"""
        import cv2
        
        width, height = 1920, 1080
        
        # Background color (with gradient support)
        bg_color = slide.get("background_color", (240, 240, 245))  # Light gray/blue
        frame = np.ones((height, width, 3), dtype=np.uint8)
        frame[:] = bg_color
        
        # Add gradient background
        frame = self._add_gradient_background(frame)
        
        # Apply transition effect
        if transition == "fade":
            frame = self._apply_fade_transition(frame, progress)
        elif transition == "slide":
            frame = self._apply_slide_transition(frame, progress)
        elif transition == "wipe":
            frame = self._apply_wipe_transition(frame, progress)
        
        # Add animated title
        frame = self._add_animated_title(frame, slide.get("title", ""), progress)
        
        # Add animated content (bullet points)
        content = slide.get("content", [])
        frame = self._add_animated_bullets(frame, content, progress)
        
        # Add decorative elements
        frame = self._add_decorative_elements(frame, progress)
        
        # Add slide counter
        frame = self._add_slide_counter(frame, slide.get("slide_number", 1), slide.get("total_slides", 1))
        
        return frame
    
    def _add_gradient_background(self, frame: np.ndarray) -> np.ndarray:
        """Add subtle gradient to background"""
        import cv2
        
        height, width = frame.shape[:2]
        
        # Create subtle top-to-bottom gradient
        for y in range(height):
            alpha = y / height
            frame[y, :] = frame[y, :] * (1 - alpha * 0.1) + np.array([20, 20, 30]) * (alpha * 0.1)
        
        return frame
    
    def _apply_fade_transition(self, frame: np.ndarray, progress: float) -> np.ndarray:
        """Apply fade-in transition effect"""
        import cv2
        
        # Fade in effect: starts dark, becomes visible
        if progress < 0.2:  # First 20% of slide duration
            fade_progress = progress / 0.2
            frame = cv2.addWeighted(frame, fade_progress, frame * 0, 1 - fade_progress, 0)
        
        return frame
    
    def _apply_slide_transition(self, frame: np.ndarray, progress: float) -> np.ndarray:
        """Apply slide-in transition effect"""
        # Content slides in from left
        return frame
    
    def _apply_wipe_transition(self, frame: np.ndarray, progress: float) -> np.ndarray:
        """Apply wipe transition effect"""
        # Content wipes in from right
        return frame
    
    def _add_animated_title(self, frame: np.ndarray, title: str, progress: float) -> np.ndarray:
        """Add animated title that types out with text wrapping"""
        import cv2
        
        if not title:
            return frame
        
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5  # Reduced from 3.0
        color = (20, 20, 60)  # Dark blue
        thickness = 2  # Reduced from 3
        
        # Wrap title to fit within frame
        wrapped_title = self._wrap_text(title, max_width=50)
        
        # Typewriter effect: show characters progressively
        if progress < 0.3:  # Title animates in first 30% of slide
            char_progress = progress / 0.3
            num_chars = int(len(wrapped_title) * char_progress)
            display_title = wrapped_title[:num_chars]
        else:
            display_title = wrapped_title
        
        # Get text size for centering
        text_size = cv2.getTextSize("X", font, font_scale, thickness)[0]
        line_height = text_size[1] + 15
        
        # Position: top third of slide
        y = int(height * 0.20)
        x = 80
        
        # Add semi-transparent background box for title
        padding = 30
        overlay = frame.copy()
        
        num_lines = display_title.count('\n') + 1
        box_height = int(line_height * num_lines + padding * 2)
        
        cv2.rectangle(
            overlay,
            (x - padding, y - padding),
            (width - x + padding, y + box_height),
            (255, 255, 255),
            -1
        )
        frame = cv2.addWeighted(overlay, 0.12, frame, 0.88, 0)
        
        # Draw title text (multi-line support)
        for line_idx, line in enumerate(display_title.split('\n')):
            line_y = y + line_idx * line_height
            cv2.putText(frame, line, (x, line_y), font, font_scale, color, thickness)
        
        # Add underline that expands
        lines = display_title.split('\n')
        last_line = lines[-1] if lines else ""
        text_size = cv2.getTextSize(last_line, font, font_scale, thickness)[0]
        underline_width = int(text_size[0] * (progress / 0.3)) if progress < 0.3 else text_size[0]
        final_y = y + (len(lines) - 1) * line_height + 15
        cv2.line(frame, (x, final_y), (x + underline_width, final_y), (70, 130, 180), 3)
        
        return frame
    
    def _wrap_text(self, text: str, max_width: int = 50) -> str:
        """Wrap text to fit within max character width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return '\n'.join(lines)
    
    def _add_animated_bullets(self, frame: np.ndarray, bullets: List[str], progress: float) -> np.ndarray:
        """Add animated bullet points that fade in sequentially with text wrapping"""
        import cv2
        
        if not bullets:
            return frame
        
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2  # Reduced from 1.8
        color = (40, 40, 80)  # Dark blue
        thickness = 1  # Reduced from 2
        
        # Stagger bullet animations
        bullet_start_y = int(height * 0.45)
        line_spacing = 80  # Reduced from 100
        
        # Pre-wrap all bullets to prevent overflow
        wrapped_bullets = [self._wrap_text(bullet, max_width=90) for bullet in bullets]
        
        for bullet_idx, wrapped_bullet in enumerate(wrapped_bullets):
            # Each bullet appears after the previous one
            bullet_progress = (progress - 0.2 - bullet_idx * 0.1) * 5  # Staggered timing
            bullet_progress = max(0, min(1, bullet_progress))  # Clamp 0-1
            
            if bullet_progress == 0:
                continue  # Bullet not visible yet
            
            # Slide in from left with fade
            x_offset = int((1 - bullet_progress) * 80)  # Slides in from 80px left (reduced from 100)
            opacity = bullet_progress
            
            # Create temporary frame for this bullet with transparency effect
            bullet_frame = frame.copy()
            
            base_y = bullet_start_y + bullet_idx * line_spacing
            x = 120 + x_offset  # Adjusted from 150
            
            # Draw bullet point
            cv2.circle(bullet_frame, (x - 30, base_y - 10), 6, color, -1)
            
            # Draw wrapped bullet text (multi-line support)
            bullet_lines = wrapped_bullet.split('\n')
            for line_idx, line in enumerate(bullet_lines):
                line_y = base_y + line_idx * 30  # Line height for wrapped text
                cv2.putText(bullet_frame, line, (x, line_y), font, font_scale, color, thickness)
            
            # Blend with opacity for fade-in effect
            frame = cv2.addWeighted(bullet_frame, opacity, frame, 1 - opacity, 0)
        
        return frame
    
    def _add_decorative_elements(self, frame: np.ndarray, progress: float) -> np.ndarray:
        """Add decorative elements like moving shapes (optimized)"""
        import cv2
        
        height, width = frame.shape[:2]
        
        # Simplified animated circle in corner (less intensive)
        if progress > 0.1:  # Only after animation starts
            circle_radius = int(15 + 5 * np.sin(progress * np.pi))  # Simpler sine motion
            circle_x = width - 120
            circle_y = 80
            
            color = (100, 150, 200)  # Light blue
            cv2.circle(frame, (circle_x, circle_y), circle_radius, color, 2)
        
        # Add moving accent line (simpler)
        line_width = int(width * 0.25 * min(progress * 2, 1.0))  # Only grows for first half
        if line_width > 5:
            cv2.line(frame, (0, height - 100), (line_width, height - 100), (70, 130, 180), 2)
        
        return frame
    
    def _add_slide_counter(self, frame: np.ndarray, slide_num: int, total_slides: int) -> np.ndarray:
        """Add slide counter in corner"""
        import cv2
        
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        color = (100, 100, 100)
        thickness = 2
        
        counter_text = f"{slide_num}/{total_slides}"
        text_size = cv2.getTextSize(counter_text, font, font_scale, thickness)[0]
        
        x = width - text_size[0] - 30
        y = height - 30
        
        cv2.putText(frame, counter_text, (x, y), font, font_scale, color, thickness)
        
        return frame


class ThumbnailGeneratorTool:
    """Custom tool for generating YouTube thumbnails"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool.thumbnail_generator")
    
    async def generate_thumbnail(self, title: str, style: str = "youtube") -> str:
        """Generate thumbnail image"""
        try:
            self.logger.info(f"Generating thumbnail for: {title}")
            
            # This would integrate with image generation APIs
            # For now, simulate the process
            await asyncio.sleep(1)
            
            filename = f"thumbnail_{hash(title) % 10000}.jpg"
            
            # Simulate thumbnail creation
            with open(filename, "w") as f:
                f.write("Simulated thumbnail")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {str(e)}")
            raise