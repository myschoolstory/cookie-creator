"""
yt-dlp Cookie Integration Module
Provides seamless integration between the Cookie Creator utility and yt-dlp.
"""

import os
import sys
import json
import tempfile
from typing import Dict, Optional, Any
from urllib.parse import urlparse

# Try to import yt-dlp components if available
try:
    import yt_dlp
    from yt_dlp.utils import sanitize_filename
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    print("Warning: yt-dlp not found. Install with: pip install yt-dlp")

from .cookie_creator import CookieCreator

class YtDlpCookieIntegration:
    """Integration class for yt-dlp cookie functionality."""
    
    def __init__(self, cookie_file: str = None):
        """
        Initialize the integration.
        
        Args:
            cookie_file: Path to cookie file
        """
        self.cookie_creator = CookieCreator(cookie_file)
        self.temp_files = []
        
    def __del__(self):
        """Cleanup temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    def prepare_cookies_for_url(self, url: str, visit_first: bool = True) -> str:
        """
        Prepare cookies for a specific URL by visiting it first if needed.
        
        Args:
            url: Target URL for yt-dlp
            visit_first: Whether to visit the URL first to collect cookies
            
        Returns:
            Path to cookie file compatible with yt-dlp
        """
        if visit_first:
            success, message = self.cookie_creator.visit_website(url)
            if not success:
                print(f"Warning: Could not visit {url}: {message}")
        
        # Export cookies in Netscape format for yt-dlp
        cookie_file = self.cookie_creator.export_cookies_for_ytdlp("netscape")
        return cookie_file
    
    def download_with_cookies(self, url: str, output_path: str = None, 
                            visit_first: bool = True, **ytdlp_opts) -> bool:
        """
        Download content using yt-dlp with collected cookies.
        
        Args:
            url: URL to download
            output_path: Output directory/filename pattern
            visit_first: Whether to visit URL first for cookies
            **ytdlp_opts: Additional yt-dlp options
            
        Returns:
            Success status
        """
        if not YTDLP_AVAILABLE:
            raise ImportError("yt-dlp is not installed. Install with: pip install yt-dlp")
        
        # Prepare cookies
        cookie_file = self.prepare_cookies_for_url(url, visit_first)
        
        # Set up yt-dlp options
        ydl_opts = {
            'cookiefile': cookie_file,
            'outtmpl': output_path or '%(title)s.%(ext)s',
        }
        
        # Merge user options
        ydl_opts.update(ytdlp_opts)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def create_ytdlp_config(self, urls: list, config_path: str = "ytdlp_config.conf") -> str:
        """
        Create a yt-dlp configuration file with cookie settings.
        
        Args:
            urls: List of URLs to prepare cookies for
            config_path: Path for the config file
            
        Returns:
            Path to the created config file
        """
        # Visit all URLs to collect cookies
        for url in urls:
            self.cookie_creator.visit_website(url)
        
        # Export cookies
        cookie_file = self.cookie_creator.export_cookies_for_ytdlp("netscape")
        
        # Create config file
        config_content = f"""# yt-dlp configuration with cookies
--cookies {cookie_file}
--output "%(uploader)s - %(title)s.%(ext)s"
--write-description
--write-info-json
--extract-flat false
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return config_path

class CookieExtractor:
    """Extract cookies from various browser formats for yt-dlp compatibility."""
    
    @staticmethod
    def from_browser_export(browser_cookie_file: str) -> str:
        """
        Convert browser-exported cookies to yt-dlp compatible format.
        
        Args:
            browser_cookie_file: Path to browser cookie export
            
        Returns:
            Path to converted cookie file
        """
        # This is a placeholder for browser cookie conversion
        # In practice, you'd implement parsers for Chrome, Firefox, etc.
        print(f"Converting browser cookies from {browser_cookie_file}")
        return browser_cookie_file
    
    @staticmethod
    def extract_from_session(session_data: dict) -> str:
        """
        Extract cookies from a session data dictionary.
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            Path to created cookie file
        """
        temp_file = tempfile.mktemp(suffix='.txt')
        
        # Convert session data to Netscape format
        with open(temp_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This is a generated file! Do not edit.\n\n")
            
            for domain, cookies in session_data.items():
                for name, value in cookies.items():
                    # Simple Netscape format line
                    f.write(f"{domain}\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
        
        return temp_file

# Convenience functions for easy integration
def quick_download_with_cookies(url: str, output_path: str = None, 
                               visit_first: bool = True) -> bool:
    """
    Quick function to download with automatic cookie handling.
    
    Args:
        url: URL to download
        output_path: Output path
        visit_first: Visit URL first for cookies
        
    Returns:
        Success status
    """
    integration = YtDlpCookieIntegration()
    return integration.download_with_cookies(url, output_path, visit_first)

def prepare_cookies_for_ytdlp(urls: list, cookie_file: str = "cookies_for_ytdlp.txt") -> str:
    """
    Visit multiple URLs and prepare a cookie file for yt-dlp.
    
    Args:
        urls: List of URLs to visit
        cookie_file: Output cookie file path
        
    Returns:
        Path to the cookie file
    """
    integration = YtDlpCookieIntegration(cookie_file)
    
    for url in urls:
        integration.cookie_creator.visit_website(url)
    
    return integration.cookie_creator.export_cookies_for_ytdlp("netscape")