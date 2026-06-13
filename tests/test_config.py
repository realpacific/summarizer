import json
import os
import stat

import pytest

from summarizer import config


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Point config storage at a temp dir for the duration of a test."""
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path / "summarizer")
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "summarizer" / "config.json")
    return config.CONFIG_PATH


def test_providers_self_register():
    assert set(config.Provider.registry) == {"anthropic", "gemini", "openai", "ollama"}
    for provider in config.Provider.registry.values():
        assert provider.label and provider.models


def test_model_id_per_provider():
    assert config.Provider.registry["anthropic"].model_id("claude-sonnet-4-6") == "anthropic:claude-sonnet-4-6"
    assert config.Provider.registry["gemini"].model_id("gemini-2.0-flash") == "google_genai:gemini-2.0-flash"


def test_save_load_round_trip(tmp_config):
    cfg = {"provider": "anthropic", "model": "claude-sonnet-4-6", "api_key": "secret"}
    config._save_config(cfg)
    assert config.load_config() == cfg


def test_saved_file_is_user_only(tmp_config):
    config._save_config({"provider": "gemini", "model": "gemini-2.0-flash", "api_key": "k"})
    assert stat.S_IMODE(os.stat(config.CONFIG_PATH).st_mode) == stat.S_IRUSR | stat.S_IWUSR
    assert stat.S_IMODE(os.stat(config.CONFIG_DIR).st_mode) == stat.S_IRWXU


def test_load_returns_none_when_missing(tmp_config):
    assert config.load_config() is None


def test_load_rejects_invalid_json(tmp_config):
    tmp_config.parent.mkdir(parents=True)
    tmp_config.write_text("not json")
    assert config.load_config() is None


def test_load_rejects_unknown_provider(tmp_config):
    tmp_config.parent.mkdir(parents=True)
    tmp_config.write_text(json.dumps({"provider": "nope", "model": "x", "api_key": "y"}))
    assert config.load_config() is None


def test_load_rejects_missing_fields(tmp_config):
    tmp_config.parent.mkdir(parents=True)
    tmp_config.write_text(json.dumps({"provider": "anthropic"}))
    assert config.load_config() is None


@pytest.mark.parametrize(
    "cfg",
    [
        {},
        {"provider": "anthropic"},
        {"model": "claude-opus-4-8"},
    ],
)
def test_valid_rejects_missing_keys(cfg):
    assert config._valid(cfg) is False


def test_valid_rejects_unknown_provider():
    assert config._valid({"provider": "nope", "model": "x"}) is False


def test_valid_accepts_api_key_provider():
    assert config._valid({"provider": "anthropic", "model": "claude-opus-4-8"}) is True


def test_valid_api_key_provider_ignores_base_url():
    # A cloud provider is valid even with an empty base_url; it is not used.
    assert config._valid({"provider": "openai", "model": "gpt-5.5", "base_url": ""}) is True


def test_valid_accepts_keyless_provider_with_base_url():
    cfg = {"provider": "ollama", "model": "llama3.2", "base_url": "http://localhost:11434"}
    assert config._valid(cfg) is True


@pytest.mark.parametrize(
    "base_url",
    [
        None,
        ""
    ],
)
def test_valid_rejects_keyless_provider_with_empty_base_url(base_url):
    cfg = {"provider": "ollama", "model": "llama3.2", "base_url": base_url}
    assert config._valid(cfg) is False
