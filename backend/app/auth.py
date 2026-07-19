import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl, unquote

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings
from backend.app.db import get_session
from backend.app.models import User


@dataclass(frozen=True)
class TelegramIdentity:
    telegram_id: int
    display_name: str


def validate_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int) -> TelegramIdentity:
    values = dict(parse_qsl(init_data, keep_blank_values=True))
    supplied_hash = values.pop("hash", "")
    if not supplied_hash:
        raise ValueError("Missing Telegram signature")
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, supplied_hash):
        raise ValueError("Invalid Telegram signature")

    try:
        auth_date = int(values["auth_date"])
        user_data = json.loads(values["user"])
        telegram_id = int(user_data["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid Telegram authentication data") from exc
    if auth_date > int(time.time()) + 30 or int(time.time()) - auth_date > max_age_seconds:
        raise ValueError("Expired Telegram authentication data")
    display_name = (
        " ".join(value for value in (user_data.get("first_name"), user_data.get("last_name")) if value).strip()
        or user_data.get("username")
        or f"Telegram {telegram_id}"
    )
    return TelegramIdentity(telegram_id=telegram_id, display_name=display_name)


def _identity_from_request(
    request: Request,
    telegram_init_data: str | None,
    dev_user_id: str | None,
    dev_name: str | None,
) -> TelegramIdentity:
    settings: Settings = request.app.state.settings
    if settings.dev_auth_enabled and dev_user_id:
        try:
            return TelegramIdentity(int(dev_user_id), unquote(dev_name) if dev_name else f"Developer {dev_user_id}")
        except ValueError as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid developer identity") from exc
    if not telegram_init_data or not settings.bot_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Telegram authentication required")
    try:
        return validate_telegram_init_data(
            telegram_init_data, settings.bot_token, settings.telegram_auth_max_age_seconds
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
    telegram_init_data: str | None = Header(default=None, alias="X-Telegram-Init-Data"),
    dev_user_id: str | None = Header(default=None, alias="X-Dev-Telegram-User-Id"),
    dev_name: str | None = Header(default=None, alias="X-Dev-Telegram-Name"),
) -> User:
    identity = _identity_from_request(request, telegram_init_data, dev_user_id, dev_name)
    user = session.scalar(select(User).where(User.telegram_id == identity.telegram_id))
    if user is None:
        user = User(telegram_id=identity.telegram_id, display_name=identity.display_name)
        session.add(user)
        session.commit()
        session.refresh(user)
    elif user.display_name != identity.display_name:
        user.display_name = identity.display_name
        session.commit()
        session.refresh(user)
    return user
