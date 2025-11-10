# 🌐 GrantGPT - Remote-Setup Guide

## Wichtig: Remote-Betrieb (kein localhost!)

Da Sie remote arbeiten, müssen Sie **Server-IPs** statt `localhost` verwenden.

## 📝 Setup-Schritte

### 1. Server-IP herausfinden

```bash
# Auf dem Remote-Server:
hostname -I
# Oder:
ip addr show | grep "inet " | grep -v 127.0.0.1
```

Beispiel-Ausgabe: `192.168.1.100` (Ihre Server-IP)

### 2. .env Datei konfigurieren

```bash
cd /opt/projects/saas-project-8
cp .env.example .env
nano .env
```

**Wichtig:** Ersetze `your-server-ip` mit deiner echten Server-IP:

```env
# OpenRouter API Key (WICHTIG!)
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Remote URLs mit Server-IP
BACKEND_URL=http://192.168.1.100:8008
FRONTEND_URL=http://192.168.1.100:3008

# CORS erlauben
ALLOWED_ORIGINS=http://192.168.1.100:3008,http://192.168.1.100:3000
```

### 3. Docker-Stack starten

```bash
docker-compose up -d --build
```

### 4. Services prüfen

```bash
# Status checken
docker ps

# Logs anschauen
docker logs grantgpt-backend
docker logs grantgpt-frontend
```

### 5. Grant-Daten laden

```bash
docker exec -it grantgpt-backend python scripts/seed_grants.py
```

### 6. Im Browser öffnen

**Von deinem lokalen Rechner aus:**

- Frontend: `http://192.168.1.100:3008` (deine Server-IP!)
- Backend API: `http://192.168.1.100:8008/docs`
- Qdrant: `http://192.168.1.100:6333/dashboard`

---

## 🔥 OpenRouter Setup

### OpenRouter API Key erhalten:

1. Gehe zu: https://openrouter.ai/
2. Registriere dich / Login
3. Gehe zu: https://openrouter.ai/keys
4. Erstelle einen neuen API Key
5. Kopiere den Key (beginnt mit `sk-or-v1-...`)

### In .env eintragen:

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### Modelle:

GrantGPT nutzt via OpenRouter:
- **Chat/Generation:** `anthropic/claude-3.5-sonnet` (beste Qualität)
- **Embeddings:** `openai/text-embedding-3-large` (via OpenRouter)

### Fallback zu OpenAI:

Falls du keinen OpenRouter-Key hast, kannst du auch OpenAI nutzen:

```env
OPENAI_API_KEY=sk-your-openai-key
OPENROUTER_API_KEY=  # leer lassen
```

---

## 🛠️ Troubleshooting

### Problem: "Cannot connect to backend"

**Lösung:**
1. Prüfe ob Backend läuft: `docker logs grantgpt-backend`
2. Prüfe Firewall: Port 8008 muss offen sein
3. Prüfe CORS in `.env`: `ALLOWED_ORIGINS` muss deine Frontend-URL enthalten

```bash
# Firewall-Port öffnen (Ubuntu/Debian)
sudo ufw allow 8008
sudo ufw allow 3008
sudo ufw allow 6333
```

### Problem: "OpenRouter API error"

**Lösung:**
1. Prüfe API Key: `echo $OPENROUTER_API_KEY`
2. Prüfe Credits auf OpenRouter Dashboard
3. Logs checken: `docker logs grantgpt-backend`

### Problem: "Frontend zeigt keine Daten"

**Lösung:**
1. Prüfe `NEXT_PUBLIC_API_URL` in Frontend-Container:
   ```bash
   docker exec grantgpt-frontend env | grep NEXT_PUBLIC
   ```
2. Sollte deine Backend-URL sein (mit Server-IP!)

### Problem: "Connection refused to localhost"

**Lösung:**
Du arbeitest remote! Ersetze **alle** `localhost` durch deine Server-IP:
- In `.env`: `BACKEND_URL`, `FRONTEND_URL`, `ALLOWED_ORIGINS`
- Im Browser: Nutze Server-IP statt localhost

---

## 🔒 Sicherheit (für Production)

### Wichtig vor Production-Deployment:

1. **Ändere alle Passwörter in `.env`:**
   ```bash
   # Generiere sichere Passwörter
   openssl rand -base64 32
   ```

2. **HTTPS aktivieren** (nginx reverse proxy + Let's Encrypt)

3. **Firewall konfigurieren:**
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   ```

4. **Docker-Ports nicht öffentlich:**
   In `docker-compose.yml`:
   ```yaml
   ports:
     - "127.0.0.1:5432:5432"  # PostgreSQL nur lokal
   ```

---

## 📊 Monitoring

### Container-Status:

```bash
docker ps -a
docker stats
```

### Logs live verfolgen:

```bash
# Alle Logs
docker-compose logs -f

# Nur Backend
docker logs -f grantgpt-backend

# Nur Celery (Background-Jobs)
docker logs -f grantgpt-celery-worker
```

### Qdrant-Status:

```bash
curl http://192.168.1.100:6333/collections
```

---

## 🚀 Testen

### Backend-API testen:

```bash
# Health Check
curl http://192.168.1.100:8008/health

# Grant-Suche testen
curl -X POST http://192.168.1.100:8008/api/v1/grants/ \
  -H "Content-Type: application/json" \
  -d '{"query": "AI Innovation", "limit": 3}'
```

### Frontend im Browser:

1. Öffne: `http://192.168.1.100:3008`
2. Navigiere zu "Fördermittel-Suche"
3. Beschreibe ein Projekt
4. Klicke "Suchen"
5. Sollte Top-Matches anzeigen

---

## 📞 Support

Bei Problemen:
1. Prüfe Logs: `docker-compose logs`
2. Prüfe .env: `cat .env`
3. Prüfe Netzwerk: `docker network inspect grantgpt-network`

Häufige Fehler sind:
- ❌ Localhost statt Server-IP
- ❌ Fehlender OpenRouter API Key
- ❌ Firewall blockiert Ports
- ❌ CORS nicht richtig konfiguriert

---

**Viel Erfolg! 🚀**

