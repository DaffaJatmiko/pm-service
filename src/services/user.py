"""User service implementation for Performance Management System."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, Depends, status
from sqlmodel import Session

from src.core.database import get_db
from src.models.user import User, UserRole
from src.repositories.user import UserRepository
from src.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserDetailResponse,
    UserSSOLink
)
from src.services.base import BaseService


class UserService(BaseService[User, UserRepository]):
    """Service for User management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=UserRepository, session=session)
    
    async def create_user(self, user_in: UserCreate, created_by: Optional[UUID] = None) -> User:
        """Create a new user.
        
        Args:
            user_in: User creation data
            created_by: UUID of the user creating the user
            
        Returns:
            Created User object
            
        Raises:
            HTTPException: If a user with the same email or employee_number already exists
        """
        # Check if user already exists
        existing_user_email = await self.repository.get_by_email(email=user_in.email)
        if existing_user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A user with email {user_in.email} already exists"
            )
        
        existing_user_emp = await self.repository.get_by_employee_number(employee_number=user_in.employee_number)
        if existing_user_emp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A user with employee number {user_in.employee_number} already exists"
            )
        
        # Check if external_id is provided and already exists
        if user_in.external_id:
            existing_user_ext = await self.repository.get_by_external_id(external_id=user_in.external_id)
            if existing_user_ext:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A user with external ID {user_in.external_id} already exists"
                )
        
        # Create the new user
        user_data = user_in.dict()
        
        # Convert status to is_active
        user_data["is_active"] = user_data.get("status") == "Active"
        if "status" in user_data:
            user_data.pop("status")
        
        return await self.repository.create(obj_in=user_data, created_by=created_by)
    
    async def update_user(self, user_id: UUID, user_in: UserUpdate, updated_by: Optional[UUID] = None) -> User:
        """Update a user.
        
        Args:
            user_id: UUID of the user to update
            user_in: User update data
            updated_by: UUID of the user updating the user
            
        Returns:
            Updated User object
            
        Raises:
            HTTPException: If a user with the same email or employee_number already exists
        """
        # Get existing user
        db_user = await self.repository.get_or_404(id=user_id)
        
        # Check if email is being updated and already exists
        if user_in.email and user_in.email != db_user.email:
            existing_user = await self.repository.get_by_email(email=user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A user with email {user_in.email} already exists"
                )
        
        # Check if external_id is being updated and already exists
        if user_in.external_id and user_in.external_id != db_user.external_id:
            existing_user = await self.repository.get_by_external_id(external_id=user_in.external_id)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A user with external ID {user_in.external_id} already exists"
                )
        
        # Update is_active from status if provided
        user_data = user_in.dict(exclude_unset=True)
        if "status" in user_data:
            user_data["is_active"] = user_data.get("status") == "Active"
            user_data.pop("status")
        
        # Update the user
        return await self.repository.update(db_obj=db_user, obj_in=user_data, updated_by=updated_by)
    
    async def link_user_to_sso(self, user_id: UUID, sso_link: UserSSOLink, updated_by: Optional[UUID] = None) -> User:
        """Link a user to an SSO account.
        
        Args:
            user_id: UUID of the user
            sso_link: SSO link data
            updated_by: UUID of the user updating the link
            
        Returns:
            Updated User object
            
        Raises:
            HTTPException: If the external_id already exists
        """
        # Get existing user
        db_user = await self.repository.get_or_404(id=user_id)
        
        # Check if external_id already exists on another user
        if sso_link.external_id:
            existing_user = await self.repository.get_by_external_id(external_id=sso_link.external_id)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A user with external ID {sso_link.external_id} already exists"
                )
        
        # Update the user with external_id
        return await self.repository.update(
            db_obj=db_user, 
            obj_in={"external_id": sso_link.external_id}, 
            updated_by=updated_by
        )
    
    async def get_by_external_id(self, external_id: str) -> Optional[User]:
        """Get a user by external ID.
        
        Args:
            external_id: External ID from SSO system
            
        Returns:
            User object if found, None otherwise
        """
        return await self.repository.get_by_external_id(external_id=external_id)
    
    async def get_user_with_details(self, user_id: UUID) -> Dict[str, Any]:
        """Get a user with additional details like department name, position name, etc.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User data with additional details
            
        Raises:
            HTTPException: If user not found
        """
        # Get the user
        db_user = await self.repository.get_or_404(id=user_id)
        
        # Create the response object
        user_data = UserDetailResponse.from_orm(db_user).dict()
        
        # Add performance data (this would normally be fetched from other services)
        # This is a placeholder - in a real implementation, you would fetch real data
        user_data["performance_data"] = {
            "mpm_completion_rate": 92,
            "ipm_completion_rate": 87,
            "overall_score": 3.4,
            "performance_trend": [75, 82, 78, 90, 95, 92]
        }
        
        return user_data
    
    async def get_user_subordinates(self, user_id: UUID) -> List[User]:
        """Get all subordinates of a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of User objects who report to the user
        """
        return await self.repository.get_manager_subordinates(manager_id=user_id)
    
    async def search_users(
        self,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        employee_number: Optional[str] = None,
        department_id: Optional[UUID] = None,
        position_id: Optional[UUID] = None,
        manager_id: Optional[UUID] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        external_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Search users with pagination.
        
        Args:
            name: Optional name filter (partial match)
            email: Optional email filter (partial match)
            employee_number: Optional employee number filter (exact match)
            department_id: Optional department filter
            position_id: Optional position filter
            manager_id: Optional manager filter
            role: Optional role filter
            status: Optional status filter
            external_id: Optional external ID filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with results and pagination info
        """
        skip = (page - 1) * page_size
        
        # Get data with pagination
        users = await self.repository.search(
            name=name,
            email=email,
            employee_number=employee_number,
            department_id=department_id,
            position_id=position_id,
            manager_id=manager_id,
            role=role,
            status=status,
            external_id=external_id,
            skip=skip,
            limit=page_size
        )
        
        # Get total count for pagination
        total = await self.repository.search_count(
            name=name,
            email=email,
            employee_number=employee_number,
            department_id=department_id,
            position_id=position_id,
            manager_id=manager_id,
            role=role,
            status=status,
            external_id=external_id
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "data": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }