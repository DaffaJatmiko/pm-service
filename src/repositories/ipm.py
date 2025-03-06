from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.ipm import IPMPeriod, IPMIndicator, IPMTarget, IPMActual, IPMEvidence
from .base import BaseRepository

# Placeholder untuk IPM Repository 