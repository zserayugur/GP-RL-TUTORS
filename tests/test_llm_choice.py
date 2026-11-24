import sqlite3
from pathlib import Path
import unittest
from src.core.llm_choice import resolve_choice
from src.core.llm_student import answer_question
import os
from src.core.ollama_client import ask_ollama

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
            
    def test_student_scores_displayed_choice(self):
        def fake_model(text):
            self.assertIn("A) c", text)
            return "A"

        result = answer_question(
            self.db,
            1,
            "Test fixture",
            {"A": "a", "B": "b", "C": "c", "D": "d"},
            fake_model,
            order="CABD",
        )
        self.assertEqual(result.canonical_label, "C")
        self.assertIs(result.correct, True)

    def test_student_passes_persona_to_model(self):
        persona = "Kesirleri toplarken payları ve paydaları ayrı ayrı toplarsın."

        def fake_model(text):
            self.assertIn(f"Öğrenci rolü: {persona}", text)
            return "A"

        result = answer_question(
            self.db,
            1,
            "1/2 + 1/3 kaçtır?",
            {"A": "2/5", "B": "1/5", "C": "5/6", "D": "2/6"},
            fake_model,
            order="CABD",
            persona=persona,
        )

        self.assertEqual(result.canonical_label, "C")
        self.assertIs(result.correct, True)    
        

    @unittest.skipUnless(os.getenv("RUN_OLLAMA_TEST") == "1", "Ollama testi isteğe bağlı")
    def test_student_with_real_ollama(self):
        result = answer_question(
        self.db,
        1,
        "2/4 hangi kesre eşittir?",
        {"A": "1/4", "B": "1/3", "C": "1/2", "D": "3/4"},
        ask_ollama,
        order="CABD",
    )
        self.assertEqual(result.canonical_label, "C")
        self.assertIs(result.correct, True)