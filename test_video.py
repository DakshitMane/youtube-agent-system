#!/usr/bin/env python3
"""
Test script to verify video generation works
"""
import os
import sys

# Test imports
print("Testing MoviePy installation...")
try:
    from moviepy import ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips
    print("✅ MoviePy is installed and working!")
    
    # Quick test - create a 5 second video
    print("\nCreating a test video...")
    
    clip = ColorClip(size=(1920, 1080), color=(50, 50, 100), duration=5)
    txt = TextClip("Test Video - MoviePy Working!", fontsize=70, color='white').set_duration(5).set_position('center')
    final = CompositeVideoClip([clip, txt])
    
    os.makedirs("output_videos", exist_ok=True)
    final.write_videofile("output_videos/test_video.mp4", verbose=False, logger=None, codec='libx264', audio=False)
    
    print("✅ Test video created successfully!")
    print("📁 Check output_videos/test_video.mp4")
    
except ImportError as e:
    print(f"❌ MoviePy not installed: {e}")
    print("Run: pip install moviepy imageio imageio-ffmpeg")
except Exception as e:
    print(f"❌ Error: {e}")
