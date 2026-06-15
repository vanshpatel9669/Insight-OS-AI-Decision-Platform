# Insight-OS — AI Decision Intelligence Platform

Insight-OS is a runnable FastAPI decision platform that turns enterprise records into structured operational decisions. It demonstrates API-first architecture, guardrail validation, explainable scoring, and workflow-ready output.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010
```

Docs: `http://127.0.0.1:8010/docs`

## Example

```bash
curl -X POST http://127.0.0.1:8010/decide -H "Content-Type: application/json" -d '{"record_id":"R-1","customer_tier":"enterprise","risk_score":0.71,"revenue_impact":85000,"open_issues":4,"sla_hours_remaining":6}'
```
