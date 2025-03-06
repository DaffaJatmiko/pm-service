"""Organization service implementation for Performance Management System."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, Depends, status
from sqlmodel import Session

from src.core.database import get_db
from src.models.organization import Department, Position, UnitType
from src.repositories.organization import DepartmentRepository, PositionRepository
from src.schemas.organization import (
    DepartmentCreate, 
    DepartmentUpdate,
    PositionCreate,
    PositionUpdate
)
from src.services.base import BaseService


class DepartmentService(BaseService[Department, DepartmentRepository]):
    """Service for Department management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=DepartmentRepository, session=session)
    
    async def create_department(self, department_in: DepartmentCreate, created_by: Optional[UUID] = None) -> Department:
        """Create a new department.
        
        Args:
            department_in: Department creation data
            created_by: UUID of the user creating the department
            
        Returns:
            Created Department object
            
        Raises:
            HTTPException: If a department with the same code already exists
        """
        # Check if department with same code already exists
        existing_dept = await self.repository.get_by_code(code=department_in.code)
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A department with code {department_in.code} already exists"
            )
        
        # Check if parent department exists if specified
        if department_in.parent_id:
            parent_dept = await self.repository.get(id=department_in.parent_id)
            if not parent_dept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parent department with id {department_in.parent_id} not found"
                )
        
        # Create the new department
        return await self.repository.create(obj_in=department_in, created_by=created_by)
    
    async def update_department(
        self, 
        department_id: UUID, 
        department_in: DepartmentUpdate, 
        updated_by: Optional[UUID] = None
    ) -> Department:
        """Update a department.
        
        Args:
            department_id: UUID of the department to update
            department_in: Department update data
            updated_by: UUID of the user updating the department
            
        Returns:
            Updated Department object
            
        Raises:
            HTTPException: If a department with the same code already exists
        """
        # Get existing department
        db_dept = await self.repository.get_or_404(id=department_id)
        
        # Check if code is being updated and already exists
        if department_in.code and department_in.code != db_dept.code:
            existing_dept = await self.repository.get_by_code(code=department_in.code)
            if existing_dept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A department with code {department_in.code} already exists"
                )
        
        # Check if parent department exists if specified
        if department_in.parent_id:
            # Check for circular reference
            if department_in.parent_id == department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department cannot be its own parent"
                )
            
            parent_dept = await self.repository.get(id=department_in.parent_id)
            if not parent_dept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parent department with id {department_in.parent_id} not found"
                )
        
        # Update the department
        return await self.repository.update(db_obj=db_dept, obj_in=department_in, updated_by=updated_by)
    
    async def get_department_hierarchy(self, department_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get a department hierarchy starting from a specified department or top level.
        
        Args:
            department_id: Optional UUID of the starting department
            
        Returns:
            List of Department objects in a hierarchical structure
        """
        return await self.repository.get_department_hierarchy(department_id=department_id)
    
    async def search_departments(
        self,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        unit_type: Optional[UnitType] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[UUID] = None,
        include_children: bool = False,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Search departments with pagination.
        
        Args:
            name: Optional name filter (partial match)
            code: Optional code filter (partial match)
            unit_type: Optional unit type filter
            is_active: Optional active status filter
            parent_id: Optional parent department filter
            include_children: Whether to include children in the response
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with results and pagination info
        """
        skip = (page - 1) * page_size
        
        # Get data with pagination
        departments = await self.repository.search(
            name=name,
            code=code,
            unit_type=unit_type,
            is_active=is_active,
            parent_id=parent_id,
            skip=skip,
            limit=page_size
        )
        
        # Get total count for pagination
        total = await self.repository.search_count(
            name=name,
            code=code,
            unit_type=unit_type,
            is_active=is_active,
            parent_id=parent_id
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        # If include_children is True, include children for each department
        if include_children:
            result_data = []
            for dept in departments:
                dept_data = {**dept.dict()}
                children = await self.repository.get_children(dept.id)
                dept_data["children"] = children
                result_data.append(dept_data)
            
            departments = result_data
        
        return {
            "data": departments,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }


class PositionService(BaseService[Position, PositionRepository]):
    """Service for Position management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=PositionRepository, session=session)
    
    async def create_position(self, position_in: PositionCreate, created_by: Optional[UUID] = None) -> Position:
        """Create a new position.
        
        Args:
            position_in: Position creation data
            created_by: UUID of the user creating the position
            
        Returns:
            Created Position object
            
        Raises:
            HTTPException: If a position with the same code already exists
        """
        # Check if position with same code already exists
        existing_pos = await self.repository.get_by_code(code=position_in.code)
        if existing_pos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A position with code {position_in.code} already exists"
            )
        
        # Create the new position
        return await self.repository.create(obj_in=position_in, created_by=created_by)
    
    async def update_position(
        self, 
        position_id: UUID, 
        position_in: PositionUpdate, 
        updated_by: Optional[UUID] = None
    ) -> Position:
        """Update a position.
        
        Args:
            position_id: UUID of the position to update
            position_in: Position update data
            updated_by: UUID of the user updating the position
            
        Returns:
            Updated Position object
            
        Raises:
            HTTPException: If a position with the same code already exists
        """
        # Get existing position
        db_pos = await self.repository.get_or_404(id=position_id)
        
        # Check if code is being updated and already exists
        if position_in.code and position_in.code != db_pos.code:
            existing_pos = await self.repository.get_by_code(code=position_in.code)
            if existing_pos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A position with code {position_in.code} already exists"
                )
        
        # Update the position
        return await self.repository.update(db_obj=db_pos, obj_in=position_in, updated_by=updated_by)
    
    async def get_positions_by_department(self, department_id: UUID) -> List[Position]:
        """Get all positions in a department.
        
        Args:
            department_id: UUID of the department
            
        Returns:
            List of Position objects in the department
        """
        return await self.repository.get_by_department(department_id=department_id)
    
    async def search_positions(
        self,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        department_id: Optional[UUID] = None,
        level: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Search positions with pagination.
        
        Args:
            name: Optional name filter (partial match)
            code: Optional code filter (partial match)
            department_id: Optional department filter
            level: Optional level filter
            is_active: Optional active status filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with results and pagination info
        """
        skip = (page - 1) * page_size
        
        # Get data with pagination
        positions = await self.repository.search(
            name=name,
            code=code,
            department_id=department_id,
            level=level,
            is_active=is_active,
            skip=skip,
            limit=page_size
        )
        
        # Get total count for pagination
        total = await self.repository.search_count(
            name=name,
            code=code,
            department_id=department_id,
            level=level,
            is_active=is_active
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "data": positions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }