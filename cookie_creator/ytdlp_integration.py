"""
yt-dlp Cookie Integration Module
Provides seamless integration between the Cookie Creator utility and yt-dlp.
"""

import os
import sys
import json
import tempfile
from typing import Dict, Optional, Any, Union, List
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

# Try to import credential management components
try:
    from .credential_manager import CredentialManager, CredentialManagerError
    from .login_handlers import get_login_handler, list_supported_sites, LoginError
    CREDENTIALS_AVAILABLE = True
except ImportError:
    CREDENTIALS_AVAILABLE = False

class YtDlpCookieIntegration:
    """Integration class for yt-dlp cookie functionality."""
    
    def __init__(self, cookie_file: str = None, enable_credentials: bool = True):
        """
        Initialize the integration.
        
        Args:
            cookie_file: Path to cookie file
            enable_credentials: Whether to enable credential management
        """
        self.cookie_creator = CookieCreator(cookie_file, enable_credentials)
        self.temp_files = []
        
    def __del__(self):
        """Cleanup temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    def prepare_cookies_for_url(self, url: str, visit_first: bool = True, 
                              use_credentials: bool = False, site_key: str = None,
                              username: str = None, password: str = None) -> str:
        """
        Prepare cookies for a specific URL by visiting it first if needed.
        
        Args:
            url: Target URL for yt-dlp
            visit_first: Whether to visit the URL first to collect cookies
            use_credentials: Boolean flag to enable credential-based authentication
            site_key: Specific site identifier for credential lookup
            username: Optional explicit username for authentication
            password: Optional explicit password for authentication
            
        Returns:
            Path to cookie file compatible with yt-dlp
        """
        if visit_first:
            if use_credentials and CREDENTIALS_AVAILABLE:
                # Attempt authentication before visiting the URL
                print(f"Attempting authenticated visit to {url}...")
                success, message = self.cookie_creator.visit_website_with_login(
                    url, site_key, username, password
                )
                if success:
                    print(f"Authentication successful: {message}")
                else:
                    print(f"Authentication failed: {message}")
                    print("Falling back to regular cookie collection...")
                    success, message = self.cookie_creator.visit_website(url)
                    if not success:
                        print(f"Warning: Could not visit {url}: {message}")
            else:
                # Regular visit without authentication
                success, message = self.cookie_creator.visit_website(url)
                if not success:
                    print(f"Warning: Could not visit {url}: {message}")
        
        # Export cookies in Netscape format for yt-dlp
        cookie_file = self.cookie_creator.export_cookies_for_ytdlp("netscape")
        return cookie_file
    
    def download_with_cookies(self, url: str, output_path: str = None, 
                            visit_first: bool = True, use_credentials: bool = False,
                            site_key: str = None, username: str = None, 
                            password: str = None, **ytdlp_opts) -> bool:
        """
        Download content using yt-dlp with collected cookies.
        
        Args:
            url: URL to download
            output_path: Output directory/filename pattern
            visit_first: Whether to visit URL first for cookies
            use_credentials: Boolean flag to enable credential-based authentication
            site_key: Specific site identifier for credential lookup
            username: Optional explicit username for authentication
            password: Optional explicit password for authentication
            **ytdlp_opts: Additional yt-dlp options
            
        Returns:
            Success status
        """
        if not YTDLP_AVAILABLE:
            raise ImportError("yt-dlp is not installed. Install with: pip install yt-dlp")
        
        # Prepare cookies with credential support
        cookie_file = self.prepare_cookies_for_url(
            url, visit_first, use_credentials, site_key, username, password
        )
        
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
    
    def create_ytdlp_config(self, urls: Union[List[str], List[Dict[str, Any]]], 
                           config_path: str = "ytdlp_config.conf") -> str:
        """
        Create a yt-dlp configuration file with cookie settings.
        
        Args:
            urls: List of URLs to prepare cookies for, or list of dictionaries
                 containing URL and credential information. Each dict can contain:
                 - 'url': The URL to visit
                 - 'use_credentials': Whether to use credentials
                 - 'site_key': Site identifier for credentials
                 - 'username': Optional username
                 - 'password': Optional password
            config_path: Path for the config file
            
        Returns:
            Path to the created config file
        """
        # Visit all URLs to collect cookies, with credential support
        for url_info in urls:
            if isinstance(url_info, str):
                # Simple URL string
                self.cookie_creator.visit_website(url_info)
            elif isinstance(url_info, dict):
                # Dictionary with URL and credential info
                url = url_info.get('url')
                if not url:
                    continue
                
                use_credentials = url_info.get('use_credentials', False)
                site_key = url_info.get('site_key')
                username = url_info.get('username')
                password = url_info.get('password')
                
                if use_credentials and CREDENTIALS_AVAILABLE:
                    success, message = self.cookie_creator.visit_website_with_login(
                        url, site_key, username, password
                    )
                    if not success:
                        print(f"Authentication failed for {url}: {message}")
                        print("Falling back to regular visit...")
                        self.cookie_creator.visit_website(url)
                else:
                    self.cookie_creator.visit_website(url)
            else:
                print(f"Warning: Invalid URL info format: {url_info}")
        
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
                               visit_first: bool = True, use_credentials: bool = False,
                               site_key: str = None, username: str = None, 
                               password: str = None) -> bool:
    """
    Quick function to download with automatic cookie handling.
    
    Args:
        url: URL to download
        output_path: Output path
        visit_first: Visit URL first for cookies
        use_credentials: Enable credential-based authentication
        site_key: Site identifier for credential lookup
        username: Optional explicit username for authentication
        password: Optional explicit password for authentication
        
    Returns:
        Success status
    """
    integration = YtDlpCookieIntegration()
    return integration.download_with_cookies(
        url, output_path, visit_first, use_credentials, site_key, username, password
    )

def prepare_cookies_for_ytdlp(urls: Union[List[str], List[Dict[str, Any]]], 
                             cookie_file: str = "cookies_for_ytdlp.txt") -> str:
    """
    Visit multiple URLs and prepare a cookie file for yt-dlp.
    
    Args:
        urls: List of URLs to visit, or list of dictionaries containing URL
             and credential information. Each dict can contain:
             - 'url': The URL to visit
             - 'use_credentials': Whether to use credentials
             - 'site_key': Site identifier for credentials
             - 'username': Optional username
             - 'password': Optional password
        cookie_file: Output cookie file path
        
    Returns:
        Path to the cookie file
    """
    integration = YtDlpCookieIntegration(cookie_file)
    
    for url_info in urls:
        if isinstance(url_info, str):
            # Simple URL string
            integration.cookie_creator.visit_website(url_info)
        elif isinstance(url_info, dict):
            # Dictionary with URL and credential info
            url = url_info.get('url')
            if not url:
                continue
            
            use_credentials = url_info.get('use_credentials', False)
            site_key = url_info.get('site_key')
            username = url_info.get('username')
            password = url_info.get('password')
            
            if use_credentials and CREDENTIALS_AVAILABLE:
                success, message = integration.cookie_creator.visit_website_with_login(
                    url, site_key, username, password
                )
                if not success:
                    print(f"Authentication failed for {url}: {message}")
                    print("Falling back to regular visit...")
                    integration.cookie_creator.visit_website(url)
            else:
                integration.cookie_creator.visit_website(url)
        else:
            print(f"Warning: Invalid URL info format: {url_info}")
    
    return integration.cookie_creator.export_cookies_for_ytdlp("netscape")
