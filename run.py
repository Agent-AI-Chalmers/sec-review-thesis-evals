"""Run archive tools with an explicitly selected sec-review-bot checkout."""

import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--main-repo", type=Path, default=os.environ.get("SEC_REVIEW_BOT_ROOT")
    )
    parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="Python arguments after --"
    )
    args = parser.parse_args()
    if args.main_repo is None:
        parser.error("set SEC_REVIEW_BOT_ROOT or pass --main-repo")
    main_root = args.main_repo.expanduser().resolve()
    python = main_root / "agents/.venv/bin/python"
    if (
        not python.is_file()
        or not (main_root / "scripts/token_usage/summarize.py").is_file()
    ):
        parser.error(
            "main checkout must contain scripts/token_usage and agents/.venv; run uv sync in agents first"
        )
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("provide Python arguments, e.g. -- -m patcheval.pool --help")
    os.environ["SEC_REVIEW_BOT_ROOT"] = str(main_root)
    # Make repository-owned reporting tools available to this process and workers.
    os.environ["PYTHONPATH"] = os.pathsep.join(
        [str(main_root), *filter(None, [os.environ.get("PYTHONPATH", "")])]
    )
    os.chdir(Path(__file__).resolve().parent)
    os.execv(str(python), [str(python), *command])


if __name__ == "__main__":
    main()
