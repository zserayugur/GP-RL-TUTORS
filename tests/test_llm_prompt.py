import unittest

from src.core.llm_prompt import prepare_prompt


class PromptTests(unittest.TestCase):
    def setUp(self):
        self.options = {"A": "1/4", "B": "1/3", "C": "1/2", "D": "3/4"}

    def test_shuffled_options_match_saved_order(self):
        prompt = prepare_prompt("2/4 hangi kesre eşittir?", self.options, "CABD")

        self.assertEqual(prompt.order, "CABD")
        self.assertEqual(
            prompt.text.splitlines()[-4:],
            ["A) 1/2", "B) 1/4", "C) 1/3", "D) 3/4"],
        )

    def test_invalid_order_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare_prompt("2/4 hangi kesre eşittir?", self.options, "CAAD")

    def test_missing_option_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare_prompt("2/4 hangi kesre eşittir?", {"A": "1/4"})