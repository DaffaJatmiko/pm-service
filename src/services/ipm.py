from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.ipm import IPMRepository
from src.models.ipm import IPMPeriod, IPMIndicator, IPMTarget, IPMActual, IPMEvidence

# Placeholder untuk IPM Service 