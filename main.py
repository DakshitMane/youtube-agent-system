#!/usr/bin/env python3
"""
Main entry point for YouTube Video Generator Agent System
"""

import asyncio
import logging
from dotenv import load_dotenv
from agents.video_production_team import VideoProductionTeam
from memory.session_manager import SessionManager
from observability.logger import setup_logging

# Load environment variables
load_dotenv()

class YouTubeVideoGenerator:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.session_manager = SessionManager()
        self.production_team = VideoProductionTeam()
    
    async def generate_video(self, topic: str, duration: int = 600) -> dict:
        """Generate a complete YouTube video"""
        self.logger.info(f"Starting video generation for topic: {topic}")
        
        # Create new session
        session = await self.session_manager.create_session(
            topic=topic,
            target_duration=duration
        )
        
        try:
            # Execute video production workflow
            result = await self.production_team.execute_workflow(session)
            
            self.logger.info("Video generation completed successfully")
            return {
                "success": True,
                "session_id": session.session_id,
                "video_url": result.get("video_url"),
                "metadata": result.get("metadata"),
                "assets": result.get("assets")
            }
            
        except Exception as e:
            self.logger.error(f"Video generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session.session_id
            }

async def main():
    """Interactive video generation"""
    generator = YouTubeVideoGenerator()
    
    print("\n" + "="*60)
    print("🎬 YouTube Agent System - Video Generator")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Generate a new video")
        print("2. Exit")
        
        choice = input("\nSelect an option (1-2): ").strip()
        
        if choice == "2":
            print("Goodbye! 👋")
            break
        elif choice == "1":
            # Get topic from user
            topic = input("\nEnter the video topic: ").strip()
            
            if not topic:
                print("❌ Topic cannot be empty. Please try again.")
                continue
            
            # Get duration (optional)
            duration_input = input("Enter video duration in seconds (default: 600): ").strip()
            try:
                duration = int(duration_input) if duration_input else 600
            except ValueError:
                print("⚠️ Invalid duration. Using default (600 seconds).")
                duration = 600
            
            print(f"\n⏳ Generating video for: '{topic}' ({duration} seconds)...")
            print("-" * 60)
            
            # Generate video
            result = await generator.generate_video(topic=topic, duration=duration)
            
            print("-" * 60)
            if result.get("success"):
                print(f"\n✅ Video Generation Completed!")
                print(f"📁 Video File: {result.get('video_url')}")
                print(f"🎯 Session ID: {result.get('session_id')}")
                print(f"📊 Quality Score: {result.get('metadata', {}).get('quality_score', 'N/A')}")
            else:
                print(f"\n❌ Video Generation Failed!")
                print(f"Error: {result.get('error')}")
        else:
            print("❌ Invalid option. Please select 1 or 2.")

if __name__ == "__main__":
    asyncio.run(main())