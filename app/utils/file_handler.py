import os
import tempfile
from typing import Optional, Tuple
from pathlib import Path
import hashlib
from app.core.config import settings

class FileHandler:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

        # Supported file types and their max sizes (in bytes)
        max_size_mb = settings.max_file_size_mb or 10  # Default to 10MB if None
        self.supported_types = {
            '.pdf': max_size_mb * 1024 * 1024,
            '.docx': max_size_mb * 1024 * 1024,
            '.doc': max_size_mb * 1024 * 1024,
            '.txt': 1024 * 1024  # 1MB for text files
        }

    def validate_file(self, filename: str, file_size: int) -> Tuple[bool, str]:
        """
        Validate uploaded file

        Args:
            filename: Original filename
            file_size: File size in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()

        if file_ext not in self.supported_types:
            return False, f"Unsupported file type. Supported types: {', '.join(self.supported_types.keys())}"

        # Check file size
        max_size = self.supported_types[file_ext]
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"File too large. Maximum size for {file_ext} files: {max_size_mb:.1f}MB"

        if file_size == 0:
            return False, "Empty file not allowed"

        return True, ""

    def generate_safe_filename(self, original_filename: str, user_id: int) -> str:
        """Generate a safe, unique filename"""
        # Get file extension
        file_ext = Path(original_filename).suffix.lower()

        # Create hash of original filename + user_id for uniqueness
        name_hash = hashlib.md5(f"{original_filename}{user_id}".encode()).hexdigest()[:8]

        # Generate safe filename
        safe_filename = f"resume_{user_id}_{name_hash}{file_ext}"

        return safe_filename

    def save_uploaded_file(self, file_content: bytes, filename: str, user_id: int) -> Tuple[str, str]:
        """
        Save uploaded file to disk

        Args:
            file_content: Binary file content
            filename: Original filename
            user_id: User ID for unique naming

        Returns:
            Tuple of (file_path, safe_filename)
        """
        safe_filename = self.generate_safe_filename(filename, user_id)
        file_path = self.upload_dir / safe_filename

        # Write file to disk
        with open(file_path, 'wb') as f:
            f.write(file_content)

        return str(file_path), safe_filename

    def delete_file(self, file_path: str) -> bool:
        """Delete file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'exists': True
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None

# Singleton instance
file_handler = FileHandler()
