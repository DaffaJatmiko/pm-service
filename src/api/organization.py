"""Organization API endpoints for Performance Management System."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.schemas.base import DataResponse, PaginatedResponse
from src.schemas.organization import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentWithChildrenResponse,
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    DepartmentQueryParams,
    PositionQueryParams
)
from src.services.organization import DepartmentService, PositionService
from src.auth.dependencies import get_current_user, get_current_active_user, check_user_role

router = APIRouter(prefix="/organization", tags=["organization"])


# Department endpoints
@router.post(
    "/departments", 
    response_model=DataResponse[DepartmentResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new department",
    description="Create a new department with the given details. Only users with admin or HR roles can create departments."
)
async def create_department(
    department_in: DepartmentCreate,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    department_service: DepartmentService = Depends()
):
    """Create a new department."""
    try:
        department = await department_service.create_department(
            department_in=department_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=department, message="Department created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the department: {str(e)}"
        )


@router.get(
    "/departments", 
    response_model=PaginatedResponse[DepartmentResponse],
    summary="Get all departments",
    description="Get a list of all departments with optional filtering and pagination."
)
async def get_departments(
    query_params: DepartmentQueryParams = Depends(),
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends()
):
    """Get all departments with optional filtering."""
    try:
        result = await department_service.search_departments(
            name=query_params.name,
            code=query_params.code,
            unit_type=query_params.unit_type,
            is_active=query_params.is_active,
            parent_id=query_params.parent_id,
            include_children=query_params.include_children,
            page=query_params.page,
            page_size=query_params.page_size
        )
        
        return PaginatedResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            message="Departments retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving departments: {str(e)}"
        )


@router.get(
    "/departments/hierarchy", 
    response_model=DataResponse[List[DepartmentWithChildrenResponse]],
    summary="Get department hierarchy",
    description="Get the department hierarchy, optionally starting from a specific department."
)
async def get_department_hierarchy(
    parent_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends()
):
    """Get department hierarchy."""
    try:
        hierarchy = await department_service.get_department_hierarchy(department_id=parent_id)
        return DataResponse(data=hierarchy, message="Department hierarchy retrieved successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving department hierarchy: {str(e)}"
        )


@router.get(
    "/departments/{department_id}", 
    response_model=DataResponse[DepartmentResponse],
    summary="Get a department by ID",
    description="Get details of a specific department by its ID."
)
async def get_department(
    department_id: UUID,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends()
):
    """Get a department by ID."""
    try:
        department = await department_service.get_or_404(id=department_id)
        return DataResponse(data=department, message="Department retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the department: {str(e)}"
        )


@router.patch(
    "/departments/{department_id}", 
    response_model=DataResponse[DepartmentResponse],
    summary="Update a department",
    description="Update details of a specific department by its ID. Only users with admin or HR roles can update departments."
)
async def update_department(
    department_id: UUID,
    department_in: DepartmentUpdate,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    department_service: DepartmentService = Depends()
):
    """Update a department."""
    try:
        department = await department_service.update_department(
            department_id=department_id, 
            department_in=department_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=department, message="Department updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the department: {str(e)}"
        )


@router.delete(
    "/departments/{department_id}", 
    response_model=DataResponse[DepartmentResponse],
    summary="Delete a department",
    description="Delete a department by its ID (soft delete). Only users with admin roles can delete departments."
)
async def delete_department(
    department_id: UUID,
    current_user: dict = Depends(check_user_role(["admin"])),
    department_service: DepartmentService = Depends()
):
    """Delete a department (soft delete)."""
    try:
        department = await department_service.delete(
            id=department_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=department, message="Department deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the department: {str(e)}"
        )


# Position endpoints
@router.post(
    "/positions", 
    response_model=DataResponse[PositionResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new position",
    description="Create a new position with the given details. Only users with admin or HR roles can create positions."
)
async def create_position(
    position_in: PositionCreate,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    position_service: PositionService = Depends()
):
    """Create a new position."""
    try:
        position = await position_service.create_position(
            position_in=position_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=position, message="Position created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the position: {str(e)}"
        )


@router.get(
    "/positions", 
    response_model=PaginatedResponse[PositionResponse],
    summary="Get all positions",
    description="Get a list of all positions with optional filtering and pagination."
)
async def get_positions(
    query_params: PositionQueryParams = Depends(),
    current_user: dict = Depends(get_current_user),
    position_service: PositionService = Depends()
):
    """Get all positions with optional filtering."""
    try:
        result = await position_service.search_positions(
            name=query_params.name,
            code=query_params.code,
            department_id=query_params.department_id,
            level=query_params.level,
            is_active=query_params.is_active,
            page=query_params.page,
            page_size=query_params.page_size
        )
        
        return PaginatedResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            message="Positions retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving positions: {str(e)}"
        )


@router.get(
    "/departments/{department_id}/positions", 
    response_model=DataResponse[List[PositionResponse]],
    summary="Get positions by department",
    description="Get all positions in a specific department."
)
async def get_positions_by_department(
    department_id: UUID,
    current_user: dict = Depends(get_current_user),
    position_service: PositionService = Depends()
):
    """Get all positions in a department."""
    try:
        positions = await position_service.get_positions_by_department(department_id=department_id)
        return DataResponse(data=positions, message="Department positions retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving department positions: {str(e)}"
        )


@router.get(
    "/positions/{position_id}", 
    response_model=DataResponse[PositionResponse],
    summary="Get a position by ID",
    description="Get details of a specific position by its ID."
)
async def get_position(
    position_id: UUID,
    current_user: dict = Depends(get_current_user),
    position_service: PositionService = Depends()
):
    """Get a position by ID."""
    try:
        position = await position_service.get_or_404(id=position_id)
        return DataResponse(data=position, message="Position retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the position: {str(e)}"
        )


@router.patch(
    "/positions/{position_id}", 
    response_model=DataResponse[PositionResponse],
    summary="Update a position",
    description="Update details of a specific position by its ID. Only users with admin or HR roles can update positions."
)
async def update_position(
    position_id: UUID,
    position_in: PositionUpdate,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    position_service: PositionService = Depends()
):
    """Update a position."""
    try:
        position = await position_service.update_position(
            position_id=position_id, 
            position_in=position_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=position, message="Position updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the position: {str(e)}"
        )


@router.delete(
    "/positions/{position_id}", 
    response_model=DataResponse[PositionResponse],
    summary="Delete a position",
    description="Delete a position by its ID (soft delete). Only users with admin roles can delete positions."
)
async def delete_position(
    position_id: UUID,
    current_user: dict = Depends(check_user_role(["admin"])),
    position_service: PositionService = Depends()
):
    """Delete a position (soft delete)."""
    try:
        position = await position_service.delete(
            id=position_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=position, message="Position deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the position: {str(e)}"
        )