PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sessions (
    session_id          TEXT PRIMARY KEY NOT NULL,
    locked              INTEGER NOT NULL DEFAULT 0 CHECK (locked IN (0, 1)),
    locked_at           TEXT,
    stage               TEXT NOT NULL DEFAULT 'Start'
                        CHECK (stage IN ('Start', 'Explore', 'Reflect', 'Finish')),
    turn_count          INTEGER NOT NULL DEFAULT 0,
    last_reminder_turn  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL
                    REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_message    TEXT NOT NULL,
    system_message  TEXT NOT NULL,
    response_type   TEXT NOT NULL
                    CHECK (response_type IN ('normal', 'boundary', 'crisis', 'error', 'non-english')),
    risk_level      TEXT NOT NULL
                    CHECK (risk_level IN ('low', 'medium', 'high')),
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_history_session_id ON history(session_id);

CREATE TABLE IF NOT EXISTS feedback (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       TEXT NOT NULL
                     REFERENCES sessions(session_id) ON DELETE CASCADE,
    message_id       TEXT NOT NULL,
    flagged_message  TEXT NOT NULL,
    category         TEXT NOT NULL CHECK (json_valid(category)),
    comment          TEXT CHECK (comment IS NULL OR length(comment) <= 1000),
    created_at       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback(session_id);