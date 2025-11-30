from .base_agent import BaseAgent
from typing import Dict, Any, List
import asyncio

class ScriptWriterAgent(BaseAgent):
    """Sequential agent for writing video scripts"""
    
    def __init__(self):
        super().__init__("script_writer", "Write engaging YouTube scripts")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        research_data = task.get("research_data", {})
        topic = task.get("topic", "")
        duration = task.get("duration", 600)
        
        self.logger.info(f"Writing script for: {topic}")
        
        # Step 1: Outline creation
        outline = await self._create_outline(research_data, topic, duration)
        
        # Step 2: Scene development
        scenes = await self._develop_scenes(outline, research_data)
        
        # Step 3: Script polishing
        final_script = await self._polish_script(scenes)
        
        return {
            "outline": outline,
            "scenes": scenes,
            "final_script": final_script,
            "estimated_duration": self._calculate_duration(scenes)
        }
    
    async def _create_outline(self, research: Dict, topic: str, duration: int) -> Dict[str, Any]:
        """Create detailed outline based on topic"""
        await asyncio.sleep(0.5)
        
        # Generate topic-specific content
        outline_content = self._generate_topic_specific_outline(topic, duration)
        
        return outline_content
    
    def _generate_topic_specific_outline(self, topic: str, duration: int) -> Dict[str, Any]:
        """Generate specific content for the given topic"""
        
        # Extract key concepts from topic
        topic_lower = topic.lower()
        
        # Generate contextual hook and introduction
        if "video generator" in topic_lower or "ai agent" in topic_lower:
            hook = f"Discover the Future: {topic.split('-')[0].strip()}"
            intro = f"In this video, we explore {topic}. Learn how AI agents revolutionize content creation and automation."
            points = [
                {
                    "point": "Understanding Multi-Agent Architecture",
                    "duration": duration * 0.3,
                    "details": "Multi-agent systems combine multiple specialized AI agents working together. Each agent has specific responsibilities: research, writing, production, and quality control. This distributed approach ensures comprehensive content generation with diverse perspectives and expertise."
                },
                {
                    "point": "Script Writing and Content Generation",
                    "duration": duration * 0.35,
                    "details": "The script writer agent analyzes research data to create compelling narratives. It structures content logically, creates engaging hooks, develops key points with supporting details, and crafts memorable conclusions. The agent ensures pacing matches video duration and maintains audience engagement throughout."
                },
                {
                    "point": "Video Production and Assembly",
                    "duration": duration * 0.25,
                    "details": "Once the script is ready, production agents handle visual creation. They generate animated slides, add text overlays, create transitions, and assemble final videos. Quality validation ensures all components meet professional standards before delivery."
                },
                {
                    "point": "Benefits and Real-World Applications",
                    "duration": duration * 0.1,
                    "details": "Automated video generation saves time and resources. It enables rapid content creation for education, marketing, and entertainment. Multi-agent systems adapt to different topics and styles automatically."
                }
            ]
            conclusion = f"This system demonstrates how AI agents can collaborate to create professional, topic-specific content automatically. {topic.split('-')[0].strip()} represents the future of content creation."
            
        elif "ai" in topic_lower or "agent" in topic_lower or "automation" in topic_lower:
            hook = f"AI Revolution: {topic}"
            intro = f"Explore {topic} and understand how artificial intelligence transforms industries."
            points = [
                {
                    "point": "What is AI and How Does It Work?",
                    "duration": duration * 0.25,
                    "details": "AI systems learn from data and make intelligent decisions. They process information, identify patterns, and generate insights. Modern AI uses machine learning and neural networks to continuously improve."
                },
                {
                    "point": "Key Applications in Business",
                    "duration": duration * 0.35,
                    "details": "AI powers automation, analytics, customer service, and content creation. Companies use AI to reduce costs, improve quality, and accelerate innovation. Real-world examples show measurable ROI."
                },
                {
                    "point": "Challenges and Future Outlook",
                    "duration": duration * 0.25,
                    "details": "AI faces challenges around bias, interpretability, and ethics. Future developments will address these concerns. The AI industry continues to evolve with breakthrough innovations."
                },
                {
                    "point": "How You Can Get Started",
                    "duration": duration * 0.15,
                    "details": "Learn AI fundamentals through online courses. Start with Python and machine learning libraries. Build projects that solve real problems. Join the AI community and stay updated."
                }
            ]
            conclusion = f"{topic} is reshaping our world. Understanding these technologies positions you for future success."
            
        else:
            # Generic outline for other topics
            hook = f"Essential Guide to {topic}"
            intro = f"This comprehensive video covers {topic} in detail."
            points = [
                {
                    "point": f"Introduction to {topic}",
                    "duration": duration * 0.25,
                    "details": f"Understand the fundamentals of {topic}. Learn key concepts and terminology."
                },
                {
                    "point": f"Core Principles of {topic}",
                    "duration": duration * 0.35,
                    "details": f"Explore the main principles and best practices for {topic}."
                },
                {
                    "point": f"Practical Applications",
                    "duration": duration * 0.25,
                    "details": f"See real-world examples of {topic} in action."
                },
                {
                    "point": f"Next Steps and Resources",
                    "duration": duration * 0.15,
                    "details": f"Learn how to apply {topic} in your own projects."
                }
            ]
            conclusion = f"{topic} is an important skill for the modern world. Start learning today!"
        
        return {
            "hook": hook,
            "introduction": intro,
            "main_points": points,
            "conclusion": conclusion,
            "topic": topic
        }
    
    async def _develop_scenes(self, outline: Dict, research: Dict) -> List[Dict]:
        """Develop detailed scenes from outline"""
        await asyncio.sleep(0.5)
        
        scenes = []
        
        # Title scene
        scenes.append({
            "scene_number": 0,
            "type": "title",
            "title": outline.get("topic", "Video"),
            "subtitle": outline.get("hook", ""),
            "duration_seconds": 5,
            "content": f"🎬 {outline.get('hook', '')}",
            "voiceover_text": outline.get("introduction", "")
        })
        
        # Main point scenes
        for i, point in enumerate(outline.get("main_points", [])):
            scenes.append({
                "scene_number": i + 1,
                "type": "content",
                "title": point.get("point", ""),
                "content": point.get("details", point.get("point", "")),
                "duration_seconds": int(point.get("duration", 10)),
                "voiceover_text": point.get("details", ""),
                "key_points": self._extract_key_points(point.get("details", ""))
            })
        
        # Conclusion scene
        scenes.append({
            "scene_number": len(outline.get("main_points", [])) + 1,
            "type": "conclusion",
            "title": "Key Takeaways",
            "content": outline.get("conclusion", ""),
            "duration_seconds": 5,
            "voiceover_text": outline.get("conclusion", "")
        })
        
        return scenes
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from detailed text"""
        # Split text into sentences and take important ones
        sentences = text.split(". ")
        key_points = []
        
        for sentence in sentences[:3]:  # Take first 3 sentences as key points
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                # Shorten if too long
                if len(sentence) > 100:
                    sentence = sentence[:100] + "..."
                key_points.append(sentence)
        
        return key_points if key_points else [text[:100]]
    
    async def _polish_script(self, scenes: List[Dict]) -> Dict[str, Any]:
        """Polish script and format for video generation"""
        await asyncio.sleep(0.5)
        
        # Organize scenes into sections
        sections = []
        for scene in scenes:
            if scene.get("type") != "title":
                sections.append({
                    "heading": scene.get("title", ""),
                    "key_points": scene.get("key_points", [scene.get("content", "")]),
                    "duration_seconds": scene.get("duration_seconds", 10),
                    "voiceover": scene.get("voiceover_text", "")
                })
        
        # Get first scene (title)
        title_scene = next((s for s in scenes if s.get("type") == "title"), None)
        tagline = title_scene.get("subtitle", "") if title_scene else ""
        
        # Get conclusion
        conclusion_scene = next((s for s in scenes if s.get("type") == "conclusion"), None)
        conclusion = [conclusion_scene.get("content", "")] if conclusion_scene else []
        
        return {
            "title": title_scene.get("title", "Video") if title_scene else "Video",
            "tagline": tagline,
            "total_duration": sum(scene["duration_seconds"] for scene in scenes),
            "sections": sections,
            "conclusion": conclusion,
            "target_audience": "General audience",
            "style": "Educational and engaging",
            "created_at": __import__('datetime').datetime.now().isoformat()
        }
    
    def _calculate_duration(self, scenes: List[Dict]) -> int:
        return sum(scene["duration_seconds"] for scene in scenes)