"""Protect the archive's explicit companion checkout boundary."""

import os
import subprocess
import sys
from pathlib import Path

from patcheval import batch

ROOT = Path(__file__).resolve().parents[1]


def test_launcher_sets_companion_and_archive_working_directory(tmp_path):
    companion = Path(os.environ["SEC_REVIEW_BOT_ROOT"])
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "run.py"),
            "--main-repo",
            str(companion),
            "--",
            "-c",
            (
                "import os, patcheval, scripts.token_usage; "
                "print(os.getcwd()); print(os.environ['SEC_REVIEW_BOT_ROOT']); "
                "print(patcheval.__file__); print(scripts.token_usage.__file__)"
            ),
        ],
        cwd=tmp_path,
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.splitlines() == [
        str(ROOT),
        str(companion),
        str(ROOT / "patcheval/__init__.py"),
        str(companion / "scripts/token_usage/__init__.py"),
    ]


def test_code_digest_tracks_companion_source_and_dependencies(tmp_path, monkeypatch):
    package = tmp_path / "companion/agents/src/sec_review_agents"
    package.mkdir(parents=True)
    source = package / "__init__.py"
    source.write_text("value = 1\n")
    companion = tmp_path / "companion"
    lock = companion / "agents/uv.lock"
    lock.write_text("version = 1\n")
    (companion / "agents/pyproject.toml").write_text("")
    monkeypatch.setattr(batch.sec_review_agents, "__file__", str(source))
    monkeypatch.setenv("SEC_REVIEW_BOT_ROOT", str(companion))
    initial = batch.code_digest(tmp_path / "archive")
    source.write_text("value = 2\n")
    changed_source = batch.code_digest(tmp_path / "archive")
    assert changed_source != initial
    lock.write_text("version = 2\n")
    assert batch.code_digest(tmp_path / "archive") != changed_source
