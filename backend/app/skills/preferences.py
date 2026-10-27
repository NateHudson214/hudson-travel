"""Explicit saved presentation choices, independent of sessions and mock replies."""
from .sessions import SessionConflict, SkillsStorageError, canonical_json

SCHEMA = (
    """CREATE TABLE skills_preferences (
        singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
        revision INTEGER NOT NULL CHECK (revision >= 0),
        has_saved INTEGER NOT NULL CHECK (has_saved IN (0,1)),
        simpler_view INTEGER NOT NULL CHECK (simpler_view IN (0,1)),
        motion_mode TEXT NOT NULL CHECK (motion_mode IN ('system','static','gentle')),
        updated_at TEXT, last_request_id TEXT, last_payload_json TEXT
    )""",
    "INSERT INTO skills_preferences VALUES (1,0,0,0,'system',NULL,NULL,NULL)",
)


def view(row):
    return {
        'revision': row['revision'], 'updated_at': row['updated_at'],
        'last_setup': {'simpler_view': bool(row['simpler_view']), 'motion_mode': row['motion_mode']}
        if row['has_saved'] else None,
    }


class PreferenceStore:
    def __init__(self, connection):
        self.connection = connection

    def get(self):
        row = self.connection.execute('SELECT * FROM skills_preferences WHERE singleton_id=1').fetchone()
        if row is None:
            raise SkillsStorageError('Saved display choices are unavailable.')
        return row

    def read(self):
        return {'preferences': view(self.get())}

    def update(self, body, now):
        payload = canonical_json(body)
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            old = self.get()
            if old['last_request_id'] == body['request_id']:
                if old['last_payload_json'] != payload:
                    raise SessionConflict('This display-choice request ID was already used with different data.')
                return {'preferences': view(old), 'replayed': True}
            if old['revision'] != body['expected_revision']:
                raise SessionConflict('Saved choices changed. Refresh saved choices before saving or resetting again.')
            settings = body['display_settings'] if body['action'] == 'save' else {
                'simpler_view': False, 'motion_mode': 'system',
            }
            self.connection.execute('''UPDATE skills_preferences SET revision=?,has_saved=?,
                simpler_view=?,motion_mode=?,updated_at=?,last_request_id=?,last_payload_json=?
                WHERE singleton_id=1''', (old['revision']+1, int(body['action']=='save'),
                int(settings['simpler_view']), settings['motion_mode'], now, body['request_id'], payload))
            return {'preferences': view(self.get()), 'replayed': False}
