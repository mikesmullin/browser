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

def _scan_pids(predicate) -> list[int]:
    """Return PIDs of all processes where predicate(line) is True."""
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    pids = []
    for line in result.stdout.splitlines():
        if predicate(line):
            parts = line.split()
            try:
                pids.append(int(parts[1]))
            except (IndexError, ValueError):
                pass
    return pids


def find_server_pids() -> list[int]:
    """Find all uvicorn browser-server PIDs by scanning the process list."""
    return _scan_pids(lambda l: "uvicorn" in l and "src.server:app" in l)


def find_browser_pids() -> list[int]:
    """Find Chrome/Chromium PIDs that were launched by browser-use (matched by user-data-dir)."""
    marker = str(DATA_DIR)
    return _scan_pids(lambda l: marker in l and "Google Chrome" in l)


@server_app.command()
def stop():
    """Stop the browser server."""
    # Collect all PIDs: the one from the PID file plus any found via process scan
    pids_to_kill: set[int] = set()

    pid_from_file = get_server_pid()
    if pid_from_file:
        pids_to_kill.add(pid_from_file)

    scanned_pids = find_server_pids()
    pids_to_kill.update(scanned_pids)

    browser_pids = find_browser_pids()
    pids_to_kill.update(browser_pids)

    if not pids_to_kill:
        typer.echo("Server is not running.")
        if PID_FILE.exists():
            PID_FILE.unlink()
        return

    stopped: list[int] = []
    failed: list[int] = []

    for pid in sorted(pids_to_kill):
        try:
            os.kill(pid, signal.SIGTERM)
            stopped.append(pid)
        except ProcessLookupError:
            pass  # already gone
        except OSError as exc:
            typer.echo(f"Could not stop PID {pid}: {exc}")
            failed.append(pid)

    # Wait briefly, then SIGKILL any survivors
    if stopped:
        time.sleep(1)
        for pid in stopped:
            try:
                os.kill(pid, 0)  # still alive?
                os.kill(pid, signal.SIGKILL)
                typer.echo(f"Force-killed PID {pid} (did not exit after SIGTERM)")
            except ProcessLookupError:
                pass  # exited cleanly

    if PID_FILE.exists():
        PID_FILE.unlink()

    if stopped or not failed:
        typer.echo(f"✅ Server stopped (PID{'s' if len(stopped) > 1 else ''}: {', '.join(str(p) for p in sorted(stopped or pids_to_kill))})")
    else:
        typer.echo("❌ Failed to stop server.")

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
