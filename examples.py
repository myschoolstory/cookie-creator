#!/usr/bin/env python3
"""
Example usage of Cookie Creator Utility with yt-dlp integration
"""

import sys
import os

# Add the package to path if running from source
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cookie_creator import CookieCreator, YtDlpCookieIntegration, quick_download_with_cookies

# Try to import credential management components
try:
    from cookie_creator import CredentialManager, YouTubeLoginHandler
    CREDENTIALS_AVAILABLE = True
except ImportError:
    CREDENTIALS_AVAILABLE = False
    print("Note: Credential management not available. Install with: pip install cookie-creator[credentials]")

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
    """Example of yt-dlp integration with credential support."""
    print("\n=== yt-dlp Integration Example ===")
    
    try:
        # Create integration instance with credential support
        integration = YtDlpCookieIntegration("ytdlp_cookies.txt", enable_credentials=True)
        
        # Example: Prepare cookies for a video site
        test_url = "https://www.youtube.com"
        print(f"Preparing cookies for {test_url}...")
        
        # Show both regular and authenticated cookie preparation
        print("\n1. Regular cookie preparation:")
        cookie_file = integration.prepare_cookies_for_url(test_url, visit_first=True)
        print(f"  Cookie file ready: {cookie_file}")
        
        if CREDENTIALS_AVAILABLE:
            print("\n2. Authenticated cookie preparation:")
            print("  (Requires stored YouTube credentials)")
            
            # Check if credentials are available
            creator = integration.cookie_creator
            if creator.has_credentials("youtube"):
                print("  Found YouTube credentials, preparing authenticated cookies...")
                auth_cookie_file = integration.prepare_cookies_for_url(
                    test_url, 
                    visit_first=True, 
                    use_credentials=True, 
                    site_key="youtube"
                )
                print(f"  Authenticated cookie file ready: {auth_cookie_file}")
            else:
                print("  No YouTube credentials found.")
                print("  Add credentials with: creator.add_credential('youtube', 'email', 'password')")
        
        # Create a yt-dlp config file
        config_file = integration.create_ytdlp_config([test_url])
        print(f"\n3. Created yt-dlp config: {config_file}")
        
        print("\n4. Usage options:")
        print(f"  Basic: yt-dlp --config-location {config_file} <video_url>")
        print(f"  With cookies: yt-dlp --cookies {cookie_file} <video_url>")
        
        if CREDENTIALS_AVAILABLE:
            print("\n5. Authenticated usage benefits:")
            print("  - Access to private/unlisted content")
            print("  - Higher quality streams for premium users")
            print("  - Personal playlists and subscriptions")
            print("  - Age-restricted content")
        
    except ImportError:
        print("yt-dlp not installed. Install with: pip install yt-dlp")

def example_quick_download():
    """Example of quick download function with credential support."""
    print("\n=== Quick Download Example ===")
    
    # This is just an example - replace with actual video URL
    video_url = "https://example.com/video"  # Replace with real URL
    
    print(f"Attempting to download {video_url} with automatic cookie handling...")
    print("(This is just an example - replace with a real video URL)")
    
    try:
        # Show both regular and authenticated download options
        print("\nRegular download (no authentication):")
        print("  # success = quick_download_with_cookies(video_url, 'downloads/%(title)s.%(ext)s')")
        
        if CREDENTIALS_AVAILABLE:
            print("\nAuthenticated download (with credentials):")
            print("  # success = quick_download_with_cookies(")
            print("  #     video_url,")
            print("  #     'downloads/%(title)s.%(ext)s',")
            print("  #     use_credentials=True,")
            print("  #     site_key='youtube'  # or other supported site")
            print("  # )")
            print("\nThis enables downloading:")
            print("  - Private/unlisted videos")
            print("  - Age-restricted content")
            print("  - Premium quality streams")
            print("  - Personal playlists")
        
        print("\nDownload function is available but not executed in this example.")
        print("Replace with a real video URL to test actual downloads.")
    except Exception as e:
        print(f"Error: {e}")

def example_credential_management():
    """
    Example of credential management functionality.
    
    This demonstrates how to programmatically add, list, and remove credentials
    for different sites. Credential management is essential for accessing
    protected content that requires authentication.
    """
    print("\n=== Credential Management Example ===")
    
    if not CREDENTIALS_AVAILABLE:
        print("Credential management not available. Install with: pip install cookie-creator[credentials]")
        return
    
    try:
        # Create a cookie creator with credential support
        creator = CookieCreator("credential_example_cookies.txt", enable_credentials=True)
        
        print("Credential management allows you to:")
        print("- Store login credentials securely")
        print("- Automatically authenticate with websites")
        print("- Access protected content for cookie collection")
        print("- Enhance yt-dlp downloads with authenticated sessions")
        
        # Example: Adding credentials (in practice, you'd get these from user input)
        print("\n1. Adding credentials for different sites...")
        
        # Note: In a real scenario, you would never hardcode credentials
        # This is just for demonstration purposes
        example_credentials = [
            ("example-site", "demo_user", "demo_password"),
            ("test-platform", "test@example.com", "test123"),
        ]
        
        for site, username, password in example_credentials:
            success, message = creator.add_credential(site, username, password)
            print(f"  Adding {site}: {'✓' if success else '✗'} - {message}")
        
        # List stored credentials
        print("\n2. Listing stored credentials...")
        sites = creator.list_credential_sites()
        if sites:
            print(f"Found credentials for {len(sites)} sites:")
            supported_sites = creator.get_supported_login_sites()
            for site in sites:
                has_handler = site in supported_sites
                status = "supported" if has_handler else "no login handler"
                print(f"  - {site} ({status})")
        else:
            print("  No credentials stored")
        
        # Check if specific credentials exist
        print("\n3. Checking credential existence...")
        for site, _, _ in example_credentials:
            exists = creator.has_credentials(site)
            print(f"  {site}: {'✓' if exists else '✗'}")
        
        # Show supported login sites
        print("\n4. Sites with login handler support:")
        supported_sites = creator.get_supported_login_sites()
        if supported_sites:
            for site in supported_sites:
                print(f"  - {site}")
        else:
            print("  No login handlers available")
        
        # Clean up example credentials
        print("\n5. Cleaning up example credentials...")
        for site, _, _ in example_credentials:
            success, message = creator.remove_credential(site)
            print(f"  Removing {site}: {'✓' if success else '✗'} - {message}")
        
        print("\nCredential management provides secure storage using:")
        print("- System keyring (preferred) for maximum security")
        print("- Encrypted file storage as fallback")
        print("- Automatic credential retrieval for authentication")
        
    except Exception as e:
        print(f"Error in credential management example: {e}")

def example_authenticated_cookie_collection():
    """
    Example of collecting cookies from authenticated sessions.
    
    This demonstrates how authentication enhances cookie collection by
    accessing user-specific content and authenticated areas of websites.
    """
    print("\n=== Authenticated Cookie Collection Example ===")
    
    if not CREDENTIALS_AVAILABLE:
        print("Credential management not available. Install with: pip install cookie-creator[credentials]")
        return
    
    try:
        # Create cookie creator with credentials enabled
        creator = CookieCreator("authenticated_cookies.txt", enable_credentials=True)
        
        print("Authenticated cookie collection benefits:")
        print("- Access to user-specific content and preferences")
        print("- Cookies for premium/subscriber-only features")
        print("- Session tokens for API access")
        print("- Personalized content recommendations")
        
        # Example of authenticated vs non-authenticated collection
        test_url = "https://www.youtube.com"
        
        print(f"\n1. Regular (non-authenticated) visit to {test_url}...")
        success, message = creator.visit_website(test_url)
        print(f"  Result: {message}")
        
        # Count cookies from non-authenticated visit
        cookies_before = len(creator.list_cookies())
        print(f"  Cookies collected: {cookies_before}")
        
        # Clear cookies for comparison
        creator.clear_cookies()
        
        print(f"\n2. Authenticated visit to {test_url}...")
        print("  (This would use stored YouTube credentials if available)")
        
        # Check if we have YouTube credentials
        if creator.has_credentials("youtube"):
            print("  Found YouTube credentials, attempting authenticated visit...")
            success, message = creator.visit_website_with_login(test_url, "youtube")
            print(f"  Result: {message}")
            
            cookies_after = len(creator.list_cookies())
            print(f"  Cookies collected: {cookies_after}")
            
            if success:
                print("  ✓ Authenticated session provides access to:")
                print("    - User account information")
                print("    - Subscription status")
                print("    - Personalized recommendations")
                print("    - Premium content access")
        else:
            print("  No YouTube credentials found.")
            print("  To test authentication, add credentials first:")
            print("    creator.add_credential('youtube', 'your_email@gmail.com', 'your_password')")
        
        print("\n3. When to use authenticated cookie collection:")
        print("  - Downloading private/unlisted videos")
        print("  - Accessing subscriber-only content")
        print("  - Getting personalized playlists")
        print("  - Bypassing regional restrictions")
        print("  - Accessing premium streaming services")
        
        print("\n4. Security considerations:")
        print("  - Credentials are stored securely using system keyring")
        print("  - Fallback to encrypted file storage when keyring unavailable")
        print("  - Never store credentials in plain text")
        print("  - Use application-specific passwords when available")
        
    except Exception as e:
        print(f"Error in authenticated cookie collection example: {e}")

def example_youtube_integration():
    """
    Specific example for YouTube credential setup and authenticated yt-dlp downloads.
    
    This demonstrates the complete workflow for YouTube authentication,
    from credential setup to authenticated downloads.
    """
    print("\n=== YouTube Integration Example ===")
    
    if not CREDENTIALS_AVAILABLE:
        print("Credential management not available. Install with: pip install cookie-creator[credentials]")
        return
    
    try:
        # Create integration with credential support
        integration = YtDlpCookieIntegration("youtube_cookies.txt", enable_credentials=True)
        
        print("YouTube authentication enables:")
        print("- Access to private and unlisted videos")
        print("- Age-restricted content download")
        print("- Higher quality streams for premium users")
        print("- Personal playlists and watch later lists")
        print("- Bypassing some regional restrictions")
        
        print("\n1. YouTube credential setup process:")
        print("  a) Use your Google account email and password")
        print("  b) Consider using App Passwords for better security")
        print("  c) Handle 2FA if enabled (currently requires manual intervention)")
        
        # Example credential addition (commented out for safety)
        print("\n2. Adding YouTube credentials (example):")
        print("  # creator.add_credential('youtube', 'your_email@gmail.com', 'your_password')")
        print("  # Or use the interactive mode: cookie-util")
        print("  # Then: addcred youtube your_email@gmail.com")
        
        # Check for existing YouTube credentials
        creator = integration.cookie_creator
        has_youtube_creds = creator.has_credentials("youtube")
        
        print(f"\n3. YouTube credentials status: {'✓ Found' if has_youtube_creds else '✗ Not found'}")
        
        if has_youtube_creds:
            print("  With credentials available, you can:")
            
            # Example authenticated cookie preparation
            print("\n4. Preparing authenticated cookies for YouTube...")
            test_url = "https://www.youtube.com"
            
            try:
                cookie_file = integration.prepare_cookies_for_url(
                    test_url, 
                    visit_first=True, 
                    use_credentials=True, 
                    site_key="youtube"
                )
                print(f"  ✓ Authenticated cookie file ready: {cookie_file}")
                
                print("\n5. Using authenticated cookies with yt-dlp:")
                print(f"  yt-dlp --cookies {cookie_file} 'https://youtube.com/watch?v=VIDEO_ID'")
                print("  yt-dlp --cookies {cookie_file} 'https://youtube.com/playlist?list=PLAYLIST_ID'")
                
                # Example of authenticated download (commented for safety)
                print("\n6. Programmatic authenticated download:")
                print("  # success = integration.download_with_cookies(")
                print("  #     'https://youtube.com/watch?v=VIDEO_ID',")
                print("  #     output_path='downloads/%(title)s.%(ext)s',")
                print("  #     use_credentials=True,")
                print("  #     site_key='youtube'")
                print("  # )")
                
            except Exception as e:
                print(f"  Error preparing authenticated cookies: {e}")
        
        else:
            print("  To enable YouTube authentication:")
            print("  1. Run: python -m cookie_creator.cookie_creator")
            print("  2. Use command: addcred youtube your_email@gmail.com")
            print("  3. Enter your password when prompted")
            
        print("\n7. YouTube authentication best practices:")
        print("  - Use App Passwords instead of main account password")
        print("  - Enable 2FA for account security")
        print("  - Regularly rotate credentials")
        print("  - Monitor account activity for unauthorized access")
        
        print("\n8. Troubleshooting YouTube authentication:")
        print("  - Ensure credentials are correct")
        print("  - Check for 2FA requirements")
        print("  - Verify account isn't locked or suspended")
        print("  - Try using App Password instead of main password")
        print("  - Check for rate limiting (wait before retrying)")
        
    except Exception as e:
        print(f"Error in YouTube integration example: {e}")

def example_mixed_authentication():
    """
    Example showing handling of multiple sites with different authentication requirements.
    
    This demonstrates how to manage credentials for various platforms and
    handle different authentication scenarios in a single workflow.
    """
    print("\n=== Mixed Authentication Example ===")
    
    if not CREDENTIALS_AVAILABLE:
        print("Credential management not available. Install with: pip install cookie-creator[credentials]")
        return
    
    try:
        # Create integration for handling multiple sites
        integration = YtDlpCookieIntegration("mixed_auth_cookies.txt", enable_credentials=True)
        creator = integration.cookie_creator
        
        print("Managing multiple site authentications:")
        print("- Different sites require different credential formats")
        print("- Some sites have login handlers, others don't")
        print("- Fallback strategies for unsupported sites")
        print("- Batch processing with mixed authentication")
        
        # Define multiple sites with different authentication needs
        sites_config = [
            {
                'url': 'https://www.youtube.com',
                'site_key': 'youtube',
                'use_credentials': True,
                'description': 'Video platform with full login handler support'
            },
            {
                'url': 'https://github.com',
                'site_key': 'github',
                'use_credentials': False,  # No login handler yet
                'description': 'Code repository (no login handler - regular visit)'
            },
            {
                'url': 'https://www.reddit.com',
                'site_key': 'reddit',
                'use_credentials': False,  # No login handler yet
                'description': 'Social platform (no login handler - regular visit)'
            }
        ]
        
        print(f"\n1. Processing {len(sites_config)} sites with mixed authentication:")
        
        for i, site_config in enumerate(sites_config, 1):
            url = site_config['url']
            site_key = site_config['site_key']
            use_creds = site_config['use_credentials']
            description = site_config['description']
            
            print(f"\n  {i}. {site_key.upper()}: {description}")
            print(f"     URL: {url}")
            print(f"     Authentication: {'Enabled' if use_creds else 'Disabled'}")
            
            # Check if credentials are available
            if use_creds:
                has_creds = creator.has_credentials(site_key)
                print(f"     Credentials: {'✓ Available' if has_creds else '✗ Missing'}")
                
                if has_creds:
                    print(f"     Attempting authenticated visit...")
                    success, message = creator.visit_website_with_login(url, site_key)
                    print(f"     Result: {'✓' if success else '✗'} {message}")
                else:
                    print(f"     Falling back to regular visit (no credentials)")
                    success, message = creator.visit_website(url)
                    print(f"     Result: {'✓' if success else '✗'} {message}")
            else:
                print(f"     Performing regular visit...")
                success, message = creator.visit_website(url)
                print(f"     Result: {'✓' if success else '✗'} {message}")
        
        print("\n2. Creating unified yt-dlp configuration:")
        
        # Create a configuration that handles mixed authentication
        try:
            config_file = integration.create_ytdlp_config(sites_config)
            print(f"  ✓ Configuration created: {config_file}")
            print(f"  Usage: yt-dlp --config-location {config_file} <video_url>")
        except Exception as e:
            print(f"  ✗ Configuration creation failed: {e}")
        
        print("\n3. Batch cookie preparation with mixed authentication:")
        
        # Prepare cookies for multiple URLs with different auth requirements
        mixed_urls = [
            {
                'url': 'https://www.youtube.com/feed/subscriptions',
                'use_credentials': True,
                'site_key': 'youtube'
            },
            {
                'url': 'https://github.com/trending',
                'use_credentials': False
            }
        ]
        
        try:
            from cookie_creator.ytdlp_integration import prepare_cookies_for_ytdlp
            cookie_file = prepare_cookies_for_ytdlp(mixed_urls, "mixed_batch_cookies.txt")
            print(f"  ✓ Batch cookies prepared: {cookie_file}")
        except Exception as e:
            print(f"  ✗ Batch preparation failed: {e}")
        
        print("\n4. Best practices for mixed authentication:")
        print("  - Group sites by authentication requirements")
        print("  - Implement graceful fallbacks for missing credentials")
        print("  - Use site-specific error handling")
        print("  - Monitor authentication success rates")
        print("  - Implement retry logic for failed authentications")
        
        print("\n5. Extending support for new sites:")
        print("  - Create custom login handlers for unsupported sites")
        print("  - Implement site-specific authentication flows")
        print("  - Add credential validation for different formats")
        print("  - Test authentication with various account types")
        
        # Show current authentication capabilities
        print("\n6. Current authentication status:")
        supported_sites = creator.get_supported_login_sites()
        stored_sites = creator.list_credential_sites()
        
        print(f"  Sites with login handlers: {len(supported_sites)}")
        for site in supported_sites:
            has_creds = site in stored_sites
            print(f"    - {site}: {'✓ Has credentials' if has_creds else '✗ No credentials'}")
        
        print(f"  Sites with stored credentials: {len(stored_sites)}")
        for site in stored_sites:
            has_handler = site in supported_sites
            print(f"    - {site}: {'✓ Has handler' if has_handler else '✗ No handler'}")
        
    except Exception as e:
        print(f"Error in mixed authentication example: {e}")

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
        # Show how to optionally use credentials if available
        if CREDENTIALS_AVAILABLE and site == "https://youtube.com":
            # Try authenticated visit first, fall back to regular if no credentials
            success, msg = video_site_cookies.visit_website(site, use_credentials=True)
            if not success:
                print(f"  {site} (auth failed, trying regular): {'✓' if success else '✗'}")
                success, msg = video_site_cookies.visit_website(site)
        else:
            success, msg = video_site_cookies.visit_website(site)
        print(f"  {site}: {'✓' if success else '✗'}")
    
    # Save all cookies
    social_media_cookies.save_cookies()
    video_site_cookies.save_cookies()
    
    print("All cookies saved to respective files.")
    
    # Show credential-enhanced workflow if available
    if CREDENTIALS_AVAILABLE:
        print("\nCredential-enhanced workflow available:")
        print("- Use visit_website(url, use_credentials=True) for authenticated visits")
        print("- Use visit_website_with_login(url, site_key) for explicit authentication")
        print("- Manage credentials with add_credential(), list_credential_sites(), etc.")

if __name__ == "__main__":
    print("Cookie Creator Utility - Example Usage")
    print("=" * 50)
    
    try:
        # Run basic examples
        example_basic_usage()
        example_ytdlp_integration() 
        example_quick_download()
        example_programmatic_usage()
        
        # Run credential management examples if available
        if CREDENTIALS_AVAILABLE:
            print("\n" + "=" * 50)
            print("CREDENTIAL MANAGEMENT EXAMPLES")
            print("=" * 50)
            
            example_credential_management()
            example_authenticated_cookie_collection()
            example_youtube_integration()
            example_mixed_authentication()
        else:
            print("\n" + "=" * 50)
            print("CREDENTIAL MANAGEMENT EXAMPLES SKIPPED")
            print("=" * 50)
            print("To enable credential management examples:")
            print("  pip install cookie-creator[credentials]")
            print("Or install dependencies manually:")
            print("  pip install keyring cryptography")
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        
        print("\nBasic usage:")
        print("  python -m cookie_creator.cookie_creator")
        print("\nAfter installation:")
        print("  cookie-util")
        
        if CREDENTIALS_AVAILABLE:
            print("\nCredential management:")
            print("  cookie-util  # Then use addcred, listcred, delcred commands")
            print("  python -m cookie_creator.cookie_creator --add-credential")
            print("  python -m cookie_creator.cookie_creator --list-credentials")
            
            print("\nAuthenticated downloads:")
            print("  cookie-util  # Then use login <site> <url> command")
            print("  python -m cookie_creator.cookie_creator --url <url> --login-site youtube")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")
