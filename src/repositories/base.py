"""Base repository pattern implementation for Performance Management System."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from sqlmodel import Session, select, col
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime

# Generic type for SQLModel models
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class with CRUD operations."""
    
    def __init__(self, model: Type[T], session: Session):
        """Initialize repository with model and database session.
        
        Args:
            model: SQLModel model class
            session: SQLAlchemy session
        """
        self.model = model
        self.session = session
    
    async def create(self, obj_in: Union[Dict[str, Any], BaseModel], created_by: Optional[UUID] = None) -> T:
        """Create a new record.
        
        Args:
            obj_in: Input data as dict or Pydantic model
            created_by: UUID of the user creating the record
            
        Returns:
            Created model instance
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)
        
        if created_by:
            create_data["created_by"] = created_by
        
        db_obj = self.model(**create_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    async def get(self, id: UUID) -> Optional[T]:
        """Get a record by id.
        
        Args:
            id: UUID of the record to retrieve
            
        Returns:
            The model instance or None if not found
        """
        statement = select(self.model).where(
            col(self.model.id) == id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def get_or_404(self, id: UUID) -> T:
        """Get a record by id or raise 404 error.
        
        Args:
            id: UUID of the record to retrieve
            
        Returns:
            The model instance
            
        Raises:
            HTTPException: If record not found
        """
        db_obj = await self.get(id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} not found"
            )
        return db_obj
    
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
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    statement = statement.where(getattr(self.model, field) == value)
        
        statement = statement.offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    async def update(
        self,
        *,
        db_obj: T,
        obj_in: Union[Dict[str, Any], BaseModel],
        updated_by: Optional[UUID] = None
    ) -> T:
        """Update an existing record.
        
        Args:
            db_obj: Existing database object
            obj_in: New data as dict or Pydantic model
            updated_by: UUID of the user updating the record
            
        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update attributes on the DB model
        for field in update_data:
            if field in update_data and hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        # Set updated_by and updated_at
        if updated_by and hasattr(db_obj, "updated_by"):
            db_obj.updated_by = updated_by
        
        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.utcnow()
        
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: UUID, soft_delete: bool = True, deleted_by: Optional[UUID] = None) -> T:
        """Delete a record.
        
        Args:
            id: UUID of the record to delete
            soft_delete: If True, mark as deleted; if False, hard delete
            deleted_by: UUID of the user deleting the record
            
        Returns:
            The deleted model instance
            
        Raises:
            HTTPException: If record not found
        """
        db_obj = await self.get_or_404(id)
        
        if soft_delete and hasattr(db_obj, "is_deleted"):
            # Soft delete
            db_obj.is_deleted = True
            
            if hasattr(db_obj, "updated_by") and deleted_by:
                db_obj.updated_by = deleted_by
            
            if hasattr(db_obj, "updated_at"):
                db_obj.updated_at = datetime.utcnow()
            
            self.session.add(db_obj)
        else:
            # Hard delete
            self.session.delete(db_obj)
        
        self.session.commit()
        return db_obj
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering.
        
        Args:
            filters: Optional dictionary of filter conditions
            
        Returns:
            Number of records
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    statement = statement.where(getattr(self.model, field) == value)
        
        results = self.session.exec(statement)
        return len(results.all())