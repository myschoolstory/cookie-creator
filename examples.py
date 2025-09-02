#!/usr/bin/env python3
"""
Example usage of Cookie Creator Utility with yt-dlp integration
"""

import sys
import os

# Add the package to path if running from source
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cookie_creator import CookieCreator, YtDlpCookieIntegration, quick_download_with_cookies

def example_basic_usage():
    """Example of basic cookie creation."""
    print("=== Basic Cookie Creation Example ===")
    
    # Create a cookie creator instance
    creator = CookieCreator("example_cookies.txt")
    
    # Visit some websites to collect cookies
    websites = [
        "https://httpbin.org/cookies/set/example/test",
        "https://www.google.com",
        "https://github.com"
    ]
    
    for site in websites:
        print(f"Visiting {site}...")
        success, message = creator.visit_website(site)
        print(f"  {message}")
    
    # Save cookies
    creator.save_cookies()
    print(f"Cookies saved to {creator.cookie_file}")
    
    # List collected cookies
    cookies = creator.list_cookies()
    print(f"\nCollected {len(cookies)} cookies:")
    for cookie in cookies[:5]:  # Show first 5
        print(f"  {cookie['name']} = {cookie['value'][:30]}...")

def example_ytdlp_integration():
    """Example of yt-dlp integration."""
    print("\n=== yt-dlp Integration Example ===")
    
    try:
        # Create integration instance
        integration = YtDlpCookieIntegration("ytdlp_cookies.txt")
        
        # Example: Prepare cookies for a video site
        test_url = "https://www.youtube.com"
        print(f"Preparing cookies for {test_url}...")
        
        cookie_file = integration.prepare_cookies_for_url(test_url)
        print(f"Cookie file ready: {cookie_file}")
        
        # Create a yt-dlp config file
        config_file = integration.create_ytdlp_config([test_url])
        print(f"Created yt-dlp config: {config_file}")
        
        print("\nYou can now use yt-dlp with:")
        print(f"  yt-dlp --config-location {config_file} <video_url>")
        print(f"  yt-dlp --cookies {cookie_file} <video_url>")
        
    except ImportError:
        print("yt-dlp not installed. Install with: pip install yt-dlp")

def example_quick_download():
    """Example of quick download function."""
    print("\n=== Quick Download Example ===")
    
    # This is just an example - replace with actual video URL
    video_url = "https://example.com/video"  # Replace with real URL
    
    print(f"Attempting to download {video_url} with automatic cookie handling...")
    print("(This is just an example - replace with a real video URL)")
    
    try:
        # Uncomment the next line to actually attempt download
        # success = quick_download_with_cookies(video_url, "downloads/%(title)s.%(ext)s")
        # print(f"Download {'successful' if success else 'failed'}")
        print("Download function is available but not executed in this example.")
    except Exception as e:
        print(f"Error: {e}")

def example_programmatic_usage():
    """Example of using the utility programmatically."""
    print("\n=== Programmatic Usage Example ===")
    
    # Create multiple cookie creators for different purposes
    social_media_cookies = CookieCreator("social_media_cookies.txt")
    video_site_cookies = CookieCreator("video_site_cookies.txt")
    
    # Visit different categories of sites
    social_sites = ["https://twitter.com", "https://facebook.com"]
    video_sites = ["https://youtube.com", "https://vimeo.com"]
    
    print("Collecting social media cookies...")
    for site in social_sites:
        success, msg = social_media_cookies.visit_website(site)
        print(f"  {site}: {'✓' if success else '✗'}")
    
    print("Collecting video site cookies...")
    for site in video_sites:
        success, msg = video_site_cookies.visit_website(site)
        print(f"  {site}: {'✓' if success else '✗'}")
    
    # Save all cookies
    social_media_cookies.save_cookies()
    video_site_cookies.save_cookies()
    
    print("All cookies saved to respective files.")

if __name__ == "__main__":
    print("Cookie Creator Utility - Example Usage")
    print("=" * 50)
    
    try:
        example_basic_usage()
        example_ytdlp_integration() 
        example_quick_download()
        example_programmatic_usage()
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        print("\nTo use the interactive mode, run:")
        print("  python -m cookie_creator.cookie_creator")
        print("\nOr after installation:")
        print("  cookie-util")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")