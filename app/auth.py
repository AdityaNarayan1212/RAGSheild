"""Local bearer-token authentication for employee and HR demo roles."""

import hmac
import os
from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

Role = Literal["employee", "hr"]

bearer_scheme = HTTPBearer(auto_error=False)


def require_role(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Role:
    """Resolve a role only when its distinct local token is configured and valid."""
    employee_token = os.getenv("RAGSHIELD_EMPLOYEE_TOKEN", "")
    hr_token = os.getenv("RAGSHIELD_HR_TOKEN", "")

    if not employee_token or not hr_token or hmac.compare_digest(employee_token, hr_token):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Local role tokens are not configured correctly.",
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if hmac.compare_digest(credentials.credentials, employee_token):
        return "employee"
    if hmac.compare_digest(credentials.credentials, hr_token):
        return "hr"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A valid bearer token is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
