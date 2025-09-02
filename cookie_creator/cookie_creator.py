"""
Interactive Cookie Creator Utility
A command-line tool to visit websites and create cookies, with yt-dlp integration support.
"""

import requests
import json
import os
import sys
from urllib.parse import urlparse, urljoin
from http.cookiejar import MozillaCookieJar, Cookie
import time
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime, timedelta

class CookieCreator:
    """Main class for creating and managing cookies from website visits."""
    
    def __init__(self, cookie_file: str = None):
        """
        Initialize the CookieCreator.
        
        Args:
            cookie_file: Path to save/load cookies (default: cookies.txt)
        """
        self.cookie_file = cookie_file or "cookies.txt"
        self.session = requests.Session()
        self.cookie_jar = MozillaCookieJar(self.cookie_file)
        self.session.cookies = self.cookie_jar
        
        # Load existing cookies if file exists
        if os.path.exists(self.cookie_file):
            try:
                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
            except Exception as e:
                print(f"Warning: Could not load existing cookies: {e}")
    
    def visit_website(self, url: str, headers: Dict[str, str] = None) -> Tuple[bool, str]:
        """
        Visit a website and collect cookies.
        
        Args:
            url: Website URL to visit
            headers: Optional custom headers
            
        Returns:
            Tuple of (success: bool, message: str)
        """
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

def interactive_mode():
    """Run the interactive command-line interface."""
    print("\n" + "="*60)
    print("    Interactive Cookie Creator Utility")
    print("="*60)
    print("Commands:")
    print("  visit <url>     - Visit a website and collect cookies")
    print("  list           - List all collected cookies")
    print("  save           - Save cookies to file")
    print("  clear          - Clear all cookies")
    print("  export         - Export cookies for yt-dlp")
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
                url = command[6:].strip()
                if not url:
                    print("Please provide a URL. Example: visit google.com")
                    continue
                
                print(f"Visiting {url}...")
                success, message = cookie_creator.visit_website(url)
                print(message)
                
                if success:
                    print("Cookies automatically saved.")
                    cookie_creator.save_cookies()
                    
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
                print("  visit <url>     - Visit a website and collect cookies")
                print("  list           - List all collected cookies")
                print("  save           - Save cookies to file")
                print("  clear          - Clear all cookies")
                print("  export         - Export cookies for yt-dlp")
                print("  quit/exit      - Exit the program")
                
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
    
    args = parser.parse_args()
    
    if args.url:
        # Non-interactive mode
        cookie_creator = CookieCreator(args.cookie_file)
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
