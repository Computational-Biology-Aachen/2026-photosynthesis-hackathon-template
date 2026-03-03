# 2026 JII Hackathon Template

Clone this repo and await further instructions 😃

## Setup

Install uv according to the [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

For most people that should amount to

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

on linux and

```PS
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

on windows.

Then simply run

```bash
uv sync

# If you want to run jupyter, otherwise select the kernel in vscode
uv run jupyter lab  # or
uv run jupyter notebook
```
