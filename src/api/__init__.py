"""API v1 router module for Performance Management System."""

from fastapi import APIRouter

from src.api.period import router as period_router
from src.api.user import router as user_router
from src.api.organization import router as organization_router
from src.api.mpm import router as mpm_router
from src.api.bsc import router as bsc_router

# Create main v1 router
api_router = APIRouter()

# Include individual routers
api_router.include_router(period_router)
api_router.include_router(user_router)
api_router.include_router(organization_router)
api_router.include_router(bsc_router)
api_router.include_router(mpm_router)



# Add other routers as they are implemented
# api_router.include_router(bsc_router)
# api_router.include_router(ipm_router)