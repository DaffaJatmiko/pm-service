"""Organization repository implementation for Performance Management System."""

from typing import Dict, List, Optional, Any
from sqlmodel import Session, select, col, or_
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime

from src.models.organization import Department, Position, UnitType
from src.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Repository for Department model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=Department, session=session)
    
    async def get_by_code(self, code: str) -> Optional[Department]:
        """Get a department by code.
        
        Args:
            code: Department code
            
        Returns:
            Department object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.code) == code,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def get_children(self, parent_id: UUID) -> List[Department]:
        """Get all child departments of a parent department.
        
        Args:
            parent_id: UUID of the parent department
            
        Returns:
            List of Department objects that are children of the parent
        """
        statement = select(self.model).where(
            col(self.model.parent_id) == parent_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()
    
    async def get_top_level_departments(self) -> List[Department]:
        """Get all top-level departments (those without a parent).
        
        Returns:
            List of top-level Department objects
        """
        statement = select(self.model).where(
            col(self.model.parent_id) == None,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()
    
    async def get_department_hierarchy(self, department_id: Optional[UUID] = None) -> List[Department]:
        """Get a department hierarchy starting from a specified department or top level.
        
        Args:
            department_id: Optional UUID of the starting department
            
        Returns:
            List of Department objects in a hierarchical structure
        """
        if department_id:
            # Start from specified department
            statement = select(self.model).where(
                col(self.model.id) == department_id,
                col(self.model.is_deleted) == False
            )
            results = self.session.exec(statement)
            departments = [results.first()]
            
            if not departments[0]:
                return []
        else:
            # Start from top level departments
            departments = await self.get_top_level_departments()
        
        # For each department, recursively get its children
        # Note: This is a simplified approach; for large hierarchies, 
        # consider using recursive CTEs in SQL
        result = []
        for dept in departments:
            dept_dict = Department.from_orm(dept).__dict__
            children = await self.get_children(dept.id)
            dept_dict["children"] = children
            result.append(dept_dict)
        
        return result
    
    async def search(
        self,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        unit_type: Optional[UnitType] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Department]:
        """Search departments with various filters.
        
        Args:
            name: Optional name filter (partial match)
            code: Optional code filter (partial match)
            unit_type: Optional unit type filter
            is_active: Optional active status filter
            parent_id: Optional parent department filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Department objects matching the criteria
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if name:
            statement = statement.where(col(self.model.name).contains(name))
        
        if code:
            statement = statement.where(col(self.model.code).contains(code))
        
        if unit_type:
            statement = statement.where(col(self.model.unit_type) == unit_type)
        
        if is_active is not None:
            statement = statement.where(col(self.model.is_active) == is_active)
        
        if parent_id:
            statement = statement.where(col(self.model.parent_id) == parent_id)
        
        statement = statement.offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    async def search_count(
        self,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        unit_type: Optional[UnitType] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[UUID] = None
    ) -> int:
        """Count departments matching search criteria.
        
        Args:
            name: Optional name filter (partial match)
            code: Optional code filter (partial match)
            unit_type: Optional unit type filter
            is_active: Optional active status filter
            parent_id: Optional parent department filter
            
        Returns:
            Number of matching departments
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if name:
            statement = statement.where(col(self.model.name).contains(name))
        
        if code:
            statement = statement.where(col(self.model.code).contains(code))
        
        if unit_type:
            statement = statement.where(col(self.model.unit_type) == unit_type)
        
        if is_active is not None:
            statement = statement.where(col(self.model.is_active) == is_active)
        
        if parent_id:
            statement = statement.where(col(self.model.parent_id) == parent_id)
        
        results = self.session.exec(statement)
        return len(results.all())


class PositionRepository(BaseRepository[Position]):
    """Repository for Position model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=Position, session=session)
    
    async def get_by_code(self, code: str) -> Optional[Position]:
        """Get a position by code.
        
        Args:
            code: Position code
            
        Returns:
            Position object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.code) == code,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def get_by_department(self, department_id: UUID) -> List[Position]:
        """Get all positions in a department.
        
        Args:
            department_id: UUID of the department
            
        Returns:
            List of Position objects in the department
        """
        statement = select(self.model).where(
            col(self.model.department_id) == department_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()
    
    async def search(
        self,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        department_id: Optional[UUID] = None,
        level: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Position]:
        """Search positions with various filters.
        
        Args:
            name: Optional name filter (partial match)
            code: Optional code filter (partial match)
            department_id: Optional department filter
            level: Optional level filter
            is_active: Optional active status filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Position objects matching the criteria
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if name:
            statement = statement.where(col(self.model.name).contains(name))
        
        if code:
            statement = statement.where(col(self.model.code).contains(code))
        
        if department_id:
            statement = statement.where(col(self.model.department_id) == department_id)
        
        if level is not None:
            statement = statement.where(col(self.model.level) == level)
        
        if is_active is not None:
            statement = statement.where(col(self.model.is_active) == is_active)
        
        statement = statement.offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    async def search_count(
        self,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        department_id: Optional[UUID] = None,
        level: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Count positions matching search criteria.
        
        Args:
            name: Optional name filter (partial match)
            code: Optional code filter (partial match)
            department_id: Optional department filter
            level: Optional level filter
            is_active: Optional active status filter
            
        Returns:
            Number of matching positions
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if name:
            statement = statement.where(col(self.model.name).contains(name))
        
        if code:
            statement = statement.where(col(self.model.code).contains(code))
        
        if department_id:
            statement = statement.where(col(self.model.department_id) == department_id)
        
        if level is not None:
            statement = statement.where(col(self.model.level) == level)
        
        if is_active is not None:
            statement = statement.where(col(self.model.is_active) == is_active)
        
        results = self.session.exec(statement)
        return len(results.all())