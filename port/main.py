"""Port - Port conflict resolver CLI"""

import os
import signal
import subprocess
import warnings
from typing import Optional

import typer

warnings.filterwarnings("ignore", message=".*'port.main' found in sys.modules.*")

app = typer.Typer(help="Detect and resolve port conflicts", add_completion=True)


def get_process_info_linux(pid: int) -> dict:
    """Get process info on Linux"""
    try:
        cmdline = f"/proc/{pid}/cmdline"
        if os.path.exists(cmdline):
            cmd = open(cmdline).read().replace("\x00", " ")
            return {"pid": pid, "cmd": cmd[:100]}
    except Exception:
        pass
    return {"pid": pid, "cmd": "Unknown"}


def find_process_on_port(port: int) -> Optional[dict]:
    """Find process using a specific port"""
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-t"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            if pids and pids[0]:
                pid = int(pids[0])
                return get_process_info_linux(pid)
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return None


def get_all_ports() -> list[tuple[int, int]]:
    """Get all listening ports with PIDs"""
    ports = []
    try:
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True,
        )
        for line in result.stdout.split("\n"):
            if ":" in line and "LISTEN" in line:
                parts = line.split()
                for part in parts:
                    if part.startswith(":"):
                        try:
                            port = int(part.replace(":", ""))
                            ports.append((port, None))
                        except ValueError:
                            pass
    except Exception:
        pass
    return ports


def get_free_port(start: int = 8000, end: int = 9000) -> int:
    """Find a free port in range"""
    for port in range(start, end + 1):
        if find_process_on_port(port) is None:
            return port
    raise ValueError(f"No free port found in range {start}-{end}")


@app.command()
def list(
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Check specific port"),
):
    """List used ports"""
    if port:
        proc = find_process_on_port(port)
        if proc:
            typer.echo(f"🔴 Port {port} is in use:")
            typer.echo(f"   PID: {proc['pid']}")
            typer.echo(f"   Command: {proc['cmd']}")
        else:
            typer.echo(f"🟢 Port {port} is free")
    else:
        typer.echo("📋 Listening Ports")
        typer.echo("-" * 40)
        ports = get_all_ports()[:20]
        for p, _ in ports:
            proc = find_process_on_port(p)
            if proc:
                typer.echo(f"🔴 {p:5} - {proc['cmd'][:40]}")
            else:
                typer.echo(f"🟢 {p:5} - Unknown process")


@app.command()
def find(
    port: int = typer.Argument(..., help="Port number to check"),
    kill: bool = typer.Option(False, "--kill", "-k", help="Kill the process using the port"),
):
    """Find process using a port"""
    proc = find_process_on_port(port)

    if proc:
        typer.echo(f"🔴 Port {port} is in use:")
        typer.echo(f"   PID: {proc['pid']}")
        typer.echo(f"   Command: {proc['cmd']}")

        if kill:
            try:
                os.kill(proc["pid"], signal.SIGTERM)
                typer.echo(f"✅ Process {proc['pid']} terminated")
            except Exception as e:
                typer.echo(f"❌ Failed to kill process: {e}")
    else:
        typer.echo(f"🟢 Port {port} is free")


@app.command()
def free(
    start: int = typer.Option(8000, "--start", "-s", help="Start of port range"),
    end: int = typer.Option(9000, "--end", "-e", help="End of port range"),
):
    """Find a free port in range"""
    try:
        port = get_free_port(start, end)
        typer.echo(f"🟢 Free port found: {port}")
    except ValueError as e:
        typer.echo(f"❌ {e}")


def main():
    app(prog_name="port")


if __name__ == "__main__":
    main()
