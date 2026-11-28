from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class PreparedPrompt:
    text: str
    order: str


def prepare_prompt(
    question: str,
    options: Mapping[str, str],
    order: str = "ABCD",
    *,
    persona: str | None = None,
) -> PreparedPrompt:
    """Soruyu ve şıkları hazırlar; ekrandaki sırayı ayrıca saklar."""
    if set(options) != set("ABCD"):
        raise ValueError("Şıklar A, B, C ve D olmalı.")
    if sorted(order) != list("ABCD"):
        raise ValueError("Şık sırası A, B, C ve D'yi birer kez içermeli.")

    displayed_options = "\n".join(
        f"{displayed}) {options[original]}"
        for displayed, original in zip("ABCD", order)
    )

    role = persona.strip() if persona is not None else ""
    role_text = f"Öğrenci rolü: {role}\n\n" if role else ""

    text = (
        f"{role_text}"
        "Soruyu cevapla. Yalnızca A, B, C veya D harfini yaz.\n\n"
        f"Soru: {question}\n"
        f"{displayed_options}"
    )
    return PreparedPrompt(text=text, order=order)