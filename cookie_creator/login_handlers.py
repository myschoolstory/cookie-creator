"""
Login Handlers for automated authentication with various sites.

This module provides a modular login handler system with an abstract base class
and site-specific implementations for automated authentication. The handlers
integrate with the credential management system to perform secure logins.
"""

import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class LoginError(Exception):
    """Base exception for login-related errors."""
    pass


class AuthenticationError(LoginError):
    """Exception raised when authentication fails."""
    pass


class TwoFactorRequiredError(LoginError):
    """Exception raised when two-factor authentication is required."""
    pass


class RateLimitError(LoginError):
    """Exception raised when rate limiting is encountered."""
    pass


class LoginHandlerError(LoginError):
    """Exception raised for general login handler errors."""
    pass


class BaseLoginHandler(ABC):
    """
    Abstract base class for site-specific login handlers.
    
    This class defines the interface that all login handlers must implement
    to provide consistent authentication functionality across different sites.
    """
    
    def __init__(self):
        """Initialize the login handler."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def login(self, session: requests.Session, username: str, password: str) -> bool:
        """
        Perform login for the specific site.
        
        Args:
            session: Requests session to use for authentication
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            True if login successful, False otherwise
            
        Raises:
            AuthenticationError: If authentication fails
            TwoFactorRequiredError: If 2FA is required
            RateLimitError: If rate limiting is encountered
            LoginHandlerError: For other login-related errors
        """
        pass
    
    @abstractmethod
    def is_logged_in(self, session: requests.Session) -> bool:
        """
        Check if the session is currently authenticated.
        
        Args:
            session: Requests session to check
            
        Returns:
            True if authenticated, False otherwise
        """
        pass
    
    @abstractmethod
    def get_site_name(self) -> str:
        """
        Get the site identifier for this handler.
        
        Returns:
            Site identifier string (e.g., 'youtube', 'github')
        """
        pass
    
    def _setup_session(self, session: requests.Session) -> None:
        """
        Configure session with appropriate settings for the site.
        
        Args:
            session: Session to configure
        """
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set common headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })


class YouTubeLoginHandler(BaseLoginHandler):
    """
    Login handler for YouTube/Google authentication.
    
    This handler implements Google's authentication flow using requests-based
    authentication. It handles the multi-step login process including form
    extraction, credential submission, and session validation.
    """
    
    SITE_NAME = "youtube"
    LOGIN_URL = "https://accounts.google.com/signin"
    YOUTUBE_URL = "https://www.youtube.com"
    
    def __init__(self):
        """Initialize the YouTube login handler."""
        super().__init__()
        self.flow_token = None
        self.session_state = {}
    
    def get_site_name(self) -> str:
        """Get the site identifier."""
        return self.SITE_NAME
    
    def login(self, session: requests.Session, username: str, password: str) -> bool:
        """
        Perform Google/YouTube login.
        
        This method implements a multi-step authentication process:
        1. Get the initial login page and extract necessary tokens
        2. Submit the username
        3. Submit the password
        4. Handle any additional verification steps
        5. Verify successful authentication
        
        Args:
            session: Requests session for authentication
            username: Google account username/email
            password: Google account password
            
        Returns:
            True if login successful
            
        Raises:
            AuthenticationError: If credentials are invalid
            TwoFactorRequiredError: If 2FA is required
            RateLimitError: If rate limiting is encountered
            LoginHandlerError: For other authentication errors
        """
        try:
            self._setup_session(session)
            self.logger.info(f"Starting login process for {username}")
            
            # Step 1: Get initial login page
            if not self._get_login_page(session):
                raise LoginHandlerError("Failed to load initial login page")
            
            # Step 2: Submit username
            if not self._submit_username(session, username):
                raise AuthenticationError("Failed to submit username")
            
            # Step 3: Submit password
            if not self._submit_password(session, password):
                raise AuthenticationError("Invalid credentials or password submission failed")
            
            # Step 4: Handle post-login verification
            if not self._handle_post_login(session):
                raise LoginHandlerError("Failed to complete post-login verification")
            
            # Step 5: Verify authentication
            if not self.is_logged_in(session):
                raise AuthenticationError("Login appeared successful but authentication verification failed")
            
            self.logger.info("Login completed successfully")
            return True
            
        except (AuthenticationError, TwoFactorRequiredError, RateLimitError):
            raise
        except requests.exceptions.RequestException as e:
            raise LoginHandlerError(f"Network error during login: {e}")
        except Exception as e:
            raise LoginHandlerError(f"Unexpected error during login: {e}")
    
    def is_logged_in(self, session: requests.Session) -> bool:
        """
        Check if the session is authenticated with Google/YouTube.
        
        This method verifies authentication by checking for specific cookies
        and making a test request to YouTube to confirm access.
        
        Args:
            session: Session to check
            
        Returns:
            True if authenticated
        """
        try:
            # Check for essential Google authentication cookies
            auth_cookies = ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']
            session_cookies = {cookie.name for cookie in session.cookies}
            
            if not any(cookie in session_cookies for cookie in auth_cookies):
                self.logger.debug("No authentication cookies found")
                return False
            
            # Make a test request to YouTube to verify access
            response = session.get(self.YOUTUBE_URL, timeout=10)
            
            # Check for signs of being logged in
            if response.status_code == 200:
                content = response.text.lower()
                # Look for indicators of logged-in state
                logged_in_indicators = [
                    '"signed_in":true',
                    'id="avatar-btn"',
                    'aria-label="account menu"',
                    '"isSignedIn":true'
                ]
                
                if any(indicator in content for indicator in logged_in_indicators):
                    self.logger.debug("Authentication verified successfully")
                    return True
            
            self.logger.debug("Authentication verification failed")
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking authentication status: {e}")
            return False
    
    def _get_login_page(self, session: requests.Session) -> bool:
        """
        Get the initial Google login page and extract necessary tokens.
        
        Args:
            session: Session to use
            
        Returns:
            True if successful
        """
        try:
            self.logger.debug("Fetching initial login page")
            response = session.get(self.LOGIN_URL, timeout=15)
            response.raise_for_status()
            
            # Extract flow token and other necessary parameters
            content = response.text
            
            # Look for flowName and flowEntry
            flow_name_match = re.search(r'"flowName":"([^"]+)"', content)
            flow_entry_match = re.search(r'"flowEntry":"([^"]+)"', content)
            
            if flow_name_match and flow_entry_match:
                self.session_state['flowName'] = flow_name_match.group(1)
                self.session_state['flowEntry'] = flow_entry_match.group(1)
                self.logger.debug("Extracted flow parameters successfully")
            
            # Extract additional tokens that might be needed
            token_patterns = [
                (r'"([A-Za-z0-9_-]{100,})"', 'long_token'),
                (r'name="flowName" value="([^"]+)"', 'form_flow_name'),
                (r'name="flowEntry" value="([^"]+)"', 'form_flow_entry'),
                (r'name="TL" value="([^"]+)"', 'tl_token'),
            ]
            
            for pattern, key in token_patterns:
                match = re.search(pattern, content)
                if match:
                    self.session_state[key] = match.group(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get login page: {e}")
            return False
    
    def _submit_username(self, session: requests.Session, username: str) -> bool:
        """
        Submit username to Google's authentication endpoint.
        
        Args:
            session: Session to use
            username: Username to submit
            
        Returns:
            True if successful
        """
        try:
            self.logger.debug("Submitting username")
            
            # Prepare the username submission
            username_url = "https://accounts.google.com/signin/v1/lookup"
            
            data = {
                'Email': username,
                'flowName': self.session_state.get('flowName', 'GlifWebSignIn'),
                'flowEntry': self.session_state.get('flowEntry', 'ServiceLogin'),
            }
            
            # Add any additional tokens we extracted
            if 'tl_token' in self.session_state:
                data['TL'] = self.session_state['tl_token']
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.LOGIN_URL,
            }
            
            response = session.post(username_url, data=data, headers=headers, timeout=15)
            
            # Google might return various status codes for valid username submission
            if response.status_code in [200, 302]:
                # Check if we're being redirected to password page or if there are errors
                content = response.text.lower()
                
                # Check for common error indicators
                error_indicators = [
                    'couldn\'t find your google account',
                    'enter a valid email',
                    'this email address doesn\'t match',
                ]
                
                if any(error in content for error in error_indicators):
                    self.logger.error("Username not found or invalid")
                    return False
                
                # Check for rate limiting
                if 'too many attempts' in content or 'try again later' in content:
                    raise RateLimitError("Rate limited by Google")
                
                self.logger.debug("Username submitted successfully")
                return True
            
            self.logger.error(f"Username submission failed with status {response.status_code}")
            return False
            
        except RateLimitError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to submit username: {e}")
            return False
    
    def _submit_password(self, session: requests.Session, password: str) -> bool:
        """
        Submit password to Google's authentication endpoint.
        
        Args:
            session: Session to use
            password: Password to submit
            
        Returns:
            True if successful
        """
        try:
            self.logger.debug("Submitting password")
            
            # The password submission URL might be different
            password_url = "https://accounts.google.com/signin/challenge/pwd"
            
            data = {
                'Passwd': password,
                'flowName': self.session_state.get('flowName', 'GlifWebSignIn'),
                'flowEntry': self.session_state.get('flowEntry', 'ServiceLogin'),
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://accounts.google.com/',
            }
            
            response = session.post(password_url, data=data, headers=headers, timeout=15)
            
            # Check response for success/failure indicators
            if response.status_code in [200, 302]:
                content = response.text.lower()
                
                # Check for password errors
                password_errors = [
                    'wrong password',
                    'incorrect password',
                    'couldn\'t sign you in',
                    'password is incorrect',
                ]
                
                if any(error in content for error in password_errors):
                    self.logger.error("Invalid password")
                    return False
                
                # Check for 2FA requirement
                tfa_indicators = [
                    'verify it\'s you',
                    'two-step verification',
                    '2-step verification',
                    'verify your identity',
                    'security code',
                ]
                
                if any(indicator in content for indicator in tfa_indicators):
                    raise TwoFactorRequiredError("Two-factor authentication required")
                
                # Check for rate limiting
                if 'too many attempts' in content or 'try again later' in content:
                    raise RateLimitError("Rate limited by Google")
                
                self.logger.debug("Password submitted successfully")
                return True
            
            self.logger.error(f"Password submission failed with status {response.status_code}")
            return False
            
        except (TwoFactorRequiredError, RateLimitError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to submit password: {e}")
            return False
    
    def _handle_post_login(self, session: requests.Session) -> bool:
        """
        Handle any post-login verification or redirection.
        
        Args:
            session: Session to use
            
        Returns:
            True if successful
        """
        try:
            self.logger.debug("Handling post-login verification")
            
            # Try to access YouTube to complete the authentication flow
            response = session.get(self.YOUTUBE_URL, timeout=15)
            
            if response.status_code == 200:
                # Check if we need to handle any additional consent or verification pages
                content = response.text.lower()
                
                # Look for consent pages or additional verification
                if 'consent' in content or 'terms of service' in content:
                    self.logger.debug("Consent page detected, attempting to handle")
                    # In a real implementation, you might need to handle consent forms
                    # For now, we'll assume the session is valid if we got this far
                
                return True
            
            self.logger.warning(f"Post-login verification returned status {response.status_code}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed post-login verification: {e}")
            return False


class LoginHandlerRegistry:
    """
    Registry for managing login handlers for different sites.
    
    This class provides a centralized way to register and retrieve
    login handlers for different sites.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._handlers = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default login handlers."""
        self.register_handler(YouTubeLoginHandler())
    
    def register_handler(self, handler: BaseLoginHandler) -> None:
        """
        Register a login handler for a site.
        
        Args:
            handler: Login handler instance
        """
        site_name = handler.get_site_name()
        self._handlers[site_name] = handler
        logger.info(f"Registered login handler for {site_name}")
    
    def get_handler(self, site: str) -> Optional[BaseLoginHandler]:
        """
        Get a login handler for a site.
        
        Args:
            site: Site identifier
            
        Returns:
            Login handler instance if available, None otherwise
        """
        return self._handlers.get(site.lower())
    
    def list_supported_sites(self) -> list[str]:
        """
        List all sites with registered handlers.
        
        Returns:
            List of supported site identifiers
        """
        return list(self._handlers.keys())
    
    def is_site_supported(self, site: str) -> bool:
        """
        Check if a site has a registered handler.
        
        Args:
            site: Site identifier
            
        Returns:
            True if supported, False otherwise
        """
        return site.lower() in self._handlers


# Global registry instance
login_registry = LoginHandlerRegistry()


def get_login_handler(site: str) -> Optional[BaseLoginHandler]:
    """
    Convenience function to get a login handler for a site.
    
    Args:
        site: Site identifier
        
    Returns:
        Login handler instance if available, None otherwise
    """
    return login_registry.get_handler(site)


def list_supported_sites() -> list[str]:
    """
    Convenience function to list all supported sites.
    
    Returns:
        List of supported site identifiers
    """
    return login_registry.list_supported_sites()


def is_site_supported(site: str) -> bool:
    """
    Convenience function to check if a site is supported.
    
    Args:
        site: Site identifier
        
    Returns:
        True if supported, False otherwise
    """
    return login_registry.is_site_supported(site)