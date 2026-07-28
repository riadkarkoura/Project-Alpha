from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.features.product_intelligence.domain.entities.product_intelligence import (
    Pricing,
    ProductIntelligence,
    ProductIntelligenceStatus,
    PublishingMetadata,
    SeoMetadata,
)
from app.features.product_intelligence.domain.exceptions import ProductNotReadyForPublishingError


def _draft_product(**overrides: object) -> ProductIntelligence:
    now = datetime.now(UTC)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "project_id": uuid4(),
        "research_session_id": None,
        "title": "Bamboo Cutting Board",
        "subtitle": None,
        "description": "A durable, sustainable kitchen essential.",
        "features": (),
        "specifications": (),
        "category": None,
        "tags": (),
        "keywords": (),
        "seo": SeoMetadata(),
        "pricing": Pricing(amount=Decimal("19.99"), currency="USD"),
        "images": (),
        "publishing": PublishingMetadata(),
        "status": ProductIntelligenceStatus.DRAFT,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return ProductIntelligence(**defaults)  # type: ignore[arg-type]


class TestPricing:
    def test_rejects_negative_amount(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            Pricing(amount=Decimal("-1"), currency="USD")

    def test_rejects_non_three_letter_currency(self):
        with pytest.raises(ValueError, match="3-letter code"):
            Pricing(amount=Decimal("10"), currency="US")

    def test_rejects_negative_compare_at_amount(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            Pricing(amount=Decimal("10"), currency="USD", compare_at_amount=Decimal("-1"))

    def test_accepts_valid_pricing(self):
        pricing = Pricing(amount=Decimal("10"), currency="USD", compare_at_amount=Decimal("15"))
        assert pricing.amount == Decimal("10")


class TestMarkReadyForPublishing:
    def test_marks_a_complete_draft_ready(self):
        product = _draft_product()

        ready = product.mark_ready_for_publishing()

        assert ready.status == ProductIntelligenceStatus.READY_FOR_PUBLISHING
        assert ready.id == product.id
        assert product.status == ProductIntelligenceStatus.DRAFT  # original is unchanged

    def test_rejects_when_title_is_blank(self):
        product = _draft_product(title="   ")

        with pytest.raises(ProductNotReadyForPublishingError, match="title"):
            product.mark_ready_for_publishing()

    def test_rejects_when_description_is_missing(self):
        product = _draft_product(description=None)

        with pytest.raises(ProductNotReadyForPublishingError, match="description"):
            product.mark_ready_for_publishing()

    def test_rejects_when_pricing_is_missing(self):
        product = _draft_product(pricing=None)

        with pytest.raises(ProductNotReadyForPublishingError, match="pricing"):
            product.mark_ready_for_publishing()

    def test_reports_all_missing_fields_at_once(self):
        product = _draft_product(title="", description=None, pricing=None)

        with pytest.raises(ProductNotReadyForPublishingError) as exc_info:
            product.mark_ready_for_publishing()

        assert "title" in str(exc_info.value)
        assert "description" in str(exc_info.value)
        assert "pricing" in str(exc_info.value)
