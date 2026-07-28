from fastapi import APIRouter

from app.features.product_intelligence.presentation.api.routes import (
    project_router as product_intelligence_project_router,
)
from app.features.product_intelligence.presentation.api.routes import (
    router as product_intelligence_router,
)
from app.features.projects.presentation.api.routes import router as projects_router
from app.features.research_results.presentation.api.routes import (
    router as research_results_router,
)
from app.features.research_sessions.presentation.api.routes import (
    router as research_sessions_router,
)
from app.presentation.api.health import router as health_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(projects_router)
router.include_router(research_sessions_router)
router.include_router(research_results_router)
router.include_router(product_intelligence_project_router)
router.include_router(product_intelligence_router)
