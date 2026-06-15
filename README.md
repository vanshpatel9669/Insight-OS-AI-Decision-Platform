# 🧠 AI Financial Decision Optimization System

An AI-powered Reinforcement Learning platform for evaluating portfolio allocation strategies under dynamic market conditions.

The system simulates financial environments, analyzes risk factors, and generates adaptive allocation recommendations using policy-based decision optimization techniques. Designed as a production-oriented research platform for quantitative finance, portfolio analytics, and AI-driven decision systems.

---

## 🚀 Overview

Financial markets are constantly influenced by volatility, momentum shifts, liquidity constraints, and risk exposure.

This project demonstrates how Reinforcement Learning inspired decision systems can be used to evaluate portfolio strategies and recommend allocation adjustments under varying market conditions.

The platform:

- Evaluates market volatility and momentum
- Monitors portfolio drawdown levels
- Assesses liquidity through cash ratios
- Simulates portfolio allocation decisions
- Generates optimized recommendations
- Exposes predictions through a REST API
- Supports experimentation and policy evaluation workflows

---

## 🎯 Business Objective

Traditional portfolio allocation often relies on static rules and manual analysis.

This platform explores how AI-driven decision systems can:

- Adapt to changing market conditions
- Improve allocation consistency
- Reduce portfolio risk exposure
- Support quantitative research workflows
- Accelerate decision-making processes

---

## 🏗 System Architecture

```text
Market Signals
     │
     ▼
Feature Engineering
     │
     ▼
Portfolio State Generation
     │
     ▼
Decision Policy Engine
     │
     ▼
Risk Evaluation Layer
     │
     ▼
Recommendation Engine
     │
     ▼
REST API Response
```

---

## ✨ Key Features

### 📊 Portfolio Analytics

- Volatility assessment
- Momentum analysis
- Drawdown monitoring
- Liquidity evaluation
- Allocation scoring

### 🤖 Decision Intelligence

- Adaptive policy evaluation
- Allocation recommendation generation
- Risk-aware decision scoring
- Scenario simulation

### ⚙️ Production Components

- Flask REST API
- Modular architecture
- Automated testing
- Docker deployment
- Configurable environments

---

## ⚙️ Technology Stack

| Category | Technologies |
|-----------|-------------|
| Programming | Python |
| Machine Learning | PyTorch (Extensible) |
| API Development | Flask |
| Data Processing | NumPy, Pandas |
| Testing | PyTest |
| Deployment | Docker |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

```text
financial-decision-optimization-system/

├── api.py
├── train.py
├── policy.py
├── environment.py
├── requirements.txt
├── Dockerfile
├── outputs/
│   └── policy.json
├── tests/
│   └── test_policy.py
└── README.md
```

---

## 🔬 Decision Workflow

The decision engine evaluates:

### Input Features

- Volatility
- Momentum
- Drawdown
- Cash Ratio

### Processing Steps

1. Portfolio state construction
2. Risk evaluation
3. Policy scoring
4. Allocation recommendation generation

### Output

- Increase Exposure
- Maintain Allocation
- Reduce Risk

---

## 📈 Example API Request

### Request

```bash
curl -X POST http://127.0.0.1:5000/predict \
-H "Content-Type: application/json" \
-d '{
      "volatility":0.22,
      "momentum":0.08,
      "drawdown":0.04,
      "cash_ratio":0.25
    }'
```

### Response

```json
{
  "action": "Increase Equity Exposure",
  "confidence": 0.91
}
```

---

## 🛠 Installation

### Clone Repository

```bash
git clone https://github.com/vanshpatel9669/AI-Financial-decision-System.git
cd AI-Financial-decision-System
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Training

```bash
python train.py
```

Generated policy artifacts are saved in:

```text
outputs/
```

---

## 🌐 Run API

```bash
python api.py
```

API Health Check:

```text
http://127.0.0.1:5000/health
```

Prediction Endpoint:

```text
http://127.0.0.1:5000/predict
```

---

## 🧪 Run Tests

```bash
pytest tests/
```

---

## 🐳 Docker Deployment

Build:

```bash
docker build -t financial-decision-system .
```

Run:

```bash
docker run -p 5000:5000 financial-decision-system
```

---

## 📊 Future Enhancements

Planned extensions include:

- PPO-based Reinforcement Learning Agents
- DQN Baseline Models
- Experiment Tracking
- Backtesting Framework
- Portfolio Benchmark Comparison
- Multi-Asset Optimization
- Real Market Data Integration
- Policy Performance Dashboard

---

## 🎓 Learning Outcomes

This project demonstrates:

- AI-driven decision systems
- Quantitative portfolio analysis
- Risk-aware recommendation engines
- Production API deployment
- Financial analytics workflows
- Reinforcement Learning foundations

---

## 👨‍💻 Author

### Vansh Patel

MS Computer Science (AI/ML)
Stevens Institute of Technology

- GitHub: https://github.com/vanshpatel9669
- LinkedIn: https://linkedin.com/in/vanshpatel1702

---

⭐ If you found this project interesting, consider starring the repository.