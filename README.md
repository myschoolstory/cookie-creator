# Cookie Creator Utility

An interactive Python command-line utility for visiting websites and creating cookies, with seamless yt-dlp integration support and credential management for authenticated sites.

## Features

- **Interactive CLI**: Easy-to-use command-line interface for cookie management
- **Website Visiting**: Automatically visit websites and collect cookies
- **Credential Management**: Secure storage and management of login credentials
- **Authenticated Cookie Collection**: Login to sites like YouTube for enhanced access
- **Cookie Management**: Save, load, list, and export cookies
- **yt-dlp Integration**: Direct integration with yt-dlp for enhanced downloading
- **Multiple Formats**: Export cookies in Netscape and JSON formats
- **Programmatic API**: Use as a Python module in your own projects
- **Security**: Secure credential storage using system keyring or encrypted files

## Installation

### From Source
```bash
git clone <repository-url>
cd cookie-creator-utility
pip install -e .
```

### With yt-dlp Support
```bash
pip install -e .[ytdlp]
```

### With Credential Management Support
```bash
pip install -e .[credentials]
```

### Full Installation (All Features)
```bash
pip install -e .[full]
```

### Dependencies by Feature

**Base functionality:**
- Python 3.7+
- requests>=2.25.0

**yt-dlp integration:**
- yt-dlp>=2023.1.6

**Credential management:**
- keyring>=23.0.0 (for secure system credential storage)
- cryptography>=3.0.0 (for encrypted file fallback)

## Usage

### Interactive Mode

Run the interactive command-line interface:

```bash
cookie-util
```

Or using Python module:
```bash
python -m cookie_creator.cookie_creator
```

#### Available Commands:
- `visit <url> [--login]` - Visit a website and collect cookies (optionally with authentication)
- `login <site> <url>` - Visit URL with authentication for specified site
- `list` - List all collected cookies  
- `save` - Save cookies to file
- `clear` - Clear all cookies
- `export` - Export cookies for yt-dlp
- `addcred <site> <username>` - Add credentials for a site (prompts for password)
- `listcred` - List sites with stored credentials
- `delcred <site>` - Remove credentials for a site
- `quit/exit` - Exit the program

### Command Line Mode

Visit a website directly:
```bash
cookie-util --url https://example.com
```

Visit with authentication:
```bash
cookie-util --url https://youtube.com --login-site youtube --username your@email.com --password-prompt
```

Export cookies immediately:
```bash
cookie-util --url https://example.com --export netscape
```

Manage credentials:
```bash
# Add credentials
cookie-util --add-credential

# List stored credentials
cookie-util --list-credentials

# Remove credentials
cookie-util --delete-credential youtube
```

## Credential Management

The Cookie Creator utility supports secure credential storage and automated authentication for enhanced cookie collection from protected sites.

### Supported Sites

Currently supported sites with automated login handlers:
- **YouTube/Google**: Full Google account authentication support

Additional sites can be added by implementing custom login handlers or by storing credentials for manual authentication workflows.

### Security

Credential storage uses a multi-layered security approach:

1. **Primary: System Keyring** (Recommended)
   - Uses your operating system's secure credential storage
   - Windows: Windows Credential Manager
   - macOS: Keychain
   - Linux: Secret Service (GNOME Keyring, KWallet)

2. **Fallback: Encrypted File Storage**
   - AES encryption using the `cryptography` library
   - Encrypted credentials stored in `~/.cookie-creator/credentials.enc`
   - Encryption key stored separately in `~/.cookie-creator/credential_key.key`
   - File permissions set to 600 (owner read/write only)

3. **Security Best Practices**
   - Passwords are never stored in plain text
   - Credentials are validated before storage
   - Secure password input using `getpass` (hidden input)
   - Automatic cleanup of temporary authentication data

### Adding Credentials

#### Interactive Mode
```bash
cookie-util
# In interactive mode:
addcred youtube your@gmail.com
# Enter password when prompted (hidden input)
```

#### Command Line
```bash
cookie-util --add-credential
# Follow prompts for site, username, and password
```

#### Programmatic
```python
from cookie_creator import CookieCreator

creator = CookieCreator()
success, message = creator.add_credential("youtube", "your@gmail.com", "your_password")
print(message)
```

### Using Credentials

#### Interactive Mode
```bash
cookie-util
# In interactive mode:
login youtube https://youtube.com/watch?v=VIDEO_ID
# or
visit https://youtube.com/watch?v=VIDEO_ID --login
```

#### Command Line
```bash
cookie-util --url https://youtube.com --login-site youtube --username your@gmail.com --password-prompt
```

#### Programmatic
```python
from cookie_creator import CookieCreator

creator = CookieCreator()

# Using stored credentials
success, message = creator.visit_website_with_login("https://youtube.com", "youtube")

# Using explicit credentials
success, message = creator.visit_website_with_login(
    "https://youtube.com", 
    "youtube", 
    "your@gmail.com", 
    "your_password"
)
```

### Programmatic Usage

#### Basic Cookie Creation
```python
from cookie_creator import CookieCreator

# Create cookie creator
creator = CookieCreator("my_cookies.txt")

# Visit websites
success, message = creator.visit_website("https://example.com")
print(message)

# Save cookies
creator.save_cookies()

# List cookies
cookies = creator.list_cookies()
for cookie in cookies:
    print(f"{cookie['name']} = {cookie['value']}")
```

#### Credential Management
```python
from cookie_creator import CookieCreator

creator = CookieCreator()

# Add credentials
success, message = creator.add_credential("youtube", "user@gmail.com", "password")
print(message)

# List sites with credentials
sites = creator.list_credential_sites()
print(f"Stored credentials for: {', '.join(sites)}")

# Check if credentials exist
if creator.has_credentials("youtube"):
    print("YouTube credentials are available")

# Visit with authentication
success, message = creator.visit_website_with_login("https://youtube.com", "youtube")
print(message)

# Remove credentials
success, message = creator.remove_credential("youtube")
print(message)
```

#### Advanced Credential Usage
```python
from cookie_creator import CredentialManager, get_login_handler

# Direct credential manager usage
cred_manager = CredentialManager()

# Store credentials
cred_manager.save_credential("github", "username", "token")

# Retrieve credentials
username, password = cred_manager.get_credential("github")

# List all sites
sites = cred_manager.list_sites()

# Check storage backend info
info = cred_manager.get_storage_info()
print(f"Using keyring: {info['using_keyring']}")
print(f"Using encryption: {info['using_encryption']}")

# Direct login handler usage
handler = get_login_handler("youtube")
if handler:
    session = requests.Session()
    success = handler.login(session, "user@gmail.com", "password")
    if success and handler.is_logged_in(session):
        print("Successfully authenticated!")
```

#### yt-dlp Integration with Credentials
```python
from cookie_creator import YtDlpCookieIntegration, quick_download_with_cookies

# Quick download with automatic cookie handling and authentication
success = quick_download_with_cookies(
    "https://youtube.com/watch?v=VIDEO_ID",
    output_path="downloads/%(title)s.%(ext)s",
    use_credentials=True,
    site_key="youtube"
)

# Advanced integration with credentials
integration = YtDlpCookieIntegration()
cookie_file = integration.prepare_cookies_for_url(
    "https://youtube.com/watch?v=VIDEO_ID",
    visit_first=True,
    use_credentials=True,
    site_key="youtube"
)

# Download with authentication
success = integration.download_with_cookies(
    url="https://youtube.com/watch?v=VIDEO_ID",
    output_path="downloads/%(title)s.%(ext)s",
    use_credentials=True,
    site_key="youtube"
)

# Use with yt-dlp command line
# yt-dlp --cookies {cookie_file} <video_url>
```

#### Multi-Site Cookie Preparation with Credentials
```python
from cookie_creator import prepare_cookies_for_ytdlp

# Mix of authenticated and non-authenticated sites
urls = [
    "https://example.com",  # Regular visit
    {
        "url": "https://youtube.com",
        "use_credentials": True,
        "site_key": "youtube"
    },
    {
        "url": "https://another-site.com",
        "use_credentials": True,
        "site_key": "another-site",
        "username": "explicit_user",
        "password": "explicit_pass"
    }
]

cookie_file = prepare_cookies_for_ytdlp(urls, "multi_site_cookies.txt")
print(f"Cookie file ready: {cookie_file}")
```

#### Prepare Cookies for Multiple Sites
```python
from cookie_creator import prepare_cookies_for_ytdlp

# Simple URL list
urls = [
    "https://site1.com", 
    "https://site2.com",
    "https://site3.com"
]

cookie_file = prepare_cookies_for_ytdlp(urls, "multi_site_cookies.txt")
print(f"Cookie file ready: {cookie_file}")

# Advanced with credential support
urls_with_auth = [
    "https://public-site.com",  # No authentication needed
    {
        "url": "https://youtube.com",
        "use_credentials": True,
        "site_key": "youtube"
    },
    {
        "url": "https://private-site.com",
        "use_credentials": True,
        "site_key": "private-site",
        "username": "my_username",
        "password": "my_password"
    }
]

cookie_file = prepare_cookies_for_ytdlp(urls_with_auth, "authenticated_cookies.txt")
print(f"Authenticated cookie file ready: {cookie_file}")
```

## yt-dlp Integration

### Using with yt-dlp Command Line

1. **Collect cookies with authentication:**
   ```bash
   cookie-util
   # In interactive mode:
   addcred youtube your@gmail.com
   # Enter password when prompted
   login youtube https://youtube.com/watch?v=VIDEO_ID
   export
   # Choose option 1 for Netscape format
   ```

2. **Use with yt-dlp:**
   ```bash
   yt-dlp --cookies cookies_ytdlp.txt https://youtube.com/watch?v=VIDEO_ID
   ```

3. **One-command authenticated cookie collection:**
   ```bash
   cookie-util --url https://youtube.com --login-site youtube --username your@gmail.com --password-prompt --export netscape
   yt-dlp --cookies cookies_ytdlp.txt https://youtube.com/watch?v=VIDEO_ID
   ```

### Programmatic Integration

```python
from cookie_creator import YtDlpCookieIntegration

# Create integration instance with credential support
integration = YtDlpCookieIntegration(enable_credentials=True)

# Download with automatic cookie collection and authentication
success = integration.download_with_cookies(
    url="https://youtube.com/watch?v=VIDEO_ID",
    output_path="downloads/%(title)s.%(ext)s",
    visit_first=True,  # Visit site first to collect cookies
    use_credentials=True,  # Use stored credentials for authentication
    site_key="youtube"  # Specify which site credentials to use
)

# Download with explicit credentials
success = integration.download_with_cookies(
    url="https://youtube.com/watch?v=VIDEO_ID",
    output_path="downloads/%(title)s.%(ext)s",
    visit_first=True,
    use_credentials=True,
    site_key="youtube",
    username="your@gmail.com",
    password="your_password"
)
```

## API Reference

### CookieCreator Class

#### Constructor:
```python
CookieCreator(cookie_file=None, enable_credentials=True)
```
- `cookie_file`: Path to save/load cookies (default: "cookies.txt")
- `enable_credentials`: Whether to enable credential management (default: True)

#### Core Methods:
- `visit_website(url, headers=None, use_credentials=False, site_key=None)` - Visit a website and collect cookies
- `visit_website_with_login(url, site_key=None, username=None, password=None, headers=None)` - Visit with authentication
- `save_cookies()` - Save cookies to file
- `list_cookies()` - Get list of all cookies with details
- `clear_cookies()` - Clear all cookies
- `export_cookies_for_ytdlp(format_type="netscape")` - Export for yt-dlp

#### Credential Management Methods:
- `add_credential(site, username, password)` - Store credentials for a site
- `list_credential_sites()` - List sites with stored credentials
- `remove_credential(site)` - Delete stored credentials for a site
- `has_credentials(site)` - Check if credentials exist for a site
- `get_supported_login_sites()` - Get list of sites with login handlers

### CredentialManager Class

#### Constructor:
```python
CredentialManager(storage_dir=None)
```
- `storage_dir`: Directory for encrypted file storage (default: ~/.cookie-creator/)

#### Methods:
- `save_credential(site, username, password)` - Store credentials securely
- `get_credential(site)` - Retrieve stored credentials (returns tuple or None)
- `list_sites()` - List all sites with stored credentials
- `delete_credential(site)` - Remove credentials for a site
- `has_credential(site)` - Check if credentials exist for a site
- `get_storage_info()` - Get information about storage backend

#### Exceptions:
- `CredentialManagerError` - Base exception for credential operations
- `CredentialStorageError` - Storage operation failures
- `CredentialRetrievalError` - Retrieval operation failures
- `CredentialValidationError` - Validation failures

### Login Handler Classes

#### BaseLoginHandler (Abstract)
- `login(session, username, password)` - Perform authentication
- `is_logged_in(session)` - Check authentication status
- `get_site_name()` - Get site identifier

#### YouTubeLoginHandler
- Implements Google/YouTube authentication
- Handles multi-step login process
- Supports error detection and 2FA detection
- Site name: "youtube"

#### Login Handler Functions:
- `get_login_handler(site)` - Get handler for a site
- `list_supported_sites()` - List all supported sites
- `is_site_supported(site)` - Check if site is supported

#### Exceptions:
- `LoginError` - Base login exception
- `AuthenticationError` - Invalid credentials
- `TwoFactorRequiredError` - 2FA required
- `RateLimitError` - Rate limiting encountered
- `LoginHandlerError` - General handler errors

### YtDlpCookieIntegration Class

#### Constructor:
```python
YtDlpCookieIntegration(cookie_file=None, enable_credentials=True)
```

#### Methods:
- `prepare_cookies_for_url(url, visit_first=True, use_credentials=False, site_key=None, username=None, password=None)` - Prepare cookies for URL
- `download_with_cookies(url, output_path=None, visit_first=True, use_credentials=False, site_key=None, username=None, password=None, **ytdlp_opts)` - Download with yt-dlp
- `create_ytdlp_config(urls, config_path="ytdlp_config.conf")` - Create yt-dlp config file

### Convenience Functions

- `quick_download_with_cookies(url, output_path=None, visit_first=True, use_credentials=False, site_key=None, username=None, password=None)` - Quick download with credential support
- `prepare_cookies_for_ytdlp(urls, cookie_file="cookies_for_ytdlp.txt")` - Prepare multi-site cookies with credential support

## Command Reference

### Interactive Mode Commands

| Command | Description | Example |
|---------|-------------|---------|
| `visit <url> [--login]` | Visit website, optionally with authentication | `visit https://youtube.com --login` |
| `login <site> <url>` | Visit URL with site-specific authentication | `login youtube https://youtube.com` |
| `addcred <site> <username>` | Add credentials for a site | `addcred youtube user@gmail.com` |
| `listcred` | List sites with stored credentials | `listcred` |
| `delcred <site>` | Remove credentials for a site | `delcred youtube` |
| `list` | List all collected cookies | `list` |
| `save` | Save cookies to file | `save` |
| `clear` | Clear all cookies | `clear` |
| `export` | Export cookies for yt-dlp | `export` |
| `help` | Show help information | `help` |
| `quit/exit` | Exit the program | `quit` |

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--url <url>` | Visit URL in non-interactive mode | `--url https://example.com` |
| `--cookie-file <path>` | Specify cookie file path | `--cookie-file my_cookies.txt` |
| `--export <format>` | Export cookies (netscape/json) | `--export netscape` |
| `--add-credential` | Add credentials interactively | `--add-credential` |
| `--list-credentials` | List stored credentials | `--list-credentials` |
| `--delete-credential <site>` | Remove credentials for site | `--delete-credential youtube` |
| `--login-site <site>` | Use credentials for site | `--login-site youtube` |
| `--username <username>` | Specify username for authentication | `--username user@gmail.com` |
| `--password-prompt` | Prompt for password securely | `--password-prompt` |

## File Formats

### Netscape Cookie Format
Compatible with yt-dlp `--cookies` option and most tools.

### JSON Cookie Format
```json
{
  "example.com": {
    "session_id": "abc123",
    "user_pref": "dark_mode"
  }
}
```

## Examples

See `examples.py` for comprehensive usage examples including:
- Basic cookie creation
- Credential management
- Authenticated cookie collection
- yt-dlp integration with authentication
- Programmatic usage
- Multi-site cookie collection
- Security best practices

### Quick Start Examples

#### 1. Basic Usage
```bash
# Start interactive mode
cookie-util

# Visit a site and collect cookies
visit https://example.com

# Save and export cookies
save
export
```

#### 2. YouTube Authentication
```bash
# Add YouTube credentials
cookie-util --add-credential
# Enter: youtube, your@gmail.com, password

# Collect authenticated cookies
cookie-util --url https://youtube.com --login-site youtube --username your@gmail.com --password-prompt

# Use with yt-dlp
yt-dlp --cookies cookies_ytdlp.txt "https://youtube.com/watch?v=VIDEO_ID"
```

#### 3. Programmatic Usage
```python
from cookie_creator import CookieCreator

# Setup with credentials
creator = CookieCreator()
creator.add_credential("youtube", "your@gmail.com", "your_password")

# Collect authenticated cookies
success, message = creator.visit_website_with_login("https://youtube.com", "youtube")

# Export for yt-dlp
cookie_file = creator.export_cookies_for_ytdlp("netscape")
print(f"Use: yt-dlp --cookies {cookie_file} <video_url>")
```

#### 4. Advanced yt-dlp Integration
```python
from cookie_creator import quick_download_with_cookies

# One-line authenticated download
success = quick_download_with_cookies(
    "https://youtube.com/watch?v=VIDEO_ID",
    output_path="downloads/%(uploader)s - %(title)s.%(ext)s",
    use_credentials=True,
    site_key="youtube"
)
```

## Requirements

**Base Requirements:**
- Python 3.7+
- requests>=2.25.0

**Optional Dependencies:**
- yt-dlp>=2023.1.6 (for yt-dlp integration features)
- keyring>=23.0.0 (for secure credential storage)
- cryptography>=3.0.0 (for encrypted credential fallback)

**Installation Extras:**
- `pip install -e .[ytdlp]` - Includes yt-dlp
- `pip install -e .[credentials]` - Includes credential management
- `pip install -e .[full]` - Includes all features

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Common Issues

1. **Cookies not working with yt-dlp**: Ensure you're using the Netscape format export
2. **Permission errors**: Check file permissions for cookie files
3. **Import errors**: Install optional dependencies with `pip install -e .[credentials]` or `pip install -e .[full]`
4. **Credential storage errors**: Check if keyring is available on your system
5. **Authentication failures**: Verify credentials and check for 2FA requirements
6. **Login handler not found**: Check supported sites with `listcred` command

### Credential Management Issues

1. **Keyring not available**: The tool will automatically fall back to encrypted file storage
2. **Permission denied on credential files**: Check that `~/.cookie-creator/` directory has proper permissions
3. **Credentials not found**: Use `listcred` to verify stored credentials
4. **Authentication timeout**: Some sites may have rate limiting; wait and retry

### Debug Mode

Check system capabilities:
```bash
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import requests
    print(f'Requests: {requests.__version__}')
except ImportError:
    print('Requests: Not installed')

try:
    import keyring
    print(f'Keyring: {keyring.__version__}')
    print(f'Keyring backend: {keyring.get_keyring()}')
except ImportError:
    print('Keyring: Not installed')

try:
    import cryptography
    print(f'Cryptography: {cryptography.__version__}')
except ImportError:
    print('Cryptography: Not installed')

try:
    import yt_dlp
    print(f'yt-dlp: {yt_dlp.version.__version__}')
except ImportError:
    print('yt-dlp: Not installed')
"
```

Check credential storage:
```python
from cookie_creator import CredentialManager

manager = CredentialManager()
info = manager.get_storage_info()
for key, value in info.items():
    print(f"{key}: {value}")
```

### Verbose Logging

Enable detailed logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from cookie_creator import CookieCreator
creator = CookieCreator()
# Your operations here
```

## Security Notice

This tool handles cookies and credentials which may contain sensitive information. Always:

### Cookie Security:
- Keep cookie files secure and don't share them
- Regularly clear cookies for sensitive sites
- Be aware of privacy implications when visiting sites
- Use appropriate file permissions (600) for cookie files

### Credential Security:
- **Never store credentials in plain text**
- Use the system keyring when available (most secure)
- Encrypted file storage is used as fallback with AES encryption
- Credential files are created with restrictive permissions (600)
- Passwords are never logged or displayed
- Use `getpass` for secure password input in interactive mode

### Best Practices:
- Regularly review stored credentials with `listcred`
- Remove unused credentials with `delcred <site>`
- Use unique, strong passwords for each site
- Enable 2FA where supported (note: 2FA may require manual intervention)
- Monitor for suspicious authentication attempts
- Keep the tool and its dependencies updated

### Privacy Considerations:
- Cookies may contain tracking information
- Authenticated sessions may have elevated privileges
- Some sites may log authentication attempts
- Consider using dedicated accounts for automation
- Be aware of terms of service for automated access

### Data Storage Locations:
- **Cookies**: Specified cookie file (default: `cookies.txt`)
- **Credentials (keyring)**: System-specific secure storage
- **Credentials (encrypted)**: `~/.cookie-creator/credentials.enc`
- **Encryption key**: `~/.cookie-creator/credential_key.key`
- **Logs**: Standard Python logging (configure as needed)
