"""Isolated skills APIs; mocks default, live dispatch requires host and UI opt-in."""

from datetime import timezone
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from .sessions import (
    InvalidCursor,
    SessionConflict,
    SessionNotFound,
    SkillsStorageError,
    open_sessions,
)


router = APIRouter(prefix="/api/skills", tags=["Skills sessions"])
Milliseconds = Annotated[int, Field(strict=True, ge=0, le=2**53-1)]


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DisplaySettings(StrictBody):
    simpler_view: Annotated[bool, Field(strict=True)] = False
    motion_mode: Literal["system", "static", "gentle"] = "system"


class CreateSession(StrictBody):
    history_epoch: Milliseconds = 0
    session_id: UUID
    display_settings: DisplaySettings = Field(default_factory=DisplaySettings)


class SessionSnapshot(StrictBody):
    active_ms: Milliseconds
    pause_ms: Milliseconds
    support_ms: Milliseconds
    setup_ms: Milliseconds
    cycles_completed: Annotated[int, Field(strict=True, ge=0, le=6)]
    phase: Literal["inhale", "exhale"]
    phase_remaining_ms: Annotated[int, Field(strict=True, ge=0, le=6000)]


class SessionEvent(StrictBody):
    history_epoch: Milliseconds = 0
    event_id: UUID
    sequence: Annotated[int, Field(strict=True, ge=1, le=2**53-1)]
    expected_revision: Milliseconds
    kind: Literal[
        "start", "checkpoint", "pause", "resume", "support_open", "support_close",
        "stop", "complete", "interrupt",
    ]
    snapshot: SessionSnapshot
    reason: Literal["user", "hidden", "timing"] | None = None


def storage(request: Request):
    try:
        with open_sessions(
            Path(request.app.state.skills_database_path),
            Path(request.app.state.database_path),
        ) as store:
            yield store
    except SessionNotFound:
        raise HTTPException(404, "Skills session not found.") from None
    except SessionConflict as error:
        raise HTTPException(409, str(error)) from None
    except InvalidCursor:
        raise HTTPException(400, "Invalid skills history cursor.") from None
    except SkillsStorageError:
        raise HTTPException(503, "Skills session storage is unavailable.") from None


def timestamp(request):
    return request.app.state.skills_now_provider().astimezone(timezone.utc).isoformat(
        timespec="microseconds",
    )


@router.post("/sessions", status_code=201)
def create_session(body: CreateSession, request: Request, response: Response,
                   store=Depends(storage)):
    session, replayed = store.create(
        str(body.session_id), body.display_settings.model_dump(), timestamp(request), body.history_epoch,
    )
    response.status_code = 200 if replayed else 201
    return {"session": session, "replayed": replayed}


@router.post("/sessions/{session_id}/events")
def append_event(session_id: UUID, body: SessionEvent, request: Request,
                 store=Depends(storage)):
    return store.append(str(session_id), body.model_dump(mode="json"), timestamp(request))


@router.get("/sessions")
def list_sessions(limit: Annotated[int, Query(ge=1, le=50)] = 50,
                  cursor: Annotated[str | None, Query(max_length=1000)] = None,
                  store=Depends(storage)):
    return store.history(limit, cursor)


@router.get("/sessions/{session_id}")
def get_session(session_id: UUID,
                after_sequence: Annotated[int, Query(ge=0, le=2**53-1)] = 0,
                limit: Annotated[int, Query(ge=1, le=50)] = 50,
                store=Depends(storage)):
    return store.detail(str(session_id), after_sequence, limit)


class ConversationTurn(StrictBody):
    allow_live: Annotated[bool, Field(strict=True)] = False
    history_epoch: Milliseconds = 0
    conversation_id: UUID
    request_id: UUID
    session_id: UUID | None = None
    placement: Literal["before", "after"]
    expected_revision: Milliseconds
    message: Annotated[str, Field(strict=True, min_length=1, max_length=500)]


def mock_selector():
    from .conversations import fixed_mock
    return fixed_mock


@router.post("/conversations/turns")
async def conversation_turn(body: ConversationTurn, request: Request,
                      store=Depends(storage), selector=Depends(mock_selector)):
    from .conversations import ConversationStore
    payload = body.model_dump(mode="json")
    payload['message'] = payload['message'].strip()
    if not payload['message']:
        raise HTTPException(422, "Enter a fictional message of 1 to 500 characters.")
    from .live import LiveStore
    from .provider import select_reply, ProviderFailure
    live = LiveStore(store.connection)
    live.recover(timestamp(request))
    # Replays keep their original mode even after the host disables live mode.
    old = store.connection.execute('SELECT mode FROM skills_model_runs WHERE request_id=?', (payload['request_id'],)).fetchone()
    if old and old['mode'] == 'live':
        require_epoch_for_run(store.connection, payload)
        from .sessions import canonical_json
        original = store.connection.execute('SELECT payload_json FROM skills_model_runs WHERE request_id=?',(payload['request_id'],)).fetchone()[0]
        if original != canonical_json(payload):
            raise SessionConflict('Request ID was already used with different data.')
        return live.response(payload['request_id'], True)
    if old or not payload['allow_live'] or not request.app.state.skills_live_enabled_provider():
        return ConversationStore(store.connection).turn(payload, timestamp(request), selector)
    key = request.app.state.openai_key_provider()
    if not key:
        raise HTTPException(503, 'Skills model configuration is unavailable. Continue without conversation.')
    try:
        pending, context = live.prepare(payload, timestamp(request))
        if pending is None:
            result = ConversationStore(store.connection).turn(payload, timestamp(request), selector)
            result['mode_notice'] = 'Live allowance reached; this reply uses the fixed mock.'
            return result
        if context is None:
            return pending
        selection = await select_reply(context, key, transport=request.app.state.skills_live_transport_provider())
        return live.finish(payload['request_id'], payload['history_epoch'], timestamp(request), selection=selection)
    except ProviderFailure as error:
        # A preflight failure has no pending row or charge; return a safe error.
        if store.connection.execute('SELECT 1 FROM skills_model_runs WHERE request_id=?',(payload['request_id'],)).fetchone() is None:
            raise HTTPException(503, 'Skills conversation is unavailable. Continue without it.') from None
        return live.finish(payload['request_id'], payload['history_epoch'], timestamp(request), category=error.category)


@router.get("/conversations")
def conversation_history(request: Request, limit: Annotated[int, Query(ge=1, le=50)] = 20,
                         cursor: Annotated[str | None, Query(max_length=1000)] = None,
                         store=Depends(storage)):
    from .conversations import ConversationStore
    from .live import LiveStore
    LiveStore(store.connection).recover(timestamp(request))
    return ConversationStore(store.connection).history(limit, cursor)


@router.get("/conversations/{conversation_id}")
def conversation_detail(conversation_id: UUID, request: Request,
                        after_sequence: Annotated[int, Query(ge=0, le=2**53-1)] = 0,
                        limit: Annotated[int, Query(ge=1, le=50)] = 50,
                        store=Depends(storage)):
    from .conversations import ConversationStore
    from .live import LiveStore
    LiveStore(store.connection).recover(timestamp(request))
    return ConversationStore(store.connection).detail(str(conversation_id), after_sequence, limit)


class PreferenceChange(StrictBody):
    request_id: UUID
    expected_revision: Milliseconds
    action: Literal["save", "reset"]
    display_settings: DisplaySettings | None = None


@router.get("/preferences")
def get_preferences(store=Depends(storage)):
    from .preferences import PreferenceStore
    return PreferenceStore(store.connection).read()


@router.post("/preferences")
def change_preferences(body: PreferenceChange, request: Request, store=Depends(storage)):
    from .preferences import PreferenceStore
    if (body.action == 'save') != (body.display_settings is not None):
        raise HTTPException(422, "Save requires display settings; reset does not accept them.")
    return PreferenceStore(store.connection).update(body.model_dump(mode="json"), timestamp(request))


class ClearHistory(StrictBody):
    request_id: UUID
    expected_epoch: Milliseconds
    confirm: Annotated[bool, Field(strict=True)]


@router.get("/history")
def history_state(store=Depends(storage)):
    from .history import read
    return read(store.connection)


@router.delete("/history")
def clear_history(body: ClearHistory, store=Depends(storage)):
    from .history import clear
    if not body.confirm:
        raise HTTPException(422, "Confirm clearing saved skills history.")
    return clear(store.connection, body.model_dump(mode="json"))


def require_epoch_for_run(connection, payload):
    from .history import require_epoch
    require_epoch(connection, payload['history_epoch'])


class RunControl(StrictBody):
    history_epoch: Milliseconds


@router.post('/runs/{request_id}/cancel')
def cancel_run(request_id: UUID, body: RunControl, request: Request, store=Depends(storage)):
    from .live import LiveStore
    return LiveStore(store.connection).cancel(str(request_id), body.history_epoch, timestamp(request))


@router.get('/runs/{request_id}')
def run_status(request_id: UUID, request: Request, history_epoch: Annotated[int, Query(ge=0, le=2**53-1)], store=Depends(storage)):
    from .history import require_epoch
    from .live import LiveStore
    require_epoch(store.connection, history_epoch)
    live = LiveStore(store.connection)
    live.recover(timestamp(request))
    return live.response(str(request_id), True)


@router.get('/model-status')
def model_status(request: Request, store=Depends(storage)):
    budget = dict(store.connection.execute('SELECT * FROM skills_call_budget WHERE singleton_id=1').fetchone())
    enabled = request.app.state.skills_live_enabled_provider()
    exhausted = budget['reserved_calls'] >= budget['call_limit'] or budget['reserved_micro'] + 100000 > budget['dollar_limit_micro']
    return {'mode': 'live' if enabled and not exhausted else 'mock',
            'model_id': budget['model_id'] if enabled and not exhausted else 'local-fixed-fixture-v1',
            'live_enabled': enabled, 'allowance_exhausted': exhausted,
            'budget': budget}
