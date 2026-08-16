# summarizer

![](https://img.shields.io/github/v/tag/realpacific/summarizer?style=for-the-badge&logo=github&color=7c3aed)

CLI tool that summarizes text or articles at a URL using LLM.
Supports Anthropic (Claude), OpenAI (GPT), Google (Gemini), and local Ollama models.

## Install

```bash
uv tool install git+https://github.com/realpacific/summarizer
```

## Setup

Run the interactive wizard to choose a provider, model, and API key:

```bash
summarizer init

#? Choose a provider: Anthropic (Claude)
#? Choose a model: claude-haiku-4-5
#? Enter your Anthropic (Claude) API key: ****************
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

# Choose how the summary is shaped
summarizer https://prashantbarahi.com.np/blog/your-readme-md-is-obsolete --style=brief

# Enter a follow-up chat with the content
summarizer https://prashantbarahi.com.np/blog/your-readme-md-is-obsolete --ask

# For dynamic pages or paywalled content, copy to clipboard and pipe:
pbpaste | summarizer
```

## Summary Styles

`--style` controls how the summary is shaped. All styles output plain text with no markdown,
so they stay readable in a terminal and pipe cleanly into other tools.

| Style        | Output                                                                                |
|--------------|---------------------------------------------------------------------------------------|
| `default`    | Title, key facts, then the main insight. Used when `--style` is omitted.              |
| `brief`      | One paragraph, three sentences at most — what it is and the single biggest takeaway.  |
| `detailed`   | Every substantive argument as its own paragraph, plus any caveats the content raises. |
| `key-points` | A numbered list of five to ten takeaways.                                             |

```bash
summarizer https://example.com/long-article --style=brief

summarizer https://example.com/long-article --style=key-points
```

## Ask Mode

`--ask` enters a follow-up chat with the content.

```bash
summarizer https://prashantbarahi.com.np/blog/your-readme-md-is-obsolete --ask

# Ask a follow-up question (Ctrl+C or Ctrl+D to quit)
# > what is the key takeaway of this
# The key takeaway is that files written for AI agents like AGENTS.md, GEMINI.md, or CLAUDE.md have become 
# better sources of project documentation than the traditional README.md. This is because developers are forced to 
# be more detailed, precise, and thorough when writing instructions for machines in order to get the best results 
# from AI agents. Other machine-readable files like package management files and CI/CD pipeline configs 
# also serve as reliable, up-to-date sources of project understanding. 
```

## Summarizer + TTS

Pair it with [realpacific/readthis](https://github.com/realpacific/readthis) to turn any summary into on-demand audio.

Install `realpacific/readthis`:

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
