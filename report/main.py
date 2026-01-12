"""Main entry point for the report CLI application"""
from report.cli.app import app


def main():
    """Main entry point for the report CLI"""
    app(prog_name="report")


if __name__ == "__main__":
    main()
