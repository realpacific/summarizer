import json
import os
import stat
from pathlib import Path
from typing import Any

import questionary
from questionary import Style
from rich.console import Console

from summarizer.providers import Provider

console = Console()

_STYLE = Style(
    [
        ("qmark", "fg:#00b4d8 bold"),
        ("question", "bold"),
        ("answer", "fg:#06d6a0 bold"),
        ("pointer", "fg:#00b4d8 bold"),
        ("highlighted", "fg:#00b4d8 bold"),
        ("instruction", "fg:#666666 italic"),
        ("disabled", "fg:#666666 italic"),
    ]
)

# Readable/writable by the owner only.
OWNER_RW = stat.S_IRUSR | stat.S_IWUSR  # 0o600
OWNER_RWX = stat.S_IRWXU  # 0o700
CONFIG_DIR = Path.home() / ".config" / "summarizer"
CONFIG_PATH = CONFIG_DIR / "config.json"


def _valid(cfg: object) -> bool:
    if not isinstance(cfg, dict):
        return False
    if not {"provider", "model"} <= cfg.keys():
        return False
    provider_name = cfg["provider"]
    if provider_name not in Provider.registry:
        return False
    provider = Provider.registry[provider_name]
    if provider.env_var_name is None or provider.env_var_name == "":
        base_url = cfg.get("base_url")
        return base_url != "" and base_url is not None

    return True


def load_config() -> dict | None:
    """Return the saved config, or None if it is missing or invalid."""
    if not CONFIG_PATH.exists():
        return None
    try:
        cfg = json.loads(CONFIG_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return cfg if _valid(cfg) else None


def _save_config(cfg: dict) -> None:
    """Write the config readable/writable only by the current user."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, OWNER_RWX)
    fd = os.open(CONFIG_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, OWNER_RW)
    with os.fdopen(fd, "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONFIG_PATH, OWNER_RW)


def run_setup() -> dict:
    provider = _choose_provider()
    model = _choose_model(provider)

    api_key = ""
    base_url = ""
    if provider.env_var_name:
        api_key = questionary.password(
            f"Enter your {provider.label} API key:",
            style=_STYLE,
        ).ask()
        if not api_key:
            raise SystemExit(0)
    else:
        base_url = questionary.text(
            "Base URL:",
            default="http://localhost:11434",
            style=_STYLE,
        ).ask()
        if base_url is None:
            raise SystemExit(0)

    cfg = {"provider": provider.name, "model": model, "api_key": api_key, "base_url": base_url}
    _save_config(cfg)
    console.print("\n[bold green]✓[/bold green] Setup complete.")
    return cfg


def _choose_model(provider: Provider) -> Any:
    _OTHER = "__other__"
    choices = provider.models + [questionary.Choice(title="Other (type a name)", value=_OTHER)]
    model = questionary.select(
        "Choose a model:",
        choices=choices,
        style=_STYLE,
    ).ask()
    if model is None:
        raise SystemExit(0)
    if model == _OTHER:
        model = questionary.text("Model name:", style=_STYLE).ask()
        if not model:
            raise SystemExit(0)
    return model


def _choose_provider() -> Provider:
    providers = list(Provider.registry.values())
    provider_name = questionary.select(
        "Choose a provider:",
        choices=[questionary.Choice(title=p.label, value=p.name) for p in providers],
        style=_STYLE,
    ).ask()
    if provider_name is None:
        raise SystemExit(0)

    provider = Provider.registry[provider_name]
    return provider


def build_llm_config(cfg: dict, model_override: str | None = None) -> dict:
    """Set the provider API key env var and return the LangChain configurable dict."""
    provider = Provider.registry[cfg["provider"]]
    if provider.env_var_name:
        os.environ[provider.env_var_name] = cfg["api_key"]
    model_id = provider.model_id(model_override or cfg["model"])
    llm_config = {"model": model_id}
    if base_url := cfg.get("base_url"):
        llm_config["base_url"] = base_url
    return llm_config
