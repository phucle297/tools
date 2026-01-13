"""Translate - i18n helper CLI"""

import json
import warnings
from pathlib import Path
from typing import Optional

import typer

warnings.filterwarnings("ignore", message=".*'translate.main' found in sys.modules.*")

app = typer.Typer(help="Manage and translate i18n resource files", add_completion=True)


def find_i18n_files(directory: Path) -> list[Path]:
    """Find i18n files in directory"""
    patterns = ["**/*.json", "**/*.yaml", "**/*.yml"]
    files = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))
    return sorted(set(files))


def load_i18n_file(path: Path) -> dict:
    """Load i18n file"""
    if path.suffix == ".json":
        return json.loads(path.read_text())
    elif path.suffix in [".yaml", ".yml"]:
        import yaml
        return yaml.safe_load(path.read_text())
    return {}


def get_keys_recursive(data: dict, prefix: str = "") -> dict[str, str]:
    """Extract all keys from nested dict"""
    keys = {}
    for k, v in data.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(get_keys_recursive(v, full_key))
        else:
            keys[full_key] = str(v)
    return keys


@app.command()
def check(
    directory: Path = typer.Argument(Path("."), help="Directory containing i18n files"),
    reference: str = typer.Option("en", "--reference", "-r", help="Reference language code"),
):
    """Check for missing keys across languages"""
    files = find_i18n_files(directory)

    if not files:
        typer.echo("No i18n files found")
        raise typer.Exit(code=0)

    lang_files = {}
    for f in files:
        lang = f.stem.split(".")[-1] if "." in f.name else f.stem
        if f.name.startswith(f"{reference}."):
            lang_files[reference] = f
        else:
            lang = f.stem.split(".")[-1] if len(f.stem.split(".")) > 1 else f.stem
            lang_files[lang] = f

    if reference not in lang_files:
        typer.echo(f"❌ Reference language '{reference}' not found")
        raise typer.Exit(code=1)

    ref_data = load_i18n_file(lang_files[reference])
    ref_keys = get_keys_recursive(ref_data)

    typer.echo(f"📋 i18n Check (reference: {reference})")
    typer.echo("-" * 50)

    missing_report = {}
    for lang, filepath in lang_files.items():
        if lang == reference:
            continue

        data = load_i18n_file(filepath)
        keys = get_keys_recursive(data)
        missing = set(ref_keys.keys()) - set(keys.keys())

        if missing:
            missing_report[lang] = list(missing)
            typer.echo(f"\n⚠️  {lang}: {len(missing)} missing keys")
            for key in list(missing)[:5]:
                typer.echo(f"  • {key}")
            if len(missing) > 5:
                typer.echo(f"  ... and {len(missing) - 5} more")

    if not missing_report:
        typer.echo("✅ All languages are complete!")


@app.command()
def missing(
    directory: Path = typer.Argument(Path("."), help="Directory containing i18n files"),
    reference: str = typer.Option("en", "--reference", "-r", help="Reference language code"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for missing keys"),
):
    """Export missing keys to a file"""
    files = find_i18n_files(directory)
    lang_files = {}

    for f in files:
        lang = f.stem.split(".")[-1] if "." in f.name else f.stem
        lang_files[lang] = f

    if reference not in lang_files:
        typer.echo(f"❌ Reference language '{reference}' not found")
        raise typer.Exit(code=1)

    ref_data = load_i18n_file(lang_files[reference])
    ref_keys = get_keys_recursive(ref_data)

    missing_all = {}
    for lang, filepath in lang_files.items():
        if lang == reference:
            continue

        data = load_i18n_file(filepath)
        keys = get_keys_recursive(data)
        missing = set(ref_keys.keys()) - set(keys.keys())

        if missing:
            missing_all[lang] = {k: ref_keys[k] for k in missing}

    if output:
        output.write_text(json.dumps(missing_all, indent=2, ensure_ascii=False))
        typer.echo(f"💾 Missing keys exported to: {output}")
    else:
        typer.echo(json.dumps(missing_all, indent=2, ensure_ascii=False))


@app.command()
def stats(
    directory: Path = typer.Argument(Path("."), help="Directory containing i18n files"),
):
    """Show i18n statistics"""
    files = find_i18n_files(directory)

    if not files:
        typer.echo("No i18n files found")
        raise typer.Exit(code=0)

    typer.echo("📊 i18n Statistics")
    typer.echo("-" * 50)

    for f in sorted(files):
        data = load_i18n_file(f)
        keys = get_keys_recursive(data)
        typer.echo(f"{f.name}: {len(keys)} keys")


def main():
    app(prog_name="translate")


if __name__ == "__main__":
    main()
