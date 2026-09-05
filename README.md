# RNA Secondary Structure Vienna

> **Domain:** Computational Biology & AI Drug Discovery
> **Reference Guidelines & Standards:** `wwPDB, IUPAC & CLSI Computational Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**RNA Secondary Structure Vienna** is an analytical and computational platform implementing a multi-agent evaluation engine for RNA secondary structure analysis. It provides threshold-based assessment of biological metrics with cryptographic audit trails and PHI protection.

The system uses a supervisor-worker architecture where specialized workers evaluate payloads against domain-specific thresholds, producing consensus dossiers with HMAC-SHA256 signed audit records.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Multi-Agent Evaluation Engine**: Supervisor orchestrates specialized workers (QC, Safety, Protocol Conformance) for threshold-based assessment
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated recommendations
- **Validation & Guardrails**: Rigorous input bounds checking, path traversal prevention, and anomaly detection
- **Zero-PHI Outbound Guard**: AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation
- **FastAPI REST API**: Exposes OpenAPI 3.1 REST endpoints and operational metrics

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/rna-secondary-structure-vienna.git
cd rna-secondary-structure-vienna

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Run a Single Audit
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Query the Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task identifier (required, max 128 chars)
- `--target`: Target identifier (required, max 128 chars)
- `--primary`: Primary metric value (float)
- `--secondary`: Secondary metric value (float, default: 0.0)
- `--critical`: Flag for critical/emergency status
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT, ANOMALY)
- `-i/--input`: Input CSV file path (batch mode)
- `-o/--output`: Output CSV file path (batch mode)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary measurement value | Optional |
| `is_critical_flag` | Emergency escalation flag | Optional |
| `status_descriptor` | Status/phenotype descriptor | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Set `AUDIT_SECRET_KEY` environment variable for production deployments.
* **Input Validation:** Path traversal prevention, identifier sanitization, and finite metric validation.
* **FastAPI REST API:** Exposes OpenAPI 3.1 REST endpoints and operational metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t rna-secondary-structure-vienna .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key rna-secondary-structure-vienna
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
├── agents/                  # Core multi-agent system
│   ├── __init__.py          # Package metadata
│   ├── api.py               # FastAPI REST server
│   ├── base.py              # Security, PHI guard, audit trail
│   ├── models.py            # Pydantic data models
│   ├── supervisor.py        # Supervisor orchestrator
│   ├── workers.py           # Specialized evaluation workers
│   ├── llm_factory.py       # LLM client factory
│   ├── learning.py          # Bayesian calibration engine
│   ├── metrics.py           # Prometheus metrics collector
│   └── streamer.py          # WebSocket telemetry broadcaster
├── rna_shape_predictor/     # RNA structure prediction module
│   ├── __init__.py
│   ├── agents.py            # RNA-specific agents and coordinator
│   ├── cli.py               # RNA predictor CLI
│   ├── engine.py            # Core algorithmic engine
│   ├── models.py            # Data models
│   └── server.py            # FastAPI server factory
├── tests/                   # Test suite
├── web/                     # Web console (HTML)
├── cli.py                   # Main CLI entry point
├── enrichment.py            # Enrichment feature engines
├── simulator.py             # High-throughput simulation
├── pyproject.toml           # Project configuration
├── Dockerfile               # Docker build config
└── docker-compose.yml       # Docker Compose config
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
