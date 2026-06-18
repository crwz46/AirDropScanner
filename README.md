# AirDropScanner[![CI](https://github.com/crwz46/AirDropScanner/actions/workflows/test.yml/badge.svg)](https://github.com/crwz46/AirDropScanner/actions/workflows/test.yml)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

**Multi-protocol airdrop eligibility checker** — paste any wallet address and instantly see which airdrops they qualify for, powered by a custom rule engine.

```
Wallet: 0xdead...0000

🔵 Arbitrum     ✅ ELIGIBLE   80%   (4/5 rules)
🌐 LayerZero    ✅ ELIGIBLE   80%   (4/5 rules)
⚡ zkSync       ❌ NOT ELIG   0%    (0/5 rules)
🔴 Optimism     ✅ ELIGIBLE   80%   (4/5 rules)
🟣 StarkNet     ❌ NOT ELIG   0%    (0/5 rules)
🟠 EigenLayer   ✅ ELIGIBLE   100%  (5/5 rules)

📊 Portfolio Value: ⭐⭐⭐⭐  (💎 Diamond)
```

## Features

| Feature | Description |
|---------|-------------|
| 🧠 **Rule Engine** | Customizable eligibility criteria per protocol |
| 🔄 **6 Protocols** | Arbitrum, LayerZero, zkSync, Optimism, StarkNet, EigenLayer |
| 📊 **Portfolio Rating** | ⭐1–5 star rating based on on-chain activity |
| 🌐 **Live Data** | Etherscan API integration for real wallet data |
| 🚀 **Web API** | FastAPI server with Swagger docs |
| 🐳 **Docker** | One-command containerized deployment |

## Quick Start

```bash
pip install -r requirements.txt
python main.py 0x1234...
```

## Usage

### CLI

```bash
# Scan wallet across all protocols
python main.py 0x1234...

# Check specific protocol
python main.py 0x1234... --protocol arbitrum

# Simulate high-activity wallet (tier 0-4)
python main.py 0x1234... --tier 4

# JSON output
python main.py 0x1234... --json

# List supported protocols
python main.py --list
```

### Web Server

```bash
python main.py --server
# → http://localhost:8000/docs
```

### Docker

```bash
docker-compose up -d
# → http://localhost:8000
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Service info |
| `GET /scan/{address}` | Scan wallet (`?protocol=arbitrum`) |
| `GET /protocols` | List supported protocols & criteria |
| `GET /health` | Health check |
| `GET /docs` | Swagger UI |

## Supported Protocols

| Protocol | Chain | Criteria |
|----------|-------|----------|
| 🔵 Arbitrum | Arbitrum One | 5 rules |
| 🌐 LayerZero | Multi-Chain | 5 rules |
| ⚡ zkSync | zkSync Era | 5 rules |
| 🔴 Optimism | OP Mainnet | 5 rules |
| 🟣 StarkNet | StarkNet | 5 rules |
| 🟠 EigenLayer | Ethereum | 5 rules |

## Rule Engine

Each protocol defines eligibility criteria as rules. A wallet is **eligible** if it meets ≥60% of the rules.

Example — Arbitrum eligibility:
```
✅ TX Count ≥ 4          Made at least 4 transactions on Arbitrum
✅ Bridged Funds         Bridged at least 0.01 ETH to Arbitrum
❌ Protocol Diversity    Interacted with at least 3 protocols on Arbitrum
✅ Active ≥ 3 Months     Wallet active on Arbitrum for 3+ months
✅ Nova Check            Also used Arbitrum Nova

Result: ✅ ELIGIBLE (4/5 rules = 80%)
```

## Project Structure

```
AirDropScanner/
├── main.py
├── airdrop_scanner/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── engine.py           # Rule engine + wallet profile
│   ├── rules.py            # Protocol-specific rules (6 airdrops)
│   ├── fetcher.py          # Wallet data (sample + Etherscan)
│   ├── config.py           # Environment config
│   ├── cache.py            # JSON cache layer
│   └── api.py              # FastAPI web service
├── tests/
│   └── test_scanner.py     # 30+ tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Portfolio Rating System

| Score | Stars | Label |
|-------|-------|-------|
| 0–20 | ⭐ | Bronze |
| 21–40 | ⭐⭐ | Silver |
| 41–60 | ⭐⭐⭐ | Gold |
| 61–80 | ⭐⭐⭐⭐ | Diamond |
| 81–100 | ⭐⭐⭐⭐⭐ | Legend |

## Tests

```bash
pytest tests/ -v
```

## Why Recruiters Love This

| Skill | Shown |
|-------|-------|
| Python | Clean OOP, dataclasses, typed |
| Rule Engine | Plugable rules, threshold logic, scoring |
| Multi-API Design | Extensible protocol registry |
| CLI + API | argparse + FastAPI dual interface |
| Data Analysis | Portfolio scoring, chain activity metrics |
| Docker | Containerized deployment |
| Testing | pytest, comprehensive coverage |
| Crypto | Airdrop mechanics, wallet analysis |

## 🌐 Ecosystem

This project is part of a **5-repo analytics & AI ecosystem** by [crwz46](https://github.com/crwz46):

| Repo | Focus |
|------|-------|
| 🏠 [WallTrack](https://github.com/crwz46/WallTrack) | Multi-chain wallet tracking, gas alerts, flash loans |
| 🔍 [TokenVision](https://github.com/crwz46/TokenVision) | Token holder concentration, HHI/Gini, whale detection |
| 🪂 [AirDropScanner](https://github.com/crwz46/AirDropScanner) | Multi-protocol airdrop eligibility checker |
| 📊 [TradeLens](https://github.com/crwz46/TradeLens) | Market intelligence, risk engine, portfolio tracker |
| 🧠 [DocuMind](https://github.com/crwz46/DocuMind) | RAG-powered Document Q&A with LLMs |

## 📝 License

MIT &mdash; see [LICENSE](LICENSE)

---

*Built by [crwz46](https://github.com/crwz46) &mdash; Data Scientist &amp; AI Engineer*