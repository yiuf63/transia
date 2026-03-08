"""CLI entrypoint for translating books and managing engine profiles."""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .translation_service import TranslationService, TransiaEvent
from .standalone_utils import ConfigurationManager, logger

app = typer.Typer(help="Transia: Next-Gen AI Ebook Translator", rich_markup_mode="rich")
config_app = typer.Typer(help="Manage engine profiles")
app.add_typer(config_app, name="config")

console = Console()
config_manager = ConfigurationManager()


def _validate_output_path(input_file: Path, output_file: Path) -> Optional[str]:
    expected_ext = {
        ".epub": ".epub",
        ".srt": ".srt",
    }.get(input_file.suffix.lower())
    if expected_ext is None:
        return None
    if output_file.suffix.lower() != expected_ext:
        return (
            f"Output extension mismatch: input '{input_file.suffix.lower()}' "
            f"requires output '{expected_ext}'."
        )
    return None


@app.command()
def translate(
    input_file: Path = typer.Argument(..., help="Input EPUB/SRT file", exists=True),
    output_file: Path = typer.Argument(..., help="Output file path"),
    target: str = typer.Option("zh", "--target", "-t", help="Target language code"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile from config.json"),
    bilingual: bool = typer.Option(True, "--bilingual/--single", help="Bilingual or single output"),
    search: bool = typer.Option(False, "--search", "-s", help="Enable internet search"),
    summarize: bool = typer.Option(False, "--summarize", help="Enable rolling chapter summary"),
    translator_notes: Optional[Path] = typer.Option(None, "--notes", help="Path to save cultural/historical notes (MD)."),
    concurrency: int = typer.Option(5, "--concurrency", "-c")
) -> None:
    """Translate an ebook with high performance."""
    profile_data: Optional[Dict[str, Any]] = (
        config_manager.get_profile(profile) if profile else {"engine": "google"}
    )
    if profile and profile_data is None:
        console.print(f"[red]Error: Profile '{profile}' not found.[/red]")
        raise typer.Exit(1)
    if profile_data is None:
        console.print("[red]Error: Invalid profile configuration.[/red]")
        raise typer.Exit(1)
    if validation_error := _validate_output_path(input_file, output_file):
        console.print(f"[red]Error: {validation_error}[/red]")
        raise typer.Exit(1)

    service = TranslationService(profile_data, target_lang=target)
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(bar_width=40), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task("Initializing...", total=100)
        def update_progress(curr: int, total: int, msg: str) -> None:
            percent = (curr / total) * 100 if total > 0 else 0
            progress.update(task, completed=percent, description=f"Processing: {msg}")
        service.subscribe(TransiaEvent.PROGRESS, update_progress)

        try:
            success = asyncio.run(service.translate(
                str(input_file), str(output_file), 
                {"bilingual": bilingual, "summarize": summarize, "concurrency": concurrency, "search": search, "notes_path": str(translator_notes) if translator_notes else None}
            ))
            if not success:
                console.print("[bold red]Translation failed. Check logs for details.[/bold red]")
                raise typer.Exit(1)
            progress.update(task, completed=100, description="Done!")
        except typer.Exit:
            raise
        except Exception as e:
            logger.error(f"Translation Error: {e}")
            console.print(f"[bold red]Translation Error: {e}[/bold red]")
            raise typer.Exit(1)

    console.print(f"[bold green]✨ Success! Saved to {output_file}[/bold green]")
    if translator_notes: console.print(f"[blue]✒️ Translator's notes saved to {translator_notes}[/blue]")

@config_app.command("list")
def list_profiles() -> None:
    profiles = config_manager.get("profiles", {})
    if not profiles:
        console.print("No profiles configured.")
        return
    table = Table(title="Transia Engine Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Engine", style="magenta")
    table.add_column("Model")
    table.add_column("Endpoint")
    for name, data in profiles.items():
        table.add_row(name, data.get("engine", "openai"), data.get("model", "N/A"), data.get("endpoint", "Official API"))
    console.print(table)

@config_app.command("add")
def add_profile(
    name: str,
    engine: str = typer.Option("openai", help="openai, deepseek, anthropic"),
    model: str = typer.Option(..., prompt=True),
    api_key: str = typer.Option(..., prompt=True, hide_input=True),
    endpoint: Optional[str] = typer.Option(None, help="Custom API endpoint URL"),
    system_prompt: Optional[str] = typer.Option(None, help="Custom translation instructions (style)")
) -> None:
    """Add a new engine profile."""
    profiles = config_manager.get("profiles", {})
    profiles[name] = {"engine": engine, "model": model, "api_key": api_key}
    if endpoint: profiles[name]["endpoint"] = endpoint
    if system_prompt: profiles[name]["system_prompt"] = system_prompt
    config_manager.set("profiles", profiles)
    console.print(f"[green]Profile '{name}' added successfully![/green]")

if __name__ == "__main__":
    app()
