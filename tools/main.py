"""Tools CLI - Toolkit management"""

import typer

from shared.completion import TOOLS as ALL_TOOLS

app = typer.Typer(
    name="tools",
    help="Manage toolkit commands",
    no_args_is_help=True,
)


@app.command(name="list")
def list_tools():
    """List all available toolkit commands"""
    typer.echo("🛠️  Available toolkit commands:\n")

    tools_info = {
        "report": "Daily & Weekly Git Report CLI",
        "review": "Code review helper",
        "benchmark": "Performance benchmark CLI",
        "translate": "i18n helper",
        "port": "Port conflict resolver",
    }

    for tool in ALL_TOOLS:
        desc = tools_info.get(tool, "")
        typer.echo(f"  • {tool:<12} {desc}")

    typer.echo()


@app.command(name="completion")
def tools_completion(
    shell: str = typer.Option(
        None,
        "--shell",
        "-s",
        help="Shell type (bash, zsh, fish). Auto-detected if not specified.",
    ),
):
    """Install shell completion for all toolkit commands"""
    from pathlib import Path

    import typer

    from shared.completion import (
        detect_shell,
        install_all_bash_completion,
        install_all_zsh_completion,
        install_all_fish_completion,
    )

    if not shell:
        shell = detect_shell()

    if shell == "unknown":
        typer.echo("❌ Could not detect shell. Please specify with --shell", err=True)
        typer.echo("\nAvailable shells: bash, zsh, fish")
        raise typer.Exit(code=1)

    typer.echo(f"🔧 Installing {shell} completion for all toolkit commands...")

    if shell == "bash":
        install_all_bash_completion()
        tools_script = """# tools bash completion
_tools_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _TOOLS_COMPLETE=complete_bash tools ) )
    return 0
}
complete -o default -F _tools_completion tools
"""
        bash_completion_file = Path.home() / ".bash_completions" / "tools.sh"
        bash_completion_file.write_text(tools_script)
        typer.echo(f"✅ Created: {bash_completion_file}")

    elif shell == "zsh":
        install_all_zsh_completion()
        tools_script = """#compdef tools

_tools_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[tools] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _TOOLS_COMPLETE=complete_zsh tools)}")

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

compdef _tools_completion tools"""
        zsh_completion_file = Path.home() / ".zsh" / "completions" / "_tools"
        zsh_completion_file.write_text(tools_script)
        typer.echo(f"✅ Created: {zsh_completion_file}")

    elif shell == "fish":
        install_all_fish_completion()
        tools_script = "complete --command tools --no-files --arguments '(env _TOOLS_COMPLETE=complete_fish _TYPER_COMPLETE_FISH_ACTION=get-args _TYPER_COMPLETE_ARGS=(commandline -cp) tools)'\n"
        fish_completion_file = Path.home() / ".config" / "fish" / "completions" / "tools.fish"
        fish_completion_file.write_text(tools_script)
        typer.echo(f"✅ Created: {fish_completion_file}")

    typer.echo("\nRestart terminal or run: source ~/.config/fish/config.fish (fish)")


def main():
    app(prog_name="tools")


if __name__ == "__main__":
    main()
