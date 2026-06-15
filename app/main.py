from fastapi import FastAPI
from app.decision_engine import DecisionEngine
from app.models import EnterpriseRecord, DecisionResponse
from app.repository import save_decision, list_decisions

app = FastAPI(title="Insight-OS Decision Intelligence Platform", version="1.0.0")
engine = DecisionEngine()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/decide", response_model=DecisionResponse)
def decide(record: EnterpriseRecord):
    decision = engine.decide(record)
    save_decision(decision)
    return decision

@app.get("/decisions")
def decisions():
    return {"items": list_decisions()}
