"""Commit message generator - Main entry point"""

from commit.cli import app


def main():
    """Main entry point"""
    app(prog_name="commit")


if __name__ == "__main__":
    main()
