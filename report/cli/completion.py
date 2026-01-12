"""Shell completion command"""

import os
from pathlib import Path

import typer

# Create a sub-app for completion
completion_app = typer.Typer(
    help="Install or show shell completion",
    no_args_is_help=True,
)


@completion_app.command(name="install")
def install(
    shell: str = typer.Option(
        None,
        "--shell",
        "-s",
        help="Shell type (bash, zsh, fish). Auto-detected if not specified.",
    ),
):
    """Install shell completion for the 'report' command"""
    # Detect shell if not specified
    if not shell:
        shell_env = os.environ.get("SHELL", "")
        if "bash" in shell_env:
            shell = "bash"
        elif "zsh" in shell_env:
            shell = "zsh"
        elif "fish" in shell_env:
            shell = "fish"
        else:
            typer.echo("❌ Could not detect shell. Please specify with --shell", err=True)
            typer.echo("\nAvailable shells: bash, zsh, fish")
            raise typer.Exit(code=1)

    typer.echo(f"Installing {shell} completion for 'report' command...")

    if shell == "bash":
        install_bash_completion()
    elif shell == "zsh":
        install_zsh_completion()
    elif shell == "fish":
        install_fish_completion()
    else:
        typer.echo(f"❌ Unsupported shell: {shell}", err=True)
        typer.echo("\nSupported shells: bash, zsh, fish")
        raise typer.Exit(code=1)


def install_bash_completion():
    """Install bash completion"""
    completion_dir = Path.home() / ".bash_completions"
    completion_dir.mkdir(exist_ok=True)

    completion_file = completion_dir / "report.sh"

    # Generate completion script
    script = """_report_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   _REPORT_COMPLETE=complete_bash $1 ) )
    return 0
}

complete -o default -F _report_completion report"""

    completion_file.write_text(script)

    # Check if it's sourced in .bashrc
    bashrc = Path.home() / ".bashrc"
    source_line = f"source {completion_file}"

    if bashrc.exists():
        content = bashrc.read_text()
        if source_line not in content:
            typer.echo(f"\n✅ Completion script created at: {completion_file}")
            typer.echo("\nTo enable completion, add this line to your ~/.bashrc:")
            typer.echo(f"    {source_line}")
            typer.echo("\nThen run: source ~/.bashrc")
        else:
            typer.echo(f"✅ Completion already configured in ~/.bashrc")
            typer.echo(f"✅ Completion script updated at: {completion_file}")
            typer.echo("\nRun: source ~/.bashrc (or restart your terminal)")
    else:
        typer.echo(f"✅ Completion script created at: {completion_file}")
        typer.echo("\nAdd this line to your ~/.bashrc:")
        typer.echo(f"    {source_line}")


def install_zsh_completion():
    """Install zsh completion"""
    # For zsh, we need to add to fpath
    completion_dir = Path.home() / ".zsh" / "completions"
    completion_dir.mkdir(parents=True, exist_ok=True)

    completion_file = completion_dir / "_report"

    # Generate completion script
    script = """#compdef report

_report_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[report] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _REPORT_COMPLETE=complete_zsh report)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _report_completion report"""

    completion_file.write_text(script)

    zshrc = Path.home() / ".zshrc"
    fpath_line = f"fpath=({completion_dir} $fpath)"

    typer.echo(f"✅ Completion script created at: {completion_file}")
    typer.echo("\nAdd these lines to your ~/.zshrc:")
    typer.echo(f"    {fpath_line}")
    typer.echo("    autoload -Uz compinit && compinit")
    typer.echo("\nThen run: source ~/.zshrc (or restart your terminal)")


def install_fish_completion():
    """Install fish completion"""
    completion_dir = Path.home() / ".config" / "fish" / "completions"
    completion_dir.mkdir(parents=True, exist_ok=True)

    completion_file = completion_dir / "report.fish"

    # Generate completion script using Typer's fish completion format
    script = """complete --command report --no-files --arguments "(env _REPORT_COMPLETE=complete_fish _TYPER_COMPLETE_FISH_ACTION=get-args _TYPER_COMPLETE_ARGS=(commandline -cp) report)" --condition "env _REPORT_COMPLETE=complete_fish _TYPER_COMPLETE_FISH_ACTION=is-args _TYPER_COMPLETE_ARGS=(commandline -cp) report"
"""

    completion_file.write_text(script)

    typer.echo(f"✅ Completion installed at: {completion_file}")
    typer.echo("\nRestart your terminal or run: source ~/.config/fish/config.fish")


@completion_app.command(name="show")
def show(
    shell: str = typer.Option(
        None,
        "--shell",
        "-s",
        help="Shell type (bash, zsh, fish). Auto-detected if not specified.",
    ),
):
    """Show completion script for the current shell"""
    # Detect shell if not specified
    if not shell:
        shell_env = os.environ.get("SHELL", "")
        if "bash" in shell_env:
            shell = "bash"
        elif "zsh" in shell_env:
            shell = "zsh"
        elif "fish" in shell_env:
            shell = "fish"
        else:
            typer.echo("❌ Could not detect shell. Please specify with --shell", err=True)
            raise typer.Exit(code=1)

    typer.echo(f"# {shell.upper()} completion script for 'report'\n")

    if shell == "bash":
        typer.echo(
            """_report_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   _REPORT_COMPLETE=complete_bash $1 ) )
    return 0
}

complete -o default -F _report_completion report"""
        )
    elif shell == "zsh":
        typer.echo(
            """#compdef report

_report_completion() {
    # ZSH completion script
    # Add to fpath and run: autoload -Uz compinit && compinit
}

compdef _report_completion report"""
        )
    elif shell == "fish":
        typer.echo(
            """complete --command report --no-files --arguments "(env _REPORT_COMPLETE=complete_fish _TYPER_COMPLETE_FISH_ACTION=get-args _TYPER_COMPLETE_ARGS=(commandline -cp) report)" --condition "env _REPORT_COMPLETE=complete_fish _TYPER_COMPLETE_FISH_ACTION=is-args _TYPER_COMPLETE_ARGS=(commandline -cp) report"
"""
        )
    else:
        typer.echo(f"❌ Unsupported shell: {shell}", err=True)
        raise typer.Exit(code=1)
