# 🚀 Deployment Guide: Funding.WPMA.io

Vollständige Anleitung zur Deployment des GrantGPT-Systems auf einem Production-Server.

---

## 📋 Inhaltsverzeichnis

1. [Voraussetzungen](#voraussetzungen)
2. [Server-Setup](#server-setup)
3. [DNS-Konfiguration](#dns-konfiguration)
4. [Automatisches Deployment](#automatisches-deployment)
5. [Manuelles Deployment](#manuelles-deployment)
6. [Firewall-Konfiguration](#firewall-konfiguration)
7. [Monitoring & Wartung](#monitoring--wartung)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Voraussetzungen

### Server-Anforderungen

- **OS:** Ubuntu 20.04+ / Debian 11+
- **RAM:** Minimum 4GB (empfohlen: 8GB+)
- **CPU:** 2+ Cores
- **Disk:** 20GB+ freier Speicher
- **Netzwerk:** Öffentliche IP-Adresse

### Software-Anforderungen

- Docker 20.10+
- Docker Compose 2.0+
- Nginx
- Certbot (für SSL)
- Git

### Domain-Anforderungen

- Domain oder Subdomain (z.B. `funding.wpma.io`)
- DNS-Zugriff für A-Record-Konfiguration

---

## 🖥️ Server-Setup

### 1. Basis-Software installieren

```bash
# System aktualisieren
sudo apt-get update && sudo apt-get upgrade -y

# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose installieren
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Nginx installieren
sudo apt-get install -y nginx

# Certbot installieren
sudo apt-get install -y certbot python3-certbot-nginx

# Git installieren (falls nicht vorhanden)
sudo apt-get install -y git
```

### 2. Projekt klonen

```bash
cd /opt/projects
git clone <YOUR_GITHUB_REPO_URL> saas-project-8
cd saas-project-8
```

### 3. Environment Variables konfigurieren

```bash
# .env.example kopieren
cp .env.example .env

# .env bearbeiten
nano .env
```

**Wichtige Variablen:**

```env
# Domain
FRONTEND_URL=https://funding.wpma.io
BACKEND_URL=https://funding.wpma.io
ALLOWED_ORIGINS=https://funding.wpma.io,http://localhost:3008

# Database
DATABASE_URL=postgresql://grantgpt:secure_password@postgres:5432/grantgpt

# Redis
REDIS_URL=redis://redis:6379/0

# Qdrant
QDRANT_URL=http://qdrant:6333

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key_here

# JWT
JWT_SECRET=your_very_secure_random_secret_here
SECRET_KEY=your_very_secure_random_secret_here
```

---

## 🌐 DNS-Konfiguration

### A-Record anlegen

1. **DNS-Provider öffnen** (z.B. Cloudflare, Hetzner DNS, etc.)
2. **A-Record hinzufügen:**
   - **Name:** `funding` (oder leer für Root-Domain)
   - **Type:** `A`
   - **Value:** `<DEINE_SERVER_IP>` (z.B. `85.215.125.171`)
   - **TTL:** `3600` (1 Stunde)

3. **Propagation prüfen:**
   ```bash
   dig funding.wpma.io +short
   # Sollte deine Server-IP zurückgeben
   ```

---

## 🤖 Automatisches Deployment

### Vollständiges Deployment (empfohlen)

```bash
cd /opt/projects/saas-project-8
sudo bash deployment/scripts/deploy.sh
```

**Was passiert:**
1. ✅ Prerequisites prüfen
2. ✅ SSL-Zertifikat einrichten
3. ✅ Nginx konfigurieren
4. ✅ Environment Variables aktualisieren
5. ✅ Docker Container bauen & starten
6. ✅ Deployment verifizieren

---

## 🔧 Manuelles Deployment

### Schritt 1: SSL-Zertifikat

```bash
sudo certbot certonly --nginx \
    -d funding.wpma.io \
    --non-interactive \
    --agree-tos \
    --email admin@wpma.io
```

### Schritt 2: Nginx konfigurieren

```bash
# Config kopieren
sudo cp deployment/nginx/funding.wpma.io.conf /etc/nginx/sites-available/

# Site aktivieren
sudo ln -sf /etc/nginx/sites-available/funding.wpma.io.conf /etc/nginx/sites-enabled/

# Config testen
sudo nginx -t

# Nginx neu laden
sudo systemctl reload nginx
```

### Schritt 3: Environment Variables aktualisieren

```bash
bash deployment/scripts/update-env.sh funding.wpma.io
```

### Schritt 4: Docker Container starten

```bash
# Container bauen
docker-compose build

# Container starten
docker-compose up -d

# Status prüfen
docker-compose ps

# Logs ansehen
docker-compose logs -f
```

---

## 🔥 Firewall-Konfiguration

### UFW (Ubuntu Firewall)

```bash
# UFW aktivieren
sudo ufw enable

# Ports öffnen
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Status prüfen
sudo ufw status
```

### Cloud Provider Firewall

**Wichtig:** Auch die Firewall deines Cloud-Providers konfigurieren!

**Hetzner Cloud:**
- Firewall → Rules → Inbound
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 22 (SSH)

**AWS:**
- Security Groups → Inbound Rules
- Port 80, 443, 22

**DigitalOcean:**
- Networking → Firewalls
- Inbound Rules für 80, 443, 22

---

## 📊 Monitoring & Wartung

### Container-Status prüfen

```bash
docker-compose ps
```

### Logs ansehen

```bash
# Alle Services
docker-compose logs -f

# Nur Backend
docker-compose logs -f backend

# Nur Frontend
docker-compose logs -f frontend
```

### Container neu starten

```bash
# Alle Services
docker-compose restart

# Einzelner Service
docker-compose restart backend
```

### Updates deployen

```bash
# Code aktualisieren
git pull origin main

# Container neu bauen & starten
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### SSL-Zertifikat erneuern

```bash
# Manuell erneuern
sudo certbot renew

# Auto-Renewal testen
sudo certbot renew --dry-run
```

**Auto-Renewal ist standardmäßig aktiv** via systemd timer.

---

## 🐛 Troubleshooting

### Problem: Container startet nicht

```bash
# Logs prüfen
docker-compose logs backend

# Container-Status
docker-compose ps

# Ports prüfen
sudo netstat -tulpn | grep -E '3008|8008|5432|6379|6333'
```

### Problem: SSL-Zertifikat funktioniert nicht

```bash
# Zertifikat-Status prüfen
sudo certbot certificates

# Nginx-Config testen
sudo nginx -t

# Nginx-Logs prüfen
sudo tail -f /var/log/nginx/funding.wpma.io.error.log
```

### Problem: Frontend zeigt Fehler

```bash
# Frontend-Logs
docker-compose logs frontend

# Browser-Console prüfen (F12)
# Network-Tab für API-Calls
```

### Problem: Backend API antwortet nicht

```bash
# Backend-Logs
docker-compose logs backend

# API direkt testen
curl http://localhost:8008/api/v1/health

# Qdrant-Status
curl http://localhost:6333/collections/grants
```

### Problem: Database-Verbindung fehlgeschlagen

```bash
# PostgreSQL-Container prüfen
docker-compose ps postgres

# Datenbank-Logs
docker-compose logs postgres

# Verbindung testen
docker-compose exec postgres psql -U grantgpt -d grantgpt -c "SELECT 1;"
```

---

## 📁 Projekt-Struktur

```
saas-project-8/
├── backend/              # FastAPI Backend
├── frontend/             # Next.js Frontend
├── deployment/           # Deployment-Konfigurationen
│   ├── nginx/           # Nginx-Configs
│   │   └── funding.wpma.io.conf
│   └── scripts/         # Deployment-Skripte
│       ├── deploy.sh    # Vollständiges Deployment
│       ├── setup-ssl.sh # SSL-Setup
│       ├── setup-nginx.sh # Nginx-Setup
│       └── update-env.sh # Env-Variablen aktualisieren
├── docker-compose.yml    # Docker-Orchestrierung
├── .env.example         # Environment-Variablen Template
└── DEPLOYMENT.md        # Diese Datei
```

---

## 🔐 Sicherheit

### Best Practices

1. **Environment Variables:**
   - Niemals `.env` in Git committen
   - Starke Passwörter für Datenbank & JWT
   - API-Keys sicher aufbewahren

2. **SSL/TLS:**
   - Immer HTTPS verwenden
   - Auto-Renewal für SSL aktiviert
   - Security Headers in Nginx

3. **Firewall:**
   - Nur notwendige Ports öffnen
   - SSH nur mit Key-Auth (kein Passwort)

4. **Updates:**
   - Regelmäßig System-Updates
   - Docker-Images aktuell halten
   - Dependencies aktualisieren

---

## 📞 Support

Bei Problemen:

1. **Logs prüfen:** `docker-compose logs -f`
2. **Container-Status:** `docker-compose ps`
3. **Nginx-Status:** `sudo systemctl status nginx`
4. **SSL-Status:** `sudo certbot certificates`

---

## ✅ Deployment-Checkliste

- [ ] Server vorbereitet (Docker, Nginx, Certbot)
- [ ] DNS A-Record konfiguriert
- [ ] Firewall-Regeln gesetzt (80, 443, 22)
- [ ] `.env` Datei konfiguriert
- [ ] SSL-Zertifikat installiert
- [ ] Nginx konfiguriert
- [ ] Docker Container laufen
- [ ] Frontend erreichbar: `https://funding.wpma.io`
- [ ] Backend API erreichbar: `https://funding.wpma.io/api`
- [ ] SSL-Renewal getestet

---

**🎉 Viel Erfolg mit deinem Deployment!**
