# summarizer

CLI tool that summarizes text or articles at a URL using an LLM. 
Supports Anthropic (Claude), OpenAI (GPT), Google (Gemini) and your Ollama models.

## Install

```bash
uv tool install git+https://github.com/realpacific/summarizer
```

## Setup

Run the interactive setup wizard to choose a provider, model, and enter your API key:

```bash
summarizer init
```

Re-run it anytime to switch providers or models.

## Usage

```bash
# Summarize a URL
summarizer https://example.com/article

# Summarize inline text
summarizer "some text to summarize"

# Summarize from stdin
cat file.txt | summarizer

# Override model for one run
summarizer --model claude-haiku-4-5 https://example.com/article

# Summarize then enter follow-up chat
summarizer --ask https://example.com/article
```

Output is plain text — no markdown or bullet symbols — suitable for piping.
