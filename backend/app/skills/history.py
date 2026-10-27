"""Atomic history clearing and generation checks; never delete display choices."""
from .sessions import SessionConflict, SkillsStorageError, canonical_json

SCHEMA = (
    """CREATE TABLE skills_history_state (
        singleton_id INTEGER PRIMARY KEY CHECK(singleton_id=1),
        epoch INTEGER NOT NULL CHECK(epoch>=0),
        last_request_id TEXT, last_payload_json TEXT, last_response_json TEXT
    )""",
    "INSERT INTO skills_history_state VALUES (1,0,NULL,NULL,NULL)",
)


def state(connection):
    row = connection.execute('SELECT * FROM skills_history_state WHERE singleton_id=1').fetchone()
    if row is None:
        raise SkillsStorageError('Skills history state is unavailable.')
    return row


def require_epoch(connection, expected):
    if state(connection)['epoch'] != expected:
        raise SessionConflict('Skills history was cleared. Reload this view before choosing a new session or conversation; this earlier save cannot be restored.')


def read(connection):
    with connection:
        connection.execute('BEGIN')
        return {'history_epoch': state(connection)['epoch']}


def clear(connection, body):
    import json
    payload = canonical_json(body)
    with connection:
        connection.execute('BEGIN IMMEDIATE')
        old = state(connection)
        if old['last_request_id'] == body['request_id']:
            if old['last_payload_json'] != payload:
                raise SessionConflict('Clear request ID was already used with different data.')
            return {**json.loads(old['last_response_json']), 'replayed': True}
        require_epoch(connection, body['expected_epoch'])
        counts = {table: connection.execute('SELECT count(*) FROM '+table).fetchone()[0]
                  for table in ('skills_sessions','skills_session_events','skills_conversations','skills_messages','skills_model_runs')}
        connection.execute('DELETE FROM skills_run_control')
        connection.execute('DELETE FROM skills_conversations')
        connection.execute('DELETE FROM skills_sessions')
        response = {'history_epoch': old['epoch']+1, 'deleted': counts, 'replayed': False}
        connection.execute('''UPDATE skills_history_state SET epoch=?,last_request_id=?,
            last_payload_json=?,last_response_json=? WHERE singleton_id=1''',
            (response['history_epoch'],body['request_id'],payload,canonical_json(response)))
        return response
