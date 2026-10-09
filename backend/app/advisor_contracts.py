from dataclasses import dataclass
from typing import Literal, TypeAlias


QueryParameter: TypeAlias = str | int | float | None
AnswerStatus: TypeAlias = Literal[
    "answered", "no_matches", "insufficient_data"
]


@dataclass(frozen=True)
class QueryProposal:
    sql: str
    parameters: dict[str, QueryParameter]


@dataclass(frozen=True)
class GroundedAnswer:
    status: AnswerStatus
    answer: str
    total_cost_cents: int | None = None


class AdvisorProviderConfigurationError(Exception):
    """Raised when the selected backend provider is not configured."""


class AdvisorProviderAuthenticationError(Exception):
    """Raised when the selected provider rejects backend authentication."""


class AdvisorProviderRateLimitError(Exception):
    """Raised when the provider rejects a request for quota or rate limits."""


class AdvisorProviderModelUnavailableError(Exception):
    """Raised when the configured provider model is unavailable or invalid."""


class AdvisorProviderTransportError(Exception):
    """Raised when a timeout or network failure prevents a provider response."""


class AdvisorProviderHTTPError(Exception):
    """Raised for other unsuccessful provider HTTP responses."""


class AdvisorProviderResponseError(Exception):
    """Raised when a provider response is malformed, incomplete, or unsafe."""
