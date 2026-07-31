from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.features.product_intelligence.application.dtos import (
    CreateProductIntelligenceRequestDTO,
    DeleteProductIntelligenceRequestDTO,
    GenerateProductDescriptionRequestDTO,
    GetProductIntelligenceRequestDTO,
    ListProductIntelligenceRequestDTO,
    MarkReadyForPublishingRequestDTO,
    ProductIntelligenceDTO,
    UpdateProductIntelligenceRequestDTO,
)
from app.features.product_intelligence.application.use_cases.create_product_intelligence import (
    CreateProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.delete_product_intelligence import (
    DeleteProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.generate_product_description import (
    GenerateProductDescriptionUseCase,
)
from app.features.product_intelligence.application.use_cases.get_product_intelligence import (
    GetProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.list_product_intelligence import (
    ListProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.mark_ready_for_publishing import (
    MarkReadyForPublishingUseCase,
)
from app.features.product_intelligence.application.use_cases.update_product_intelligence import (
    UpdateProductIntelligenceUseCase,
)
from app.features.product_intelligence.domain.entities.product_intelligence import (
    ImageAsset,
    Pricing,
    ProductIntelligenceStatus,
    PublishingMetadata,
    SeoMetadata,
    Specification,
)
from app.features.product_intelligence.domain.exceptions import (
    AIGenerationFailedError,
    InvalidProductIntelligenceError,
    ProductIntelligenceNotFoundError,
    ProductNotReadyForPublishingError,
)
from app.features.product_intelligence.presentation.api.dependencies import (
    get_create_product_intelligence_use_case,
    get_delete_product_intelligence_use_case,
    get_generate_product_description_use_case,
    get_get_product_intelligence_use_case,
    get_list_product_intelligence_use_case,
    get_mark_ready_for_publishing_use_case,
    get_update_product_intelligence_use_case,
)
from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError

project_router = APIRouter(
    prefix="/projects/{project_id}/product-intelligence",
    tags=["product-intelligence"],
    dependencies=[Depends(verify_api_key)],
)
router = APIRouter(
    prefix="/product-intelligence",
    tags=["product-intelligence"],
    dependencies=[Depends(verify_api_key)],
)


class SpecificationModel(BaseModel):
    name: str
    value: str


class SeoMetadataModel(BaseModel):
    meta_title: str | None = None
    meta_description: str | None = None
    slug: str | None = None


class PricingModel(BaseModel):
    amount: Decimal
    currency: str
    compare_at_amount: Decimal | None = None


class ImageAssetModel(BaseModel):
    url: str
    alt_text: str | None = None


class PublishingMetadataModel(BaseModel):
    published_channels: list[str] = []
    published_at: datetime | None = None


class ProductIntelligenceFields(BaseModel):
    title: str
    subtitle: str | None = None
    description: str | None = None
    features: list[str] = []
    specifications: list[SpecificationModel] = []
    category: str | None = None
    tags: list[str] = []
    keywords: list[str] = []
    seo: SeoMetadataModel = SeoMetadataModel()
    pricing: PricingModel | None = None
    images: list[ImageAssetModel] = []
    publishing: PublishingMetadataModel = PublishingMetadataModel()


class CreateProductIntelligenceRequest(ProductIntelligenceFields):
    research_session_id: UUID | None = None


class UpdateProductIntelligenceRequest(ProductIntelligenceFields):
    pass


class GeneratedDescriptionResponse(BaseModel):
    """Deliberately not ProductIntelligenceResponse: generation never
    saves anything, so returning the full product would wrongly imply it
    did. The caller accepts a draft via the existing update endpoint."""

    product_id: UUID
    description: str


class ProductIntelligenceResponse(BaseModel):
    id: UUID
    project_id: UUID
    research_session_id: UUID | None
    title: str
    subtitle: str | None
    description: str | None
    features: list[str]
    specifications: list[SpecificationModel]
    category: str | None
    tags: list[str]
    keywords: list[str]
    seo: SeoMetadataModel
    pricing: PricingModel | None
    images: list[ImageAssetModel]
    publishing: PublishingMetadataModel
    status: ProductIntelligenceStatus
    created_at: datetime
    updated_at: datetime


def _specs_from_request(models: list[SpecificationModel]) -> tuple[Specification, ...]:
    return tuple(Specification(name=model.name, value=model.value) for model in models)


def _seo_from_request(model: SeoMetadataModel) -> SeoMetadata:
    return SeoMetadata(
        meta_title=model.meta_title, meta_description=model.meta_description, slug=model.slug
    )


def _pricing_from_request(model: PricingModel | None) -> Pricing | None:
    if model is None:
        return None
    return Pricing(
        amount=model.amount, currency=model.currency, compare_at_amount=model.compare_at_amount
    )


def _images_from_request(models: list[ImageAssetModel]) -> tuple[ImageAsset, ...]:
    return tuple(ImageAsset(url=model.url, alt_text=model.alt_text) for model in models)


def _publishing_from_request(model: PublishingMetadataModel) -> PublishingMetadata:
    return PublishingMetadata(
        published_channels=tuple(model.published_channels), published_at=model.published_at
    )


def _to_response(dto: ProductIntelligenceDTO) -> ProductIntelligenceResponse:
    return ProductIntelligenceResponse(
        id=dto.id,
        project_id=dto.project_id,
        research_session_id=dto.research_session_id,
        title=dto.title,
        subtitle=dto.subtitle,
        description=dto.description,
        features=list(dto.features),
        specifications=[
            SpecificationModel(name=spec.name, value=spec.value) for spec in dto.specifications
        ],
        category=dto.category,
        tags=list(dto.tags),
        keywords=list(dto.keywords),
        seo=SeoMetadataModel(
            meta_title=dto.seo.meta_title,
            meta_description=dto.seo.meta_description,
            slug=dto.seo.slug,
        ),
        pricing=PricingModel(
            amount=dto.pricing.amount,
            currency=dto.pricing.currency,
            compare_at_amount=dto.pricing.compare_at_amount,
        )
        if dto.pricing
        else None,
        images=[ImageAssetModel(url=image.url, alt_text=image.alt_text) for image in dto.images],
        publishing=PublishingMetadataModel(
            published_channels=list(dto.publishing.published_channels),
            published_at=dto.publishing.published_at,
        ),
        status=dto.status,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@project_router.post("", response_model=ProductIntelligenceResponse, status_code=201)
async def create_product_intelligence(
    project_id: UUID,
    payload: CreateProductIntelligenceRequest,
    use_case: CreateProductIntelligenceUseCase = Depends(  # noqa: B008
        get_create_product_intelligence_use_case
    ),
) -> ProductIntelligenceResponse:
    try:
        result = await use_case.execute(
            CreateProductIntelligenceRequestDTO(
                project_id=project_id,
                research_session_id=payload.research_session_id,
                title=payload.title,
                subtitle=payload.subtitle,
                description=payload.description,
                features=tuple(payload.features),
                specifications=_specs_from_request(payload.specifications),
                category=payload.category,
                tags=tuple(payload.tags),
                keywords=tuple(payload.keywords),
                seo=_seo_from_request(payload.seo),
                pricing=_pricing_from_request(payload.pricing),
                images=_images_from_request(payload.images),
                publishing=_publishing_from_request(payload.publishing),
            )
        )
    except (ProjectNotFoundError, ResearchSessionNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidProductIntelligenceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _to_response(result)


@project_router.get("", response_model=list[ProductIntelligenceResponse], status_code=200)
async def list_product_intelligence(
    project_id: UUID,
    use_case: ListProductIntelligenceUseCase = Depends(  # noqa: B008
        get_list_product_intelligence_use_case
    ),
) -> list[ProductIntelligenceResponse]:
    try:
        results = await use_case.execute(ListProductIntelligenceRequestDTO(project_id=project_id))
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [_to_response(result) for result in results]


@router.get("/{product_id}", response_model=ProductIntelligenceResponse, status_code=200)
async def get_product_intelligence(
    product_id: UUID,
    use_case: GetProductIntelligenceUseCase = Depends(  # noqa: B008
        get_get_product_intelligence_use_case
    ),
) -> ProductIntelligenceResponse:
    try:
        result = await use_case.execute(GetProductIntelligenceRequestDTO(product_id=product_id))
    except ProductIntelligenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return _to_response(result)


@router.put("/{product_id}", response_model=ProductIntelligenceResponse, status_code=200)
async def update_product_intelligence(
    product_id: UUID,
    payload: UpdateProductIntelligenceRequest,
    use_case: UpdateProductIntelligenceUseCase = Depends(  # noqa: B008
        get_update_product_intelligence_use_case
    ),
) -> ProductIntelligenceResponse:
    try:
        result = await use_case.execute(
            UpdateProductIntelligenceRequestDTO(
                product_id=product_id,
                title=payload.title,
                subtitle=payload.subtitle,
                description=payload.description,
                features=tuple(payload.features),
                specifications=_specs_from_request(payload.specifications),
                category=payload.category,
                tags=tuple(payload.tags),
                keywords=tuple(payload.keywords),
                seo=_seo_from_request(payload.seo),
                pricing=_pricing_from_request(payload.pricing),
                images=_images_from_request(payload.images),
                publishing=_publishing_from_request(payload.publishing),
            )
        )
    except ProductIntelligenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidProductIntelligenceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _to_response(result)


@router.delete("/{product_id}", status_code=204)
async def delete_product_intelligence(
    product_id: UUID,
    use_case: DeleteProductIntelligenceUseCase = Depends(  # noqa: B008
        get_delete_product_intelligence_use_case
    ),
) -> None:
    try:
        await use_case.execute(DeleteProductIntelligenceRequestDTO(product_id=product_id))
    except ProductIntelligenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{product_id}/mark-ready-for-publishing",
    response_model=ProductIntelligenceResponse,
    status_code=200,
)
async def mark_ready_for_publishing(
    product_id: UUID,
    use_case: MarkReadyForPublishingUseCase = Depends(  # noqa: B008
        get_mark_ready_for_publishing_use_case
    ),
) -> ProductIntelligenceResponse:
    try:
        result = await use_case.execute(MarkReadyForPublishingRequestDTO(product_id=product_id))
    except ProductIntelligenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProductNotReadyForPublishingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _to_response(result)


@router.post(
    "/{product_id}/generate-description",
    response_model=GeneratedDescriptionResponse,
    status_code=200,
)
async def generate_product_description(
    product_id: UUID,
    use_case: GenerateProductDescriptionUseCase = Depends(  # noqa: B008
        get_generate_product_description_use_case
    ),
) -> GeneratedDescriptionResponse:
    """Generates a draft only - nothing is saved. The frontend shows the
    draft alongside the current description and calls the existing update
    endpoint if the user explicitly accepts it."""
    try:
        result = await use_case.execute(
            GenerateProductDescriptionRequestDTO(product_id=product_id)
        )
    except ProductIntelligenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AIGenerationFailedError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GeneratedDescriptionResponse(
        product_id=result.product_id, description=result.description
    )
