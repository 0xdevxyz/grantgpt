# 🎯 FörderScout AI - Sofortmaßnahmen (Diese Woche)

**Datum:** 13. Februar 2026  
**Ziel:** Beta-Launch-Readiness in 5-6 Arbeitstagen  
**Team:** 1 Full-Stack-Entwickler (empfohlen: 2 Devs parallel)

---

## 📅 Wochenplan (Tag für Tag)

### 🔴 Tag 1 (Montag): Backend-Kern-Features - 8 Stunden

#### Vormittag (4h): Applications API vollständig implementieren

**Ziel:** CRUD-Operationen mit echter DB-Integration

**Tasks:**
1. [ ] `POST /api/v1/applications` - Create mit User-ID
   - DB-Model verwenden (`Application`)
   - User aus JWT-Token extrahieren (`current_user`)
   - Initial status: "draft"
   - Timestamp setzen

2. [ ] `GET /api/v1/applications` - Liste aller Anträge des Users
   - Filter nach Status (draft, submitted, approved)
   - Pagination (skip, limit)
   - Sortierung nach created_at DESC

3. [ ] `GET /api/v1/applications/{id}` - Details eines Antrags
   - Inkl. Sections aus DB
   - 404 wenn nicht gefunden oder nicht Owner

4. [ ] `PATCH /api/v1/applications/{id}` - Antrag aktualisieren
   - Nur Owner darf updaten
   - Status-Workflow validieren

5. [ ] `DELETE /api/v1/applications/{id}` - Antrag löschen
   - Soft-Delete (deleted_at setzen)
   - Nur bei status="draft"

**Code-Location:** `/backend/app/api/v1/applications.py`

**Test:**
```bash
curl -X POST http://localhost:8008/api/v1/applications \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"grant_id":"...", "title":"Test"}'
```

#### Nachmittag (4h): Documents API & Celery-Persistence

**Ziel:** PDF/DOCX-Generierung mit DB-Speicherung

**Tasks:**
1. [ ] `POST /api/v1/documents/{application_id}/generate` - Async-Generierung
   - Celery-Task triggern
   - Document-Record in DB erstellen (status="generating")
   - Task-ID zurückgeben

2. [ ] `GET /api/v1/documents/{document_id}` - Status abfragen
   - "generating", "completed", "error"

3. [ ] `GET /api/v1/documents/{document_id}/download` - PDF/DOCX herunterladen
   - FileResponse mit korrekten Headers
   - Content-Disposition: attachment

4. [ ] Celery-Task: `generate_application_document.py`
   - Application-Sections aus DB laden
   - `ApplicationWriter` verwenden
   - PDF/DOCX in `/storage/documents/` speichern
   - Document-Record updaten (status="completed", file_path)

**Code-Location:** 
- `/backend/app/api/v1/documents.py`
- `/backend/app/tasks/application_tasks.py`

**Test:**
```bash
curl -X POST http://localhost:8008/api/v1/documents/app-123/generate \
  -H "Authorization: Bearer <TOKEN>"
# Response: {"task_id": "...", "status": "generating"}

# Nach 30 Sekunden:
curl http://localhost:8008/api/v1/documents/doc-456/download \
  -H "Authorization: Bearer <TOKEN>" \
  -o antrag.pdf
```

---

### 🔴 Tag 2 (Dienstag): Backend-Vervollständigung - 8 Stunden

#### Vormittag (4h): Grants API finalisieren

**Ziel:** Vollständige Grant-Suche, Details, Listing

**Tasks:**
1. [ ] `GET /api/v1/grants/{grant_id}` - Details aus Qdrant
   - `qdrant_service.get_by_id(grant_id)`
   - 404 wenn nicht gefunden
   - Schema: `GrantDetail`

2. [ ] `GET /api/v1/grants` - Liste mit Filtern
   - Pagination (skip, limit)
   - Filter: category, region, min_funding, max_funding
   - Qdrant-Filter-Syntax verwenden

3. [ ] `POST /api/v1/grants/search` - Bereits vorhanden, nur testen

**Code-Location:** `/backend/app/api/v1/grants.py`

**Test:**
```bash
curl http://localhost:8008/api/v1/grants?limit=10&category=innovation
curl http://localhost:8008/api/v1/grants/grant-id-123
```

#### Nachmittag (4h): Celery-Tasks DB-Speicherung

**Ziel:** Generierte Inhalte persistent machen

**Tasks:**
1. [ ] Task: `generate_application_content` - DB-Speicherung
   - Application aus DB laden
   - Status auf "generating" setzen
   - Alle 7 Sections generieren (Writer-Service)
   - Jede Section in `application_sections` Tabelle speichern
   - Status auf "draft" setzen
   - Error-Handling mit Rollback

2. [ ] Model: `ApplicationSection` prüfen
   - Felder: application_id, section_type, content, version, created_at
   - Relationship zu `Application`

**Code-Location:** `/backend/app/tasks/application_tasks.py`

**Test:**
```bash
# Celery-Task manuell triggern
docker exec grantgpt-backend python -c "
from app.tasks.application_tasks import generate_application_content
generate_application_content.delay('app-123')
"

# Logs prüfen
docker logs grantgpt-celery-worker -f
```

---

### 🟠 Tag 3 (Mittwoch): Frontend-Auth & API-Client - 8 Stunden

#### Vormittag (4h): Authentication-System

**Ziel:** Login/Register mit Session-Management

**Tasks:**
1. [ ] Zustand-Store für Auth
   - `useAuth` Hook
   - login, logout, register Functions
   - Persist in localStorage
   - Token-Auto-Refresh (optional)

2. [ ] `/login` Page
   - Form mit react-hook-form + zod
   - Error-Handling (401, 500)
   - Redirect nach Dashboard bei Erfolg

3. [ ] `/register` Page
   - Form mit Validierung (email, password, company_name)
   - Success-Message
   - Redirect nach Login

4. [ ] Middleware für Protected Routes
   - `middleware.ts` prüfen Token
   - Redirect nach `/login` wenn fehlt

**Code-Location:** 
- `/frontend/src/store/auth.ts`
- `/frontend/src/app/login/page.tsx`
- `/frontend/src/app/register/page.tsx`
- `/frontend/src/middleware.ts`

**Test:**
- Registrierung → Login → Dashboard
- Logout → Kein Zugriff auf /dashboard
- Direkter Aufruf /dashboard → Redirect /login

#### Nachmittag (4h): Zentraler API-Client

**Ziel:** Axios-Client mit Interceptors

**Tasks:**
1. [ ] `api-client.ts` erstellen
   - axios.create mit baseURL
   - Request-Interceptor: Token in Header
   - Response-Interceptor: 401 → Logout

2. [ ] Typed API-Funktionen:
   - `/lib/api/auth.ts` (login, register, me)
   - `/lib/api/grants.ts` (search, list, getDetails)
   - `/lib/api/applications.ts` (create, list, getDetails, update, delete)
   - `/lib/api/documents.ts` (generate, download)

3. [ ] Error-Handling & Loading-States
   - Custom Hook: `useApi`
   - Loading-Spinner-Komponente
   - Error-Toast-Komponente

**Code-Location:** 
- `/frontend/src/lib/api-client.ts`
- `/frontend/src/lib/api/*.ts`

**Test:**
```typescript
// In Browser-Console:
import { grantsApi } from '@/lib/api/grants';
const results = await grantsApi.search('Digitalisierung');
console.log(results);
```

---

### 🟠 Tag 4 (Donnerstag): Frontend-Pages vervollständigen - 8 Stunden

#### Vormittag (4h): Application-Detail-Page

**Ziel:** Vollständige Anzeige eines Antrags

**Tasks:**
1. [ ] `/dashboard/application/[id]/page.tsx` erstellen
   - Dynamic Route mit useParams
   - API-Call: `applicationsApi.getDetails(id)`
   - Loading-State während API-Call
   - Error-State bei 404

2. [ ] UI-Komponenten:
   - Header mit Titel + Status-Badge
   - Tabs für Sections (Projektbeschreibung, Markt, Budget, ...)
   - Edit-Button (öffnet Wizard im Edit-Modus)
   - Download-Button (PDF/DOCX)
   - Versionshistorie (optional)

3. [ ] PDF-Download-Funktion
   ```typescript
   const downloadPDF = async (appId: string) => {
     const blob = await documentsApi.download(appId, 'pdf');
     const url = window.URL.createObjectURL(blob);
     const a = document.createElement('a');
     a.href = url;
     a.download = `antrag-${appId}.pdf`;
     a.click();
   };
   ```

**Code-Location:** `/frontend/src/app/dashboard/application/[id]/page.tsx`

**Test:**
- Navigiere vom Dashboard zu einem Antrag
- Alle Sections werden angezeigt
- PDF-Download funktioniert

#### Nachmittag (4h): UI-Verbesserungen

**Ziel:** Konsistente Navigation & Error-Handling

**Tasks:**
1. [ ] Navbar-Komponente
   - Logo (links)
   - Navigation: Dashboard, Suche
   - User-Menu (rechts): Profil, Logout
   - Mobile-Responsive (Hamburger-Menu)

2. [ ] Footer-Komponente
   - Links: Impressum, Datenschutz, AGB
   - Copyright-Notice

3. [ ] Loading-Spinner-Komponente
   - Zentrale Spinner-Komponente
   - Skelett-Loader für Tabellen/Listen

4. [ ] Error-Handling
   - Toast-Notifications (react-hot-toast o.ä.)
   - Error-Boundary für unerwartete Fehler

5. [ ] Dashboard-Integration
   - API-Calls statt Mock-Daten
   - Echte Statistiken (Anzahl Anträge, Status)

**Code-Location:** 
- `/frontend/src/components/Navbar.tsx`
- `/frontend/src/components/Footer.tsx`
- `/frontend/src/components/Spinner.tsx`

**Test:**
- Navbar erscheint auf allen Seiten
- Footer am Ende
- Error-Toast bei fehlgeschlagenem API-Call

---

### 🟡 Tag 5 (Freitag): Scraping & Deployment - 8 Stunden

#### Vormittag (4h): Förderprogramme scrapen

**Ziel:** 200+ Programme in Qdrant

**Tasks:**
1. [ ] Alle Scraper ausführen
   ```bash
   cd /opt/projects/saas-project-8/backend
   python scripts/scraper/bafa_scraper.py
   python scripts/scraper/kfw_scraper.py
   python scripts/scraper/sab_scraper.py
   python scripts/scraper/bmwk_scraper.py
   python scripts/scraper/godigital_scraper.py
   python scripts/scraper/foerderdatenbank_scraper.py
   ```

2. [ ] Daten-Qualität prüfen
   - JSON-Dateien in `/backend/data/grants/` prüfen
   - Duplikate entfernen
   - Fehlende Felder ergänzen (z.B. funding_max)

3. [ ] Embeddings generieren & in Qdrant laden
   ```bash
   python scripts/seed_comprehensive_grants.py
   ```

4. [ ] Verifizieren
   ```bash
   curl http://localhost:6333/collections/grants | jq '.result.points_count'
   # Sollte > 200 sein
   ```

**Code-Location:** `/backend/scripts/scraper/*.py`

**Erwartetes Ergebnis:**
- 200-300 Förderprogramme in Qdrant
- Such-Qualität testen (semantische Suche)

#### Nachmittag (4h): Production-Deployment

**Ziel:** Live auf https://funding.wpma.io

**Tasks:**
1. [ ] Server-Zugriff prüfen
   ```bash
   ssh root@funding.wpma.io
   # oder IP: 85.215.125.171
   ```

2. [ ] Projekt auf Server deployen
   ```bash
   # Auf Server:
   cd /opt/projects/saas-project-8
   git pull origin main
   
   # .env für Production anpassen
   cp .env.example .env
   nano .env
   # FRONTEND_URL=https://funding.wpma.io
   # BACKEND_URL=https://funding.wpma.io
   # OPENROUTER_API_KEY=...
   ```

3. [ ] Deployment-Skript ausführen
   ```bash
   bash deployment/scripts/deploy.sh
   ```
   
   Oder manuell:
   ```bash
   # SSL-Zertifikat
   sudo certbot certonly --nginx -d funding.wpma.io
   
   # Nginx-Config
   sudo cp deployment/nginx/funding.wpma.io.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/funding.wpma.io.conf /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   
   # Docker-Container
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

4. [ ] Smoke-Tests
   ```bash
   # Health-Check
   curl https://funding.wpma.io/api/v1/health
   
   # Frontend
   curl https://funding.wpma.io
   
   # API-Docs
   open https://funding.wpma.io/docs
   ```

5. [ ] Monitoring aktivieren
   - [ ] Sentry DSN in .env
   - [ ] UptimeRobot-Monitor einrichten
   - [ ] Logs prüfen: `docker-compose logs -f`

**Test:**
- ✅ https://funding.wpma.io lädt
- ✅ Login funktioniert
- ✅ Grant-Search funktioniert
- ✅ Application-Erstellung funktioniert

---

## ⏱️ Zeitaufwand Gesamt

| Tag | Thema | Stunden | Kumulativ |
|-----|-------|---------|-----------|
| **Tag 1** | Backend (Applications + Documents) | 8h | 8h |
| **Tag 2** | Backend (Grants + Celery) | 8h | 16h |
| **Tag 3** | Frontend (Auth + API-Client) | 8h | 24h |
| **Tag 4** | Frontend (Detail-Page + UI) | 8h | 32h |
| **Tag 5** | Scraping + Deployment | 8h | 40h |

**Gesamt: 40 Stunden (1 Woche Vollzeit)**

Bei 2 Entwicklern parallel: **2,5 Tage** (Backend + Frontend gleichzeitig)

---

## ✅ Definition of Done (Ende Woche)

**Beta-Launch-Ready bedeutet:**

- [x] User kann sich registrieren und einloggen
- [x] User kann nach Förderprogrammen suchen (200+ Programme)
- [x] User kann einen Antrag erstellen (Wizard)
- [x] User kann Antrags-Details sehen
- [x] User kann PDF/DOCX herunterladen
- [x] System läuft auf https://funding.wpma.io
- [x] SSL ist aktiv
- [x] Monitoring ist aktiv
- [x] Keine kritischen Bugs

**Noch NICHT notwendig für Beta:**
- ❌ Payment-Integration (kommt erst bei Bewilligung)
- ❌ Expert-Review (Tier 2/3, Post-Launch)
- ❌ Email-Automation (nice-to-have)
- ❌ Admin-Dashboard (intern, nicht User-facing)

---

## 🚨 Risiken & Blocker

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| **Scraper liefern zu wenig Daten** | Mittel | Timeout erhöhen, Rate-Limiting beachten |
| **Deployment schlägt fehl** | Niedrig | Lokales Docker-Setup bereits getestet |
| **API-Performance** | Niedrig | Caching aktivieren (Redis) |
| **Frontend-Bugs** | Mittel | Tägliches Testing, Error-Boundaries |
| **OpenRouter-API-Limit** | Niedrig | Fallback auf OpenAI, Rate-Limiting |

**Notfall-Plan:**
- Bei kritischen Blockern: Feature temporär deaktivieren (z.B. PDF-Download)
- Beta-Launch notfalls ohne PDF-Export (nur online anzeigen)
- Monitoring: Sentry meldet Fehler sofort

---

## 📞 Daily-Standup (empfohlen)

**Zeit:** Täglich 9:00 Uhr (15 Min.)

**Agenda:**
1. Was habe ich gestern geschafft?
2. Was mache ich heute?
3. Gibt es Blocker?

**Tool:** Slack, Discord, oder Telefon

---

## 🎯 Nach dieser Woche

**Nächste Schritte (Woche 2):**
1. Beta-Einladungen versenden (20 Kunden)
2. Onboarding-Calls durchführen
3. Feedback sammeln
4. Erste Bugs fixen
5. Vorbereitung Public-Launch (Stripe, Email, SEO)

**Dokumentation:**
- `AMORTISIERUNGSPLAN.md` - Gesamtstrategie
- `FEHLENDE_FEATURES.md` - Vollständige Feature-Liste
- `IMPLEMENTATION_SUMMARY.md` - Technische Übersicht

---

## 💪 Motivation

**Diese Woche entscheidet über den Erfolg des Projekts!**

Nach 40 Stunden harter Arbeit:
- ✅ Funktionsfähige Plattform
- ✅ Live auf Production
- ✅ Bereit für erste Kunden
- ✅ Potenzial: 4,3 Mio. € Profit Jahr 1
- ✅ Exit-Potenzial: 700 Mio. - 1,2 Mrd. €

**Let's go! 🚀**
