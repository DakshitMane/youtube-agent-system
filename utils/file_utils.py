import os
import json
import shutil
from typing import Dict, Any, List
import logging
from datetime import datetime

class FileManager:
    """Manage file operations for the agent system"""
    
    def __init__(self, base_dir: str = "workspace"):
        self.logger = logging.getLogger("file_manager")
        self.base_dir = base_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.base_dir,
            os.path.join(self.base_dir, "sessions"),
            os.path.join(self.base_dir, "assets"),
            os.path.join(self.base_dir, "voiceovers"),
            os.path.join(self.base_dir, "visuals"),
            os.path.join(self.base_dir, "thumbnails"),
            os.path.join(self.base_dir, "videos"),
            os.path.join(self.base_dir, "logs"),
            os.path.join(self.base_dir, "temp")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        self.logger.debug("All workspace directories created")
    
    def save_session_data(self, session_id: str, data: Dict[str, Any]) -> str:
        """Save session data to file"""
        session_dir = os.path.join(self.base_dir, "sessions", session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        file_path = os.path.join(session_dir, "session_data.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.debug(f"Session data saved: {file_path}")
        return file_path
    
    def load_session_data(self, session_id: str) -> Dict[str, Any]:
        """Load session data from file"""
        file_path = os.path.join(self.base_dir, "sessions", session_id, "session_data.json")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Session data not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.logger.debug(f"Session data loaded: {file_path}")
        return data
    
    def save_agent_output(self, session_id: str, agent_name: str, output: Dict[str, Any]) -> str:
        """Save agent output to file"""
        session_dir = os.path.join(self.base_dir, "sessions", session_id, "agent_outputs")
        os.makedirs(session_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(session_dir, f"{agent_name}_{timestamp}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.logger.debug(f"Agent output saved: {file_path}")
        return file_path
    
    def save_asset(self, session_id: str, asset_type: str, asset_data: bytes, filename: str) -> str:
        """Save binary asset file"""
        asset_dir = os.path.join(self.base_dir, "assets", session_id, asset_type)
        os.makedirs(asset_dir, exist_ok=True)
        
        file_path = os.path.join(asset_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(asset_data)
        
        self.logger.debug(f"Asset saved: {file_path}")
        return file_path
    
    def get_asset_path(self, session_id: str, asset_type: str, filename: str) -> str:
        """Get path to asset file"""
        return os.path.join(self.base_dir, "assets", session_id, asset_type, filename)
    
    def list_session_assets(self, session_id: str, asset_type: str = None) -> List[str]:
        """List all assets for a session"""
        if asset_type:
            asset_dir = os.path.join(self.base_dir, "assets", session_id, asset_type)
        else:
            asset_dir = os.path.join(self.base_dir, "assets", session_id)
        
        if not os.path.exists(asset_dir):
            return []
        
        assets = []
        for root, dirs, files in os.walk(asset_dir):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), asset_dir)
                assets.append(relative_path)
        
        return assets
    
    def cleanup_session(self, session_id: str, keep_assets: bool = False):
        """Clean up session files"""
        session_dir = os.path.join(self.base_dir, "sessions", session_id)
        assets_dir = os.path.join(self.base_dir, "assets", session_id)
        
        try:
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
                self.logger.info(f"Session directory cleaned up: {session_dir}")
            
            if not keep_assets and os.path.exists(assets_dir):
                shutil.rmtree(assets_dir)
                self.logger.info(f"Session assets cleaned up: {assets_dir}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up session {session_id}: {str(e)}")
    
    def get_session_size(self, session_id: str) -> Dict[str, Any]:
        """Calculate total size of session data"""
        session_dir = os.path.join(self.base_dir, "sessions", session_id)
        assets_dir = os.path.join(self.base_dir, "assets", session_id)
        
        def get_directory_size(path: str) -> int:
            if not os.path.exists(path):
                return 0
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            return total_size
        
        session_size = get_directory_size(session_dir)
        assets_size = get_directory_size(assets_dir)
        
        return {
            "session_id": session_id,
            "session_data_size_mb": round(session_size / (1024 * 1024), 2),
            "assets_size_mb": round(assets_size / (1024 * 1024), 2),
            "total_size_mb": round((session_size + assets_size) / (1024 * 1024), 2)
        }
    
    def archive_session(self, session_id: str, archive_name: str = None) -> str:
        """Archive session data"""
        if not archive_name:
            archive_name = f"session_{session_id}_{datetime.now().strftime('%Y%m%d')}"
        
        session_dir = os.path.join(self.base_dir, "sessions", session_id)
        assets_dir = os.path.join(self.base_dir, "assets", session_id)
        archive_path = os.path.join(self.base_dir, "archives", f"{archive_name}.zip")
        
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        # Create archive
        import zipfile
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add session data
            if os.path.exists(session_dir):
                for root, dirs, files in os.walk(session_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.join(self.base_dir, "sessions"))
                        zipf.write(file_path, os.path.join("sessions", arcname))
            
            # Add assets
            if os.path.exists(assets_dir):
                for root, dirs, files in os.walk(assets_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.join(self.base_dir, "assets"))
                        zipf.write(file_path, os.path.join("assets", arcname))
        
        self.logger.info(f"Session archived: {archive_path}")
        return archive_path
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get file system statistics"""
        total_size = 0
        file_count = 0
        session_count = 0
        
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
            
            if "session_data.json" in files:
                session_count += 1
        
        return {
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "session_count": session_count,
            "workspace_path": os.path.abspath(self.base_dir),
            "last_updated": datetime.now().isoformat()
        }