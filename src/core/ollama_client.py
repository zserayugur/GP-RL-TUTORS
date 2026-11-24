import json
from urllib.request import Request, urlopen


def ask_ollama(prompt: str, model: str = "qwen3:4b") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"temperature": 0},
    }

    request = Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=120) as response:
        result = json.load(response)

        text = result["response"]
    return text.rsplit("</think>", 1)[-1].strip()