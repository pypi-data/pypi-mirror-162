from typing import List

from fastapi import HTTPException, status

from .models import User

def can_access_resource(user: User, allowed_roles: List[str], resource: str):
    forbidden_exception = (
        HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to resource is forbidden",
        )
    )

    if not user.resources or resource not in user.resources:
        raise forbidden_exception

    api_resource = user.resources[resource]

    if not 'roles' in api_resource:
        raise forbidden_exception
    
    user_roles = api_resource.get('roles', [])
    has_access = any(role in allowed_roles for role in user_roles)
    
    if not has_access:
        raise forbidden_exception
    
    return user_roles
