"""User API endpoints for Performance Management System."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.schemas.base import DataResponse, PaginatedResponse
from src.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserDetailResponse,
    UserSSOLink,
    UserQueryParams
)
from src.services.user import UserService
from src.auth.dependencies import get_current_user, get_current_active_user, check_user_role

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", 
    response_model=DataResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the given details. Only users with admin or HR roles can create users."
)
async def create_user(
    user_in: UserCreate,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    user_service: UserService = Depends()
):
    """Create a new user."""
    try:
        user = await user_service.create_user(
            user_in=user_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=user, message="User created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the user: {str(e)}"
        )


@router.get(
    "/", 
    response_model=PaginatedResponse[UserResponse],
    summary="Get all users",
    description="Get a list of all users with optional filtering and pagination."
)
async def get_users(
    query_params: UserQueryParams = Depends(),
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Get all users with optional filtering."""
    try:
        result = await user_service.search_users(
            name=query_params.name,
            email=query_params.email,
            employee_number=query_params.employee_number,
            department_id=query_params.department_id,
            position_id=query_params.position_id,
            manager_id=query_params.manager_id,
            role=query_params.role.value if query_params.role else None,
            status=query_params.status.value if query_params.status else None,
            external_id=query_params.external_id,
            page=query_params.page,
            page_size=query_params.page_size
        )
        
        return PaginatedResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            message="Users retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving users: {str(e)}"
        )


@router.get(
    "/me", 
    response_model=DataResponse[UserResponse],
    summary="Get current user",
    description="Get details of the currently authenticated user."
)
async def get_current_user_details(
    current_user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    """Get current user details."""
    try:
        user = await user_service.get_or_404(id=UUID(current_user["id"]))
        return DataResponse(data=user, message="Current user retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving current user: {str(e)}"
        )


@router.get(
    "/{user_id}", 
    response_model=DataResponse[UserDetailResponse],
    summary="Get a user by ID",
    description="Get detailed information of a specific user by their ID."
)
async def get_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Get a user by ID with details."""
    try:
        user_data = await user_service.get_user_with_details(id=user_id)
        return DataResponse(data=user_data, message="User retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the user: {str(e)}"
        )


@router.get(
    "/{user_id}/subordinates", 
    response_model=DataResponse[List[UserResponse]],
    summary="Get user subordinates",
    description="Get a list of all users who report to a specific user."
)
async def get_user_subordinates(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Get all subordinates of a user."""
    try:
        subordinates = await user_service.get_user_subordinates(user_id=user_id)
        return DataResponse(data=subordinates, message="User subordinates retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving subordinates: {str(e)}"
        )


@router.patch(
    "/{user_id}", 
    response_model=DataResponse[UserResponse],
    summary="Update a user",
    description="Update details of a specific user by their ID. Users can update their own info, managers can update their subordinates, and admins/HR can update any user."
)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    """Update a user."""
    # Check if user has permission to update this user
    if (
        str(user_id) != current_user["id"] and  # Not updating self
        "admin" not in current_user["roles"] and  # Not an admin
        "hr" not in current_user["roles"]  # Not HR
    ):
        # Check if the user is a manager of the target user
        target_user = await user_service.get_or_404(id=user_id)
        if not target_user.manager_id or str(target_user.manager_id) != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this user"
            )
    
    try:
        user = await user_service.update_user(
            user_id=user_id, 
            user_in=user_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=user, message="User updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the user: {str(e)}"
        )


@router.patch(
    "/{user_id}/sso-link", 
    response_model=DataResponse[UserResponse],
    summary="Link user to SSO",
    description="Link a user to an SSO account using external ID. Only users with admin or HR roles can perform this action."
)
async def link_user_to_sso(
    user_id: UUID,
    sso_link: UserSSOLink,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    user_service: UserService = Depends()
):
    """Link a user to an SSO account."""
    try:
        user = await user_service.link_user_to_sso(
            user_id=user_id, 
            sso_link=sso_link,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=user, message="User linked to SSO successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while linking user to SSO: {str(e)}"
        )


@router.get(
    "/external/{external_id}", 
    response_model=DataResponse[UserResponse],
    summary="Get user by external ID",
    description="Get a user by their external ID from the SSO system."
)
async def get_user_by_external_id(
    external_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Get a user by external ID."""
    try:
        user = await user_service.get_by_external_id(external_id=external_id)
        if not user:
            return DataResponse(
                data=None,
                message=f"No user found with external ID {external_id}",
                success=False
            )
        
        return DataResponse(data=user, message="User retrieved successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the user: {str(e)}"
        )


@router.delete(
    "/{user_id}", 
    response_model=DataResponse[UserResponse],
    summary="Delete a user",
    description="Delete a user by their ID (soft delete). Only users with admin roles can delete users."
)
async def delete_user(
    user_id: UUID,
    current_user: dict = Depends(check_user_role(["admin"])),
    user_service: UserService = Depends()
):
    """Delete a user (soft delete)."""
    try:
        user = await user_service.delete(
            id=user_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=user, message="User deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the user: {str(e)}"
        )