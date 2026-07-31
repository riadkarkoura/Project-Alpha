from collections.abc import Mapping

from app.shared.ai.domain.capabilities.ai_capability import AICapability
from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.capability_name import CapabilityName

GENERATE_PRODUCT_DESCRIPTION = CapabilityName("generate_product_description")
"""The one place this capability's identifier is spelled out - every other
reference (the capability's own `.name`, the use case that builds the
AIJob, the DI registration) imports this constant rather than repeating
the literal string."""


class GenerateProductDescriptionCapability(AICapability):
    """Generates a draft product description from a product's existing
    title/subtitle/category.

    Deliberately narrow: this capability produces a description only - not
    a title, SEO copy, keywords, or bullet points. Those are separate
    capabilities to add later, each following this same shape, once this
    one is validated with real usage.

    Lives in product_intelligence/, not shared/ai/: this is product-content
    logic (it knows what title/subtitle/category mean), not a platform-wide
    execution concern. shared/ai stays unaware this capability exists.
    """

    @property
    def name(self) -> CapabilityName:
        return GENERATE_PRODUCT_DESCRIPTION

    def build_request(self, input_data: Mapping[str, str]) -> AICompletionRequest:
        title = input_data.get("title", "")
        subtitle = input_data.get("subtitle", "")
        category = input_data.get("category", "")

        prompt = f"Write a product description for '{title}'"
        if subtitle:
            prompt += f" ({subtitle})"
        if category:
            prompt += f" in the '{category}' category"
        prompt += "."

        return AICompletionRequest(prompt=prompt)

    def parse_response(self, response: AICompletionResponse) -> Mapping[str, str]:
        return {"description": response.content}
