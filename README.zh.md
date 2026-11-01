# sec-review-thesis-evals

语言：[English](README.md) | 中文

本仓库留存 sec-review-bot 的实验、评测产物与 PatchEval 适配脚本，必须配合兼容的 sec-review-bot 主仓库使用，不是可独立安装的应用。

## 职责归属

- 本仓库维护[评测产物](evaluation/README.md)和 [PatchEval 适配脚本](patcheval/README.zh.md)。
- sec-review-bot 维护 agent 主包、模型配置、Python 环境和通用的 `scripts/token_usage/` 工具。这里复用主仓库的统计能力，不复制这些工具，也不把它们纳入 agent 主包。

历史报告保留原始结果与背景。复现还依赖模型可用性、评测镜像和配置；留档不保证再次运行得到相同结果。

## 配置

从本仓库根目录执行，替换主仓库的绝对路径：

```bash
export SEC_REVIEW_BOT_ROOT=/absolute/path/to/sec-review-bot
uv sync --project "$SEC_REVIEW_BOT_ROOT/agents" --group dev
python run.py -- -m patcheval.pool --help
```

在主仓库的 `agents/.env` 中配置模型访问。入口使用主仓库的 `agents/.venv/bin/python`，设置主仓库路径，并从本留档仓库根目录运行。也可以用 `--main-repo /absolute/path/to/sec-review-bot` 代替环境变量。生成补丁及官方评测需要 Docker。

## 评测版本兼容性

请配合 [sec-review-bot thesis-v1 release](https://github.com/Agent-AI-Chalmers/sec-review-bot/releases/tag/thesis-v1) 使用，对应提交为 `c42cbc9d59b2ee9b1ef07b8eae60086a61195777`。这是已验证的配套版本；后续版本可能需要同步调整适配脚本。

适配脚本读取旧版 PatchEval 数据集和 `strict_evaluation` / `poc_only_evaluation` 结果。请在 `PatchEval/` 使用 [Agent-AI-Chalmers/PatchEval](https://github.com/Agent-AI-Chalmers/PatchEval) 的 [v1](https://github.com/Agent-AI-Chalmers/PatchEval/releases/tag/v1)（`000dd918ea17f027dd59b272188c8b89f9e50673`）：

```bash
git clone https://github.com/Agent-AI-Chalmers/PatchEval.git PatchEval
git -C PatchEval checkout --detach 000dd918ea17f027dd59b272188c8b89f9e50673
```

这些脚本尚未支持采用 `poc_evaluation` 的新版 Verified 评测。其数据集、镜像和结果语义需要另行适配。历史 Strict/PoC-only 报告不能解释为 Verified 结果。

## 使用

检查单案例队列，不调用模型：

```bash
python run.py -- -m patcheval.pool \
  --tag LOCAL-CHECK --variant end-to-end-single-agent \
  --only CVE-2023-41039 --dry-run
```

生成、续跑、导出和汇总见[适配脚本指南](patcheval/README.zh.md)。生成工作区和评测仓库已加入 Git 忽略规则。需要检查输入和配置一致性时使用 `--freeze-inputs`；代码摘要包含实际安装的 agent 源码与主仓库依赖文件。

通用 token 报告应在主仓库根目录调用其工具，并传入留档运行目录的绝对路径：

```bash
(cd "$SEC_REVIEW_BOT_ROOT" && agents/.venv/bin/python -m scripts.token_usage.summarize /absolute/path/to/local-run)
```

入口将主仓库加入 `PYTHONPATH`，PatchEval 汇总直接导入其 `scripts.token_usage` 统计库。

## 检查

```bash
python run.py -- -m ruff check .
python run.py -- -m black --check .
python run.py -- -m compileall -q run.py patcheval tests
python run.py -- -m pytest -q
```

这些检查使用主仓库的开发依赖，不运行真实模型评测。
