from typing import Annotated

import typer

from error_digest.config import load_config
from error_digest.pipeline import run_digest

app = typer.Typer()


@app.command()
def run(
    config: Annotated[
        str, typer.Option("--config", "-c", help="YAML Config path")
    ] = "error_digest.yaml",
    dry_run: Annotated[
        bool, typer.Option("--dry-run/--apply", help="Only view, no sinks call")
    ] = True,
):
    cfg = load_config(config)
    result = run_digest(cfg, dry_run=dry_run)


@app.callback()
def main():
    """error-digest: Turn noisy production logs into a short, actionable list of issues."""
