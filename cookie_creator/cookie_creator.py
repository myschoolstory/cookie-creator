"""
Interactive Cookie Creator Utility
A command-line tool to visit websites and create cookies, with yt-dlp integration support.
"""

import requests
import json
import os
import sys
import getpass
from urllib.parse import urlparse, urljoin
from http.cookiejar import MozillaCookieJar, Cookie
import time
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime, timedelta

try:
    from .credential_manager import CredentialManager, CredentialManagerError
    from .login_handlers import get_login_handler, list_supported_sites, LoginError
    CREDENTIALS_AVAILABLE = True
except ImportError:
    CREDENTIALS_AVAILABLE = False

class CookieCreator:
    """Main class for creating and managing cookies from website visits."""
    
    def __init__(self, cookie_file: str = None, enable_credentials: bool = True):
        """
        Initialize the CookieCreator.
        
        Args:
            cookie_file: Path to save/load cookies (default: cookies.txt)
            enable_credentials: Whether to enable credential management (default: True)
        """
        self.cookie_file = cookie_file or "cookies.txt"
        self.session = requests.Session()
        self.cookie_jar = MozillaCookieJar(self.cookie_file)
        self.session.cookies = self.cookie_jar
        
        # Initialize credential manager if available and enabled
        self.credential_manager = None
        if enable_credentials and CREDENTIALS_AVAILABLE:
            try:
                self.credential_manager = CredentialManager()
            except Exception as e:
                print(f"Warning: Could not initialize credential manager: {e}")
        
        # Load existing cookies if file exists
        if os.path.exists(self.cookie_file):
            try:
                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
            except Exception as e:
                print(f"Warning: Could not load existing cookies: {e}")
    
    def visit_website(self, url: str, headers: Dict[str, str] = None, use_credentials: bool = False, site_key: str = None) -> Tuple[bool, str]:
        """
        Visit a website and collect cookies.
        
        Args:
            url: Website URL to visit
            headers: Optional custom headers
            use_credentials: Whether to use stored credentials for authentication
            site_key: Site identifier for credential lookup (auto-detected if not provided)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if use_credentials:
            return self.visit_website_with_login(url, site_key, headers=headers)
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Default headers to mimic a real browser
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            if headers:
                default_headers.update(headers)
            
            # Make the request
            response = self.session.get(url, headers=default_headers, timeout=30)
            response.raise_for_status()
            
            # Count new cookies
            cookie_count = len(self.session.cookies)
            
            return True, f"Successfully visited {url}. Collected {cookie_count} cookies total."
            
        except requests.exceptions.RequestException as e:
            return False, f"Error visiting {url}: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def save_cookies(self) -> bool:
        """Save cookies to file."""
        try:
            self.cookie_jar.save(ignore_discard=True, ignore_expires=True)
            return True
        except Exception as e:
            print(f"Error saving cookies: {e}")
            return False
    
    def list_cookies(self) -> List[Dict]:
        """List all cookies with details."""
        cookies_list = []
        for cookie in self.session.cookies:
            cookies_list.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires,
                'secure': cookie.secure,
                'httponly': hasattr(cookie, 'rest') and cookie.rest.get('HttpOnly', False)
            })
        return cookies_list
    
    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self.session.cookies.clear()
        if os.path.exists(self.cookie_file):
            try:
                os.remove(self.cookie_file)
            except Exception as e:
                print(f"Warning: Could not remove cookie file: {e}")
    
    def export_cookies_for_ytdlp(self, format_type: str = "netscape") -> str:
        """
        Export cookies in a format compatible with yt-dlp.
        
        Args:
            format_type: Format type ('netscape' or 'json')
            
        Returns:
            Path to exported cookie file
        """
        if format_type.lower() == "json":
            export_file = self.cookie_file.replace('.txt', '_ytdlp.json')
            cookies_dict = {}
            for cookie in self.session.cookies:
                domain = cookie.domain
                if domain not in cookies_dict:
                    cookies_dict[domain] = {}
                cookies_dict[domain][cookie.name] = cookie.value
            with open(export_file, 'w') as f:
                json.dump(cookies_dict, f, indent=2)
        else:  # netscape format (default)
            export_file = self.cookie_file.replace('.txt', '_ytdlp.txt')
            self.cookie_jar.save(export_file, ignore_discard=True, ignore_expires=True)
        return export_file
    
    def visit_website_with_login(self, url: str, site_key: str = None, username: str = None, password: str = None, headers: Dict[str, str] = None) -> Tuple[bool, str]:
        """
        Visit a website with authentication using stored or provided credentials.
        
        Args:
            url: Website URL to visit
            site_key: Site identifier for credential lookup (auto-detected if not provided)
            username: Username for authentication (retrieved from storage if not provided)
            password: Password for authentication (retrieved from storage if not provided)
            headers: Optional custom headers
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not CREDENTIALS_AVAILABLE:
            return False, "Credential management not available. Please install required dependencies."
        
        if not self.credential_manager:
            return False, "Credential manager not initialized."
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Auto-detect site key if not provided
            if not site_key:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                
                # Map common domains to site keys
                domain_mapping = {
                    'youtube.com': 'youtube',
                    'www.youtube.com': 'youtube',
                    'm.youtube.com': 'youtube',
                    'music.youtube.com': 'youtube',
                }
                
                site_key = domain_mapping.get(domain)
                if not site_key:
                    # Use the main domain as site key
                    site_key = domain.replace('www.', '').replace('m.', '')
            
            # Get credentials if not provided
            if not username or not password:
                stored_creds = self.credential_manager.get_credential(site_key)
                if stored_creds:
                    stored_username, stored_password = stored_creds
                    username = username or stored_username
                    password = password or stored_password
                else:
                    return False, f"No credentials found for {site_key}. Please add credentials first."
            
            # Get login handler for the site
            login_handler = get_login_handler(site_key)
            if not login_handler:
                return False, f"No login handler available for {site_key}. Falling back to regular visit."
            
            # Perform authentication
            try:
                success = login_handler.login(self.session, username, password)
                if not success:
                    return False, f"Authentication failed for {site_key}"
                
                # Verify authentication
                if not login_handler.is_logged_in(self.session):
                    return False, f"Authentication verification failed for {site_key}"
                
                # Now visit the target URL with authenticated session
                return self.visit_website(url, headers)
                
            except LoginError as e:
                return False, f"Login error for {site_key}: {str(e)}"
            
        except Exception as e:
            # Fall back to regular visit if authentication fails
            print(f"Warning: Authentication failed ({str(e)}), falling back to regular visit")
            return self.visit_website(url, headers)
    
    def add_credential(self, site: str, username: str, password: str) -> Tuple[bool, str]:
        """
        Store credentials for a site using CredentialManager.
        
        Args:
            site: Site identifier
            username: Username for the site
            password: Password for the site
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not CREDENTIALS_AVAILABLE:
            return False, "Credential management not available. Please install required dependencies."
        
        if not self.credential_manager:
            return False, "Credential manager not initialized."
        
        try:
            self.credential_manager.save_credential(site, username, password)
            return True, f"Credentials saved for {site}"
        except CredentialManagerError as e:
            return False, f"Failed to save credentials for {site}: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error saving credentials: {str(e)}"
    
    def list_credential_sites(self) -> List[str]:
        """
        List sites with stored credentials.
        
        Returns:
            List of site identifiers with stored credentials
        """
        if not CREDENTIALS_AVAILABLE or not self.credential_manager:
            return []
        
        try:
            return self.credential_manager.list_sites()
        except Exception as e:
            print(f"Warning: Could not list credential sites: {e}")
            return []
    
    def remove_credential(self, site: str) -> Tuple[bool, str]:
        """
        Delete stored credentials for a site.
        
        Args:
            site: Site identifier
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not CREDENTIALS_AVAILABLE:
            return False, "Credential management not available. Please install required dependencies."
        
        if not self.credential_manager:
            return False, "Credential manager not initialized."
        
        try:
            if self.credential_manager.delete_credential(site):
                return True, f"Credentials removed for {site}"
            else:
                return False, f"No credentials found for {site}"
        except CredentialManagerError as e:
            return False, f"Failed to remove credentials for {site}: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error removing credentials: {str(e)}"
    
    def has_credentials(self, site: str) -> bool:
        """
        Check if credentials exist for a site.
        
        Args:
            site: Site identifier
            
        Returns:
            True if credentials exist, False otherwise
        """
        if not CREDENTIALS_AVAILABLE or not self.credential_manager:
            return False
        
        try:
            return self.credential_manager.has_credential(site)
        except Exception:
            return False
    
    def get_supported_login_sites(self) -> List[str]:
        """
        Get list of sites with available login handlers.
        
        Returns:
            List of supported site identifiers
        """
        if not CREDENTIALS_AVAILABLE:
            return []
        
        try:
            return list_supported_sites()
        except Exception:
            return []

def interactive_mode():
    """Run the interactive command-line interface."""
    print("\n" + "="*60)
    print("    Interactive Cookie Creator Utility")
    print("="*60)
    print("Commands:")
    print("  visit <url>     - Visit a website and collect cookies")
    print("  login <site> <url> - Visit URL with authentication for site")
    print("  list           - List all collected cookies")
    print("  save           - Save cookies to file")
    print("  clear          - Clear all cookies")
    print("  export         - Export cookies for yt-dlp")
    if CREDENTIALS_AVAILABLE:
        print("  addcred <site> <username> - Add credentials for a site")
        print("  listcred       - List sites with stored credentials")
        print("  delcred <site> - Remove credentials for a site")
    print("  quit/exit      - Exit the program")
    print("="*60)
    
    # Initialize cookie creator
    cookie_creator = CookieCreator()
    
    while True:
        try:
            command = input("\ncookie-util> ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                print("Saving cookies and exiting...")
                cookie_creator.save_cookies()
                break
                
            elif command.startswith('visit '):
                parts = command[6:].strip().split()
                if not parts:
                    print("Please provide a URL. Example: visit google.com")
                    continue
                
                url = parts[0]
                use_login = '--login' in parts
                
                if use_login and CREDENTIALS_AVAILABLE:
                    print(f"Visiting {url} with authentication...")
                    success, message = cookie_creator.visit_website(url, use_credentials=True)
                else:
                    print(f"Visiting {url}...")
                    success, message = cookie_creator.visit_website(url)
                
                print(message)
                
                if success:
                    print("Cookies automatically saved.")
                    cookie_creator.save_cookies()
            
            elif command.startswith('login '):
                if not CREDENTIALS_AVAILABLE:
                    print("Credential management not available. Please install required dependencies.")
                    continue
                
                parts = command[6:].strip().split()
                if len(parts) < 2:
                    print("Please provide site and URL. Example: login youtube https://youtube.com")
                    continue
                
                site = parts[0]
                url = parts[1]
                
                print(f"Visiting {url} with {site} authentication...")
                success, message = cookie_creator.visit_website_with_login(url, site)
                print(message)
                
                if success:
                    print("Cookies automatically saved.")
                    cookie_creator.save_cookies()
            
            elif command.startswith('addcred '):
                if not CREDENTIALS_AVAILABLE:
                    print("Credential management not available. Please install required dependencies.")
                    continue
                
                parts = command[8:].strip().split()
                if len(parts) < 2:
                    print("Please provide site and username. Example: addcred youtube myemail@gmail.com")
                    continue
                
                site = parts[0]
                username = parts[1]
                
                # Check if site has login handler support
                supported_sites = cookie_creator.get_supported_login_sites()
                if supported_sites and site not in supported_sites:
                    print(f"Warning: No login handler available for '{site}'.")
                    print(f"Supported sites: {', '.join(supported_sites)}")
                    confirm = input("Continue anyway? (y/N): ")
                    if confirm.lower() != 'y':
                        continue
                
                try:
                    password = getpass.getpass(f"Enter password for {username} on {site}: ")
                    if not password:
                        print("Password cannot be empty.")
                        continue
                    
                    success, message = cookie_creator.add_credential(site, username, password)
                    print(message)
                    
                except KeyboardInterrupt:
                    print("\nOperation cancelled.")
                except Exception as e:
                    print(f"Error: {e}")
            
            elif command == 'listcred':
                if not CREDENTIALS_AVAILABLE:
                    print("Credential management not available. Please install required dependencies.")
                    continue
                
                sites = cookie_creator.list_credential_sites()
                if not sites:
                    print("No stored credentials found.")
                else:
                    print(f"\nStored credentials for {len(sites)} sites:")
                    supported_sites = cookie_creator.get_supported_login_sites()
                    for site in sites:
                        status = " (supported)" if site in supported_sites else " (no login handler)"
                        print(f"  - {site}{status}")
            
            elif command.startswith('delcred '):
                if not CREDENTIALS_AVAILABLE:
                    print("Credential management not available. Please install required dependencies.")
                    continue
                
                site = command[8:].strip()
                if not site:
                    print("Please provide a site. Example: delcred youtube")
                    continue
                
                if not cookie_creator.has_credentials(site):
                    print(f"No credentials found for {site}")
                    continue
                
                confirm = input(f"Are you sure you want to remove credentials for {site}? (y/N): ")
                if confirm.lower() == 'y':
                    success, message = cookie_creator.remove_credential(site)
                    print(message)
                else:
                    print("Operation cancelled.")
                    
            elif command == 'list':
                cookies = cookie_creator.list_cookies()
                if not cookies:
                    print("No cookies found.")
                else:
                    print(f"\nFound {len(cookies)} cookies:")
                    print("-" * 80)
                    for i, cookie in enumerate(cookies, 1):
                        print(f"{i}. {cookie['name']} = {cookie['value'][:50]}{'...' if len(cookie['value']) > 50 else ''}")
                        print(f"   Domain: {cookie['domain']}, Path: {cookie['path']}")
                        print(f"   Secure: {cookie['secure']}, HttpOnly: {cookie['httponly']}")
                        print("-" * 80)
                        
            elif command == 'save':
                if cookie_creator.save_cookies():
                    print(f"Cookies saved to {cookie_creator.cookie_file}")
                else:
                    print("Failed to save cookies.")
                    
            elif command == 'clear':
                confirm = input("Are you sure you want to clear all cookies? (y/N): ")
                if confirm.lower() == 'y':
                    cookie_creator.clear_cookies()
                    print("All cookies cleared.")
                else:
                    print("Operation cancelled.")
                    
            elif command == 'export':
                print("Export formats:")
                print("1. Netscape format (for yt-dlp --cookies)")
                print("2. JSON format")
                
                choice = input("Choose format (1/2): ").strip()
                
                if choice == '1':
                    export_file = cookie_creator.export_cookies_for_ytdlp("netscape")
                    print(f"Cookies exported to {export_file}")
                    print(f"Use with yt-dlp: yt-dlp --cookies {export_file} <url>")
                elif choice == '2':
                    export_file = cookie_creator.export_cookies_for_ytdlp("json")
                    print(f"Cookies exported to {export_file}")
                else:
                    print("Invalid choice.")
                    
            elif command == 'help' or command == '?':
                print("\nAvailable commands:")
                print("  visit <url> [--login] - Visit a website and collect cookies")
                print("  login <site> <url>    - Visit URL with authentication for site")
                print("  list                  - List all collected cookies")
                print("  save                  - Save cookies to file")
                print("  clear                 - Clear all cookies")
                print("  export                - Export cookies for yt-dlp")
                if CREDENTIALS_AVAILABLE:
                    print("  addcred <site> <username> - Add credentials for a site")
                    print("  listcred              - List sites with stored credentials")
                    print("  delcred <site>        - Remove credentials for a site")
                print("  quit/exit             - Exit the program")
                
                if CREDENTIALS_AVAILABLE:
                    supported_sites = cookie_creator.get_supported_login_sites()
                    if supported_sites:
                        print(f"\nSupported login sites: {', '.join(supported_sites)}")
                
            elif command == '':
                continue  # Empty command, just show prompt again
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            cookie_creator.save_cookies()
            break
        except EOFError:
            print("\n\nExiting...")
            cookie_creator.save_cookies()
            break

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Interactive Cookie Creator Utility")
    parser.add_argument("--cookie-file", "-c", default="cookies.txt",
                       help="Path to cookie file (default: cookies.txt)")
    parser.add_argument("--url", "-u", help="URL to visit (non-interactive mode)")
    parser.add_argument("--export", "-e", choices=['netscape', 'json'],
                       help="Export cookies in specified format")
    
    # Credential management arguments
    if CREDENTIALS_AVAILABLE:
        parser.add_argument("--add-credential", action="store_true",
                           help="Add credentials for a site (prompts for details)")
        parser.add_argument("--list-credentials", action="store_true",
                           help="List all stored credentials")
        parser.add_argument("--delete-credential", metavar="SITE",
                           help="Remove credentials for a site")
        parser.add_argument("--login-site", metavar="SITE",
                           help="Specify which site credentials to use for authentication")
        parser.add_argument("--username", metavar="USERNAME",
                           help="Provide username for authentication")
        parser.add_argument("--password-prompt", action="store_true",
                           help="Prompt for password securely")
    
    args = parser.parse_args()
    
    # Handle credential management operations
    if CREDENTIALS_AVAILABLE:
        cookie_creator = CookieCreator(args.cookie_file)
        
        if args.add_credential:
            try:
                site = input("Enter site identifier (e.g., youtube, github): ").strip()
                if not site:
                    print("Site identifier cannot be empty.")
                    return
                
                username = input(f"Enter username for {site}: ").strip()
                if not username:
                    print("Username cannot be empty.")
                    return
                
                password = getpass.getpass(f"Enter password for {username} on {site}: ")
                if not password:
                    print("Password cannot be empty.")
                    return
                
                success, message = cookie_creator.add_credential(site, username, password)
                print(message)
                return
                
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
            except Exception as e:
                print(f"Error: {e}")
                return
        
        if args.list_credentials:
            sites = cookie_creator.list_credential_sites()
            if not sites:
                print("No stored credentials found.")
            else:
                print(f"Stored credentials for {len(sites)} sites:")
                supported_sites = cookie_creator.get_supported_login_sites()
                for site in sites:
                    status = " (supported)" if site in supported_sites else " (no login handler)"
                    print(f"  - {site}{status}")
            return
        
        if args.delete_credential:
            site = args.delete_credential
            if not cookie_creator.has_credentials(site):
                print(f"No credentials found for {site}")
                return
            
            confirm = input(f"Are you sure you want to remove credentials for {site}? (y/N): ")
            if confirm.lower() == 'y':
                success, message = cookie_creator.remove_credential(site)
                print(message)
            else:
                print("Operation cancelled.")
            return
    
    if args.url:
        # Non-interactive mode
        cookie_creator = CookieCreator(args.cookie_file)
        
        # Handle authentication if requested
        if CREDENTIALS_AVAILABLE and args.login_site:
            username = args.username
            password = None
            
            if args.password_prompt:
                try:
                    password = getpass.getpass(f"Enter password for {args.login_site}: ")
                except KeyboardInterrupt:
                    print("\nOperation cancelled.")
                    return
            
            print(f"Visiting {args.url} with {args.login_site} authentication...")
            success, message = cookie_creator.visit_website_with_login(
                args.url, args.login_site, username, password
            )
        else:
            print(f"Visiting {args.url}...")
            success, message = cookie_creator.visit_website(args.url)
        
        print(message)
        
        if success:
            cookie_creator.save_cookies()
            
            if args.export:
                export_file = cookie_creator.export_cookies_for_ytdlp(args.export)
                print(f"Cookies exported to {export_file}")
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
