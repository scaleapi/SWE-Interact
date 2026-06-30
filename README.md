# SWE-Interact

[![arXiv](https://img.shields.io/badge/arXiv-2606.30573-b31b1b.svg)](https://arxiv.org/abs/2606.30573)

SWE-Interact is a benchmark of 75 tasks for evaluating coding agents on multi-turn software engineering tasks in a realistic user-driven development setting. The repository contains the task data and example Harbor run configs needed to run the tasks.

## Repository Layout

```text
data/
  multiturn/   
run_configs/
  multiturn/    # example configs for data/multiturn
```

## Requirements

Install Harbor:

```bash
git clone https://github.com/laude-institute/harbor.git
cd harbor
uv tool install .
```

Set up Modal for sandbox environments:

```bash
uv pip install modal
modal setup
```

## Environment Variables

Run configs load credentials from `harbor/.env` relative to this repository root. Create that file before launching a run:

```bash
mkdir -p harbor
$EDITOR harbor/.env
```

### Common User/Rubric Settings

Put this block in `harbor/.env`. It covers the shared simulated-user setup (GPT 5.5 high) and RF rubric grading (the RF task default uses Anthropic Opus 4.5, matching the original SWE Atlas Refactoring task):

```bash
OPENAI_API_KEY=<your-gateway-api-key>
OPENAI_API_BASE=<openai-compatible-gateway-url>/v1
```

`OPENAI_API_BASE` must support both `openai/gpt-5.5` and the RF rubric default model, `anthropic/claude-opus-4-5-20251101`. A LiteLLM gateway works for this; direct `https://api.openai.com/v1` does not support the Anthropic rubric model unless you override `EVAL_MODEL` to an OpenAI model.

### Per-Model Settings

Add only the variables needed for the agent config you run:

| Config | Additional `harbor/.env` setting |
| --- | --- |
| `gpt-5p5-high_codex.sh` | None beyond the common block |
| `opus-4p8-high_claude-code.sh` | `ANTHROPIC_API_KEY=<your-anthropic-api-key>` |
| `sonnet-4p6-high_claude-code.sh` | `ANTHROPIC_API_KEY=<your-anthropic-api-key>` |
| `gemini-3p5-flash-high_opencode.sh` | `GEMINI_API_KEY=<your-gemini-api-key>` |
| `kimi-k2p6_kimi-cli.sh` | `OPENAI_API_KEY=<key-for-openai-compatible-endpoint>` and `OPENAI_API_BASE=<endpoint-url>` or `OPENAI_BASE_URL=<endpoint-url>` |

## Running

Run commands from the repository root.

Multi-turn example:

```bash
bash run_configs/multiturn/gpt-5p5-high_codex.sh
```

Multi-turn run configs set the simulated user model to `openai/gpt-5.5` via `SIM_USER_MODEL`.

To run the baseline single-turn example:

```bash
bash run_configs/singleturn/gpt-5p5-high_codex.sh
```

The scripts write outputs under `results/`. To make a custom config, copy an existing script and update the agent, model, sampling count, or Harbor arguments.

## Citation

If you use SWE-Interact in your research, please cite our paper:

```bibtex
@misc{raghavendra2026sweinteractreimaginingswebenchmarks,
      title={SWE-INTERACT: Reimagining SWE Benchmarks as User-Driven Long-Horizon Coding Sessions}, 
      author={Mohit Raghavendra and Anisha Gunjal and Aakash Sabharwal and Yunzhong He},
      year={2026},
      eprint={2606.30573},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2606.30573}, 
}
```
