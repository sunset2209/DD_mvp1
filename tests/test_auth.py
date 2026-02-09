"""
Тесты аутентификации и безопасности.
"""

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Тесты хеширования паролей."""

    def test_hash_password(self):
        """Тест хеширования пароля."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """Тест верификации правильного пароля."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Тест верификации неправильного пароля."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False


class TestJWT:
    """Тесты JWT токенов."""

    def test_create_access_token(self):
        """Тест создания access токена."""
        data = {"sub": 1, "role": "student"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Тест создания refresh токена."""
        data = {"sub": 1, "role": "student"}
        token = create_refresh_token(data)

        assert token is not None
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Тест декодирования валидного токена."""
        data = {"sub": 1, "role": "teacher"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "1"  # sub конвертируется в строку
        assert decoded["role"] == "teacher"
        assert decoded["type"] == "access"

    def test_decode_invalid_token(self):
        """Тест декодирования невалидного токена."""
        decoded = decode_token("invalid_token")

        assert decoded is None
