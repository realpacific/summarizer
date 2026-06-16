This file provides guidance to LLM model when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run directly via uv (equivalent to summarizer)
uv run summarizer <input>

# Lint
ruff check
ruff format
```

## Run tests

Tests live in `tests/`. Run with:

```bash
uv run pytest
```

## Design

Config lives at `~/.config/summarizer/config.json` (dir `0700`, file `0600`) and is the sole source of credentials.
For initial one-time setup, `run_setup()` drives the `questionary` arrow-key menus.

LLM Providers are modeled as a `Provider` abstract base class; each concrete provider (like Anthropic, Gemini and so on)
is a subclass that self-registers into `Provider.registry` via `__init_subclass__`.

To add a provider, define `Provider` subclass in `providers.py`. The `package_name` MUST correspond to a langchain package.
For e.g. langchain-anthropic for Anthropic. It will be installed dynamically when needed via `_ensure_provider_installed`

`cli.py`** — runtime logic: argument parsing, URL content extraction (trafilatura), the summarization prompt, model
invocation via LangChain.
The exact invocation `summarizer init` (no other args) runs the setup wizard.
