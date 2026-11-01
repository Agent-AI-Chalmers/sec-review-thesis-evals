"""Select PatchEval cost views using the companion-owned token statistics library."""

import json
from dataclasses import asdict
from pathlib import Path

from scripts.token_usage import (
    collect_used_prices,
    effective_patch_run,
    lightweight_two_stage_run,
    load_price_index,
    load_run_usage,
    run_cost,
)
from scripts.token_usage.output import RenderConfig, render_json

from patcheval.experiments import LIGHTWEIGHT_COST_VARIANTS


def read_usage(records, *, fetch_prices=False, all_runs=()):
    runs = sorted(
        {
            (
                str(Path(row["run_dir"]).resolve()),
                row["experiment"] in LIGHTWEIGHT_COST_VARIANTS.values(),
            )
            for row in records
            if row.get("run_dir") and Path(row["run_dir"]).is_dir()
        }
    )
    if not runs and not all_runs:
        return {"runs": [], "fetched_at": None, "all_runs": []}
    index = load_price_index() if fetch_prices else None
    payload = []
    for path, lightweight in runs:
        run = load_run_usage(Path(path))
        selected = (
            lightweight_two_stage_run(run) if lightweight else effective_patch_run(run)
        )
        cost = run_cost(selected, index)
        payload.append(
            {
                "path": path,
                "lightweight": lightweight,
                "total_tokens": selected.total_tokens,
                "ai_message_count": selected.ai_message_count,
                "ai_messages_with_usage_count": selected.ai_messages_with_usage_count,
                "amount": cost.amount if cost else None,
                "used_prices": {
                    key: asdict(value) if value else None
                    for key, value in collect_used_prices([selected], index).items()
                },
            }
        )
    output = {"runs": payload, "fetched_at": index.fetched_at if index else None}
    if all_runs:
        output["all_runs"] = json.loads(
            render_json(
                [load_run_usage(Path(path)) for path in all_runs],
                RenderConfig(index=index),
            )
        )
    return output
