from enum import StrEnum


class AIProviderName(StrEnum):
    """Identifies which AIProvider implementation to use.

    New providers (Google Gemini, local models, ...) are added here plus a
    new provider class plus one registry entry - no existing code changes.
    """

    MOCK = "mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
