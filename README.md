# RL-TUTORS

An RL-based tutoring system for studying policy generalization across different student models.

## Project Structure

- `src/` – Source code
- `doc/` – Project documentation
- `ref/` – Research papers, reports, and references
- `log/` – Meeting notes, progress, risks, and decisions
  - `log/worklog/` – Team work log: each member adds what they did to their own file (see its README)
- `data/` – Project data
- `models/` – AI models and related files
- `ai/` – AI-related prompts, plans, task templates, and generated records

## Setup (NFR-13: required)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

All tests should pass on a clean checkout. No raw data (ASSISTments, Eedi) is needed to run the test
suite — those live outside Git per their licenses (see `data/raw/`).

A Docker setup is optional (not required by NFR-13) and not provided yet.
