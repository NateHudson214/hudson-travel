from backend.app.advisor_contracts import (
    AdvisorProviderAuthenticationError,
    AdvisorProviderConfigurationError,
    AdvisorProviderHTTPError,
    AdvisorProviderModelUnavailableError,
    AdvisorProviderRateLimitError,
    AdvisorProviderResponseError,
    AdvisorProviderTransportError,
    GroundedAnswer,
    QueryProposal,
)
from backend.app.openrouter import (
    OpenRouterAuthenticationError,
    OpenRouterConfigurationError,
    OpenRouterModelUnavailableError,
    OpenRouterProviderError,
    OpenRouterRateLimitError,
    OpenRouterResponseError,
    OpenRouterTransportError,
)


def test_shared_advisor_value_contracts_are_provider_neutral() -> None:
    proposal = QueryProposal(
        sql="SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id LIMIT 1",
        parameters={"id": "provider-hotel-1"},
    )
    answer = GroundedAnswer(
        status="answered",
        answer="The saved simulated data supports this result.",
    )

    assert proposal.parameters == {"id": "provider-hotel-1"}
    assert answer.status == "answered"
    assert answer.total_cost_cents is None


def test_existing_openrouter_errors_preserve_provider_neutral_categories() -> None:
    mappings = [
        (OpenRouterConfigurationError, AdvisorProviderConfigurationError),
        (OpenRouterAuthenticationError, AdvisorProviderAuthenticationError),
        (OpenRouterRateLimitError, AdvisorProviderRateLimitError),
        (OpenRouterModelUnavailableError, AdvisorProviderModelUnavailableError),
        (OpenRouterTransportError, AdvisorProviderTransportError),
        (OpenRouterProviderError, AdvisorProviderHTTPError),
        (OpenRouterResponseError, AdvisorProviderResponseError),
    ]

    for provider_error, shared_error in mappings:
        assert issubclass(provider_error, shared_error)
