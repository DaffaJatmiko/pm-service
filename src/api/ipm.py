from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from services.ipm import IPMService
from src.schemas.ipm import IPMPeriodCreate, IPMIndicatorCreate, IPMTargetCreate, IPMActualCreate
from src.schemas.base import BaseResponse, PaginatedResponse

router = APIRouter(prefix="/ipm", tags=["ipm"])

# Placeholder untuk IPM API endpoints 