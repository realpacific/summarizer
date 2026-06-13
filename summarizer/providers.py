from abc import ABC


class Provider(ABC):
    """A model provider. Subclass and set the class attributes to register a
    new provider — no other code needs to change."""

    registry: dict[str, "Provider"] = {}
    name: str = ""
    label: str = ""
    env_var_name: str = ""
    models: list[str] = []
    package_name: str = ""
    import_name: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Provider.registry[cls.name] = cls()

    def model_id(self, model: str) -> str:
        return f"{self.name}:{model}"


class Anthropic(Provider):
    name = "anthropic"
    label = "Anthropic (Claude)"
    env_var_name = "ANTHROPIC_API_KEY"
    models = ["claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5"]
    package_name = "langchain-anthropic"
    import_name = "langchain_anthropic"

    def model_id(self, model: str) -> str:
        return f"anthropic:{model}"


class OpenAI(Provider):
    name = "openai"
    label = "OpenAI (GPT)"
    env_var_name = "OPENAI_API_KEY"
    models = ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini"]
    package_name = "langchain-openai"
    import_name = "langchain_openai"

    def model_id(self, model: str) -> str:
        return f"openai:{model}"


class Gemini(Provider):
    name = "gemini"
    label = "Google (Gemini)"
    env_var_name = "GOOGLE_API_KEY"
    models = ["gemini-3.1-flash-lite", "gemini-3.1-pro", "gemini-3.5-flash"]
    package_name = "langchain-google-genai"
    import_name = "langchain_google_genai"

    def model_id(self, model: str) -> str:
        return f"google_genai:{model}"


class Ollama(Provider):
    name = "ollama"
    label = "Ollama (local)"
    env_var_name = ""
    models = ["llama3.2", "llama3.1", "mistral", "gemma3", "qwen2.5"]
    package_name = "langchain-ollama"
    import_name = "langchain_ollama"

    def model_id(self, model: str) -> str:
        return f"ollama:{model}"
