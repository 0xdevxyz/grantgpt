# FörderScout AI (GrantGPT)

**KI-gestützte Fördermittelsuche und Antragsassistenz für deutsche Unternehmen**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 Übersicht

FörderScout AI ist eine intelligente Plattform, die Unternehmen dabei hilft, passende Förderprogramme zu finden und bei der Antragstellung unterstützt. Die Plattform kombiniert automatisches Programm-Discovery (Scraping), KI-basiertes Matching (Vector Search + LLM) und einen KI-gestützten Antragsassistenten.

### Features

- **🔍 Automatisches Programm-Discovery**
  - 6 Tier-1 Scraper (BAFA, KfW, SAB, BMWK, go-digital, Förderdatenbank)
  - GPT-4 basierte Datenextraktion
  - Change Detection mit LLM-Klassifikation
  - Tägliches/wöchentliches automatisches Scraping

- **🎯 KI-Matching**
  - Vector Search mit Qdrant
  - OpenAI Embeddings (text-embedding-3-large)
  - Semantische Suche nach passenden Programmen
  - Match-Score Berechnung

- **📝 Antragsassistent**
  - 7-teilige Antragsgenerierung per KI
  - PDF/DOCX Export
  - Compliance-Checks
  - Versionierung

- **💳 Success-Fee Abrechnung**
  - Stripe Integration
  - Automatische Rechnungserstellung
  - 15-25% Success-Fee bei Bewilligung

---

## 🏗️ Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│                    https://foerderscout.de                      │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway (Nginx + SSL)                    │
│                   https://api.foerderscout.de                   │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌────────────────┐
│   FastAPI     │    │  Celery Worker  │    │  Celery Beat   │
│   Backend     │    │  (Background)   │    │  (Scheduler)   │
└───────────────┘    └─────────────────┘    └────────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌────────────────┐
│  PostgreSQL   │    │     Redis       │    │     Qdrant     │
│   (Users,     │    │  (Cache, Queue) │    │  (Vectors)     │
│  Applications)│    │                 │    │                │
└───────────────┘    └─────────────────┘    └────────────────┘
```

---

## 📁 Projektstruktur

```
saas-project-8/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API Routes
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── grants.py     # Grant endpoints
│   │   │   ├── applications.py
│   │   │   ├── payments.py   # Stripe integration
│   │   │   └── ...
│   │   ├── core/             # Configuration
│   │   ├── models/           # SQLAlchemy models
│   │   ├── services/         # Business logic
│   │   │   ├── grant_matcher.py
│   │   │   ├── application_writer.py
│   │   │   ├── change_detection.py
│   │   │   └── stripe_service.py
│   │   └── tasks/            # Celery tasks
│   │       └── scraper_tasks.py
│   ├── scripts/
│   │   ├── scraper/          # Funding scrapers
│   │   │   ├── base_scraper.py
│   │   │   ├── bafa_scraper.py
│   │   │   ├── kfw_scraper.py
│   │   │   ├── sab_scraper.py
│   │   │   ├── bmwk_scraper.py
│   │   │   ├── godigital_scraper.py
│   │   │   └── program_extractor.py
│   │   └── deployment/
│   ├── alembic/              # Database migrations
│   ├── data/grants/          # Scraped grant data
│   └── tests/
├── frontend/                 # Next.js frontend
├── nginx/                    # Nginx configuration
├── monitoring/               # Prometheus config
├── docs/
│   └── BETA_LAUNCH_CHECKLIST.md
├── docker-compose.prod.yml
└── .env.production.template
```

---

## 🚀 Quick Start

### Voraussetzungen

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- OpenAI API Key
- Stripe Account (für Payments)

### Development Setup

```bash
# Repository klonen
git clone https://github.com/yourorg/foerderscout.git
cd foerderscout

# Environment Variables kopieren
cp .env.production.template .env
# .env mit deinen Keys befüllen

# Docker Container starten
docker compose up -d

# Database Migrations
docker compose exec api alembic upgrade head

# Seed Data laden
docker compose exec api python scripts/seed_comprehensive_grants.py
```

### API aufrufen

```bash
# Health Check
curl http://localhost:8008/health

# API Documentation
open http://localhost:8008/docs
```

---

## 📦 Komponenten

### Scraper

| Scraper | Quelle | Tier | Intervall |
|---------|--------|------|-----------|
| BAFA | bafa.de | 1 | Täglich |
| KfW | kfw.de | 1 | Täglich |
| SAB | sab.sachsen.de | 1 | Täglich |
| BMWK | bmwk.de | 1 | Täglich |
| go-digital | bmwk.de | 1 | Täglich |
| Förderdatenbank | foerderdatenbank.de | 1 | Täglich |

### API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/auth/login` | POST | Login |
| `/api/v1/auth/register` | POST | Registrierung |
| `/api/v1/grants/search` | POST | Programm-Suche |
| `/api/v1/grants/match` | POST | KI-Matching |
| `/api/v1/applications` | POST | Antrag erstellen |
| `/api/v1/payments/calculate-fee` | POST | Fee berechnen |

---

## 💰 Business Model

### Pricing

| Tier | Monatlich | Success-Fee |
|------|-----------|-------------|
| Success-Fee | 0€ | 25% |
| Hybrid | 199€ | 20% |
| Enterprise | 499€ | 15% |

- **Minimum Fee:** 500€
- **Maximum Fee:** 50.000€

---

## 🔐 Sicherheit

- HTTPS/TLS 1.3
- JWT Authentication
- bcrypt Password Hashing
- Rate Limiting
- CORS Configuration
- DSGVO-konform

---

## 📊 Monitoring

- **Sentry**: Error Tracking
- **Prometheus**: Metrics
- **Grafana**: Dashboards
- **Structured Logging**: JSON Logs

---

## 🚢 Deployment

### Production

```bash
# Deployment Script ausführen
./scripts/deployment/deploy.sh

# Oder manuell
docker compose -f docker-compose.prod.yml up -d
```

### Backups

```bash
# Backup ausführen
./scripts/deployment/backup.sh

# Cron einrichten (täglich um 2:00)
0 2 * * * /opt/foerderscout/scripts/deployment/backup.sh
```

---

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

## 🤝 Kontakt

- **Website:** https://foerderscout.de
- **Email:** support@foerderscout.de
- **API Docs:** https://api.foerderscout.de/docs

---

*FörderScout AI - Fördermittel finden war noch nie so einfach.*
