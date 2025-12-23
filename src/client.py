
import typer
import httpx
import sys
import json
from typing import Optional

app = typer.Typer()
SERVER_URL = "http://localhost:3001"

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
    """Get the status of the browser server."""
    try:
        response = httpx.get(f"{SERVER_URL}/status")
        handle_response(response)
    except httpx.ConnectError:
        print("Error: Could not connect to server. Is it running?", file=sys.stderr)
        sys.exit(1)

@app.command()
def navigate(url: str):
    """Navigate the browser to a URL."""
    response = httpx.post(f"{SERVER_URL}/navigate", json={"url": url})
    handle_response(response)

@app.command()
def click(selector: str):
    """Click an element matching the selector."""
    response = httpx.post(f"{SERVER_URL}/click", json={"selector": selector})
    handle_response(response)

@app.command()
def fill(selector: str, value: str):
    """Fill an input element matching the selector with a value."""
    response = httpx.post(f"{SERVER_URL}/fill", json={"selector": selector, "value": value})
    handle_response(response)

@app.command()
def execute(script: str):
    """Execute JavaScript in the browser."""
    response = httpx.post(f"{SERVER_URL}/execute", json={"script": script})
    handle_response(response)

@app.command()
def dom(selector: str = "body"):
    """Get the outerHTML of an element."""
    response = httpx.post(f"{SERVER_URL}/dom", json={"selector": selector})
    handle_response(response)

@app.command()
def wait(selector: str, timeout: int = 10000):
    """Wait for an element to appear (simulated via polling)."""
    # Since we are moving logic to client/server, we can implement a simple poll here
    # or add a wait endpoint to the server.
    # For simplicity, let's use a simple poll loop in the client or just check once.
    # But the original client had a wait command.
    
    # Let's implement a simple poll using execute
    import time
    start_time = time.time()
    while (time.time() - start_time) * 1000 < timeout:
        check_script = f"!!document.querySelector('{selector}')"
        try:
            response = httpx.post(f"{SERVER_URL}/execute", json={"script": check_script})
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
