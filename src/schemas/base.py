"""Base schemas for Performance Management System."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from uuid import UUID


class ResponseBase(BaseModel):
    """Base schema for API responses."""
    
    success: bool = True
    message: str = "Operation successful"


T = TypeVar('T')


class PaginatedResponse(ResponseBase, Generic[T]):
    """Schema for paginated API responses."""
    
    data: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 1


class DataResponse(ResponseBase, Generic[T]):
    """Schema for API responses with data."""
    
    data: T


class ErrorResponse(ResponseBase):
    """Schema for API error responses."""
    
    success: bool = False
    message: str = "An error occurred"
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None