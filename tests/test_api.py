"""
Тесты API эндпоинтов.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.constants import UserRole
from app.core.security import create_access_token
from app.main import app


@pytest.fixture
def auth_headers():
    """Создать заголовки авторизации для тестов."""
    def _make_headers(user_id: int = 1, role: UserRole = UserRole.TEACHER):
        token = create_access_token({"sub": user_id, "role": role})
        return {"Authorization": f"Bearer {token}"}
    return _make_headers


class TestHealthEndpoint:
    """Тесты эндпоинта здоровья."""

    @pytest.mark.asyncio
    async def test_ping(self):
        """Тест ping эндпоинта."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/ping")

        assert response.status_code == 200
        assert response.json() == {"ping": "pong"}


class TestAuthEndpoints:
    """Тесты эндпоинтов аутентификации."""

    @pytest.mark.asyncio
    async def test_register_validation(self):
        """Тест валидации при регистрации."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Невалидный email
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "invalid-email",
                    "password": "password123",
                    "role": "teacher",
                },
            )

        assert response.status_code == 422  # Validation error


class TestProtectedEndpoints:
    """Тесты защищённых эндпоинтов."""

    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Тест доступа без авторизации."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/users/")

        assert response.status_code == 401  # Unauthorized (no auth header)

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Тест с невалидным токеном."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/users/",
                headers={"Authorization": "Bearer invalid_token"},
            )

        assert response.status_code == 401


class TestOpenAPIDocumentation:
    """Тесты OpenAPI документации."""

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self):
        """Тест доступности OpenAPI схемы."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    @pytest.mark.asyncio
    async def test_docs_available(self):
        """Тест доступности Swagger UI."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/docs")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_redoc_available(self):
        """Тест доступности ReDoc."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/redoc")

        assert response.status_code == 200
