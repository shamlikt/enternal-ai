"""
Unit tests for app.core.security — JWT token creation/validation and password hashing.
"""
import time
from datetime import timedelta

import pytest
from jose import JWTError, jwt

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = get_password_hash("mysecretpassword")
        assert hashed != "mysecretpassword"

    def test_verify_correct_password(self):
        password = "correct-horse-battery-staple"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_two_hashes_of_same_password_are_different(self):
        """bcrypt uses random salt — each hash is unique."""
        password = "same-password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        # But both should verify correctly.
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_empty_password_hashes_and_verifies(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True
        assert verify_password("not-empty", hashed) is False


class TestJWTTokenCreation:
    def test_create_token_returns_string(self):
        token = create_access_token({"sub": "testuser", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_correct_subject(self):
        token = create_access_token({"sub": "user123"})
        payload = decode_access_token(token)
        assert payload["sub"] == "user123"

    def test_token_contains_role(self):
        token = create_access_token({"sub": "user1", "role": "analyst"})
        payload = decode_access_token(token)
        assert payload["role"] == "analyst"

    def test_token_has_expiry(self):
        token = create_access_token({"sub": "user1"})
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_custom_expires_delta(self):
        """Token with 1-second expiry should be valid immediately."""
        token = create_access_token({"sub": "user1"}, expires_delta=timedelta(seconds=1))
        payload = decode_access_token(token)
        assert payload["sub"] == "user1"

    def test_expired_token_returns_empty_dict(self):
        """Tokens with negative expiry are already expired."""
        token = create_access_token({"sub": "user1"}, expires_delta=timedelta(seconds=-1))
        payload = decode_access_token(token)
        assert payload == {}

    def test_different_data_produces_different_tokens(self):
        token1 = create_access_token({"sub": "user1"})
        token2 = create_access_token({"sub": "user2"})
        assert token1 != token2


class TestJWTTokenDecoding:
    def test_decode_valid_token(self):
        token = create_access_token({"sub": "user42", "role": "viewer"})
        payload = decode_access_token(token)
        assert payload["sub"] == "user42"
        assert payload["role"] == "viewer"

    def test_decode_tampered_token_returns_empty_dict(self):
        token = create_access_token({"sub": "user1"})
        # Tamper the signature by modifying the last character.
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        payload = decode_access_token(tampered)
        assert payload == {}

    def test_decode_garbage_string_returns_empty_dict(self):
        payload = decode_access_token("not.a.valid.jwt.token")
        assert payload == {}

    def test_decode_empty_string_returns_empty_dict(self):
        payload = decode_access_token("")
        assert payload == {}

    def test_decode_token_with_multiple_claims(self):
        data = {"sub": "user99", "role": "admin", "email": "admin@example.com"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload["sub"] == "user99"
        assert payload["role"] == "admin"
        assert payload["email"] == "admin@example.com"
