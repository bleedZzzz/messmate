"""API integration and unit tests for FastAPI REST endpoints (Milestone M6).

Tests required per PROMPTS.md:
- Every endpoint: success and validation-error cases.
- Onboarding without consent is rejected; a pending provider does not appear in match results.
- Rate limit returns 429 after the threshold.
- /optimize works end to end with LLM_PROVIDER=none.
- Standardized error schema {"error": {"code", "message"}}.
- Request-ID header propagation.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db, get_llm
from app.api.middleware import InMemoryRateLimiter, default_rate_limiter
from app.data.seed import seed_database
from app.db.base import Base
from app.llm.base import NoneProvider
from app.main import create_app


@pytest.fixture(scope="module")
def test_db_factory():
    """Create in-memory SQLite database pre-seeded with synthetic test data."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with session_factory() as session:
        seed_database(session, seed=42)
    return session_factory


@pytest.fixture
async def client(test_db_factory) -> AsyncGenerator[AsyncClient, None]:
    """Test client configured with overridden DB and LLM dependencies."""
    test_app = create_app()

    def override_get_db():
        with test_db_factory() as session:
            yield session

    def override_get_llm():
        return NoneProvider()

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_llm] = override_get_llm

    # Reset rate limiter before test
    default_rate_limiter.reset()

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# 1. Health & Infrastructure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """GET /api/v1/health returns 200 ok and sets X-Request-ID."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_request_id_propagation(client: AsyncClient):
    """X-Request-ID header passed by client is preserved in response."""
    custom_id = "test-request-uuid-12345"
    response = await client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


# ---------------------------------------------------------------------------
# 2. Areas endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_areas_success(client: AsyncClient):
    """GET /api/v1/areas returns list of localities and distinct towns."""
    response = await client.get("/api/v1/areas")
    assert response.status_code == 200
    data = response.json()
    assert "areas" in data
    assert "towns" in data
    assert len(data["areas"]) > 0
    assert len(data["towns"]) > 0

    first_area = data["areas"][0]
    assert "id" in first_area
    assert "town" in first_area
    assert "area" in first_area
    assert "cluster_id" in first_area


# ---------------------------------------------------------------------------
# 3. Match endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_match_endpoint_success(client: AsyncClient):
    """POST /api/v1/match scores and ranks providers against matched cluster."""
    payload = {
        "area": "College Para",
        "radius_km": 10.0,
        "top_n": 3,
    }
    response = await client.post("/api/v1/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "cluster" in data
    assert "matches" in data
    assert len(data["matches"]) > 0
    assert data["matches"][0]["score"] > 0


@pytest.mark.asyncio
async def test_match_endpoint_validation_error(client: AsyncClient):
    """POST /api/v1/match with negative radius returns 422 with standardized error."""
    payload = {
        "area": "College Para",
        "radius_km": -5.0,  # Invalid: must be gt 0
    }
    response = await client.post("/api/v1/match", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "radius_km" in data["error"]["message"]


@pytest.mark.asyncio
async def test_match_endpoint_not_found(client: AsyncClient):
    """POST /api/v1/match with non-existent locality returns 404."""
    payload = {"area": "CompletelyUnknownLocality12345"}
    response = await client.post("/api/v1/match", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# 4. Provider Detail endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_provider_details_success(client: AsyncClient):
    """GET /api/v1/providers/{id} returns provider profile with dishes."""
    # Find a valid provider ID via match
    match_resp = await client.post("/api/v1/match", json={"area": "College Para"})
    provider_id = match_resp.json()["matches"][0]["provider_id"]

    response = await client.get(f"/api/v1/providers/{provider_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == provider_id
    assert "dishes" in data
    assert len(data["dishes"]) > 0


@pytest.mark.asyncio
async def test_get_provider_details_not_found(client: AsyncClient):
    """GET /api/v1/providers/{id} with invalid ID returns 404 error envelope."""
    response = await client.get("/api/v1/providers/non-existent-provider-id")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# 5. Menu endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_menu_endpoint_success(client: AsyncClient):
    """POST /api/v1/menu returns a valid 7-day meal plan."""
    match_resp = await client.post("/api/v1/match", json={"area": "College Para"})
    match_data = match_resp.json()
    cluster_id = match_data["cluster"]["id"]
    provider_id = match_data["matches"][0]["provider_id"]

    payload = {
        "provider_id": provider_id,
        "cluster_id": cluster_id,
    }
    response = await client.post("/api/v1/menu", json=payload)
    assert response.status_code == 200
    menu = response.json()
    assert menu["provider_id"] == provider_id
    assert menu["cluster_id"] == cluster_id
    assert len(menu["days"]) == 7


@pytest.mark.asyncio
async def test_menu_endpoint_not_found(client: AsyncClient):
    """POST /api/v1/menu with missing provider returns 404."""
    payload = {
        "provider_id": "non-existent-p999",
        "cluster_id": "some-cluster-id",
    }
    response = await client.post("/api/v1/menu", json=payload)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_menu_endpoint_validation_error(client: AsyncClient):
    """POST /api/v1/menu with missing fields returns 422."""
    response = await client.post("/api/v1/menu", json={})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# 6. Negotiate endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_negotiate_endpoint_success(client: AsyncClient):
    """POST /api/v1/negotiate returns negotiation simulation result."""
    match_resp = await client.post("/api/v1/match", json={"area": "College Para"})
    match_data = match_resp.json()
    cluster_id = match_data["cluster"]["id"]
    provider_id = match_data["matches"][0]["provider_id"]

    payload = {
        "provider_id": provider_id,
        "cluster_id": cluster_id,
        "max_rounds": 5,
    }
    response = await client.post("/api/v1/negotiate", json=payload)
    assert response.status_code == 200
    neg = response.json()
    assert neg["status"] in ("deal", "compromise", "no_deal")
    assert "rounds" in neg
    assert len(neg["rounds"]) > 0


@pytest.mark.asyncio
async def test_negotiate_endpoint_validation_error(client: AsyncClient):
    """POST /api/v1/negotiate with invalid max_rounds returns 422."""
    payload = {
        "provider_id": "p001",
        "cluster_id": "c001",
        "max_rounds": 50,  # Invalid: max is 10
    }
    response = await client.post("/api/v1/negotiate", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# 7. Optimize endpoint (Full Pipeline)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_optimize_endpoint_success_llm_none(client: AsyncClient):
    """POST /api/v1/optimize works end-to-end with LLM_PROVIDER=none."""
    payload = {
        "area": "College Para",
        "radius_km": 10.0,
        "top_n": 3,
    }
    response = await client.post("/api/v1/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["cluster"] is not None
    assert len(data["matches"]) > 0
    assert data["top_provider"] is not None
    assert data["menu"] is not None
    assert data["menu"]["source"] == "fallback"
    assert data["negotiation"] is not None
    assert len(data["trace"]) == 4
    assert data["errors"] == []


@pytest.mark.asyncio
async def test_optimize_endpoint_validation_error(client: AsyncClient):
    """POST /api/v1/optimize with invalid radius returns 422."""
    payload = {"radius_km": 0.0}
    response = await client.post("/api/v1/optimize", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# 8. Provider Onboarding & Consent Checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_provider_onboarding_without_consent_rejected(client: AsyncClient):
    """Onboarding without explicit consent is rejected with 422 validation error."""
    payload = {
        "name": "Maa Annapurna Tiffin",
        "town": "Uluberia",
        "area": "College Para",
        "lat": 22.47,
        "lon": 88.11,
        "cuisines": ["bengali"],
        "diet_types": ["veg", "non_veg"],
        "capacity_total": 50,
        "capacity_available": 30,
        "list_price_monthly": 2800.0,
        "cost_per_meal": 35.0,
        "min_margin": 0.15,
        "flexibility": 0.20,
        "phone": "+91 98300 12345",
        "consent_given": False,  # Missing consent!
    }
    response = await client.post("/api/v1/providers", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "consent" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_provider_onboarding_pending_excluded_from_matches(client: AsyncClient):
    """Pending providers are saved with 'pending' status and excluded from match results."""
    # Register new provider with consent
    payload = {
        "name": "Shree Krishna Veg Mess",
        "town": "Uluberia",
        "area": "College Para",
        "lat": 22.4722,
        "lon": 88.1125,
        "cuisines": ["north_indian"],
        "diet_types": ["veg"],
        "capacity_total": 40,
        "capacity_available": 25,
        "list_price_monthly": 2400.0,
        "cost_per_meal": 30.0,
        "min_margin": 0.10,
        "flexibility": 0.25,
        "phone": "+91 98311 54321",
        "consent_given": True,
        "dishes": [
            {
                "name": "Dal Makhani with Roti",
                "slot": "lunch",
                "diet": "veg",
                "cuisine": "north_indian",
                "main_item": "dal",
                "cost_tier": 2,
            }
        ],
    }
    create_resp = await client.post("/api/v1/providers", json=payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["status"] == "pending"
    new_provider_id = created_data["id"]

    # Verify provider is in database with status 'pending'
    detail_resp = await client.get(f"/api/v1/providers/{new_provider_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["status"] == "pending"

    # Query match endpoint for the same area
    match_resp = await client.post(
        "/api/v1/match",
        json={"area": "College Para", "top_n": 50},
    )
    assert match_resp.status_code == 200
    matched_ids = [m["provider_id"] for m in match_resp.json()["matches"]]

    # Pending provider MUST NOT appear in active match results!
    assert new_provider_id not in matched_ids


# ---------------------------------------------------------------------------
# 9. Provider Contact endpoint (WhatsApp link)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_provider_contact_endpoint_success(client: AsyncClient):
    """GET /api/v1/providers/{id}/contact returns wa.me URL with clean digits."""
    match_resp = await client.post("/api/v1/match", json={"area": "College Para"})
    provider_id = match_resp.json()["matches"][0]["provider_id"]

    response = await client.get(f"/api/v1/providers/{provider_id}/contact")
    assert response.status_code == 200
    data = response.json()
    assert data["provider_id"] == provider_id
    assert "https://wa.me/" in data["whatsapp_url"]
    assert "?text=" in data["whatsapp_url"]


@pytest.mark.asyncio
async def test_provider_contact_endpoint_not_found(client: AsyncClient):
    """GET /api/v1/providers/{id}/contact with unknown provider returns 404."""
    response = await client.get("/api/v1/providers/unknown-p999/contact")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# 10. Rate Limiting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rate_limiter_returns_429_after_threshold():
    """Rate limiter returns 429 when client exceeds requests per minute threshold."""
    limiter = InMemoryRateLimiter(requests_per_minute=3)
    client_ip = "192.168.1.100"

    assert limiter.check(client_ip) is True  # 1st
    assert limiter.check(client_ip) is True  # 2nd
    assert limiter.check(client_ip) is True  # 3rd
    assert limiter.check(client_ip) is False  # 4th exceeds threshold!


@pytest.mark.asyncio
async def test_rate_limit_route_rejection(client: AsyncClient):
    """Route with depleted rate limiter raises 429 with Retry-After header."""
    test_ip = "198.51.100.1"
    headers = {"X-Forwarded-For": test_ip}

    # Exhaust default limiter for test_ip
    for _ in range(65):
        default_rate_limiter.check(test_ip)

    # Now make request through test client to a rate-limited route
    response = await client.get("/api/v1/areas", headers=headers)
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "Retry-After" in response.headers

    # Reset limiter for other tests
    default_rate_limiter.reset()
