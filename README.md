# Cookie Creator Utility

An interactive Python command-line utility for visiting websites and creating cookies, with seamless yt-dlp integration support.

## Features

- **Interactive CLI**: Easy-to-use command-line interface for cookie management
- **Website Visiting**: Automatically visit websites and collect cookies
- **Cookie Management**: Save, load, list, and export cookies
- **yt-dlp Integration**: Direct integration with yt-dlp for enhanced downloading
- **Multiple Formats**: Export cookies in Netscape and JSON formats
- **Programmatic API**: Use as a Python module in your own projects

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
- `visit <url>` - Visit a website and collect cookies
- `list` - List all collected cookies  
- `save` - Save cookies to file
- `clear` - Clear all cookies
- `export` - Export cookies for yt-dlp
- `quit/exit` - Exit the program

### Command Line Mode

Visit a website directly:
```bash
cookie-util --url https://example.com
```

Export cookies immediately:
```bash
cookie-util --url https://example.com --export netscape
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

#### yt-dlp Integration
```python
from cookie_creator import YtDlpCookieIntegration, quick_download_with_cookies

# Quick download with automatic cookie handling
success = quick_download_with_cookies(
    "https://example.com/video",
    output_path="downloads/%(title)s.%(ext)s"
)

# Advanced integration
integration = YtDlpCookieIntegration()
cookie_file = integration.prepare_cookies_for_url("https://example.com")

# Use with yt-dlp command line
# yt-dlp --cookies {cookie_file} <video_url>
```

#### Prepare Cookies for Multiple Sites
```python
from cookie_creator import prepare_cookies_for_ytdlp

urls = [
    "https://site1.com", 
    "https://site2.com",
    "https://site3.com"
]

cookie_file = prepare_cookies_for_ytdlp(urls, "multi_site_cookies.txt")
print(f"Cookie file ready: {cookie_file}")
```

## yt-dlp Integration

### Using with yt-dlp Command Line

1. **Collect cookies interactively:**
   ```bash
   cookie-util
   # In interactive mode:
   visit https://example.com
   export
   # Choose option 1 for Netscape format
   ```

2. **Use with yt-dlp:**
   ```bash
   yt-dlp --cookies cookies_ytdlp.txt https://example.com/video
   ```

### Programmatic Integration

```python
from cookie_creator import YtDlpCookieIntegration

# Create integration instance
integration = YtDlpCookieIntegration()

# Download with automatic cookie collection
success = integration.download_with_cookies(
    url="https://example.com/video",
    output_path="downloads/%(title)s.%(ext)s",
    visit_first=True  # Visit site first to collect cookies
)
```

## API Reference

### CookieCreator Class

#### Methods:
- `visit_website(url, headers=None)` - Visit a website and collect cookies
- `save_cookies()` - Save cookies to file
- `list_cookies()` - Get list of all cookies with details
- `clear_cookies()` - Clear all cookies
- `export_cookies_for_ytdlp(format_type="netscape")` - Export for yt-dlp

### YtDlpCookieIntegration Class

#### Methods:
- `prepare_cookies_for_url(url, visit_first=True)` - Prepare cookies for URL
- `download_with_cookies(url, output_path=None, visit_first=True, **ytdlp_opts)` - Download with yt-dlp
- `create_ytdlp_config(urls, config_path)` - Create yt-dlp config file

### Convenience Functions

- `quick_download_with_cookies(url, output_path, visit_first=True)` - Quick download
- `prepare_cookies_for_ytdlp(urls, cookie_file)` - Prepare multi-site cookies

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
- yt-dlp integration
- Programmatic usage
- Multi-site cookie collection

## Requirements

- Python 3.7+
- requests>=2.25.0
- yt-dlp>=2023.1.6 (optional, for integration features)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Common Issues

1. **Cookies not working with yt-dlp**: Ensure you're using the Netscape format export
2. **Permission errors**: Check file permissions for cookie files
3. **Import errors**: Install optional dependencies with `pip install -e .[ytdlp]`

### Debug Mode

Run with debug information:
```bash
python -c "import requests; print(requests.__version__)"
```

## Security Notice

This tool handles cookies which may contain sensitive information. Always:
- Keep cookie files secure
- Don't share cookie files
- Regularly clear cookies for sensitive sites
- Be aware of privacy implications when visiting sites