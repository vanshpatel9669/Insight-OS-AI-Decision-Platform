import json
from pathlib import Path

DB = Path("data/decisions.jsonl")
DB.parent.mkdir(exist_ok=True)

def save_decision(decision: dict) -> None:
    with DB.open("a", encoding="utf-8") as f:
        f.write(json.dumps(decision) + "\n")

def list_decisions() -> list[dict]:
    if not DB.exists():
        return []
    return [json.loads(line) for line in DB.read_text(encoding="utf-8").splitlines() if line]
