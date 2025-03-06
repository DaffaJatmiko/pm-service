"""Base service implementation for Performance Management System."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from fastapi import HTTPException, Depends, status
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_db
from src.repositories.base import BaseRepository

# Generic types
T = TypeVar('T')  # SQLModel model
R = TypeVar('R')  # Repository


class BaseService(Generic[T, R]):
    """Base service with common CRUD operations."""
    
    def __init__(self, repository: Type[R], session: Session = Depends(get_db)):
        """Initialize with repository type and database session.
        
        Args:
            repository: Repository class for this service
            session: Database session dependency
        """
        self.repository = repository(session=session)
    
    async def create(self, obj_in: BaseModel, created_by: Optional[UUID] = None) -> T:
        """Create a new record.
        
        Args:
            obj_in: Pydantic model for input data
            created_by: UUID of the user creating the record
            
        Returns:
            Created model instance
        """
        return await self.repository.create(obj_in=obj_in, created_by=created_by)
    
    async def get(self, id: UUID) -> Optional[T]:
        """Get a record by id.
        
        Args:
            id: UUID of the record to retrieve
            
        Returns:
            The model instance or None if not found
        """
        return await self.repository.get(id=id)
    
    async def get_or_404(self, id: UUID) -> T:
        """Get a record by id or raise 404 error.
        
        Args:
            id: UUID of the record to retrieve
            
        Returns:
            The model instance
            
        Raises:
            HTTPException: If record not found
        """
        return await self.repository.get_or_404(id=id)
    
    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get multiple records with filtering.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Optional dictionary of filter conditions
            
        Returns:
            List of model instances
        """
        return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def update(
        self,
        *,
        id: UUID,
        obj_in: Union[Dict[str, Any], BaseModel],
        updated_by: Optional[UUID] = None
    ) -> T:
        """Update an existing record.
        
        Args:
            id: UUID of the record to update
            obj_in: New data as dict or Pydantic model
            updated_by: UUID of the user updating the record
            
        Returns:
            Updated model instance
        """
        db_obj = await self.repository.get_or_404(id=id)
        return await self.repository.update(db_obj=db_obj, obj_in=obj_in, updated_by=updated_by)
    
    async def delete(self, id: UUID, soft_delete: bool = True, deleted_by: Optional[UUID] = None) -> T:
        """Delete a record.
        
        Args:
            id: UUID of the record to delete
            soft_delete: If True, mark as deleted; if False, hard delete
            deleted_by: UUID of the user deleting the record
            
        Returns:
            The deleted model instance
        """
        return await self.repository.delete(id=id, soft_delete=soft_delete, deleted_by=deleted_by)
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering.
        
        Args:
            filters: Optional dictionary of filter conditions
            
        Returns:
            Number of records
        """
        return await self.repository.count(filters=filters)