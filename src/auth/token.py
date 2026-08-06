import uuid
from datetime import datetime, timedelta, timezone

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