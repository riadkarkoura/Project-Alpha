from collections.abc import Mapping

import pytest

from app.shared.ai.application.capability_registry import AICapabilityRegistry
from app.shared.ai.domain.capabilities.ai_capability import AICapability
from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.exceptions import CapabilityNotFoundError


class _FakeCapability(AICapability):
    def __init__(self, capability_name: str) -> None:
        self._name = capability_name

    @property
    def name(self) -> str:
        return self._name

    def build_request(self, input_data: Mapping[str, str]) -> AICompletionRequest:
        return AICompletionRequest(prompt="fake prompt")

    def parse_response(self, response: AICompletionResponse) -> Mapping[str, str]:
        return {"content": response.content}


def test_get_resolves_a_registered_capability():
    capability = _FakeCapability("generate_title")
    registry = AICapabilityRegistry({"generate_title": capability})

    assert registry.get("generate_title") is capability


def test_get_raises_for_an_unregistered_capability():
    registry = AICapabilityRegistry()

    with pytest.raises(CapabilityNotFoundError):
        registry.get("generate_title")


def test_registry_starts_empty_by_default():
    registry = AICapabilityRegistry()

    assert registry.list_names() == []


def test_register_adds_a_new_capability_without_touching_existing_ones():
    title_capability = _FakeCapability("generate_title")
    registry = AICapabilityRegistry({"generate_title": title_capability})
    seo_capability = _FakeCapability("generate_seo")

    registry.register(seo_capability)

    assert registry.get("generate_seo") is seo_capability
    assert registry.get("generate_title") is title_capability


def test_list_names_reports_every_registered_capability():
    registry = AICapabilityRegistry()
    registry.register(_FakeCapability("generate_title"))
    registry.register(_FakeCapability("generate_seo"))

    assert registry.list_names() == ["generate_seo", "generate_title"]
