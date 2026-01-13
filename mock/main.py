"""Mock - Mock data generator CLI"""

import json
import random
import string
import warnings
from datetime import datetime, timedelta
from typing import Any

import typer

warnings.filterwarnings("ignore", message=".*'mock.main' found in sys.modules.*")

app = typer.Typer(help="Generate mock data for testing and demos", add_completion=True)

SEED = 42


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def random_email() -> str:
    domains = ["example.com", "test.org", "demo.net", "sample.io"]
    return f"{random_string(8)}@{random_domain()}"


def random_domain() -> str:
    domains = ["example.com", "test.org", "demo.net", "sample.io"]
    return random.choice(domains)


def random_name() -> str:
    first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def random_phone() -> str:
    return f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def random_address() -> dict[str, Any]:
    streets = ["Main St", "Oak Ave", "Park Blvd", "Cedar Ln", "Maple Dr", "Pine Rd"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
    return {
        "street": f"{random.randint(100, 9999)} {random.choice(streets)}",
        "city": random.choice(cities),
        "state": random.choice(["NY", "CA", "IL", "TX", "AZ", "PA"]),
        "zip": f"{random.randint(10000, 99999)}",
    }


GENERATORS = {
    "user": lambda: {
        "id": random.randint(1, 10000),
        "name": random_name(),
        "email": random_email(),
        "phone": random_phone(),
        "address": random_address(),
        "created_at": datetime.now().isoformat(),
    },
    "product": lambda: {
        "id": random.randint(1, 1000),
        "name": f"Product {random_string(8).title()}",
        "sku": f"SKU-{random_string(6).upper()}",
        "price": round(random.uniform(10, 1000), 2),
        "category": random.choice(["Electronics", "Clothing", "Books", "Home", "Sports"]),
        "in_stock": random.choice([True, False]),
    },
    "order": lambda: {
        "id": random.randint(1, 100000),
        "customer": random_name(),
        "items": random.randint(1, 5),
        "total": round(random.uniform(50, 500), 2),
        "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
        "created_at": datetime.now().isoformat(),
    },
    "log": lambda: {
        "timestamp": datetime.now().isoformat(),
        "level": random.choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        "message": random.choice([
            "Request processed successfully",
            "Cache miss for key",
            "Database connection established",
            "User login successful",
            "API rate limit approaching",
            "Background job completed",
        ]),
        "service": random.choice(["api", "auth", "database", "cache", "worker"]),
    },
    "event": lambda: {
        "id": random.randint(1, 10000),
        "type": random.choice(["click", "view", "purchase", "signup", "login", "logout"]),
        "user_id": random.randint(1, 1000),
        "timestamp": datetime.now().isoformat(),
        "properties": {
            "page": f"/{random_string(5)}",
            "duration": random.randint(1, 300),
        },
    },
}


@app.command()
def generate(
    type: str = typer.Option("user", "--type", "-t", help="Data type: user, product, order, log, event"),
    count: int = typer.Option(10, "--count", "-n", help="Number of records to generate"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, csv"),
    seed: int = typer.Option(SEED, "--seed", "-s", help="Random seed for reproducibility"),
):
    """Generate mock data"""
    random.seed(seed)

    if type not in GENERATORS:
        typer.echo(f"❌ Unknown type: {type}", err=True)
        typer.echo(f"Available types: {', '.join(GENERATORS.keys())}")
        raise typer.Exit(code=1)

    generator = GENERATORS[type]
    data = [generator() for _ in range(count)]

    if format == "json":
        output = json.dumps(data, indent=2)
    elif format == "csv":
        if data:
            headers = list(data[0].keys())
            output = ",".join(headers) + "\n"
            for item in data:
                values = []
                for v in item.values():
                    if isinstance(v, dict):
                        values.append(json.dumps(v))
                    elif isinstance(v, bool):
                        values.append(str(v).lower())
                    else:
                        values.append(str(v))
                output += ",".join(values) + "\n"
        else:
            output = ""
    else:
        typer.echo(f"❌ Unknown format: {format}", err=True)
        raise typer.Exit(code=1)

    typer.echo(output)


@app.command()
def list():
    """List available generators"""
    typer.echo("📦 Available generators:")
    for name in GENERATORS:
        typer.echo(f"  • {name}")


def main():
    app(prog_name="mock")


if __name__ == "__main__":
    main()
