import json
from typing import Dict, Any, List
import logging
from pydantic import BaseModel

try:
    import aiohttp
except ImportError:
    aiohttp = None

class OpenAPIClient(BaseModel):
    """Generic OpenAPI client"""
    base_url: str
    api_key: str
    headers: Dict[str, str] = {}

class YouTubeAPITool:
    """YouTube Data API v3 integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.logger = logging.getLogger("tool.youtube_api")
    
    async def search_videos(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search YouTube videos"""
        if aiohttp is None:
            return {"error": "aiohttp not installed. Install with: pip install aiohttp"}
            
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'part': 'snippet',
                    'q': query,
                    'maxResults': max_results,
                    'type': 'video',
                    'key': self.api_key
                }
                
                async with session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = []
                        
                        for item in data.get('items', []):
                            videos.append({
                                'video_id': item['id']['videoId'],
                                'title': item['snippet']['title'],
                                'description': item['snippet']['description'],
                                'channel_title': item['snippet']['channelTitle'],
                                'published_at': item['snippet']['publishedAt'],
                                'thumbnail': item['snippet']['thumbnails']['default']['url']
                            })
                        
                        self.logger.info(f"Found {len(videos)} YouTube videos for: {query}")
                        return {"videos": videos}
                    else:
                        error_msg = f"YouTube API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg}
                        
        except Exception as e:
            self.logger.error(f"YouTube search failed: {str(e)}")
            return {"error": f"YouTube API error: {str(e)}"}
    
    async def get_video_statistics(self, video_id: str) -> Dict[str, Any]:
        """Get video statistics"""
        if aiohttp is None:
            return {"error": "aiohttp not installed. Install with: pip install aiohttp"}
            
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'part': 'statistics,snippet',
                    'id': video_id,
                    'key': self.api_key
                }
                
                async with session.get(f"{self.base_url}/videos", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('items'):
                            video_data = data['items'][0]
                            return {
                                'view_count': video_data['statistics'].get('viewCount'),
                                'like_count': video_data['statistics'].get('likeCount'),
                                'comment_count': video_data['statistics'].get('commentCount'),
                                'title': video_data['snippet']['title'],
                                'description': video_data['snippet']['description']
                            }
                        return {"error": "Video not found"}
                    else:
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            self.logger.error(f"Failed to get video stats: {str(e)}")
            return {"error": str(e)}

class PexelsAPITool:
    """Pexels API for stock footage and images"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com"
        self.headers = {"Authorization": api_key}
        self.logger = logging.getLogger("tool.pexels_api")
    
    async def search_videos(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """Search stock videos"""
        if aiohttp is None:
            return {"error": "aiohttp not installed. Install with: pip install aiohttp"}
            
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                params = {
                    'query': query,
                    'per_page': per_page,
                    'orientation': 'landscape'
                }
                
                async with session.get(f"{self.base_url}/videos/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = []
                        
                        for video in data.get('videos', []):
                            videos.append({
                                'id': video['id'],
                                'url': video['url'],
                                'duration': video['duration'],
                                'image': video['image'],
                                'video_files': video['video_files']
                            })
                        
                        self.logger.info(f"Found {len(videos)} stock videos for: {query}")
                        return {"videos": videos}
                    else:
                        error_msg = f"Pexels API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg}
                        
        except Exception as e:
            self.logger.error(f"Pexels search failed: {str(e)}")
            return {"error": f"Pexels API error: {str(e)}"}

class ElevenLabsAPITool:
    """ElevenLabs API for voice synthesis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger("tool.elevenlabs_api")
    
    async def text_to_speech(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Dict[str, Any]:
        """Convert text to speech"""
        if aiohttp is None:
            return {"error": "aiohttp not installed. Install with: pip install aiohttp"}
            
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                payload = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        
                        # Save audio file
                        filename = f"elevenlabs_{hash(text) % 10000}.mp3"
                        with open(filename, 'wb') as f:
                            f.write(audio_data)
                        
                        self.logger.info(f"Generated speech for {len(text)} characters")
                        return {
                            "success": True,
                            "audio_file": filename,
                            "voice_id": voice_id,
                            "text_length": len(text)
                        }
                    else:
                        error_data = await response.text()
                        self.logger.error(f"ElevenLabs API error: {response.status} - {error_data}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_data
                        }
                        
        except Exception as e:
            self.logger.error(f"ElevenLabs TTS failed: {str(e)}")
            return {
                "success": False,
                "error": f"TTS failed: {str(e)}"
            }
    
    async def get_voices(self) -> Dict[str, Any]:
        """Get available voices"""
        if aiohttp is None:
            return {"error": "aiohttp not installed. Install with: pip install aiohttp"}
            
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(f"{self.base_url}/voices") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"voices": data.get('voices', [])}
                    else:
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            self.logger.error(f"Failed to get voices: {str(e)}")
            return {"error": str(e)}