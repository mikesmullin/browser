# Interactive Browser Agent

Uses [browser-use](https://github.com/browser-use/browser-use) (via Chrome DevTools Protocol) to browse any website.

Remotely orchestrate a browser to navigate the web.
Meaning any task that can be accomplished via a browser.

## 🏗️ File Structure
```
src/
├── browser_server.py         # Interactive browser debug server (FastAPI)
├── browser_client.py         # Command-line interface (Typer)
└── browser-server.sh         # Server management script
requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- `uv` (recommended)

### Step 1: Setup Environment
```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Step 2: Start Interactive Debug Session
```bash
cd src

# Start the server (background)
./browser-server.sh start
```

### Step 3: Verify Connection
```bash
# Check server status
./browser-server.sh status

# Test client connection
python browser_client.py status

# Should show: URL: about:blank, ready: true
```

### Step 4: Test Basic Browser Functions
```bash
# Test navigation
python browser_client.py navigate "https://httpbin.org/html"

# Check DOM inspection
python browser_client.py dom "h1"

# Execute JavaScript
python browser_client.py execute "() => document.title"
```

### Step 5: Test Form Interaction (Example)
```bash
# Navigate to a page with a search form
python browser_client.py navigate "https://www.google.com"

# Fill search input
python browser_client.py fill "[name='q']" "test query"

# Click search button
python browser_client.py click "[name='btnK']"

# Wait for results (manual check or poll)
python browser_client.py execute "() => document.querySelector('#search') ? true : false"
```

## 🛠️ Server Management

### Using browser-server.sh (Recommended)
```bash
# Start server in background
./browser-server.sh start

# Check server status and logs
./browser-server.sh status

# Stop server
./browser-server.sh stop

# Restart server
./browser-server.sh restart

# View live logs
tail -f ../browser-server.log
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
