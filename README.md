# Interactive Browser Agent

Uses [browser-use](https://github.com/browser-use/browser-use) (via Chrome DevTools Protocol) to browse any website.

Remotely orchestrate a browser to navigate the web.
Meaning any task that can be accomplished via a browser.

| Tag | Description |
|-----|-------------|
| [`v1-playwright`](../../tree/v1-playwright) | Node.js implementation using Playwright |
| [`v2-browser-use`](../../tree/v2-browser-use) (latest) | Python implementation using browser-use (CDP)|

## 🏗️ File Structure
```
src/
├── cli.py                # Main entry point
├── server.py             # Interactive browser debug server (FastAPI)
└── client.py             # Command-line interface (Typer)
pyproject.toml            # Project configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- `uv` (recommended)

### Installation

Install the tool globally using `uv`:

```bash
uv tool install .
```

Now you can use the `browser` command anywhere!

### Usage

#### Server Management

```bash
# Start the server (background by default)
browser server start

# Check status
browser server status

# View logs
browser server logs --follow

# Stop server
browser server stop
```

#### Client Commands

```bash
# Check connection
browser client status

# Navigate
browser client navigate "https://www.google.com"

# Fill form
browser client fill "[name='q']" "hamster dance"

# Click
browser client click "[name='btnK']"

# Execute JS
browser client execute "() => document.title"
```

## 🔌 API Reference

The server runs on `http://localhost:3001`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Get current page URL and title |
| `/navigate` | POST | Navigate to a URL |
| `/click` | POST | Click an element (via JS) |
| `/fill` | POST | Fill an input field (via JS) |
| `/execute` | POST | Execute JavaScript (arrow function) |
| `/dom` | POST | Get element outerHTML |
