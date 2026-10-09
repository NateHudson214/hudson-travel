from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import date, datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any, Literal

from fastapi import Body, FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, FiniteFloat, field_validator

from .advisor_contracts import (
    AdvisorProviderAuthenticationError,
    AdvisorProviderConfigurationError,
    AdvisorProviderHTTPError,
    AdvisorProviderModelUnavailableError,
    AdvisorProviderRateLimitError,
    AdvisorProviderResponseError,
    AdvisorProviderTransportError,
    GroundedAnswer,
    QueryParameter,
    QueryProposal,
)
from .advisor_query import (
    AdvisorQueryExecutionError,
    AdvisorQueryLimitError,
    AdvisorQueryRejectedError,
    AdvisorQueryResultError,
    ResultScalar,
    execute_read_only_query,
)
from .advisor_history import (
    AdvisorConversationNotFoundError,
    AdvisorPersistenceError,
    complete_advisor_run,
    fail_advisor_run,
    get_advisor_conversation,
    list_advisor_conversations,
    record_advisor_proposal,
    record_advisor_retrieval,
    start_advisor_run,
)
from .advisor_prompt import AdvisorPromptError, load_hotel_assistant_prompt
from .config import (
    get_geoapify_api_key,
    get_openai_api_key,
    get_openai_model,
    get_openrouter_api_key,
    get_openrouter_model,
)
from .database import (
    BookingNotFoundError,
    RelatedRecordNotFoundError,
    SavedHotelNotFoundError,
    cancel_booking_record,
    create_booking_record,
    delete_booking_record,
    delete_local_hotel_record,
    initialize_database,
    list_booking_records,
    list_saved_hotel_ids,
    list_saved_hotels_for_zip,
    list_user_records,
    save_local_hotel_record,
    search_trip_records,
)
from .geoapify import (
    GeoapifyConfigurationError,
    GeoapifyProviderError,
    ZipLocationNotFoundError,
    lookup_zip_location,
)
from .places import (
    GEOAPIFY_PLACES_RADIUS_METERS,
    GEOAPIFY_PLACES_RESULT_LIMIT,
    NearbyHotel,
    lookup_nearby_hotels,
)
from .openai_client import (
    TOTAL_COST_PLACEHOLDER,
    generate_grounded_answer_openai,
    propose_hotel_query_openai,
)


BACKEND_DIRECTORY = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = BACKEND_DIRECTORY / "data"
DEFAULT_DATABASE_PATH = BACKEND_DIRECTORY / "instance" / "hudson_travel.sqlite3"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    initialize_database(Path(application.state.database_path), DATA_DIRECTORY)
    yield


app = FastAPI(title="Hudson Travel API", lifespan=lifespan)
app.state.database_path = DEFAULT_DATABASE_PATH
app.state.today_provider = date.today
app.state.geoapify_key_provider = get_geoapify_api_key
app.state.openrouter_key_provider = get_openrouter_api_key
app.state.openrouter_model_provider = get_openrouter_model
app.state.openai_key_provider = get_openai_api_key
app.state.openai_model_provider = get_openai_model
app.state.zip_location_lookup = lookup_zip_location
app.state.nearby_hotels_lookup = lookup_nearby_hotels
app.state.advisor_query_executor = execute_read_only_query
app.state.advisor_prompt_provider = load_hotel_assistant_prompt
app.state.advisor_http_transport_provider = lambda: None
app.state.advisor_now_provider = lambda: datetime.now(timezone.utc)
advisor_history_context: ContextVar[list[dict[str, str]]] = ContextVar(
    "advisor_history_context", default=[]
)


async def propose_hotel_query_with_openai(question: str) -> QueryProposal:
    api_key = app.state.openai_key_provider()
    return await propose_hotel_query_openai(
        question,
        api_key_provider=lambda: api_key,
        model_provider=app.state.openai_model_provider,
        prompt_provider=app.state.advisor_prompt_provider,
        transport=(
            app.state.advisor_http_transport_provider()
            if api_key is not None
            else None
        ),
        conversation_history=advisor_history_context.get(),
    )


async def generate_grounded_answer_with_openai(
    question: str,
    proposed_sql: str,
    query_parameters: dict[str, QueryParameter],
    retrieved_records: list[dict[str, Any]],
) -> GroundedAnswer:
    api_key = app.state.openai_key_provider()
    return await generate_grounded_answer_openai(
        question,
        proposed_sql,
        query_parameters,
        retrieved_records,
        api_key_provider=lambda: api_key,
        model_provider=app.state.openai_model_provider,
        prompt_provider=app.state.advisor_prompt_provider,
        transport=(
            app.state.advisor_http_transport_provider()
            if api_key is not None
            else None
        ),
        conversation_history=advisor_history_context.get(),
    )


app.state.advisor_query_proposer = propose_hotel_query_with_openai
app.state.advisor_answer_generator = generate_grounded_answer_with_openai


class HealthResult(BaseModel):
    status: Literal["ok"]
    geoapify: Literal["key is configured", "key is not configured"]
    openrouter: Literal["key is configured", "key is not configured"]
    openrouter_model: str
    openai: Literal["key is configured", "key is not configured"]
    openai_model: str


class ZipLocationResult(BaseModel):
    postcode: str
    country_code: str
    latitude: float
    longitude: float
    locality: str | None = None


class NearbyHotelResult(BaseModel):
    place_id: str
    name: str | None
    formatted_address: str | None
    latitude: float
    longitude: float
    distance_meters: float | None


class NearbyHotelSearchResult(BaseModel):
    location: ZipLocationResult
    radius_meters: int
    result_limit: int
    hotels: list[NearbyHotelResult]


class DemoHotelNightResult(BaseModel):
    stay_date: str
    nightly_rate_cents: int
    rooms_available: int


class SavedHotelResult(NearbyHotelResult):
    nights: list[DemoHotelNightResult]


class SavedHotelSearchResult(BaseModel):
    searched_zip_code: str
    location: ZipLocationResult | None
    hotels: list[SavedHotelResult]


class SavedHotelIdsResult(BaseModel):
    place_ids: list[str]


class ProviderHotelCreate(BaseModel):
    place_id: str = Field(min_length=1)
    name: str | None = None
    formatted_address: str | None = None
    latitude: FiniteFloat = Field(ge=-90, le=90)
    longitude: FiniteFloat = Field(ge=-180, le=180)

    @field_validator("place_id")
    @classmethod
    def reject_blank_place_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("place_id must not be blank")
        return value


class SavedHotelCreate(BaseModel):
    zip_code: str
    location: ZipLocationResult
    hotel: ProviderHotelCreate


class SavedHotelCreateResult(BaseModel):
    searched_zip_code: str
    location: ZipLocationResult
    hotel: SavedHotelResult


class TripSearchResult(BaseModel):
    trip_id: str
    trip_name: str
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float
    check_in: str
    check_out: str


class UserResult(BaseModel):
    user_id: str
    display_name: str


class BookingResult(BaseModel):
    booking_id: str
    user_id: str
    display_name: str
    trip_id: str
    trip_name: str
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float
    check_in: str
    check_out: str
    booked_on: str
    status: Literal["confirmed", "cancelled"]


class BookingCreate(BaseModel):
    user_id: str
    trip_id: str


class BookingStatusUpdate(BaseModel):
    status: Literal["cancelled"]


class HotelAdvisorResult(BaseModel):
    status: Literal["answered", "no_matches", "insufficient_data"]
    question: str
    proposed_sql: str
    query_parameters: dict[str, QueryParameter]
    retrieved_records: list[dict[str, ResultScalar]]
    answer: str
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    run_id: str
    prompt_version: str


class AdvisorConversationSummary(BaseModel):
    conversation_id: str
    created_at: str
    updated_at: str
    message_count: int
    latest_message: str | None


class AdvisorMessageResult(BaseModel):
    message_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: str


class AdvisorCompletedRunResult(BaseModel):
    status: Literal["answered", "no_matches", "insufficient_data"]
    proposed_sql: str
    query_parameters: dict[str, QueryParameter]
    retrieved_records: list[dict[str, ResultScalar]]
    run_id: str
    prompt_version: str


class AdvisorConversationResult(BaseModel):
    conversation_id: str
    created_at: str
    updated_at: str
    messages: list[AdvisorMessageResult]
    latest_completed_run: AdvisorCompletedRunResult | None


def prepare_database() -> Path:
    return Path(app.state.database_path)


def booking_not_found(booking_id: str) -> HTTPException:
    return HTTPException(
        status_code=404, detail=f"Booking {booking_id} was not found."
    )


def local_hotel_storage_error() -> HTTPException:
    return HTTPException(
        status_code=500,
        detail="Local hotel storage is temporarily unavailable.",
    )


def hotel_advisor_provider_error() -> HTTPException:
    return HTTPException(
        status_code=502,
        detail="The hotel advisor service is temporarily unavailable.",
    )


def validate_advisor_request(payload: Any) -> tuple[str, str | None]:
    question = payload.get("question") if isinstance(payload, dict) else None
    if not isinstance(question, str):
        raise HTTPException(
            status_code=400,
            detail="Enter a hotel question of 500 characters or fewer.",
        )
    normalized_question = question.strip()
    if not normalized_question or len(normalized_question) > 500:
        raise HTTPException(
            status_code=400,
            detail="Enter a hotel question of 500 characters or fewer.",
        )
    conversation_id = payload.get("conversation_id")
    if conversation_id is not None and (
        not isinstance(conversation_id, str)
        or not conversation_id.startswith("C")
        or not conversation_id[1:].isdigit()
        or len(conversation_id) > 32
    ):
        raise HTTPException(
            status_code=400,
            detail="The conversation ID is invalid.",
        )
    return normalized_question, conversation_id


def advisor_timestamp() -> str:
    timestamp = app.state.advisor_now_provider()
    if not isinstance(timestamp, datetime):
        raise AdvisorPersistenceError("Advisor history is unavailable.")
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc).isoformat()


def fail_run_or_raise(
    run_id: str, *, category: str, message: str
) -> None:
    fail_advisor_run(
        prepare_database(),
        run_id,
        error_category=category,
        error_message=message,
        now=advisor_timestamp(),
    )


def advisor_storage_error() -> HTTPException:
    return HTTPException(
        status_code=500,
        detail="The hotel advisor history is temporarily unavailable.",
    )


def ensure_consistent_grounded_answer(
    grounded_answer: GroundedAnswer,
    retrieved_records: list[dict[str, ResultScalar]],
) -> GroundedAnswer:
    if (
        not isinstance(grounded_answer, GroundedAnswer)
        or (not retrieved_records and grounded_answer.status == "answered")
        or (retrieved_records and grounded_answer.status == "no_matches")
    ):
        raise AdvisorProviderResponseError(
            "The provider returned an inconsistent grounded answer."
        )

    retrieved_totals = {
        value
        for record in retrieved_records
        if (
            isinstance((value := record.get("total_cost_cents")), int)
            and not isinstance(value, bool)
            and value >= 0
        )
    }
    placeholder_count = grounded_answer.answer.count(TOTAL_COST_PLACEHOLDER)

    if grounded_answer.status != "answered" or not retrieved_totals:
        if grounded_answer.total_cost_cents is not None or placeholder_count:
            raise AdvisorProviderResponseError(
                "The provider returned an inconsistent grounded answer."
            )
        return grounded_answer

    if (
        grounded_answer.total_cost_cents not in retrieved_totals
        or placeholder_count != 1
        or "$" in grounded_answer.answer
    ):
        raise AdvisorProviderResponseError(
            "The provider returned an inconsistent grounded answer."
        )

    cents = grounded_answer.total_cost_cents
    formatted_total = f"${cents // 100}.{cents % 100:02d}"
    return GroundedAnswer(
        status=grounded_answer.status,
        answer=grounded_answer.answer.replace(
            TOTAL_COST_PLACEHOLDER, formatted_total
        ),
        total_cost_cents=cents,
    )


@app.get("/api/health", response_model=HealthResult)
async def health_check() -> HealthResult:
    geoapify_status = (
        "key is configured"
        if app.state.geoapify_key_provider() is not None
        else "key is not configured"
    )
    openrouter_status = (
        "key is configured"
        if app.state.openrouter_key_provider() is not None
        else "key is not configured"
    )
    openai_status = (
        "key is configured"
        if app.state.openai_key_provider() is not None
        else "key is not configured"
    )
    return HealthResult(
        status="ok",
        geoapify=geoapify_status,
        openrouter=openrouter_status,
        openrouter_model=app.state.openrouter_model_provider(),
        openai=openai_status,
        openai_model=app.state.openai_model_provider(),
    )


@app.post("/api/hotel-advisor", response_model=HotelAdvisorResult)
async def hotel_advisor(
    payload: Any = Body(default=None),
) -> HotelAdvisorResult:
    question, conversation_id = validate_advisor_request(payload)

    try:
        try:
            prompt_version = app.state.advisor_prompt_provider().version
        except AdvisorPromptError:
            prompt_version = "unavailable"
        run = start_advisor_run(
            prepare_database(),
            question=question,
            conversation_id=conversation_id,
            prompt_version=prompt_version,
            now=advisor_timestamp(),
        )
    except AdvisorConversationNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="The advisor conversation was not found.",
        ) from error
    except AdvisorPersistenceError as error:
        raise advisor_storage_error() from error

    history_token = advisor_history_context.set(run.history)

    try:
        try:
            proposal = await app.state.advisor_query_proposer(question)
            record_advisor_proposal(
                prepare_database(),
                run.run_id,
                proposed_sql=proposal.sql,
                query_parameters=proposal.parameters,
            )
        except AdvisorProviderConfigurationError as error:
            fail_run_or_raise(
                run.run_id,
                category="provider_configuration",
                message="The hotel advisor is not configured.",
            )
            raise HTTPException(
                status_code=503,
                detail="The hotel advisor is not configured.",
            ) from error
        except AdvisorProviderRateLimitError as error:
            fail_run_or_raise(
                run.run_id,
                category="provider_rate_limit",
                message="The hotel advisor rate limit was reached.",
            )
            raise HTTPException(
                status_code=429,
                detail="The hotel advisor rate limit was reached. Try again later.",
            ) from error
        except (
            AdvisorProviderAuthenticationError,
            AdvisorProviderModelUnavailableError,
            AdvisorProviderTransportError,
            AdvisorProviderHTTPError,
            AdvisorProviderResponseError,
        ) as error:
            fail_run_or_raise(
                run.run_id,
                category="provider_failure",
                message="The hotel advisor service is temporarily unavailable.",
            )
            raise hotel_advisor_provider_error() from error

        try:
            records = app.state.advisor_query_executor(
                Path(app.state.database_path), proposal
            )
            record_advisor_retrieval(
                prepare_database(),
                run.run_id,
                executed_sql=proposal.sql,
                query_parameters=proposal.parameters,
                retrieved_records=records,
            )
        except (AdvisorQueryRejectedError, AdvisorQueryLimitError) as error:
            fail_run_or_raise(
                run.run_id,
                category="unsafe_query",
                message="The proposed hotel query was rejected for safety.",
            )
            raise HTTPException(
                status_code=422,
                detail="The proposed hotel query was rejected for safety.",
            ) from error
        except (AdvisorQueryExecutionError, AdvisorQueryResultError) as error:
            fail_run_or_raise(
                run.run_id,
                category="retrieval_failure",
                message="The local hotel advisor data could not be retrieved.",
            )
            raise HTTPException(
                status_code=500,
                detail="The local hotel advisor data could not be retrieved.",
            ) from error

        try:
            grounded_answer = await app.state.advisor_answer_generator(
                question,
                proposal.sql,
                proposal.parameters,
                records,
            )
            grounded_answer = ensure_consistent_grounded_answer(
                grounded_answer, records
            )
        except AdvisorProviderConfigurationError as error:
            fail_run_or_raise(
                run.run_id,
                category="provider_configuration",
                message="The hotel advisor is not configured.",
            )
            raise HTTPException(
                status_code=503,
                detail="The hotel advisor is not configured.",
            ) from error
        except AdvisorProviderRateLimitError as error:
            fail_run_or_raise(
                run.run_id,
                category="provider_rate_limit",
                message="The hotel advisor rate limit was reached.",
            )
            raise HTTPException(
                status_code=429,
                detail="The hotel advisor rate limit was reached. Try again later.",
            ) from error
        except (
            AdvisorProviderAuthenticationError,
            AdvisorProviderModelUnavailableError,
            AdvisorProviderTransportError,
            AdvisorProviderHTTPError,
            AdvisorProviderResponseError,
        ) as error:
            fail_run_or_raise(
                run.run_id,
                category="provider_failure",
                message="The hotel advisor service is temporarily unavailable.",
            )
            raise hotel_advisor_provider_error() from error

        try:
            assistant_message_id = complete_advisor_run(
                prepare_database(),
                run.run_id,
                answer=grounded_answer.answer,
                result_status=grounded_answer.status,
                now=advisor_timestamp(),
            )
        except AdvisorPersistenceError as error:
            raise advisor_storage_error() from error

        return HotelAdvisorResult(
            status=grounded_answer.status,
            question=question,
            proposed_sql=proposal.sql,
            query_parameters=proposal.parameters,
            retrieved_records=records,
            answer=grounded_answer.answer,
            conversation_id=run.conversation_id,
            user_message_id=run.user_message_id,
            assistant_message_id=assistant_message_id,
            run_id=run.run_id,
            prompt_version=prompt_version,
        )
    except AdvisorPersistenceError as error:
        raise advisor_storage_error() from error
    finally:
        advisor_history_context.reset(history_token)


@app.get(
    "/api/advisor/conversations",
    response_model=list[AdvisorConversationSummary],
)
async def advisor_conversations() -> list[AdvisorConversationSummary]:
    try:
        return [
            AdvisorConversationSummary(**record)
            for record in list_advisor_conversations(prepare_database())
        ]
    except AdvisorPersistenceError as error:
        raise advisor_storage_error() from error


@app.get(
    "/api/advisor/conversations/{conversation_id}",
    response_model=AdvisorConversationResult,
)
async def advisor_conversation(
    conversation_id: str,
) -> AdvisorConversationResult:
    try:
        return AdvisorConversationResult(
            **get_advisor_conversation(prepare_database(), conversation_id)
        )
    except AdvisorConversationNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="The advisor conversation was not found.",
        ) from error
    except AdvisorPersistenceError as error:
        raise advisor_storage_error() from error
async def resolve_zip_location(postcode: str) -> ZipLocationResult:
    try:
        location = await app.state.zip_location_lookup(postcode)
    except GeoapifyConfigurationError as error:
        raise HTTPException(
            status_code=503, detail="Geoapify is not configured."
        ) from error
    except ZipLocationNotFoundError as error:
        raise HTTPException(
            status_code=404, detail=f"ZIP {postcode} could not be resolved."
        ) from error
    except GeoapifyProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="The location service is temporarily unavailable.",
        ) from error

    return ZipLocationResult(
        postcode=location.postcode,
        country_code=location.country_code,
        latitude=location.latitude,
        longitude=location.longitude,
        locality=location.locality,
    )


def normalize_zip_code(zip_code: str | None) -> str:
    normalized_zip_code = zip_code.strip() if zip_code is not None else ""
    if len(normalized_zip_code) != 5 or not all(
        "0" <= character <= "9" for character in normalized_zip_code
    ):
        raise HTTPException(
            status_code=400,
            detail="Enter a five-digit U.S. ZIP code.",
        )
    return normalized_zip_code


@app.get("/api/demo/zip-location", response_model=ZipLocationResult)
async def demo_zip_location() -> ZipLocationResult:
    return await resolve_zip_location("16802")


@app.get("/api/zip-location", response_model=ZipLocationResult)
async def zip_location(
    zip_code: str | None = Query(default=None),
) -> ZipLocationResult:
    return await resolve_zip_location(normalize_zip_code(zip_code))


@app.get("/api/hotels/nearby", response_model=NearbyHotelSearchResult)
async def nearby_hotels(
    zip_code: str | None = Query(default=None),
) -> NearbyHotelSearchResult:
    normalized_zip_code = normalize_zip_code(zip_code)
    location = await resolve_zip_location(normalized_zip_code)

    try:
        hotels: list[NearbyHotel] = await app.state.nearby_hotels_lookup(
            location.latitude, location.longitude
        )
    except GeoapifyConfigurationError as error:
        raise HTTPException(
            status_code=503, detail="Geoapify is not configured."
        ) from error
    except GeoapifyProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="The nearby hotel service is temporarily unavailable.",
        ) from error

    return NearbyHotelSearchResult(
        location=location,
        radius_meters=GEOAPIFY_PLACES_RADIUS_METERS,
        result_limit=GEOAPIFY_PLACES_RESULT_LIMIT,
        hotels=[NearbyHotelResult(**hotel.__dict__) for hotel in hotels],
    )


@app.get("/api/saved-hotels/ids", response_model=SavedHotelIdsResult)
async def saved_hotel_ids() -> SavedHotelIdsResult:
    try:
        place_ids = list_saved_hotel_ids(prepare_database())
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return SavedHotelIdsResult(place_ids=place_ids)


@app.get("/api/saved-hotels", response_model=SavedHotelSearchResult)
async def saved_hotels(
    zip_code: str | None = Query(default=None),
) -> SavedHotelSearchResult:
    normalized_zip_code = normalize_zip_code(zip_code)
    try:
        record = list_saved_hotels_for_zip(
            prepare_database(), normalized_zip_code
        )
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return SavedHotelSearchResult(**record)


@app.post(
    "/api/saved-hotels",
    response_model=SavedHotelCreateResult,
    status_code=status.HTTP_201_CREATED,
)
async def save_hotel(payload: SavedHotelCreate) -> SavedHotelCreateResult:
    normalized_zip_code = normalize_zip_code(payload.zip_code)
    normalized_postcode = normalize_zip_code(payload.location.postcode)
    if payload.location.country_code.casefold() != "us":
        raise HTTPException(
            status_code=400,
            detail="Saved hotel location must be a U.S. ZIP code.",
        )
    try:
        record = save_local_hotel_record(
            prepare_database(),
            place_id=payload.hotel.place_id,
            name=payload.hotel.name,
            formatted_address=payload.hotel.formatted_address,
            latitude=payload.hotel.latitude,
            longitude=payload.hotel.longitude,
            zip_code=normalized_zip_code,
            postcode=normalized_postcode,
            country_code=payload.location.country_code,
            search_latitude=payload.location.latitude,
            search_longitude=payload.location.longitude,
            locality=payload.location.locality,
        )
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return SavedHotelCreateResult(**record)


@app.delete(
    "/api/saved-hotels/{hotel_id:path}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_saved_hotel(hotel_id: str) -> Response:
    try:
        delete_local_hotel_record(prepare_database(), hotel_id)
    except SavedHotelNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Saved hotel was not found.",
        ) from error
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/trips", response_model=list[TripSearchResult])
async def search_trips(
    hotel_name: str | None = Query(default=None),
) -> list[TripSearchResult]:
    normalized_hotel_name = hotel_name.strip() if hotel_name is not None else ""
    if not normalized_hotel_name:
        raise HTTPException(status_code=400, detail="Enter a hotel name to search.")

    return [
        TripSearchResult(**record)
        for record in search_trip_records(prepare_database(), normalized_hotel_name)
    ]


@app.get("/api/users", response_model=list[UserResult])
async def list_users() -> list[UserResult]:
    return [UserResult(**record) for record in list_user_records(prepare_database())]


@app.get("/api/bookings", response_model=list[BookingResult])
async def list_bookings() -> list[BookingResult]:
    return [
        BookingResult(**record)
        for record in list_booking_records(prepare_database())
    ]


@app.post(
    "/api/bookings",
    response_model=BookingResult,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(booking: BookingCreate) -> BookingResult:
    database_path = prepare_database()
    try:
        record = create_booking_record(
            database_path,
            booking.user_id,
            booking.trip_id,
            app.state.today_provider().isoformat(),
        )
    except RelatedRecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return BookingResult(**record)


@app.patch("/api/bookings/{booking_id}", response_model=BookingResult)
async def cancel_booking(
    booking_id: str, booking: BookingStatusUpdate
) -> BookingResult:
    database_path = prepare_database()
    try:
        record = cancel_booking_record(database_path, booking_id)
    except BookingNotFoundError as error:
        raise booking_not_found(booking_id) from error
    return BookingResult(**record)


@app.delete(
    "/api/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_booking(booking_id: str) -> Response:
    database_path = prepare_database()
    try:
        delete_booking_record(database_path, booking_id)
    except BookingNotFoundError as error:
        raise booking_not_found(booking_id) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
