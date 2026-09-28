"""Unit tests for the Menu agent orchestrating LLM generation, validation, and fallback."""

import pytest

from app.agents.menu import build_menu_prompt, run_menu_agent
from app.agents.menu_validator import validate_menu
from app.data.synthetic_generator import generate_clusters, generate_providers
from app.llm.base import FakeProvider, NoneProvider
from app.models.domain import MenuPlan


@pytest.fixture(scope="module")
def sample_data():
    providers = generate_providers(seed=42)
    clusters = generate_clusters(seed=42)
    provider = providers[0]
    cluster = clusters[0]
    return provider, cluster


def _build_valid_canned_menu(provider, cluster) -> MenuPlan:
    """Construct a canned MenuPlan that satisfies all domain rules."""
    from app.agents.menu_fallback import generate_fallback_menu

    menu = generate_fallback_menu(provider, cluster)
    menu.source = "llm"
    return menu


def test_build_menu_prompt(sample_data):
    provider, cluster = sample_data
    prompt = build_menu_prompt(provider, cluster)

    # Prompt contains dish IDs
    assert provider.dishes[0].id in prompt
    # Prompt contains cluster town/area
    assert cluster.town in prompt
    assert cluster.area in prompt
    # Prompt contains constraints
    assert "No Slot Repeats" in prompt
    assert "Main Item Variety" in prompt
    assert "Do NOT make any medical" in prompt


@pytest.mark.asyncio
async def test_menu_agent_valid_llm_output_accepted(sample_data):
    provider, cluster = sample_data
    valid_menu = _build_valid_canned_menu(provider, cluster)

    fake_llm = FakeProvider(canned_response=valid_menu, mode="valid")
    result = await run_menu_agent(provider, cluster, llm_provider=fake_llm)

    assert result.source == "llm"
    assert result.provider_id == provider.id
    assert result.cluster_id == cluster.id
    assert len(result.days) == 7
    assert fake_llm.call_count == 1
    # Verify resulting menu passes validation
    assert validate_menu(result, provider, cluster) == []


@pytest.mark.asyncio
async def test_menu_agent_invalid_llm_output_falls_back(sample_data):
    provider, cluster = sample_data

    # FakeProvider in "invalid" mode triggers schema validation failure
    fake_llm = FakeProvider(mode="invalid")
    result = await run_menu_agent(provider, cluster, llm_provider=fake_llm, max_retries=1)

    assert result.source == "fallback"
    assert result.provider_id == provider.id
    assert result.cluster_id == cluster.id
    assert len(result.days) == 7
    # Initial attempt + 1 retry = 2 calls
    assert fake_llm.call_count == 2
    assert validate_menu(result, provider, cluster) == []


@pytest.mark.asyncio
async def test_menu_agent_constraint_violating_llm_output_falls_back(sample_data):
    provider, cluster = sample_data
    violating_menu = _build_valid_canned_menu(provider, cluster)
    # Violate constraint: make lunch repeat on Day 2
    violating_menu.days[1].lunch.dish_id = violating_menu.days[0].lunch.dish_id

    fake_llm = FakeProvider(canned_response=violating_menu, mode="valid")
    result = await run_menu_agent(provider, cluster, llm_provider=fake_llm, max_retries=1)

    assert result.source == "fallback"
    assert result.provider_id == provider.id
    assert len(result.days) == 7
    assert fake_llm.call_count == 2  # Attempted retry
    assert validate_menu(result, provider, cluster) == []


@pytest.mark.asyncio
async def test_menu_agent_timeout_falls_back(sample_data):
    provider, cluster = sample_data

    fake_llm = FakeProvider(mode="timeout")
    result = await run_menu_agent(provider, cluster, llm_provider=fake_llm, max_retries=1)

    assert result.source == "fallback"
    assert result.provider_id == provider.id
    assert fake_llm.call_count == 2
    assert validate_menu(result, provider, cluster) == []


@pytest.mark.asyncio
async def test_menu_agent_none_provider_falls_back(sample_data):
    provider, cluster = sample_data

    result = await run_menu_agent(provider, cluster, llm_provider=NoneProvider())

    assert result.source == "fallback"
    assert result.provider_id == provider.id
    assert len(result.days) == 7
    assert validate_menu(result, provider, cluster) == []


@pytest.mark.asyncio
async def test_menu_agent_default_provider_falls_back(sample_data):
    provider, cluster = sample_data

    # llm_provider is None -> defaults to NoneProvider
    result = await run_menu_agent(provider, cluster, llm_provider=None)

    assert result.source == "fallback"
    assert result.provider_id == provider.id
    assert validate_menu(result, provider, cluster) == []


@pytest.mark.asyncio
async def test_menu_agent_retry_eventual_success(sample_data):
    provider, cluster = sample_data
    valid_menu = _build_valid_canned_menu(provider, cluster)

    # 1 failure before succeeding on the second call
    fake_llm = FakeProvider(
        canned_response=valid_menu,
        mode="valid",
        failures_before_success=1,
    )

    result = await run_menu_agent(provider, cluster, llm_provider=fake_llm, max_retries=2)

    assert result.source == "llm"
    assert fake_llm.call_count == 2
    assert validate_menu(result, provider, cluster) == []
