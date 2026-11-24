import sqlite3
from pathlib import Path
import unittest
from src.core.llm_choice import resolve_choice


def database():
    con = sqlite3.connect(":memory:")
    schema = Path(__file__).resolve().parents[1] / "src/data_prep/item_bank_schema.sql"
    con.executescript(schema.read_text(encoding="utf8"))
    con.executescript("""
        INSERT INTO skills VALUES ('S1','Equivalent','');
        INSERT INTO misconceptions VALUES (100000,'Synthetic example','team');
        INSERT INTO items (skill_id,pool,item_format,question_text,correct_answer,source,license,status)
        VALUES ('S1','teaching','multiple_choice','Test fixture','C','team','fixture','approved');
        INSERT INTO item_options VALUES (1,'A','a',0,100000),(1,'B','b',0,NULL),
                                        (1,'C','c',1,NULL),(1,'D','d',0,NULL);
    """)
    return con


def check_shuffle(db):
    original = resolve_choice(db, 1, 'ABCD', 'A')
    assert resolve_choice(db, 1, 'CABD', ' b ') == original
    assert original.correct is False and original.misconception_id == 100000
    assert resolve_choice(db, 1, 'CABD', 'A').correct is True


def check_invalid(db):
    assert resolve_choice(db, 1, 'ABCD', 'A or C').correct is None
    result = resolve_choice(db, 1, 'ABCD', 'B')
    assert result.correct is False and result.misconception_id is None


class ChoiceTests(unittest.TestCase):
    def setUp(self):
        self.db = database()
        self.addCleanup(self.db.close)

    def test_shuffle(self):
        check_shuffle(self.db)

    def test_invalid(self):
        check_invalid(self.db)

    def test_ineligible(self):
        for change in ["status='draft'", "visual_flag=1", "pool='test'", "correct_answer='B'"]:
            with self.subTest(change=change):
                self.db.execute('UPDATE items SET ' + change)
                with self.assertRaises(ValueError):
                    resolve_choice(self.db, 1, 'ABCD', 'A')
                self.db.rollback()

    def test_order(self):
        with self.assertRaises(ValueError):
            resolve_choice(self.db, 1, 'AACD', 'A')
