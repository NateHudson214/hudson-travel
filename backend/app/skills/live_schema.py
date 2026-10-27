"""Version-five migration, preserving old records and all budget reservations."""
TABLES = {'skills_call_budget', 'skills_run_control'}
SCHEMA = (
    '''CREATE TABLE skills_call_budget (
        singleton_id INTEGER PRIMARY KEY CHECK(singleton_id=1),
        model_id TEXT NOT NULL CHECK(model_id='gpt-6-luna'),
        call_limit INTEGER NOT NULL CHECK(call_limit BETWEEN 1 AND 10),
        dollar_limit_micro INTEGER NOT NULL CHECK(dollar_limit_micro BETWEEN 1 AND 1000000),
        reserved_calls INTEGER NOT NULL CHECK(reserved_calls>=0 AND reserved_calls<=call_limit),
        reserved_micro INTEGER NOT NULL CHECK(reserved_micro>=0 AND reserved_micro<=dollar_limit_micro)
    )''',
    "INSERT INTO skills_call_budget VALUES (1,'gpt-6-luna',10,1000000,0,0)",
    '''CREATE TABLE skills_run_control (
        request_id TEXT PRIMARY KEY, epoch INTEGER NOT NULL,
        deadline REAL NOT NULL, cancelled INTEGER NOT NULL CHECK(cancelled IN(0,1))
    )''',
)


def migrate(connection):
    from .conversations import SCHEMA as CHAT_SCHEMA
    # Drop dependents before replacing the checked message/run tables. All DDL
    # and data copies are in the caller's transaction; a failure rolls back.
    connection.execute('CREATE TEMP TABLE old_skills_runs AS SELECT * FROM skills_model_runs')
    connection.execute('CREATE TEMP TABLE old_skills_messages AS SELECT * FROM skills_messages')
    connection.execute('DROP TABLE skills_model_runs')
    connection.execute('DROP TABLE skills_messages')
    connection.execute(CHAT_SCHEMA[1])
    connection.execute('INSERT INTO skills_messages SELECT * FROM old_skills_messages')
    connection.execute(CHAT_SCHEMA[2])
    connection.execute('INSERT INTO skills_model_runs SELECT * FROM old_skills_runs')
    connection.execute('DROP TABLE old_skills_runs')
    connection.execute('DROP TABLE old_skills_messages')
    for statement in SCHEMA:
        connection.execute(statement)
    connection.execute("UPDATE skills_metadata SET value='5' WHERE key='schema_version'")
    connection.execute('PRAGMA user_version=5')
