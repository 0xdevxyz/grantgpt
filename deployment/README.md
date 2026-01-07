# 📦 Deployment-Konfigurationen

Dieses Verzeichnis enthält alle notwendigen Konfigurationsdateien und Skripte für das Deployment von Funding.WPMA.io.

## 📁 Struktur

```
deployment/
├── nginx/                    # Nginx-Konfigurationsdateien
│   └── funding.wpma.io.conf  # Reverse Proxy Config für funding.wpma.io
└── scripts/                  # Deployment-Skripte
    ├── deploy.sh            # Vollständiges automatisches Deployment
    ├── setup-ssl.sh         # SSL-Zertifikat Setup (Let's Encrypt)
    ├── setup-nginx.sh       # Nginx-Konfiguration
    └── update-env.sh        # Environment Variables aktualisieren
```

## 🚀 Quick Start

### Vollständiges Deployment

```bash
sudo bash deployment/scripts/deploy.sh
```

Dieses Skript führt automatisch alle notwendigen Schritte aus:
1. Prerequisites prüfen
2. SSL-Zertifikat einrichten
3. Nginx konfigurieren
4. Environment Variables aktualisieren
5. Docker Container bauen & starten
6. Deployment verifizieren

## 📋 Einzelne Schritte

### SSL-Setup

```bash
bash deployment/scripts/setup-ssl.sh
```

### Nginx-Setup

```bash
bash deployment/scripts/setup-nginx.sh
```

### Environment Variables aktualisieren

```bash
bash deployment/scripts/update-env.sh funding.wpma.io
```

## 🔧 Nginx-Konfiguration

Die Nginx-Config (`nginx/funding.wpma.io.conf`) enthält:

- ✅ HTTP → HTTPS Redirect
- ✅ SSL/TLS Konfiguration
- ✅ Security Headers
- ✅ Reverse Proxy für Frontend (Port 3008)
- ✅ Reverse Proxy für Backend API (Port 8008)
- ✅ Health Check Endpoint

**Installation:**

```bash
sudo cp deployment/nginx/funding.wpma.io.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/funding.wpma.io.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📝 Anpassungen

### Andere Domain verwenden

1. **Nginx-Config anpassen:**
   ```bash
   # In nginx/funding.wpma.io.conf
   # Alle "funding.wpma.io" durch deine Domain ersetzen
   ```

2. **SSL-Setup:**
   ```bash
   # In setup-ssl.sh
   DOMAIN="deine-domain.de"
   ```

3. **Deployment-Skript:**
   ```bash
   # deploy.sh mit Domain-Parameter aufrufen
   sudo bash deployment/scripts/deploy.sh
   ```

## 🔐 Sicherheit

- ✅ Alle Skripte prüfen Prerequisites
- ✅ SSL-Zertifikate mit Let's Encrypt
- ✅ Security Headers in Nginx
- ✅ Keine sensiblen Daten in Git

## 📚 Weitere Dokumentation

Siehe [DEPLOYMENT.md](../DEPLOYMENT.md) für die vollständige Deployment-Anleitung.
