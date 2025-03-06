from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from services.action_plan import ActionPlanService
from src.schemas.action_plan import ActionPlanCreate, ActionPlanUpdate, ActionPlanInDB
from src.schemas.base import BaseResponse, PaginatedResponse

router = APIRouter(prefix="/action-plans", tags=["action-plans"])

# Placeholder untuk Action Plan API endpoints 