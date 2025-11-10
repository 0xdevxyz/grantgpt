# 🚀 GrantGPT - Installation Guide

## Voraussetzungen

- **Docker** & **Docker Compose** installiert
- **OpenAI API Key** ([hier erhalten](https://platform.openai.com/api-keys))
- Mind. 8GB RAM empfohlen
- Mind. 10GB freier Speicherplatz

## Installation (Development)

### 1. Repository klonen

```bash
git clone <repository-url> saas-project-8
cd saas-project-8
```

### 2. Environment konfigurieren

Kopiere die `.env.example` Datei und passe sie an:

```bash
cp .env.example .env
nano .env  # Oder ein anderer Editor
```

**Wichtig:** Setze deinen OpenAI API Key:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

Optional: Ändere Passwörter und Ports nach Bedarf.

### 3. Docker Stack starten

Starte alle Services (PostgreSQL, Redis, Qdrant, Backend, Celery, Frontend):

```bash
docker-compose up -d --build
```

Dies kann beim ersten Mal 5-10 Minuten dauern.

### 4. Datenbank initialisieren

Nach dem Start der Container, initialisiere die Datenbank (Alembic Migrations):

```bash
# TODO: Alembic Setup
# docker exec -it grantgpt-backend alembic upgrade head
```

### 5. Grant-Daten laden

Lade die initialen Förderprogramme in die Datenbank:

```bash
docker exec -it grantgpt-backend python scripts/seed_grants.py
```

Dieser Vorgang embedded ca. 5 Förderprogramme in Qdrant und dauert ~1-2 Minuten.

### 6. Fertig! Services öffnen

- **Frontend:** [http://localhost:3008](http://localhost:3008)
- **Backend API (Swagger):** [http://localhost:8008/docs](http://localhost:8008/docs)
- **Qdrant Dashboard:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

## Entwicklung

### Backend-Logs anschauen

```bash
docker logs -f grantgpt-backend
```

### Frontend-Logs anschauen

```bash
docker logs -f grantgpt-frontend
```

### Celery-Worker-Logs

```bash
docker logs -f grantgpt-celery
```

### Services neu starten

```bash
docker-compose restart
```

### Alles stoppen und löschen

```bash
docker-compose down -v
```

## Tests ausführen

```bash
# Backend Tests
docker exec -it grantgpt-backend pytest

# Frontend Tests  
docker exec -it grantgpt-frontend npm test
```

## Production Deployment

Für Production:

1. Ändere alle Passwörter in `.env`
2. Setze `DEBUG=False`
3. Generiere ein starkes `SECRET_KEY`
4. Nutze managed Services für PostgreSQL, Redis, Qdrant
5. Setze CORS-Origins richtig
6. Aktiviere HTTPS

## Troubleshooting

### "OpenAI API Key nicht gesetzt"

→ Prüfe `.env` Datei und `OPENAI_API_KEY`

### "Qdrant collection not found"

→ Führe `seed_grants.py` aus

### "Port bereits belegt"

→ Ändere Ports in `.env` (z.B. `BACKEND_PORT=8009`)

### "Celery tasks laufen nicht"

→ Prüfe Celery-Logs: `docker logs grantgpt-celery`

---

**Bei Fragen:** Siehe README.md oder öffne ein Issue.
