"""Benchmark - Performance benchmark CLI"""

import json
import shutil
import subprocess
import time
import warnings
from pathlib import Path
from typing import NamedTuple, Optional

import typer

warnings.filterwarnings("ignore", message=".*'benchmark.main' found in sys.modules.*")

app = typer.Typer(help="Measure and compare performance metrics", add_completion=True)

BENCHMARK_DIR = Path.home() / ".cache" / "toolkit-benchmarks"
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)


class BenchmarkResult(NamedTuple):
    """Result of a benchmark run"""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    timestamp: str


def run_command(cmd: str, iterations: int = 3) -> dict:
    """Run a command and measure its performance"""
    times = []
    output = ""

    for _ in range(iterations):
        start = time.perf_counter()
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout or result.stderr
        except subprocess.TimeoutExpired:
            output = "Timeout"
        except Exception as e:
            output = str(e)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "iterations": iterations,
        "times": times,
        "total_time": sum(times),
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "output": output[:500],
    }


def save_result(result: dict, name: str):
    """Save benchmark result to file"""
    filepath = BENCHMARK_DIR / f"{name}.json"
    filepath.write_text(json.dumps(result, indent=2))
    return filepath


def load_result(name: str) -> Optional[dict]:
    """Load benchmark result from file"""
    filepath = BENCHMARK_DIR / f"{name}.json"
    if filepath.exists():
        return json.loads(filepath.read_text())
    return None


def format_delta(old: float, new: float) -> str:
    """Format the delta between two values"""
    delta = new - old
    percent = (delta / old * 100) if old > 0 else 0
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:.4f}s ({sign}{percent:.1f}%)"


@app.command()
def run(
    name: str = typer.Argument(..., help="Benchmark name"),
    cmd: str = typer.Option(..., "--command", "-c", help="Command to benchmark"),
    iterations: int = typer.Option(3, "--iterations", "-n", help="Number of iterations"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save result for comparison"),
):
    """Run a benchmark"""
    typer.echo(f"🏃 Running benchmark: {name}")
    typer.echo(f"Command: {cmd}")
    typer.echo(f"Iterations: {iterations}")
    typer.echo("-" * 40)

    result = run_command(cmd, iterations)

    typer.echo(f"Total time: {result['total_time']:.4f}s")
    typer.echo(f"Average: {result['avg_time']:.4f}s")
    typer.echo(f"Min: {result['min_time']:.4f}s")
    typer.echo(f"Max: {result['max_time']:.4f}s")

    if save:
        filepath = save_result(result, name)
        typer.echo(f"\n💾 Saved to: {filepath}")

    previous = load_result(name)
    if previous:
        typer.echo("\n📊 Comparison with previous run:")
        typer.echo(f"  Average: {format_delta(previous['avg_time'], result['avg_time'])}")


@app.command()
def compare(
    name1: str = typer.Argument(..., help="First benchmark name"),
    name2: str = typer.Argument(..., help="Second benchmark name"),
):
    """Compare two benchmark results"""
    result1 = load_result(name1)
    result2 = load_result(name2)

    if not result1:
        typer.echo(f"❌ Benchmark '{name1}' not found", err=True)
        raise typer.Exit(code=1)

    if not result2:
        typer.echo(f"❌ Benchmark '{name2}' not found", err=True)
        raise typer.Exit(code=1)

    typer.echo("📊 Benchmark Comparison")
    typer.echo("-" * 40)
    typer.echo(f"{name1}: {result1['avg_time']:.4f}s avg")
    typer.echo(f"{name2}: {result2['avg_time']:.4f}s avg")
    typer.echo("")
    typer.echo(f"Delta: {format_delta(result1['avg_time'], result2['avg_time'])}")

    if result1['avg_time'] < result2['avg_time']:
        typer.echo(f"✅ {name1} is faster")
    else:
        typer.echo(f"✅ {name2} is faster")


@app.command()
def history():
    """Show benchmark history"""
    typer.echo("📜 Benchmark History")
    typer.echo("-" * 40)

    benchmarks = sorted(BENCHMARK_DIR.glob("*.json"))

    if not benchmarks:
        typer.echo("No benchmarks saved yet.")
        raise typer.Exit(code=0)

    for filepath in benchmarks[-10:]:
        data = json.loads(filepath.read_text())
        typer.echo(f"  • {filepath.stem}: {data['avg_time']:.4f}s avg ({data['iterations']} iterations)")


@app.command()
def clear():
    """Clear benchmark history"""
    global BENCHMARK_DIR
    import shutil
    if BENCHMARK_DIR.exists():
        shutil.rmtree(BENCHMARK_DIR)
        BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
        typer.echo("✅ Benchmark history cleared")


def main():
    app(prog_name="benchmark")


if __name__ == "__main__":
    main()
