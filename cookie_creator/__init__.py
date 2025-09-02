"""
Cookie Creator Utility - Interactive cookie collection tool with yt-dlp integration

This package provides tools for visiting websites, collecting cookies, and integrating
with yt-dlp for enhanced downloading capabilities. Includes credential management
for authenticated cookie collection.
"""

from .cookie_creator import CookieCreator
from .ytdlp_integration import (
    YtDlpCookieIntegration,
    CookieExtractor,
    quick_download_with_cookies,
    prepare_cookies_for_ytdlp
)
from .credential_manager import CredentialManager
from .login_handlers import (
    BaseLoginHandler,
    YouTubeLoginHandler
)

__version__ = "1.0.0"
__author__ = "Cookie Creator Utility"
__email__ = "namelessonbandlab@outlook.com"

__all__ = [
    "CookieCreator",
    "YtDlpCookieIntegration", 
    "CookieExtractor",
    "quick_download_with_cookies",
    "prepare_cookies_for_ytdlp",
    "CredentialManager",
    "BaseLoginHandler",
    "YouTubeLoginHandler",
]
