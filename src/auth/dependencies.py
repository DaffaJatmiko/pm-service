"""Authentication dependencies for Performance Management System."""

from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from uuid import UUID

from src.core.settings import settings
from src.auth.jwt_handler import verify_token

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get the current authenticated user from the token.
    
    Args:
        token: JWT access token
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid or authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode the token
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Include token data in the user dict
        user_data = {
            "id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
            "roles": payload.get("roles", []),
        }
        
        return user_data
    except JWTError:
        raise credentials_exception


async def get_current_active_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Check if the current user is active.
    
    Args:
        current_user: User data dictionary
        
    Returns:
        Active user data dictionary
        
    Raises:
        HTTPException: If user is not active
    """
    if current_user.get("is_active") is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return current_user


def check_user_role(allowed_roles: list):
    """Create a dependency to check if user has required role.
    
    Args:
        allowed_roles: List of roles allowed to access the endpoint
        
    Returns:
        Dependency function that checks user roles
    """
    async def has_role(current_user: Dict = Depends(get_current_active_user)) -> Dict:
        """Check if user has any of the allowed roles.
        
        Args:
            current_user: User data dictionary
            
        Returns:
            User data if authorized
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_roles = current_user.get("roles", [])
        
        # Check if user has any of the allowed roles
        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return current_user
    
    return has_role