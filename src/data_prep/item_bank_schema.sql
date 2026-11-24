-- Item bank schema (WBS 5.2, FR-06, FR-07, FR-11, FR-12).
-- Fields follow the approved TUBITAK text (Method, "Alan, veri ve içerik"):
-- skill_id, difficulty, correct_answer, misconception_id, distractors, hint,
-- worked_example, explanation, source. Visual items are flagged and not used in experiments.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS skills (
    skill_id      TEXT PRIMARY KEY,          -- S1..S6
    name          TEXT NOT NULL,
    prerequisites TEXT NOT NULL DEFAULT ''   -- comma separated skill_ids, e.g. 'S1'
);

CREATE TABLE IF NOT EXISTS misconceptions (
    misconception_id INTEGER PRIMARY KEY,    -- Eedi MisconceptionId; team-made ids start at 100000
    name             TEXT NOT NULL,
    source           TEXT NOT NULL           -- 'eedi_kaggle' or 'team'
);

CREATE TABLE IF NOT EXISTS items (
    item_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id         TEXT NOT NULL REFERENCES skills(skill_id),
    pool             TEXT NOT NULL CHECK (pool IN ('teaching', 'test')),       -- FR-06: separate pools
    item_format      TEXT NOT NULL CHECK (item_format IN ('multiple_choice', 'short_answer')),
    difficulty       TEXT CHECK (difficulty IN ('easy', 'hard')),              -- NULL = not yet rated
    question_text    TEXT NOT NULL,
    correct_answer   TEXT NOT NULL,          -- mc: option letter; short answer: canonical value, e.g. '2/3'
    misconception_id INTEGER REFERENCES misconceptions(misconception_id),     -- main target misconception (optional)
    hint             TEXT,
    worked_example   TEXT,
    explanation      TEXT,
    visual_flag      INTEGER NOT NULL DEFAULT 0,     -- 1 = contains a visual; not used in experiments
    source           TEXT NOT NULL,          -- 'eedi_kaggle', 'team', 'openstax', ...
    source_ref       TEXT,                   -- e.g. Eedi QuestionId
    license          TEXT NOT NULL,          -- e.g. 'CC BY-NC 4.0'
    status           TEXT NOT NULL DEFAULT 'approved'
                     CHECK (status IN ('draft', 'pending', 'approved', 'rejected')),  -- FR-11
    created_by       TEXT NOT NULL DEFAULT 'team',
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- FR-07: four options for multiple-choice items; every wrong option maps to a misconception.
CREATE TABLE IF NOT EXISTS item_options (
    item_id          INTEGER NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    option_label     TEXT NOT NULL CHECK (option_label IN ('A', 'B', 'C', 'D')),
    option_text      TEXT NOT NULL,
    is_correct       INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    misconception_id INTEGER REFERENCES misconceptions(misconception_id),  -- NULL for correct or unlabelled option
    PRIMARY KEY (item_id, option_label)
);

-- FR-12: experiments run on a versioned snapshot of the approved pool.
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    note        TEXT
);
CREATE TABLE IF NOT EXISTS snapshot_items (
    snapshot_id INTEGER NOT NULL REFERENCES snapshots(snapshot_id),
    item_id     INTEGER NOT NULL REFERENCES items(item_id),
    PRIMARY KEY (snapshot_id, item_id)
);

-- Items usable by the tutor: approved and without visuals.
CREATE VIEW IF NOT EXISTS usable_items AS
    SELECT * FROM items WHERE status = 'approved' AND visual_flag = 0;
