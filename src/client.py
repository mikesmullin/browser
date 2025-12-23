
import typer
import httpx
import sys
import json
from typing import Optional

app = typer.Typer()
SERVER_URL = "http://localhost:3001"
client = httpx.Client(timeout=60.0)

def handle_response(response):
    try:
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
    except httpx.HTTPStatusError as e:
        print(f"Error: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

@app.command()
def status():
    """Get the status of the browser server, including current URL and title."""
    try:
        response = client.get(f"{SERVER_URL}/status")
        handle_response(response)
    except httpx.ConnectError:
        print("Error: Could not connect to server. Is it running?", file=sys.stderr)
        sys.exit(1)

@app.command()
def navigate(url: str):
    """Navigate the browser to a specific URL."""
    response = client.post(f"{SERVER_URL}/navigate", json={"url": url})
    handle_response(response)

@app.command()
def click(selector: str):
    """Click an element matching the CSS selector."""
    response = client.post(f"{SERVER_URL}/click", json={"selector": selector})
    handle_response(response)

@app.command()
def click_at(x: int, y: int):
    """Click at specific screen coordinates (x, y). Useful for vision-based grounding."""
    response = client.post(f"{SERVER_URL}/click_at", json={"x": x, "y": y})
    handle_response(response)

@app.command()
def fill(selector: str, value: str):
    """Fill an input element matching the selector with a specific value."""
    response = client.post(f"{SERVER_URL}/fill", json={"selector": selector, "value": value})
    handle_response(response)

@app.command()
def execute(script: str):
    """Execute a custom JavaScript arrow function in the browser context."""
    response = client.post(f"{SERVER_URL}/execute", json={"script": script})
    handle_response(response)

@app.command()
def dom(selector: str = "body"):
    """Retrieve the outerHTML of an element matching the selector."""
    response = client.post(f"{SERVER_URL}/dom", json={"selector": selector})
    handle_response(response)

@app.command()
def screenshot(full_page: bool = typer.Option(False, "--full-page", help="Take a full page screenshot")):
    """Take a screenshot of the current page."""
    response = client.post(f"{SERVER_URL}/screenshot", json={"full_page": full_page})
    handle_response(response)

@app.command()
def visualize(show_csv: bool = typer.Option(True, "--csv/--no-csv", help="Show the compact CSV representation")):
    """Take a screenshot and overlay bounding boxes of interactive elements."""
    response = client.post(f"{SERVER_URL}/visualize")
    if response.status_code == 200:
        data = response.json()
        if show_csv:
            print(data.get("csv", ""))
        else:
            # Print summary and path
            print(json.dumps({
                "success": True,
                "path": data.get("path"),
                "csv_path": data.get("csv_path"),
                "elements_count": data.get("elements_count")
            }, indent=2))
    else:
        handle_response(response)

@app.command()
def detect(show_csv: bool = typer.Option(True, "--csv/--no-csv", help="Show the compact CSV representation")):
    """Detect objects in the current page using YOLO."""
    response = client.post(f"{SERVER_URL}/detect")
    if response.status_code == 200:
        data = response.json()
        if show_csv:
            print(data.get("csv", ""))
        else:
            print(json.dumps(data, indent=2))
    else:
        handle_response(response)

@app.command()
def segment(show_csv: bool = typer.Option(True, "--csv/--no-csv", help="Show the compact CSV representation")):
    """Segment objects in the current page using SAM."""
    response = client.post(f"{SERVER_URL}/segment")
    if response.status_code == 200:
        data = response.json()
        if show_csv:
            print(data.get("csv", ""))
        else:
            print(json.dumps(data, indent=2))
    else:
        handle_response(response)

@app.command()
def wait(selector: str, timeout: int = 10000):
    """Wait for an element matching the selector to appear in the DOM, up to a timeout (ms)."""
    # Since we are moving logic to client/server, we can implement a simple poll here
    # or add a wait endpoint to the server.
    # For simplicity, let's use a simple poll loop in the client or just check once.
    # But the original client had a wait command.
    
    # Let's implement a simple poll using execute
    import time
    start_time = time.time()
    while (time.time() - start_time) * 1000 < timeout:
        check_script = f"() => !!document.querySelector('{selector}')"
        try:
            response = client.post(f"{SERVER_URL}/execute", json={"script": check_script})
            if response.status_code == 200 and response.json().get("result") is True:
                print(json.dumps({"success": True, "selector": selector}, indent=2))
                return
        except:
            pass
        time.sleep(0.5)
    
    print(f"Error: Timeout waiting for selector '{selector}'", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    app()
