import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from backend.app.auth import validate_telegram_init_data


def signed_init_data(bot_token: str, user_id: int, auth_date: int | None = None) -> str:
    values = {
        "auth_date": str(auth_date or int(time.time())),
        "query_id": "test-query",
        "user": json.dumps({"id": user_id, "first_name": "Roman"}, separators=(",", ":")),
    }
    check = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_valid_telegram_init_data_resolves_identity() -> None:
    identity = validate_telegram_init_data(signed_init_data("secret-token", 123), "secret-token", 60)
    assert identity.telegram_id == 123
    assert identity.display_name == "Roman"


@pytest.mark.parametrize("mutation", ["wrong-token", "expired"])
def test_forged_or_expired_telegram_init_data_is_rejected(mutation: str) -> None:
    auth_date = int(time.time()) - 120 if mutation == "expired" else None
    init_data = signed_init_data("secret-token", 123, auth_date)
    token = "other-token" if mutation == "wrong-token" else "secret-token"
    with pytest.raises(ValueError):
        validate_telegram_init_data(init_data, token, 60)
