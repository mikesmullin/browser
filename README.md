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

### Vision Models (Optional)

The vision features (YOLO and SAM) require model weights. These will be downloaded automatically to the `models/` directory on first use, but you can pre-download them if needed:

```bash
# The server will handle this automatically, but for manual setup:
mkdir -p models
# YOLOv8n
uv run python -c "from ultralytics import YOLO; YOLO('models/yolov8n.pt')"
# SAM
uv run python -c "from ultralytics import SAM; SAM('models/sam_b.pt')"
```

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

# Click at coordinates (Vision-based)
browser client click-at 500 300

# Execute JS
browser client execute "() => document.title"

# Visual Grounding (Set-of-Marks)
browser client visualize

# Object Detection (YOLO)
browser client detect

# Segmentation (SAM)
browser client segment

# Note: All vision commands default to CSV output. Use --no-csv for full JSON.
browser client visualize --no-csv
```

## 🔌 API Reference

The server runs on `http://localhost:3001`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Get current page URL and title |
| `/navigate` | POST | Navigate to a URL |
| `/click` | POST | Click an element (via JS) |
| `/click_at` | POST | Click at specific coordinates |
| `/fill` | POST | Fill an input field (via JS) |
| `/execute` | POST | Execute JavaScript (arrow function) |
| `/dom` | POST | Get element outerHTML |
| `/screenshot` | POST | Take a page screenshot |
| `/visualize` | POST | Generate Set-of-Marks visualization |
| `/detect` | POST | Run YOLO object detection |
| `/segment` | POST | Run SAM segmentation |
