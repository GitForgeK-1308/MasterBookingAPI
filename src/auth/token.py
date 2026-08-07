import uuid
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
import jwt

from src.config import settings


def create_access_token(
    user_id: uuid.UUID,
) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(
    token: str,
) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidTokenError

        return uuid.UUID(user_id)

    except (InvalidTokenError, ValueError):
        raise InvalidTokenError