
from typing import Annotated

from error_digest.config import load_config
from error_digest.pipeline import run_digest
import typer

app = typer.Typer()

@app.command()
def run(
    config: Annotated[str, typer.Option("--config", "-c", help="Caminho do YAML")] = "error_digest.yaml",
    dry_run: Annotated[bool, typer.Option("--dry-run/--apply", help="Só mostra, sem criar issues")] = True,
):
    cfg = load_config(config)
    result = run_digest(cfg, dry_run=dry_run)


@app.callback()
def main():
    """error-digest: transforma erros do Loki/Tempo em issues."""
