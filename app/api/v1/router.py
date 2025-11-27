"""API v1 router - combines all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.mask import router as mask_router
from app.api.v1.redact import router as redact_router
from app.api.v1.detect import router as detect_router


router = APIRouter(tags=["PII Processing"])

# Include all endpoint routers
router.include_router(mask_router)
router.include_router(redact_router)
router.include_router(detect_router)

