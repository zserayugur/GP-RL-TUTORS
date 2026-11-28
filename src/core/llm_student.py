from collections.abc import Callable, Mapping
from sqlite3 import Connection

from .llm_choice import Choice, resolve_choice
from .llm_prompt import prepare_prompt


def answer_question(
    db: Connection,
    item_id: int,
    question: str,
    options: Mapping[str, str],
    model: Callable[[str], str],
    order: str = "ABCD",
    *,
    persona: str | None = None,
) -> Choice:
    """Send the question text to the model and score its displayed choice."""
    prompt = prepare_prompt(question, options, order, persona=persona)
    reply = model(prompt.text)
    return resolve_choice(db, item_id, prompt.order, reply)