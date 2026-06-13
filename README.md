# summarizer

CLI tool that summarizes text or articles at a URL using an LLM.
Supports Anthropic (Claude), OpenAI (GPT), Google (Gemini), and local Ollama models.

Pair it with [realpacific/readthis](https://github.com/realpacific/readthis) to turn any summary into on-demand audio.

## Install

```bash
uv tool install git+https://github.com/realpacific/summarizer
```

## Setup

Run the interactive wizard to choose a provider, model, and API key:

```bash
summarizer init
```

Re-run it anytime to switch providers or models.

## Usage

```bash
# Summarize a URL
summarizer https://prashantbarahi.com.np/blog/your-readme-md-is-obsolete

# Summarize inline text
summarizer "some text to summarize"

# Summarize from stdin
cat file.txt | summarizer

# Override the model for one run
summarizer --model claude-haiku-4-5 https://prashantbarahi.com.np/blog/your-readme-md-is-obsolete

# Summarize then enter a follow-up chat
summarizer --ask https://prashantbarahi.com.np/blog/your-readme-md-is-obsolete

# For dynamic pages or paywalled content, copy to clipboard and pipe:
pbpaste | summarizer
```

## Summarizer + TTS

Install [realpacific/readthis](https://github.com/realpacific/readthis):

```bash
uv tool install --python 3.12 git+https://github.com/realpacific/readthis
```

Pipe any summary directly to it:

```bash
# Summarize a URL and read it aloud
summarizer https://prashantbarahi.com.np/blog/your-readme-md-is-obsolete | readthis

# For dynamic pages or paywalled content, copy to clipboard and pipe:
pbpaste | summarizer | readthis
```
