from datetime import timedelta

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip():
    encoded = hash_password("strong-password")
    assert encoded != "strong-password"
    assert verify_password("strong-password", encoded)
    assert not verify_password("wrong-password", encoded)


def test_access_token_round_trip():
    token = create_access_token("42", expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
