"""Period API endpoints for Performance Management System."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.models.period import Period
from src.schemas.base import DataResponse, PaginatedResponse
from src.schemas.period import (
    PeriodCreate, 
    PeriodUpdate, 
    PeriodResponse, 
    PeriodStatusUpdate,
    PeriodQueryParams
)
from src.services.period import PeriodService
from src.auth.dependencies import get_current_user, get_current_active_user

router = APIRouter(prefix="/periods", tags=["periods"])


@router.post(
    "/", 
    response_model=DataResponse[PeriodResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new period",
    description="Create a new period with the given details. Only users with admin or manager roles can create periods."
)
async def create_period(
    period_in: PeriodCreate,
    current_user: dict = Depends(get_current_active_user),
    period_service: PeriodService = Depends()
):
    """Create a new period."""
    # Check if user has permission to create periods
    if "admin" not in current_user["roles"] and "manager" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create periods"
        )
    
    try:
        period = await period_service.create_period(
            period_in=period_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=period, message="Period created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the period: {str(e)}"
        )


@router.get(
    "/", 
    response_model=PaginatedResponse[PeriodResponse],
    summary="Get all periods",
    description="Get a list of all periods with optional filtering and pagination."
)
async def get_periods(
    query_params: PeriodQueryParams = Depends(),
    current_user: dict = Depends(get_current_user),
    period_service: PeriodService = Depends()
):
    """Get all periods with optional filtering."""
    try:
        result = await period_service.search_periods(
            type=query_params.type,
            year=query_params.year,
            status=query_params.status,
            page=query_params.page,
            page_size=query_params.page_size
        )
        
        return PaginatedResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            message="Periods retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving periods: {str(e)}"
        )


@router.get(
    "/active", 
    response_model=DataResponse[PeriodResponse],
    summary="Get the active period",
    description="Get the currently active period, if any."
)
async def get_active_period(
    current_user: dict = Depends(get_current_user),
    period_service: PeriodService = Depends()
):
    """Get the currently active period."""
    try:
        period = await period_service.get_active_period()
        if not period:
            return DataResponse(
                data=None,
                message="No active period found",
                success=False
            )
        
        return DataResponse(data=period, message="Active period retrieved successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the active period: {str(e)}"
        )


@router.get(
    "/{period_id}", 
    response_model=DataResponse[PeriodResponse],
    summary="Get a period by ID",
    description="Get details of a specific period by its ID."
)
async def get_period(
    period_id: UUID,
    current_user: dict = Depends(get_current_user),
    period_service: PeriodService = Depends()
):
    """Get a period by ID."""
    try:
        period = await period_service.get_or_404(id=period_id)
        return DataResponse(data=period, message="Period retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the period: {str(e)}"
        )


@router.patch(
    "/{period_id}", 
    response_model=DataResponse[PeriodResponse],
    summary="Update a period",
    description="Update details of a specific period by its ID. Only users with admin or manager roles can update periods."
)
async def update_period(
    period_id: UUID,
    period_in: PeriodUpdate,
    current_user: dict = Depends(get_current_active_user),
    period_service: PeriodService = Depends()
):
    """Update a period."""
    # Check if user has permission to update periods
    if "admin" not in current_user["roles"] and "manager" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update periods"
        )
    
    try:
        period = await period_service.update(
            id=period_id, 
            obj_in=period_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=period, message="Period updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the period: {str(e)}"
        )


@router.patch(
    "/{period_id}/status", 
    response_model=DataResponse[PeriodResponse],
    summary="Update period status",
    description="Update the status of a specific period. Only users with admin or manager roles can update period status."
)
async def update_period_status(
    period_id: UUID,
    status_update: PeriodStatusUpdate,
    current_user: dict = Depends(get_current_active_user),
    period_service: PeriodService = Depends()
):
    """Update period status."""
    # Check if user has permission to update period status
    if "admin" not in current_user["roles"] and "manager" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update period status"
        )
    
    try:
        period = await period_service.update_period_status(
            id=period_id, 
            status_update=status_update,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=period, message=f"Period status updated to {status_update.status} successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the period status: {str(e)}"
        )


@router.delete(
    "/{period_id}", 
    response_model=DataResponse[PeriodResponse],
    summary="Delete a period",
    description="Delete a period by its ID. This is a soft delete. Only users with admin roles can delete periods."
)
async def delete_period(
    period_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    period_service: PeriodService = Depends()
):
    """Delete a period (soft delete)."""
    # Check if user has permission to delete periods
    if "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete periods"
        )
    
    try:
        period = await period_service.delete(
            id=period_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=period, message="Period deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the period: {str(e)}"
        )