# sec-review-thesis-evals

Language: English | [中文](README.zh.md)

An archive of sec-review-bot experiments, evaluation artifacts, and PatchEval adapter scripts. This repository must be used with a compatible sec-review-bot checkout: it is not an independently installable application.

## Ownership

- This repository owns the [evaluation artifacts](evaluation/README.md) and [PatchEval adapters](patcheval/README.md).
- sec-review-bot owns the agent package, model configuration, Python environment, and general-purpose `scripts/token_usage/` tools. Token accounting is reused from that checkout; it is not copied into this archive or moved into the agent package.

Historical reports retain their original results and context. Reproduction also depends on model availability, benchmark images, and configuration; retaining artifacts does not guarantee identical reruns.

## Setup

Run these commands from this repository root, replacing the main checkout path:

```bash
export SEC_REVIEW_BOT_ROOT=/absolute/path/to/sec-review-bot
uv sync --project "$SEC_REVIEW_BOT_ROOT/agents" --group dev
python run.py -- -m patcheval.pool --help
```

Configure model access in the companion checkout's `agents/.env`. The launcher uses its `agents/.venv/bin/python`, sets the companion path, and runs from this archive's root. You can pass `--main-repo /absolute/path/to/sec-review-bot` instead of setting the environment variable. Docker is required for generation and official evaluation.

## Benchmark Compatibility

Use the companion [sec-review-bot thesis-v1 release](https://github.com/Agent-AI-Chalmers/sec-review-bot/releases/tag/thesis-v1), commit `c42cbc9d59b2ee9b1ef07b8eae60086a61195777`. This is the validated companion revision; later revisions may require adapter updates.

The adapters consume legacy PatchEval datasets and `strict_evaluation` / `poc_only_evaluation` results. Use [Agent-AI-Chalmers/PatchEval](https://github.com/Agent-AI-Chalmers/PatchEval) [v1](https://github.com/Agent-AI-Chalmers/PatchEval/releases/tag/v1) (`000dd918ea17f027dd59b272188c8b89f9e50673`) under `PatchEval/`:

```bash
git clone https://github.com/Agent-AI-Chalmers/PatchEval.git PatchEval
git -C PatchEval checkout --detach 000dd918ea17f027dd59b272188c8b89f9e50673
```

The newer Verified benchmark with `poc_evaluation` is not supported by these adapters. Its datasets, images, and result semantics require a separate migration. Do not interpret historical Strict/PoC-only reports as Verified results.

## Usage

Inspect a single-case queue without making a model call:

```bash
python run.py -- -m patcheval.pool \
  --tag LOCAL-CHECK --variant end-to-end-single-agent \
  --only CVE-2023-41039 --dry-run
```

Follow the [adapter guide](patcheval/README.md) for generation, resume, export, and summaries. Generated workspaces and benchmark checkouts are ignored by Git. Use `--freeze-inputs` when the experiment requires input and configuration checks; the code digest includes the installed agent source and the companion dependency files.

For general token reporting, invoke the main repository's tool from its own root and pass absolute paths to archived run directories:

```bash
(cd "$SEC_REVIEW_BOT_ROOT" && agents/.venv/bin/python -m scripts.token_usage.summarize /absolute/path/to/local-run)
```

The launcher adds the companion checkout to `PYTHONPATH`, so PatchEval summaries directly import its `scripts.token_usage` library.

## Checks

```bash
python run.py -- -m ruff check .
python run.py -- -m black --check .
python run.py -- -m compileall -q run.py patcheval tests
python run.py -- -m pytest -q
```

These checks use the companion development dependencies. They do not run real model evaluations.
