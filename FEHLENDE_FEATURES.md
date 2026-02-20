# 🔧 FörderScout AI - Fehlende Features & Implementierungsplan

**Stand:** 13. Februar 2026  
**Basierend auf:** Code-Analyse Backend + Frontend

---

## 📊 Übersicht Implementierungsstatus

| Komponente | Status | Vollständigkeit |
|------------|--------|-----------------|
| **Backend API** | ⚠️ Teilweise | 70% |
| **Frontend UI** | ⚠️ Teilweise | 60% |
| **AI-Services** | ✅ Vollständig | 95% |
| **Scraper** | ✅ Vollständig | 100% |
| **Datenbank** | ✅ Vollständig | 100% |
| **Deployment** | ⚠️ Vorbereitet | 80% |
| **Testing** | ⚠️ Basic | 40% |

---

## 🔴 KRITISCHE Lücken (Beta-Blocker)

### 1. Backend API - Applications Management

**Problem:** `applications.py` enthält nur Mock-Daten, keine DB-Integration

**Aktuell:**
```python
# /backend/app/api/v1/applications.py
@router.post("/")
async def create_application(application: ApplicationCreate):
    # TODO: Create in database
    return {
        "id": "mock-id",
        "status": "draft",
        ...
    }
```

**Fehlende Funktionen:**
- [ ] Echte DB-Speicherung in `applications` Tabelle
- [ ] CRUD-Operationen (Create, Read, Update, Delete)
- [ ] Status-Workflow (draft → in_progress → submitted → approved/rejected)
- [ ] Versionierung der Anträge
- [ ] Zuordnung zu User (current_user dependency)

**Lösung:**
```python
from app.models.application import Application
from sqlalchemy.orm import Session

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_application = Application(
        user_id=current_user.id,
        grant_id=application.grant_id,
        title=application.title,
        description=application.description,
        status="draft",
        created_at=datetime.utcnow()
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application
```

**Aufwand:** 12 Stunden

---

### 2. Backend API - Documents Generation

**Problem:** PDF/DOCX-Generierung ist implementiert, aber nicht in API integriert

**Aktuell:**
- `/backend/app/services/application_writer.py` ✅ Funktioniert
- `/backend/app/api/v1/documents.py` ❌ Nur Placeholder

**Fehlende Funktionen:**
- [ ] Endpunkt `/documents/{application_id}/generate` (PDF/DOCX)
- [ ] Endpunkt `/documents/{document_id}/download`
- [ ] Speicherung generierter Dokumente in `documents` Tabelle
- [ ] Datei-Upload in `/backend/storage/`
- [ ] Asynchrone Generierung via Celery

**Lösung:**
```python
@router.post("/{application_id}/generate")
async def generate_document(
    application_id: str,
    format: str = "pdf",  # pdf or docx
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Trigger Celery Task
    task = generate_application_document.delay(application_id, format)
    
    # Save document record
    document = Document(
        application_id=application_id,
        type=format,
        status="generating",
        task_id=task.id
    )
    db.add(document)
    db.commit()
    
    return {"task_id": task.id, "status": "generating"}
```

**Aufwand:** 8 Stunden

---

### 3. Backend API - Grants Details & Listing

**Problem:** `/grants/{grant_id}` und `/grants/` sind Placeholder

**Aktuell:**
```python
@router.get("/{grant_id}")
async def get_grant_detail(grant_id: str):
    # TODO: Query Qdrant or Database
    return {"id": grant_id, "name": "Mock Grant"}
```

**Fehlende Funktionen:**
- [ ] Grant-Details aus Qdrant abrufen
- [ ] Listing aller Grants mit Paginierung
- [ ] Filter (Kategorie, Region, Förderhöhe)
- [ ] Sortierung (Relevanz, Deadline, Förderhöhe)

**Lösung:**
```python
from app.services.qdrant_service import qdrant_service

@router.get("/{grant_id}")
async def get_grant_detail(grant_id: str):
    grant = qdrant_service.get_by_id(grant_id)
    if not grant:
        raise HTTPException(404, "Grant not found")
    return grant

@router.get("/")
async def list_grants(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    region: str = None
):
    grants = qdrant_service.search(
        filter={
            "must": [
                {"key": "category", "match": {"value": category}} if category else None,
                {"key": "region", "match": {"value": region}} if region else None
            ]
        },
        limit=limit,
        offset=skip
    )
    return grants
```

**Aufwand:** 6 Stunden

---

### 4. Celery Tasks - Database Persistence

**Problem:** Generierte Inhalte werden nicht in DB gespeichert

**Aktuell:**
```python
# /backend/app/tasks/application_tasks.py
@celery_app.task
def generate_application_content(application_id: str):
    # Generate content (works)
    content = writer.generate_all_sections(...)
    
    # TODO: Save to database
    # Currently content is lost after generation!
```

**Fehlende Funktionen:**
- [ ] Speicherung generierter Sections in `application_sections` Tabelle
- [ ] Status-Updates während Generierung
- [ ] Error-Handling mit Rollback
- [ ] Progress-Tracking (z.B. 3/7 Sections fertig)

**Lösung:**
```python
@celery_app.task
def generate_application_content(application_id: str):
    db = SessionLocal()
    try:
        application = db.query(Application).filter_by(id=application_id).first()
        application.status = "generating"
        db.commit()
        
        # Generate content
        content = writer.generate_all_sections(...)
        
        # Save each section
        for section_name, section_content in content.items():
            section = ApplicationSection(
                application_id=application_id,
                section_type=section_name,
                content=section_content,
                version=1
            )
            db.add(section)
        
        application.status = "draft"
        db.commit()
        
    except Exception as e:
        application.status = "error"
        db.commit()
        raise
    finally:
        db.close()
```

**Aufwand:** 6 Stunden

---

### 5. Frontend - Authentication System

**Problem:** Keine Login/Register-Pages, keine Session-Verwaltung

**Aktuell:**
- Dashboard zeigt Mock-Daten
- Kein Schutz von Routes
- Kommentar im Code: `// For now, without auth`

**Fehlende Funktionen:**
- [ ] `/login` Page mit Form
- [ ] `/register` Page mit Validation
- [ ] JWT-Token-Management (localStorage oder httpOnly cookies)
- [ ] Protected Routes mit Middleware
- [ ] Session-State (Zustand Store)
- [ ] Logout-Funktionalität
- [ ] Passwort-Reset (optional für MVP)

**Lösung:**

**1. Auth-Store (Zustand):**
```typescript
// /frontend/src/store/auth.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      login: async (email, password) => {
        const res = await fetch('/api/v1/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        set({ user: data.user, token: data.access_token });
      },
      logout: () => set({ user: null, token: null }),
      register: async (data) => { /* ... */ }
    }),
    { name: 'auth-storage' }
  )
);
```

**2. Protected Route Middleware:**
```typescript
// /frontend/src/middleware.ts
import { NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}
```

**3. Login Page:**
```typescript
// /frontend/src/app/login/page.tsx
'use client';
import { useAuth } from '@/store/auth';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await login(email, password);
    router.push('/dashboard');
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

**Aufwand:** 10 Stunden

---

### 6. Frontend - API Integration

**Problem:** Nur punktuelle `fetch`-Calls, kein zentraler Client

**Aktuell:**
```typescript
// In verschiedenen Pages verstreut:
const response = await fetch('http://localhost:8008/api/v1/grants/search', {
  method: 'POST',
  body: JSON.stringify(data)
});
```

**Fehlende Funktionen:**
- [ ] Zentraler API-Client (axios)
- [ ] Error-Handling (401, 404, 500)
- [ ] Loading-States
- [ ] Token-Injection (Authorization Header)
- [ ] Request/Response-Interceptors

**Lösung:**

**API-Client:**
```typescript
// /frontend/src/lib/api-client.ts
import axios from 'axios';
import { useAuth } from '@/store/auth';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8008',
});

// Request Interceptor (Token injection)
apiClient.interceptors.request.use((config) => {
  const token = useAuth.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor (Error handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuth.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**Typed API-Funktionen:**
```typescript
// /frontend/src/lib/api/grants.ts
import { apiClient } from '../api-client';

export const grantsApi = {
  search: async (query: string) => {
    const { data } = await apiClient.post('/api/v1/grants/search', { query });
    return data;
  },
  
  getDetails: async (grantId: string) => {
    const { data } = await apiClient.get(`/api/v1/grants/${grantId}`);
    return data;
  },
  
  list: async (params?: { skip?: number; limit?: number }) => {
    const { data } = await apiClient.get('/api/v1/grants', { params });
    return data;
  }
};
```

**Usage in Components:**
```typescript
'use client';
import { grantsApi } from '@/lib/api/grants';
import { useState } from 'react';

export default function SearchPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  
  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await grantsApi.search(query);
      setResults(data.matches);
    } catch (err) {
      setError('Fehler beim Suchen');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <>
      {loading && <Spinner />}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {results.map(...)}
    </>
  );
}
```

**Aufwand:** 8 Stunden

---

### 7. Frontend - Application Detail Page

**Problem:** Route `/dashboard/application/[id]` ist verlinkt, aber nicht implementiert

**Fehlende Funktionen:**
- [ ] Application-Details anzeigen
- [ ] Status-Anzeige (draft, in_progress, submitted, approved)
- [ ] Generierte Sections anzeigen
- [ ] Edit-Modus für Sections
- [ ] PDF/DOCX-Download-Button
- [ ] Versionshistorie

**Lösung:**
```typescript
// /frontend/src/app/dashboard/application/[id]/page.tsx
'use client';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { applicationsApi } from '@/lib/api/applications';

export default function ApplicationDetailPage() {
  const { id } = useParams();
  const [application, setApplication] = useState(null);
  
  useEffect(() => {
    applicationsApi.getDetails(id).then(setApplication);
  }, [id]);
  
  if (!application) return <Spinner />;
  
  return (
    <div>
      <h1>{application.title}</h1>
      <StatusBadge status={application.status} />
      
      <Tabs>
        <Tab label="Projektbeschreibung">
          <Section content={application.sections.project_description} />
        </Tab>
        <Tab label="Marktanalyse">
          <Section content={application.sections.market_analysis} />
        </Tab>
        {/* ... weitere Sections */}
      </Tabs>
      
      <Button onClick={() => downloadPDF(id)}>
        PDF herunterladen
      </Button>
    </div>
  );
}
```

**Aufwand:** 6 Stunden

---

### 8. Daten - Förderprogramme scrapen

**Problem:** Nur 5 Mock-Programme vorhanden, Ziel: 200+

**Aktuell:**
```bash
$ find backend/data/grants -name "*.json" | wc -l
5
```

**Scraper vorhanden für:**
- ✅ BAFA (`bafa_scraper.py`)
- ✅ KfW (`kfw_scraper.py`)
- ✅ SAB (`sab_scraper.py`)
- ✅ BMWK (`bmwk_scraper.py`)
- ✅ go-digital (`godigital_scraper.py`)
- ✅ Förderdatenbank (`foerderdatenbank_scraper.py`)

**Fehlende Schritte:**
- [ ] Alle Scraper ausführen
- [ ] JSON-Dateien in `/backend/data/grants/` speichern
- [ ] Embeddings generieren
- [ ] In Qdrant hochladen
- [ ] Datenqualität prüfen (Duplikate, fehlende Felder)

**Lösung:**
```bash
# 1. Alle Scraper ausführen
cd /opt/projects/saas-project-8/backend
python scripts/run_all_scrapers.py

# 2. Embeddings generieren und in Qdrant laden
python scripts/seed_comprehensive_grants.py

# 3. Verifizieren
curl http://localhost:6333/collections/grants | jq '.result.points_count'
# Sollte > 200 sein
```

**Aufwand:** 8 Stunden (inkl. Debugging & Qualitätsprüfung)

---

### 9. Deployment - Production Setup

**Problem:** Docker-Setup vorhanden, aber nicht auf https://funding.wpma.io deployt

**Aktuell:**
- ✅ `docker-compose.yml` funktioniert lokal
- ✅ Nginx-Config vorhanden (`/deployment/nginx/funding.wpma.io.conf`)
- ✅ SSL-Setup-Skript vorhanden (`/deployment/scripts/setup-ssl.sh`)
- ❌ Nicht auf Server deployt

**Fehlende Schritte:**
- [ ] Server-Zugang verifizieren (SSH)
- [ ] Docker + Docker-Compose installieren
- [ ] Projekt auf Server klonen
- [ ] `.env` für Production konfigurieren
- [ ] SSL-Zertifikat via Certbot
- [ ] Nginx als Reverse-Proxy
- [ ] Docker-Container starten
- [ ] Firewall-Regeln (80, 443, 22)
- [ ] Smoke-Tests

**Lösung:**
```bash
# Auf Server (SSH):
ssh root@85.215.125.171

# 1. Deployment-Skript ausführen
cd /opt/projects/saas-project-8
bash deployment/scripts/deploy.sh

# 2. Manuell prüfen:
docker-compose ps
curl https://funding.wpma.io/api/v1/health
```

**Aufwand:** 4 Stunden

---

## 🟡 WICHTIGE Lücken (für Public Launch)

### 10. Stripe Payment Integration (Frontend)

**Problem:** Stripe-Service im Backend vorhanden, aber kein Frontend-UI

**Fehlende Funktionen:**
- [ ] Pricing-Page mit 3 Tiers
- [ ] Checkout-Flow (Stripe Checkout)
- [ ] Success-Fee-Berechnung anzeigen
- [ ] Invoice-Download
- [ ] Subscription-Management-Page

**Aufwand:** 10 Stunden

---

### 11. Expert-Review-Modul (Tier 2/3)

**Problem:** Tier 2/3 bieten "Expert-Review", aber Feature fehlt komplett

**Fehlende Funktionen:**
- [ ] Admin-Interface für Reviewer
- [ ] Review-Workflow (zuweisen, kommentieren, freigeben)
- [ ] Notification-System (E-Mail + In-App)
- [ ] Feedback-Loop zum Kunden

**Aufwand:** 16 Stunden

---

### 12. Email-Automation

**Problem:** Keine automatischen E-Mails

**Fehlende Funktionen:**
- [ ] Welcome-E-Mail nach Registrierung
- [ ] Status-Updates (Antrag eingereicht, bewilligt)
- [ ] Deadline-Reminder
- [ ] Weekly-Digest (neue Förderprogramme)

**Lösung:**
```python
# /backend/app/services/email_service.py
from fastapi_mail import FastMail, MessageSchema

async def send_welcome_email(user: User):
    message = MessageSchema(
        subject="Willkommen bei FörderScout AI",
        recipients=[user.email],
        body=render_template("welcome.html", user=user),
        subtype="html"
    )
    await fastmail.send_message(message)
```

**Aufwand:** 8 Stunden

---

### 13. Admin-Dashboard

**Problem:** Keine interne Verwaltungs-Oberfläche

**Fehlende Funktionen:**
- [ ] User-Verwaltung (Liste, Details, Sperren)
- [ ] Application-Übersicht (alle Anträge, Filter)
- [ ] Grant-Management (hinzufügen, bearbeiten, löschen)
- [ ] Analytics (Conversion-Rates, Revenue)
- [ ] Scraper-Status & Logs

**Aufwand:** 20 Stunden

---

### 14. SEO & Landing-Page

**Problem:** Landing-Page ist minimal, keine SEO-Optimierung

**Fehlende Funktionen:**
- [ ] Hero-Section mit Value-Proposition
- [ ] Features-Section mit Icons
- [ ] Testimonials / Case-Studies
- [ ] FAQ-Section
- [ ] Meta-Tags (title, description, og:image)
- [ ] Sitemap.xml
- [ ] robots.txt

**Aufwand:** 12 Stunden

---

### 15. UI-Komponenten & Navigation

**Problem:** Keine konsistente Navigation, minimale UI

**Fehlende Funktionen:**
- [ ] Navbar mit Logo, Links, User-Menu
- [ ] Footer mit Links (Impressum, Datenschutz, AGB)
- [ ] Breadcrumbs
- [ ] Mobile-Responsive-Tests
- [ ] Dark-Mode (optional)

**Aufwand:** 8 Stunden

---

## 🟢 OPTIONALE Features (Post-Launch)

### 16. Deadline-Reminder

**Funktionen:**
- [ ] Automatische E-Mails 7/3/1 Tage vor Deadline
- [ ] In-App-Notification
- [ ] Kalender-Export (iCal)

**Aufwand:** 6 Stunden

---

### 17. Document-Upload (Bewilligungsbescheid)

**Funktionen:**
- [ ] Upload von PDFs (Bewilligungsbescheid)
- [ ] OCR-Extraktion (Fördersumme, Bewilligungsdatum)
- [ ] Automatische Success-Fee-Berechnung
- [ ] Trigger für Stripe-Rechnung

**Aufwand:** 12 Stunden

---

### 18. Team-Collaboration

**Funktionen:**
- [ ] Multi-User-Accounts (Team-Mitglieder einladen)
- [ ] Rollen (Owner, Editor, Viewer)
- [ ] Kommentare auf Sections
- [ ] Aktivitäts-Log

**Aufwand:** 24 Stunden

---

### 19. API für Partner (Steuerberater)

**Funktionen:**
- [ ] Public API mit API-Keys
- [ ] Webhooks (Application-Status-Changes)
- [ ] White-Label-Optionen
- [ ] Partner-Dashboard

**Aufwand:** 30 Stunden

---

### 20. Mobile-App

**Funktionen:**
- [ ] React Native App (iOS + Android)
- [ ] Push-Notifications
- [ ] Offline-Support
- [ ] Barcode-Scanner (für Dokumente)

**Aufwand:** 200+ Stunden (separates Projekt)

---

## 📋 Priorisierte To-Do-Liste

### Sprint 1: Beta-Readiness (Woche 1-2) - KRITISCH

**Ziel:** Minimale funktionsfähige Plattform

| # | Feature | Aufwand | Verantwortlich |
|---|---------|---------|----------------|
| 1 | Auth-System (Frontend) | 10h | Frontend-Dev |
| 2 | Applications CRUD (Backend) | 12h | Backend-Dev |
| 3 | Documents API (Backend) | 8h | Backend-Dev |
| 4 | Grants Details/Listing (Backend) | 6h | Backend-Dev |
| 5 | Celery DB-Persistence | 6h | Backend-Dev |
| 6 | Frontend API-Integration | 8h | Frontend-Dev |
| 7 | Application-Detail-Page | 6h | Frontend-Dev |
| 8 | Förderprogramme scrapen | 8h | Backend-Dev |
| 9 | Production-Deployment | 4h | DevOps |

**Gesamt:** 68 Stunden (~1,5 Wochen für 2 Devs)

---

### Sprint 2: Public-Launch-Readiness (Woche 3-4) - WICHTIG

**Ziel:** Vollständige User-Experience

| # | Feature | Aufwand | Verantwortlich |
|---|---------|---------|----------------|
| 10 | Stripe-Payment-Flow (Frontend) | 10h | Frontend-Dev |
| 11 | Email-Automation | 8h | Backend-Dev |
| 12 | SEO & Landing-Page | 12h | Frontend-Dev |
| 13 | Navbar/Footer | 8h | Frontend-Dev |
| 14 | Expert-Review-Modul | 16h | Full-Stack-Dev |
| 15 | Admin-Dashboard (Basic) | 20h | Full-Stack-Dev |

**Gesamt:** 74 Stunden (~1,5 Wochen für 2 Devs)

---

### Sprint 3: Post-Launch-Optimierung (Woche 5-8) - OPTIONAL

**Ziel:** Advanced Features & Skalierung

| # | Feature | Aufwand | Verantwortlich |
|---|---------|---------|----------------|
| 16 | Deadline-Reminder | 6h | Backend-Dev |
| 17 | Document-Upload | 12h | Full-Stack-Dev |
| 18 | Team-Collaboration | 24h | Full-Stack-Dev |
| 19 | Analytics-Dashboard | 16h | Full-Stack-Dev |
| 20 | Performance-Optimierung | 12h | DevOps |

**Gesamt:** 70 Stunden (~1,5 Wochen für 2 Devs)

---

## ✅ Definition of Done (DoD)

Jedes Feature gilt als "Done", wenn:

- [ ] Code implementiert und committed
- [ ] Unit-Tests geschrieben (min. 70% Coverage)
- [ ] Manuell getestet (Happy-Path + Edge-Cases)
- [ ] Code-Review durchgeführt
- [ ] Dokumentation aktualisiert
- [ ] Deployed auf Staging (oder Production)
- [ ] QA-Sign-Off

---

## 📊 Gesamt-Aufwand

| Sprint | Dauer | Aufwand | Team-Size |
|--------|-------|---------|-----------|
| **Sprint 1 (Beta)** | 2 Wochen | 68h | 2 Devs |
| **Sprint 2 (Launch)** | 2 Wochen | 74h | 2 Devs |
| **Sprint 3 (Post-Launch)** | 4 Wochen | 70h | 2 Devs |
| **GESAMT** | **8 Wochen** | **212h** | **2 Devs** |

**Bei 1 Full-Time-Dev (40h/Woche):** 5-6 Wochen bis Public Launch

---

## 🚨 Blocker & Abhängigkeiten

| Blocker | Abhängig von | Impact |
|---------|--------------|--------|
| Frontend-Auth | Backend JWT funktioniert ✅ | Mittel |
| Applications-Detail-Page | Applications-API implementiert | Hoch |
| Document-Download | Documents-API + Storage | Hoch |
| Stripe-Frontend | Stripe-Backend ✅ | Mittel |
| Expert-Review | Admin-Dashboard + Email | Niedrig |

**Aktuell keine kritischen Blocker!** Alle Dependencies sind entweder fertig oder parallelisierbar.

---

## 📞 Kontakt

**Fragen zu Features?** → [Projektleiter-Email]  
**Code-Repository:** `/opt/projects/saas-project-8`  
**Projekt-Docs:** `AMORTISIERUNGSPLAN.md`, `IMPLEMENTATION_SUMMARY.md`

---

**Letzte Aktualisierung:** 13. Februar 2026
