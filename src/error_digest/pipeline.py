from error_digest.core.fingerprint import group_by_fingerprint

from src.error_digest.config import Config


def run_digest(config: Config, dry_run: bool = True):
    logs = config.source.fetch_errors(since=config.window)

    groups = group_by_fingerprint(logs)



    return
