from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.settings import get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    role: str


def _parse_static_tokens(raw: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        token, role = pair.split(":", 1)
        mapping[token.strip()] = role.strip()
    return mapping


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_user_id: str | None = Header(default=None),
) -> AuthUser:
    settings = get_settings()

    if settings.auth_mode == "dev":
        return AuthUser(user_id=(x_user_id or "dev-user"), role="admin")

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = credentials.credentials
    static_tokens = _parse_static_tokens(settings.static_tokens)
    if token in static_tokens:
        return AuthUser(user_id=(x_user_id or "token-user"), role=static_tokens[token])

    if settings.jwt_secret:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            user_id = str(payload.get("sub") or payload.get("user_id") or x_user_id or "unknown-user")
            role = str(payload.get("role") or "viewer")
            return AuthUser(user_id=user_id, role=role)
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized token")


def require_roles(*roles: str) -> Callable[[AuthUser], AuthUser]:
    allowed = set(roles)

    def dependency(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dependency


def require_editor(user: AuthUser = Depends(require_roles("admin", "editor"))) -> AuthUser:
    return user


def require_admin(user: AuthUser = Depends(require_roles("admin"))) -> AuthUser:
    return user
