import argparse
import sys

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from rich.console import Console

from summarizer.config import Provider, build_llm_config, load_config, run_setup
from summarizer.prompts import DEFAULT_STYLE, Style, build_prompt

spinner = Console(stderr=True)  # spinners / errors → stderr
console = Console(highlight=False)  # summary / answers → stdout


def _is_url(text: str) -> bool:
    return text.startswith(("http://", "https://"))


def _fetch_url(url: str) -> str:
    import trafilatura

    content = trafilatura.fetch_url(url)
    text = trafilatura.extract(
        content,
        output_format="markdown",
        include_links=True,
        include_images=True,
        include_tables=True,
    )
    if not text:
        raise ValueError(f"Could not extract content from {url}")
    return text


LLM = init_chat_model(configurable_fields=["model", "base_url", "max_tokens"])


def _call_model(content: str, configurable: dict, style: str) -> str:
    response = LLM.invoke(
        [HumanMessage(content=build_prompt(content, style))],
        config={
            "configurable": configurable
        },
    )
    return response.text


def _chat_loop(content: str, configurable: dict) -> None:
    # input() does not support arrow keys or backspace, so we use readline for better input handling.
    # https://stackoverflow.com/questions/14796323/input-using-backspace-and-arrow-keys
    import readline  # noqa: F401

    system = (
        "You are a helpful assistant answering questions about the following content. "
        "Answer only based on what is in the content. If the answer is not in the content, say so. "
        "If the question is unrelated to the content, say so and do not answer from general knowledge. "
        "No markdown or any formatting, just plain text answers with clear paragraphs. Be concise and to the point. "
        f"Here is the content:\n{content}"
    )
    history: list[BaseMessage] = [
        SystemMessage(content=system),
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


def _ensure_provider_installed(provider: Provider) -> None:
    import importlib.util
    import subprocess

    from rich.live import Live
    from rich.spinner import Spinner as RichSpinner
    from rich.text import Text

    if importlib.util.find_spec(provider.import_name) is not None:
        return

    msg = Text.assemble(
        "Initiating one-time setup for ",
        (provider.name, "green"),
        "…",
    )
    with Live(RichSpinner("dots", text=msg), console=spinner, transient=True, refresh_per_second=10):
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", provider.package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if result.returncode != 0:
        spinner.print(f"[red]Error:[/red] Failed to install {provider.package_name}")
        sys.exit(1)
    spinner.print(f"[green]✓[/green] Enabled support for {provider.name}")
    sys.exit(0)


def main() -> None:
    # Exact `summarizer init` (and nothing else) runs the setup wizard.
    if sys.argv[1:] == ["init"]:
        run_setup()
        cfg = load_config()
        if cfg is None:
            return
        provider = Provider.registry[cfg["provider"]]
        _ensure_provider_installed(provider)
        return

    cfg = load_config()
    if cfg is None:
        cfg = run_setup()

    provider = Provider.registry[cfg["provider"]]
    _ensure_provider_installed(provider)

    parser = argparse.ArgumentParser(description="Summarize text or an article at a URL.")
    parser.add_argument("input", nargs="?", default="-", help="Text, URL, or - to read from stdin")
    parser.add_argument(
        "--model",
        default=None,
        choices=provider.models,
        help="Override the configured model for this run",
    )
    styles = "; ".join(f"{s.name} — {s.description}" for s in Style.registry.values())
    parser.add_argument(
        "--style",
        default=None,
        choices=list(Style.registry),
        help=f"How to shape the summary (default: {DEFAULT_STYLE}); not valid with --ask. "
        # argparse %-formats help text, so a literal % in a style description must be escaped.
        + styles.replace("%", "%%"),
    )
    parser.add_argument(
        "--ask",
        action="store_true",
        help="Enable follow-up question mode after summarizing",
    )
    args = parser.parse_args()

    # --ask never summarizes, so a style would be silently ignored.
    if args.ask and args.style is not None:
        parser.error("--style cannot be used with --ask")
    style = args.style or DEFAULT_STYLE

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
        if args.ask:
            _chat_loop(content, llm_config)
        else:
            summary = ""
            with spinner.status(f"Summarizing using [bold]{llm_config['model']}[/bold]…", spinner="dots"):
                summary = _call_model(content, llm_config, style)
            console.print(summary, markup=False)

    except Exception as e:
        spinner.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
