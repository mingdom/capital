"""Interactive shell that wraps the Typer CLI commands."""

from __future__ import annotations

import cmd
import os
import shlex
import sys
from typing import Iterable

import click
import typer

from typer.main import get_command

from portfolio_cli.performance import SUPPORTED_SOURCES


class PortfolioShell(cmd.Cmd):
    intro = (
        "Welcome to the Mingdom Capital CLI. Default source is SavvyTrader. "
        "Use 'sources' to view available formats, 'help' for commands, and press Tab "
        "to autocomplete known options."
    )
    prompt = "portfolio> "

    def __init__(self, typer_app: typer.Typer, commands: Iterable[str] | None = None) -> None:
        super().__init__()
        self._typer_app = typer_app
        self._click_app = get_command(self._typer_app)
        if commands is not None:
            self.cmdqueue = list(commands)

    # ---------- helpers -------------------------------------------------
    def _run_cli(self, args: Iterable[str]) -> None:
        """Execute the Typer CLI with the provided argument list."""

        try:
            self._click_app.main(
                args=list(args),
                prog_name="portfolio-cli",
                standalone_mode=False,
            )
        except click.ClickException as exc:
            exc.show()
        except SystemExit as exc:  # pragma: no cover - handled to avoid shell exit
            if exc.code not in (0, None):
                typer.echo(f"Command exited with status {exc.code}")

    def _show_command_help(self, command_name: str) -> None:
        ctx = click.Context(self._click_app)
        command = self._click_app.get_command(ctx, command_name)
        if command is None:
            typer.echo(f"Unknown command: {command_name}")
            return
        with click.Context(command) as sub_ctx:
            typer.echo(command.get_help(sub_ctx))

    # ---------- commands ------------------------------------------------
    def do_performance(self, arg: str) -> bool | None:
        """Show portfolio performance. Usage: performance [sources] [options]"""

        parsed = shlex.split(arg)
        self._run_cli(["performance", *parsed])
        return None

    def complete_performance(self, text: str, line: str, begidx: int, endidx: int):
        try:
            tokens = shlex.split(line[:begidx])
        except ValueError:
            tokens = line[:begidx].split()

        flags = [
            "--savvy-json",
            "--fidelity-csv",
            "--rf",
            "--year",
            "--benchmarks",
            "--no-benchmarks",
        ]

        if len(tokens) <= 1:
            if not text:
                return list(SUPPORTED_SOURCES)
            return [src for src in SUPPORTED_SOURCES if src.startswith(text)]

        if text.startswith("--"):
            return [flag for flag in flags if flag.startswith(text)]

        if tokens and tokens[-1] in SUPPORTED_SOURCES:
            return [flag for flag in flags if flag.startswith(text)]

        return [src for src in SUPPORTED_SOURCES if src.startswith(text)]

    def help_performance(self) -> None:  # pragma: no cover - passthrough help
        self._show_command_help("performance")

    def do_report(self, arg: str) -> bool | None:
        """Generate the HTML report. Usage: report [sources] [options]"""

        parsed = shlex.split(arg)
        self._run_cli(["report", *parsed])
        return None

    def complete_report(self, text: str, line: str, begidx: int, endidx: int):
        try:
            tokens = shlex.split(line[:begidx])
        except ValueError:
            tokens = line[:begidx].split()

        flags = [
            "--output",
            "--title",
            "--savvy-json",
            "--fidelity-csv",
            "--rf",
            "--year",
            "--benchmarks",
            "--no-benchmarks",
        ]

        if len(tokens) <= 1:
            if not text:
                return list(SUPPORTED_SOURCES)
            return [src for src in SUPPORTED_SOURCES if src.startswith(text)]

        if text.startswith("--"):
            return [flag for flag in flags if flag.startswith(text)]

        if tokens and tokens[-1] in SUPPORTED_SOURCES:
            return [flag for flag in flags if flag.startswith(text)]

        return [src for src in SUPPORTED_SOURCES if src.startswith(text)]

    def help_report(self) -> None:  # pragma: no cover - passthrough help
        self._show_command_help("report")

    def do_commands(self, arg: str) -> bool | None:  # pragma: no cover - passthrough
        """List available commands."""

        self.stdout.write("Available commands:\n")
        for name in sorted(self.get_names()):
            if name.startswith("do_"):
                self.stdout.write(f"  {name[3:]}\n")
        return None

    def do_reload(self, arg: str) -> bool | None:
        """Reload the CLI by restarting the current Python process."""

        typer.echo("Reloading CLI...")
        python = sys.executable
        args = [python, "-m", "portfolio_cli", "interactive"]
        os.execv(python, args)
        return None

    def do_sources(self, arg: str) -> bool | None:
        """Describe supported portfolio data formats."""

        typer.echo("Supported sources:")
        typer.echo("  savvytrader (default)")
        typer.echo("    File: data/valuations.json")
        typer.echo("    Use: performance savvytrader [flags]")
        typer.echo("  fidelity")
        typer.echo("    File: data/private/fidelity-performance.csv")
        typer.echo("    Use: performance fidelity --fidelity-csv path/to/export.csv")
        return None

    def do_help(self, arg: str) -> bool | None:  # pragma: no cover - passthrough
        arg = arg.strip()
        if arg:
            return super().do_help(arg)
        typer.echo("Core commands:")
        typer.echo("  performance [sources]  Show monthly returns (e.g., performance fidelity)")
        typer.echo("  report [sources]       Generate HTML report")
        typer.echo("  sources                Show supported data formats and default files")
        typer.echo("  reload                 Restart the CLI to pull in code changes")
        typer.echo("  help <command>       Show command-specific help")
        typer.echo("  exit                 Quit the shell")
        typer.echo("\nTyper CLI usage remains available via 'portfolio-cli <command>'.")
        return None

    def do_ls(self, arg: str) -> bool | None:
        """Alias for `help` to list available commands."""

        return self.do_help(arg)

    def do_exit(self, arg: str) -> bool | None:
        """Exit the shell."""

        typer.echo("Goodbye!")
        return True

    do_quit = do_exit

    def do_EOF(self, line: str) -> bool | None:  # pragma: no cover - interactive
        typer.echo("Goodbye!")
        return True


def start_shell(typer_app: typer.Typer, commands: Iterable[str] | None = None) -> None:
    """Launch the interactive shell."""

    PortfolioShell(typer_app, commands=commands).cmdloop()
