from app.features.product_intelligence.infrastructure.ai.generate_description_capability import (
    GENERATE_PRODUCT_DESCRIPTION,
    GenerateProductDescriptionCapability,
)
from app.shared.ai.domain.entities.ai_completion import AICompletionResponse
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName


def test_name_matches_the_shared_capability_constant():
    capability = GenerateProductDescriptionCapability()

    assert capability.name == GENERATE_PRODUCT_DESCRIPTION


def test_build_request_includes_title_subtitle_and_category():
    capability = GenerateProductDescriptionCapability()

    request = capability.build_request(
        {"title": "Bamboo Board", "subtitle": "Sustainable", "category": "Kitchen"}
    )

    assert "Bamboo Board" in request.prompt
    assert "Sustainable" in request.prompt
    assert "Kitchen" in request.prompt


def test_build_request_tolerates_missing_optional_fields():
    capability = GenerateProductDescriptionCapability()

    request = capability.build_request({"title": "Bamboo Board"})

    assert "Bamboo Board" in request.prompt


def test_parse_response_returns_the_content_as_description():
    capability = GenerateProductDescriptionCapability()
    response = AICompletionResponse(content="A lovely bamboo board.", provider=AIProviderName.MOCK)

    output = capability.parse_response(response)

    assert output == {"description": "A lovely bamboo board."}
