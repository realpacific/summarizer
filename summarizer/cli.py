import argparse
import sys

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from rich.console import Console

from summarizer.config import Provider, build_llm_config, load_config, run_setup

spinner = Console(stderr=True)  # spinners / errors → stderr
console = Console(highlight=False)  # summary / answers → stdout


def _is_url(text: str) -> bool:
    return text.startswith(("http://", "https://"))


def _fetch_url(url: str) -> str:
    import trafilatura

    content = trafilatura.fetch_url(url)
    text = trafilatura.extract(content)
    if not text:
        raise ValueError(f"Could not extract content from {url}")
    return text


PROMPT = """\
Summarize the following content. Write in plain text only — no markdown, no bullet symbols, \
no asterisks, no pound signs, no dashes as list markers.

Structure your response into:

* Title and a concise description of what this content is about and what to expect.
Ignore any author names or publication dates or any metadata. Just give a descriptive title and the essence.
* The important facts, arguments, or takeaways, each as a short paragraph or sentences.
Keep it as short as possible while still conveying the main ideas.
* Conclude with the main insight or outcome from the content.

Constraints:
- No fluff and no repetitions
- Do not label or title any section. Never output words like "Title", "Description", "Conclusion", "Summary",
"Key Takeaways", or any other heading. Output ONLY the raw content of each section, back to back.
- Preserve important data.
- If the language is in a non-English language, respond to in English.
- Maintain an objective, neutral tone, no personal commentary.
- Strictly rely only on the provided text .
- Focus on the core arguments and skip minor digressions or anecdotes.
- Keep sentences concise and easy to read.

Content to summarize:
{content}"""

LLM = init_chat_model(max_tokens=1024, configurable_fields=["model", "base_url"])


def _call_model(content: str, configurable: dict) -> str:
    response = LLM.invoke(
        [HumanMessage(content=PROMPT.format(content=content))],
        config={
            "configurable": configurable
        },
    )
    return response.text


def _chat_loop(content: str, summary: str, configurable: dict) -> None:
    system = (
        "You are a helpful assistant answering questions about the following content. "
        "Answer only based on what is in the content. If the answer is not in the content, say so."
        "If the question is unrelated to the content, say so and do not answer from general knowledge."
        "No markdown or any formatting, just plain text answers with clear paragraphs. Be concise and to the point."
    )
    history = [
        SystemMessage(content=system),
        HumanMessage(content=PROMPT.format(content=content)),
        AIMessage(content=summary),
    ]
    spinner.print("\n[dim]Ask a follow-up question (Ctrl+C or Ctrl+D to quit)[/dim]")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            spinner.print()
            break
        if not question:
            continue
        history.append(HumanMessage(content=question))
        with spinner.status("Thinking…", spinner="dots"):
            response = LLM.invoke(history, config={"configurable": configurable})
        answer = response.text
        history.append(AIMessage(content=answer))
        console.print(answer, style="bold", markup=False)


def main() -> None:
    # Exact `summarizer init` (and nothing else) runs the setup wizard.
    if sys.argv[1:] == ["init"]:
        run_setup()
        return

    cfg = load_config()
    if cfg is None:
        cfg = run_setup()

    provider = Provider.registry[cfg["provider"]]

    parser = argparse.ArgumentParser(description="Summarize text or an article at a URL.")
    parser.add_argument("input", nargs="?", default="-", help="Text, URL, or - to read from stdin")
    parser.add_argument(
        "--model",
        default=None,
        choices=provider.models,
        help="Override the configured model for this run",
    )
    parser.add_argument(
        "--ask",
        action="store_true",
        help="Enable follow-up question mode after summarizing",
    )
    args = parser.parse_args()

    llm_config = build_llm_config(cfg, args.model)

    try:
        if args.input == "-":
            if sys.stdin.isatty():
                sys.exit(1)
            content = sys.stdin.read().strip()
        elif _is_url(args.input):
            with spinner.status("Fetching article…", spinner="dots"):
                content = _fetch_url(args.input)
        else:
            content = args.input

        if not content:
            spinner.print("[red]No content to summarize.[/red]")
            sys.exit(1)

        with spinner.status(f"Summarizing using [bold]{llm_config['model']}[/bold]…", spinner="dots"):
            summary = _call_model(content, llm_config)
        console.print(summary, markup=False)
        if args.ask:
            _chat_loop(content, summary, llm_config)
    except Exception as e:
        spinner.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
