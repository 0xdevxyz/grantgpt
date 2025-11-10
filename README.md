# 💎 GrantGPT - AI-Fördermittelberater

**Der intelligente Weg zu Fördermitteln: Von der Suche bis zur Bewilligung - komplett automatisiert.**

> Verwandle 160 Mrd. € ungenutzte Fördermittel in dein Business-Wachstum

---

## 🎯 Was ist GrantGPT?

GrantGPT ist eine KI-gestützte Plattform, die Unternehmen dabei hilft, passende Förderprogramme zu finden und erfolgreiche Anträge zu stellen - automatisiert, schnell und erfolgsbasiert.

### Das Problem
- **2.000+ Förderprogramme** in Deutschland - niemand kennt alle
- **90% der KMUs** wissen nicht, dass sie Anspruch haben
- **80% der Fördermittel** werden nicht abgerufen
- **50-200 Seiten Anträge** - dauert 40-80 Stunden
- **Komplexe Bürokratie** - ständige Änderungen

### Die Lösung
**GrantGPT automatisiert den kompletten Prozess:**
1. 🔍 **AI-Matching**: Findet passende Förderprogramme (aus 2.000+)
2. ✍️ **Auto-Antrag**: KI schreibt kompletten Antrag (2h statt 80h!)
3. ✅ **Compliance-Check**: Prüft Förderfähigkeit automatisch
4. 📤 **Einreichung**: Upload zu Förderportalen
5. 📊 **Verwendungsnachweis**: Automatische Berichte nach Bewilligung

---

## 💰 Marktpotenzial

### Fördermittel in Deutschland
- **EU-Fördermittel:** ~30 Mrd. €/Jahr
- **Bundesfördermittel:** ~80 Mrd. €/Jahr
- **Landesfördermittel:** ~40 Mrd. €/Jahr
- **Kommunale Programme:** ~10 Mrd. €/Jahr
- **GESAMT:** **~160 Mrd. €/Jahr**

### Target-Market
- **3,5 Mio. KMUs** in Deutschland
- **~2 Mio. förderfähig** (>10 Mitarbeiter, Innovation/Digitalisierung)
- **Ø Förderung:** 150.000€ pro Jahr
- **TAM:** 2 Mio. × 150k€ × 50% Provision = **150 Mrd. €**

---

## 🚀 Features

### Phase 1: MVP (Monate 1-3)
- ✅ **AI-Fördermittel-Matching**
  - Intelligente Suche in 2.000+ Programmen
  - Priorität nach Erfolgswahrscheinlichkeit
  - Fristen-Tracking
- ✅ **Basis-Antragsstellung**
  - Guided Questionnaire (30 Min.)
  - KI generiert Projektbeschreibung
  - Export als PDF/Word

### Phase 2: Advanced (Monate 4-9)
- 🔄 **Vollautomatischer Antrag**
  - Marktanalyse (automatisch)
  - Technische Machbarkeit
  - Finanzplan & Arbeitsplan
  - Verwertungsplan & Risikomanagement
- 🔄 **Multi-Programm-Optimierung**
  - Kombiniere 3-5 Programme
  - Maximiere Förderung ohne Doppelförderung
  - Projekt-Splitting für optimale Ausnutzung

### Phase 3: Enterprise (Monate 10-12)
- 📊 **Dashboard & Analytics**
  - Portfolio-Übersicht (alle Anträge)
  - Status-Tracking (In Prüfung, Bewilligt, etc.)
  - Success-Rate & ROI
- 🤖 **Verwendungsnachweis-Automatisierung**
  - Automatische Zwischen-/Schlussberichte
  - Budget-Tracking
  - Reminder für Fristen

---

## 💸 Pricing-Modell (Erfolgsbasiert)

### Tier 1: **Self-Service AI** (40% Provision)
- KI macht alles
- Du checkst nur noch
- **Provision:** 40% der bewilligten Summe
- **Beispiel:** 100k€ Förderung → **40k€** für uns

### Tier 2: **AI + Experten-Review** (50% Provision)
- KI macht Antrag
- Mensch (Fördermittel-Experte) prüft + optimiert
- **Provision:** 50%
- **Beispiel:** 500k€ Förderung → **250k€** für uns

### Tier 3: **White Glove** (60% Provision)
- AI + Experte + Betreuung bis Bewilligung
- Nachverhandlung bei Ablehnung
- Verwendungsnachweis-Betreuung
- **Provision:** 60%
- **Beispiel:** 2M€ Förderung → **1,2M€** für uns

**Wichtig:** Provision nur bei Erfolg (kein Risiko für Kunden!)

---

## 🏗️ Technologie-Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **LLM:** OpenAI GPT-4 + Claude (via OpenRouter)
- **Vector DB:** Qdrant (für 2.000+ Förderprogramme)
- **Database:** PostgreSQL 15
- **Cache:** Redis
- **Queue:** Celery + Redis
- **Document-Gen:** Python-DOCX, Jinja2

### Frontend
- **Framework:** Next.js 14 (App Router)
- **UI:** Tailwind CSS + shadcn/ui
- **State:** Zustand
- **Forms:** React Hook Form + Zod
- **Charts:** Recharts

### AI/ML
- **RAG-System:** LangChain + Qdrant
- **Fine-Tuning:** GPT-4 auf erfolgreiche Anträge
- **Embeddings:** OpenAI text-embedding-3
- **Data:** 2.000+ Förderprogramme (scraped + structured)

### Infrastructure
- **Hosting:** AWS / Hetzner
- **Container:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry, Prometheus, Grafana

---

## 📊 Projektstruktur

```
saas-project-8/
├── backend/
│   ├── app/
│   │   ├── api/              # API Routes
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── grants.py      # Fördermittel-Suche
│   │   │   │   ├── applications.py # Antragstellung
│   │   │   │   ├── documents.py   # Dokument-Generierung
│   │   │   │   └── users.py
│   │   ├── core/             # Core-Funktionalität
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/           # Database-Models
│   │   │   ├── user.py
│   │   │   ├── grant.py
│   │   │   ├── application.py
│   │   │   └── document.py
│   │   ├── services/         # Business-Logic
│   │   │   ├── grant_matcher.py   # AI-Matching
│   │   │   ├── application_writer.py # AI-Antrag
│   │   │   ├── compliance_checker.py
│   │   │   └── document_generator.py
│   │   ├── ai/               # AI-Komponenten
│   │   │   ├── rag.py        # RAG-System
│   │   │   ├── prompts.py    # Prompt-Templates
│   │   │   └── embeddings.py
│   │   └── main.py
│   ├── data/
│   │   ├── grants/           # Förderprogramm-Daten
│   │   │   ├── federal.json  # Bundesförderung
│   │   │   ├── state.json    # Landesförderung
│   │   │   └── eu.json       # EU-Förderung
│   │   └── templates/        # Antrags-Templates
│   ├── alembic/              # Database-Migrations
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   │   ├── (auth)/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── grants/   # Fördermittel-Suche
│   │   │   │   ├── applications/ # Anträge
│   │   │   │   └── documents/
│   │   │   └── layout.tsx
│   │   ├── components/       # React-Komponenten
│   │   │   ├── ui/           # shadcn/ui
│   │   │   ├── grant-card.tsx
│   │   │   ├── application-wizard.tsx
│   │   │   └── document-preview.tsx
│   │   ├── lib/              # Utils
│   │   │   ├── api.ts        # API-Client
│   │   │   └── utils.ts
│   │   └── types/            # TypeScript-Types
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.js
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚦 Quick Start

### Voraussetzungen
- Docker & Docker Compose
- Node.js 18+ (für lokale Frontend-Dev)
- Python 3.11+ (für lokale Backend-Dev)

### 1. Repository klonen & Setup
```bash
cd /opt/projects/saas-project-8

# Environment-Variablen
cp .env.example .env
nano .env  # API-Keys eintragen
```

### 2. Docker-Stack starten
```bash
# Alle Services starten
docker-compose up -d

# Logs anschauen
docker-compose logs -f
```

### 3. URLs
- **Backend-API:** http://localhost:8008
- **API-Docs:** http://localhost:8008/docs
- **Frontend:** http://localhost:3008
- **Qdrant (Vector DB):** http://localhost:6333
- **PostgreSQL:** localhost:5432

---

## 🔧 Development

### Backend (lokale Entwicklung)
```bash
cd backend

# Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Dependencies
pip install -r requirements.txt

# Database-Migration
alembic upgrade head

# Server starten
uvicorn app.main:app --reload --port 8008
```

### Frontend (lokale Entwicklung)
```bash
cd frontend

# Dependencies
npm install

# Dev-Server
npm run dev
```

---

## 📈 Roadmap

### Q1 2025: MVP
- [x] AI-Fördermittel-Matching
- [x] Basis-Antragsstellung
- [ ] 10 Beta-Kunden

### Q2 2025: Product-Market-Fit
- [ ] Vollautomatischer Antrag
- [ ] Multi-Programm-Optimierung
- [ ] 100 Kunden, 20M€ bewilligt

### Q3-Q4 2025: Scale
- [ ] Dashboard & Analytics
- [ ] Verwendungsnachweis-Automatisierung
- [ ] 500 Kunden, 100M€ bewilligt

---

## 💰 Business-Model

### Unit-Economics (Beispiel-Kunde)
**Förderung:** 500.000€ (ZIM + Digital Jetzt)  
**Unsere Provision (50%):** 250.000€

**COGS:**
- LLM-Kosten (GPT-4): 200€
- Experten-Review (10h × 80€): 800€
- Plattform: 100€
- **Total:** 1.100€

**Gross Margin:** 99,6%  
**LTV/CAC:** 275:1

### Revenue-Projection (3 Jahre)
| Jahr | Kunden | Ø Förderung | Bewilligte Summe | Revenue (50%) | EBITDA |
|------|--------|-------------|------------------|---------------|---------|
| 1 | 100 | 400k€ | 40M€ | 20M€ | 10M€ |
| 2 | 400 | 400k€ | 160M€ | 80M€ | 50M€ |
| 3 | 1.000 | 400k€ | 400M€ | 200M€ | 140M€ |

**Bewertung (Jahr 3):** 200M€ × 5-10 = **1-2 Mrd. €**

---

## 🔐 Sicherheit & Compliance

- ✅ **Datenschutz:** DSGVO-konform
- ✅ **Verschlüsselung:** End-to-End (AES-256)
- ✅ **Authentication:** JWT + OAuth2
- ✅ **Audit-Log:** Alle Aktionen protokolliert
- ✅ **Backup:** Täglich (PostgreSQL + Documents)

---

## 🆘 Support

Bei Fragen oder Problemen:
- **E-Mail:** support@grantgpt.de
- **Dokumentation:** `/docs` (Coming Soon)
- **Issues:** GitHub Issues

---

## 📝 Lizenz

Copyright © 2025 GrantGPT. Alle Rechte vorbehalten.

---

## 🎯 Warum GrantGPT funktioniert

### 1. Versteckter Riesen-Markt
- 160 Mrd. € Fördermittel/Jahr (nur DE)
- 90% der KMUs wissen nicht, dass sie Anspruch haben

### 2. KI macht es skalierbar
- Förderanträge sind 50-200 Seiten
- Nur KI kann das in 2 Stunden schreiben (statt 80h)

### 3. Erfolgsbasiertes Pricing
- 99,6% Gross Margin
- LTV/CAC: 275
- Kunde zahlt nur bei Erfolg (kein Risiko!)

### 4. Regierungs-Rückenwind
- Green Deal: 1 Billion € (bis 2030)
- Chips Act: 43 Mrd. €
- Regierungen WOLLEN, dass Geld abgerufen wird

### 5. First-Mover-Advantage
- Niemand macht AI-gestützte Antragsstellung
- 5+ Jahre Vorsprung (zu komplex zum Kopieren)

---

**Made with 🚀 to democratize access to 160 Mrd. € in funding**

