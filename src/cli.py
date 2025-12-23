import typer
import subprocess
import sys
import os
import time
import signal
from pathlib import Path
from . import client

app = typer.Typer(help="Browser Agent CLI")
server_app = typer.Typer(help="Manage the browser server")

app.add_typer(client.app, name="client", help="Client commands to control the browser")
app.add_typer(server_app, name="server", help="Server management commands")

# Constants
DATA_DIR = Path.home() / ".browser_agent"
PID_FILE = DATA_DIR / "server.pid"
LOG_FILE = DATA_DIR / "server.log"

def get_server_pid():
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except ValueError:
            return None
    return None

@server_app.command()
def start(
    port: int = 3001,
    host: str = "localhost",
    background: bool = True,
):
    """Start the browser server."""
    DATA_DIR.mkdir(exist_ok=True)
    
    pid = get_server_pid()
    if pid:
        try:
            os.kill(pid, 0)
            typer.echo(f"Server is already running (PID {pid})")
            return
        except OSError:
            # Process not found, remove stale PID file
            PID_FILE.unlink()

    typer.echo("Starting browser server...")
    
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.server:app",
        "--host",
        host,
        "--port",
        str(port),
    ]

    if background:
        with open(LOG_FILE, "a") as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=log,
                start_new_session=True
            )
        
        PID_FILE.write_text(str(process.pid))
        typer.echo(f"✅ Server started in background (PID {process.pid})")
        typer.echo(f"Logs: {LOG_FILE}")
    else:
        # Run in foreground
        subprocess.run(cmd)

@server_app.command()
def stop():
    """Stop the browser server."""
    pid = get_server_pid()
    if not pid:
        typer.echo("Server is not running.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
        typer.echo(f"✅ Server stopped (PID {pid})")
        if PID_FILE.exists():
            PID_FILE.unlink()
    except OSError:
        typer.echo(f"Could not stop server (PID {pid}). It might have already exited.")
        if PID_FILE.exists():
            PID_FILE.unlink()

@server_app.command()
def status():
    """Check server status."""
    pid = get_server_pid()
    if pid:
        try:
            os.kill(pid, 0)
            typer.echo(f"✅ Server is running (PID {pid})")
            
            # Show last few lines of log
            if LOG_FILE.exists():
                typer.echo("\nLast 5 log lines:")
                try:
                    # Simple tail implementation
                    lines = LOG_FILE.read_text().splitlines()
                    for line in lines[-5:]:
                        typer.echo(line)
                except Exception:
                    pass
        except OSError:
            typer.echo(f"❌ Server is not running (Stale PID {pid})")
    else:
        typer.echo("❌ Server is not running")

@server_app.command()
def logs(follow: bool = False):
    """View server logs."""
    if not LOG_FILE.exists():
        typer.echo("No log file found.")
        return

    if follow:
        try:
            subprocess.run(["tail", "-f", str(LOG_FILE)])
        except KeyboardInterrupt:
            pass
    else:
        typer.echo(LOG_FILE.read_text())

if __name__ == "__main__":
    app()
