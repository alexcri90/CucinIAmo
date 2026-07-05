# Christmas Menu Generator - Documento Tecnico di Progetto

> **🎄 Generatore di Menù Natalizi Personalizzati con AI**  
> Framework: **Datapizza AI** | LLM: **Google Gemini 2.5 Flash** | Linguaggio: **Python 3.12 + React/TypeScript**

---

## 📊 Stato del Progetto

**Ultimo aggiornamento:** 4 Luglio 2026  
**Versione corrente:** 0.16.0  
**Fasi completate:** 14/14 + migrazione Firebase

### ✅ Fasi Completate

| Fase | Nome | Stato | Note |
|------|------|-------|------|
| **1** | Setup e Fondamenta | ✅ Completata | Python 3.12, Virtual env, Datapizza AI 0.0.9 |
| **2** | Data Models Pydantic | ✅ Completata | 15+ modelli validati, JSON Schema generato |
| **3** | Custom Tools | ✅ Completata | 8 tool funzionanti, tutti testati |
| **4** | Sistema di Agenti | ✅ Completata | 3 agenti multi-agent con collaborazione |
| **5** | Prompt Engineering | ✅ Completata | Template ottimizzati per Gemini |
| **6** | Structured Responses | ✅ Completata | Fallback robusto per limitazioni Gemini API |
| **7** | Memory & Sessions | ✅ Completata | Memory Datapizza AI per rigenerazione contestualizzata |
| **9** | Backend API | ✅ Completata | FastAPI funzionante con tutti gli endpoint |
| **12** | Frontend React | ✅ Completata | React + TypeScript + Vite, UI funzionante |
| **13** | Testing & QA | ✅ Completata | 120 test pytest, copertura completa modelli/tools/API/services/memory |
| **15** | UI/UX Polish | ✅ Completata | CSS professionale, layout centrato, bug fix tipi |
| **16** | Frontend Rigenerazione | ✅ Completata | Pulsanti UI per rigenerare singole portate con feedback opzionale |

### 🚧 Prossime Fasi

| Fase | Nome | Priorità | Stima | Note |
|------|------|----------|-------|------|
| **14** | Deployment | 🔥 Alta | 2-3h | Docker + hosting (Railway/Vercel) |
| **10** | Sistema di Export (PDF) | ⚡ Media | 1-2h | Opzionale - già presente stampa browser |
| **8** | Pipeline Orchestrazione | ⚡ Bassa | Opzionale | Skippata |
| **11** | Tracing & Observability | ⚡ Bassa | Opzionale | Skippata |

### ✅ Ultimo Aggiornamento (4 Luglio 2026)

**v0.16.0 - Migrazione a Firebase (hosting 100% gratuito, piano Spark):**
- ✅ Web app pubblicata su **Firebase Hosting** (niente più Render.com)
- ✅ **Login con Google** obbligatorio (Firebase Authentication)
- ✅ **Allowlist** delle email autorizzate su Firestore (collection `allowlist`, gestita dal proprietario dalla console; security rules in `firestore.rules`)
- ✅ Generazione menù **client-side** via **Firebase AI Logic** (Gemini Developer API, free tier): niente backend in produzione, zero costi possibili senza carta di credito
- ✅ **Selettore modello Gemini nella UI** (gemini-2.5-flash, flash-lite, 2.5-pro, gemini-3-flash-preview) — nuovo file `frontend/src/services/aiService.ts` con porting dei prompt di `prompt_templates.py`
- ✅ Fix bug: dopo la rigenerazione di una portata la lista spesa spariva (il frontend leggeva `updated_shopping_list` che il backend non restituiva); ora viene ricalcolata client-side
- ✅ Il backend Python/FastAPI/Datapizza resta nel repo come demo multi-agent locale (120 test invariati e passanti)
- ✅ Nuovi file: `firebase.json`, `.firebaserc`, `firestore.rules`, `frontend/src/firebase.ts`, `frontend/src/components/AuthGate.tsx`, `FIREBASE_DEPLOYMENT.md` (guida passo-passo)
- ✅ Rimosso `frontend/src/services/api.ts` e dipendenza axios; aggiunta dipendenza `firebase`

**v0.15.2 - Fix User Feedback Ignorato nella Rigenerazione:**
- ✅ Risolto bug: il feedback utente (es. "più pistacchio") veniva ignorato
- ✅ Aggiornato `COURSE_REGENERATION_TEMPLATE` con nuova sezione "FEEDBACK UTENTE (PRIORITÀ MASSIMA)"
- ✅ Aggiornato `build_course_regeneration_prompt()` per accettare e usare `user_feedback`
- ✅ Aggiornato `structured_generation.py` per passare `user_feedback` al prompt builder
- ✅ Migliorato prompt in `memory_manager.py` con enfasi maggiore sul feedback
- ✅ Il feedback è ora evidenziato con 🎯 e istruzioni esplicite di seguirlo
- ✅ 120 test passano dopo le correzioni

**v0.15.1 - Fix Rigenerazione Portate (Bug Fix Critico):**
- ✅ Risolto bug rigenerazione portate che causava errore 500
- ✅ Fix Memory API: sostituito `memory.add_message()` con `memory.add_turn(blocks=TextBlock(...), role=...)`
- ✅ Fix Pydantic v2 validation: `Course.model_validate(new_course.model_dump())` per evitare errore "Input should be a valid dictionary"
- ✅ 120 test passano dopo le correzioni
- ✅ Dettaglio bug: l'errore era causato da due problemi:
  1. API Memory errata in `memory_manager.py` (add_message non esiste, usare add_turn con TextBlock)
  2. Pydantic v2 non accettava un oggetto Course esistente come input per RegenerateCourseResponse

**v0.15.0 - Frontend Rigenerazione Portate:**
- ✅ Pulsante "🔄 Rigenera" accanto a ogni portata nella tab Menù
- ✅ Due modalità: rigenerazione rapida (🔄) e con feedback (💬)
- ✅ Modal per inserire feedback opzionale ("Vorrei qualcosa di più leggero", etc.)
- ✅ Loading state durante rigenerazione (spinner sul singolo corso)
- ✅ Effetto flash verde dopo rigenerazione completata
- ✅ Aggiornamento automatico shopping list e timeline dopo rigenerazione
- ✅ Nuovi tipi TypeScript: `RegenerateCourseRequest`, `RegenerateCourseResponse`
- ✅ Stili CSS professionali per pulsanti e modal
- ✅ Responsive design per mobile

**v0.14.0 - Memory Datapizza AI per Rigenerazione Contestualizzata:**
- ✅ Implementato `memory_manager.py` per gestire Memory per ogni menù
- ✅ Salvataggio automatico del contesto (preferenze utente + menù) dopo generazione
- ✅ Rigenerazione portate con consapevolezza del menù completo
- ✅ Endpoint `/regenerate-course` supporta `user_feedback` per feedback utente
- ✅ Utilizzo `TextBlock` e `add_turn()` per API Memory Datapizza
- ✅ 10 nuovi test per Memory manager (120 test totali)
- ✅ Fix import paths da `services.X` a `backend.services.X`

**v0.13.0 - Supporto per 1 Ospite:**
- ✅ Rimosso vincolo minimo di 2 ospiti, ora il sistema accetta 1-50 ospiti
- ✅ Modifiche backend: `input_models.py` (ge=2 → ge=1) e `menu_routes.py`
- ✅ Modifiche frontend: `App.tsx` (Math.max(2) → Math.max(1))
- ✅ Test suite aggiornata: 110/110 test passano (aggiunto `test_num_guests_one_accepted`)
- ✅ Documentazione aggiornata: README.md + project_description.md (2-50 → 1-50)

**v0.12.0 - Automazione Startup:** Implementato script unificato `npm run dev:full` che avvia backend + frontend insieme usando `concurrently`. Riduce il numero di terminali da 2 a 1 e migliora l'esperienza dello sviluppatore.

---

## 🛠️ Stack Tecnologico Implementato

### Core Framework
- **Datapizza AI** `0.0.9` - Framework orchestrazione multi-agent
- **datapizza-ai-clients-google** `0.0.5` - Client per Google Gemini
- **Datapizza Memory** - Gestione contesto conversazionale per rigenerazione
- **Google Gemini 3 Flash Preview** - LLM principale (Free Tier: 15 req/min, 1500 req/day)

### Backend (✅ COMPLETATO)
- **Python** `3.12.x` (richiesto: 3.10-3.12, Python 3.13 funziona con warning)
- **Pydantic** `2.5+` - Validazione dati e Structured Responses
- **FastAPI** `0.104+` - API REST
- **Uvicorn** - Server ASGI
- **python-dotenv** - Gestione variabili ambiente

### Frontend (✅ COMPLETATO E TESTATO)
- **React** `18.x` - UI Library
- **TypeScript** `5.x` - Type safety
- **Vite** `6.x` - Build tool e dev server
- **Axios** - HTTP client per API calls
- **concurrently** `9.1.2` - Esecuzione parallela backend + frontend (Dev)

### Testing (✅ COMPLETATO)
- **pytest** `8.x` - Framework di test Python
- **pytest-asyncio** `0.24+` - Supporto test asincroni
- **httpx** - Test client per FastAPI (TestClient)
- **120 test totali** - Copertura modelli, tools, API, services, memory

### Da Implementare (Opzionale)
- **WeasyPrint** `60.1+` - Generazione PDF server-side (opzionale)
- **Docker** - Containerizzazione per deployment

---

## 🎯 Architettura Implementata

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + TypeScript)              ✅ FATTO │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Input Form  │  │ Menu View   │  │ Shopping    │  │ Timeline View       │ │
│  │ (config)    │  │ (courses)   │  │ List View   │  │ (preparation)       │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         └────────────────┴────────────────┴────────────────────┘            │
│                                    │ HTTP/JSON                              │
│                              localhost:5173                                 │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BACKEND API (FastAPI)                    ✅ COMPLETATO │
│                              localhost:8000                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                 STRUCTURED GENERATION LAYER                          │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  generate_menu_structured()                                    │  │   │
│  │  │  - Prompt Engineering ottimizzato                              │  │   │
│  │  │  - Fallback: structured_response → invoke + JSON parsing       │  │   │
│  │  │  - Auto-correzione struttura JSON                              │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌───────────────────────────────────────────────────────────────┐   │   │
│  │  │              GOOGLE CLIENT (Gemini 2.5 Flash)                  │   │   │
│  │  │        datapizza.clients.google.GoogleClient                   │   │   │
│  │  └───────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────────┐ │
│  │  Menu Service    │  │  In-Memory Store │  │  Print/PDF (browser-side)  │ │
│  │  (Business Logic)│  │  (menu_store)    │  │  ✅ Implementato           │ │
│  └──────────────────┘  └──────────────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Struttura Progetto Attuale

```
D:\GitHubRepos\Christmas-World-Menu\
├── .env                          # API key Google (NON committare!)
├── .venv\                        # Virtual environment Python
├── requirements.txt              # Dipendenze Python
│
├── backend\                      # ✅ COMPLETATO
│   ├── __init__.py
│   ├── config.py                 # Configurazione Pydantic Settings
│   ├── main.py                   # Entry point FastAPI
│   ├── test_connection.py        # Test connessione Gemini
│   ├── test_models.py            # Test modelli Pydantic
│   ├── test_tools.py             # Test custom tools
│   ├── test_agents.py            # Test sistema agenti
│   ├── test_structured.py        # Test structured generation
│   ├── test_api.py               # Test endpoint API
│   │
│   ├── api\                      # API Routes
│   │   ├── __init__.py
│   │   └── menu_routes.py        # Endpoints menù
│   │
│   ├── models\                   # Modelli Pydantic
│   │   ├── __init__.py
│   │   ├── input_models.py       # UserInput, Enums (FONTE DI VERITÀ)
│   │   ├── menu_models.py        # Course, Recipe, Ingredient
│   │   └── output_models.py      # MenuOutput, ShoppingList, Timeline
│   │
│   ├── tools\                    # Custom Tools Datapizza
│   │   ├── __init__.py
│   │   ├── ingredient_tools.py
│   │   ├── calculation_tools.py
│   │   └── validation_tools.py
│   │
│   ├── agents\                   # Agenti Datapizza AI
│   │   ├── __init__.py
│   │   ├── menu_agent.py
│   │   ├── recipe_agent.py
│   │   └── aggregation_agent.py
│   │
│   └── services\                 # Business Logic
│       ├── __init__.py
│       ├── prompt_templates.py   # Template prompt ottimizzati
│       ├── structured_generation.py  # Generazione strutturata
│       ├── menu_service.py       # Service layer + storage
│       └── memory_manager.py     # ✅ NEW: Gestione Memory Datapizza AI
│
├── frontend\                     # ✅ COMPLETATO E TESTATO
│   ├── package.json              # Dipendenze Node.js
│   ├── vite.config.ts            # Configurazione Vite
│   ├── tsconfig.json             # Configurazione TypeScript
│   ├── index.html                # HTML entry point
│   │
│   └── src\
│       ├── main.tsx              # React entry point
│       ├── App.tsx               # ✅ Componente principale (CORRETTO v2)
│       ├── App.css               # ✅ Stili professionali (centrato, no neve)
│       ├── index.css             # Stili globali (default Vite)
│       │
│       ├── types\
│       │   └── index.ts          # ✅ TypeScript interfaces (ALLINEATO AL BACKEND)
│       │
│       ├── services\
│       │   └── api.ts            # ✅ Client API Axios
│       │
│       └── assets\
│           └── react.svg         # Default Vite asset
│
└── tests\                        # ✅ COMPLETATO (120 test)
    ├── __init__.py               # Package init
    ├── conftest.py               # Fixtures pytest (UserInput, MenuOutput, mock client)
    ├── pytest.ini                # Configurazione pytest + asyncio
    ├── test_models.py            # 36 test modelli Pydantic (enum, validazione, nuovo test 1 ospite)
    ├── test_tools.py             # 23 test agent tools (validate, calculate, aggregate)
    ├── test_api.py               # 27 test FastAPI endpoints (CRUD, error handling)
    ├── test_services.py          # 24 test MenuService e storage
    └── test_memory.py            # ✅ NEW: 10 test Memory manager Datapizza
```

---

## ⚡ Quick Start

### Prerequisiti
- Python 3.12 (3.13 funziona con warning)
- Node.js 18+ (testato con v22.11.0)
- VS Code
- Google API Key per Gemini

### Setup Backend & Frontend Unificato (CONSIGLIATO)

```powershell
# 1. Naviga al progetto
cd D:\GitHubRepos\Christmas-World-Menu\frontend

# 2. Avvia backend + frontend insieme in UN SOLO TERMINALE
npm run dev:full

# Verifica:
# - Backend: http://localhost:8000/docs (Swagger UI)
# - Frontend: http://localhost:5173 (oppure 5174 se 5173 è occupato)
```

### Setup Tradizionale (Due Terminali)

**Terminale 1 - Backend:**
```powershell
# 1. Naviga al progetto
cd D:\GitHubRepos\Christmas-World-Menu

# 2. Attiva virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Avvia il server FastAPI
uvicorn backend.main:app --reload --port 8000

# Verifica: http://localhost:8000/docs per Swagger UI
```

**Terminale 2 - Frontend:**
```powershell
# In un NUOVO terminale
cd D:\GitHubRepos\Christmas-World-Menu\frontend

# Avvia il dev server React
npm run dev

# Verifica: http://localhost:5173 per l'app
```

### Configurazione .env

```bash
# .env (nella root del progetto)
GOOGLE_API_KEY=your_gemini_api_key_here
DATAPIZZA_AGENT_LOG_LEVEL=INFO
```

---

## 📚 API Endpoints Implementati

| Metodo | Endpoint | Descrizione | Status |
|--------|----------|-------------|--------|
| GET | `/health` | Health check | ✅ |
| GET | `/docs` | Swagger UI | ✅ |
| POST | `/api/menu/generate` | Genera menù completo | ✅ |
| POST | `/api/menu/regenerate-course` | Rigenera una portata | ✅ |
| GET | `/api/menu/{menu_id}` | Recupera un menù | ✅ |
| GET | `/api/menu/{menu_id}/shopping-list` | Solo lista spesa | ✅ |
| GET | `/api/menu/{menu_id}/timeline` | Solo timeline | ✅ |
| GET | `/api/menu/` | Lista tutti i menù | ✅ |
| DELETE | `/api/menu/{menu_id}` | Elimina un menù | ✅ |

### Esempio Request Generate

```json
POST /api/menu/generate
{
  "num_guests": 8,
  "cuisines": ["italiana", "francese"],
  "preferred_ingredients": ["salmone", "gamberi"],
  "avoided_ingredients": ["piccante", "funghi"],
  "dietary_restrictions": [],
  "difficulty_level": "medio",
  "budget_level": "medio"
}
```

---

## 🔴 CRITICAL: Lessons Learned e Bug Fix

### 1. Virtual Environment NON Portabile

**Problema**: Se il progetto viene spostato da `C:` a `D:` (o viceversa), il `.venv` si corrompe.

**Sintomo**:
```
Fatal error in launcher: Unable to create process using '"C:\Users\...\python.exe"
```

**Soluzione**: Ricreare il venv:
```powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# Reinstallare tutte le dipendenze
```

### 2. Gemini API NON Supporta `additionalProperties`

**Problema**: `client.structured_response()` fallisce con errore:
```
"additionalProperties is not supported in the Gemini API"
```

**Causa**: Pydantic genera `"additionalProperties": false` nello JSON schema, ma Gemini non lo supporta.

**Soluzione Implementata** (in `structured_generation.py`):
```python
# Per modelli complessi (MenuOutput): usa invoke() + parsing manuale
try:
    response = client.structured_response(input=prompt, output_cls=MenuOutput)
    return response.structured_data[0]
except Exception:
    # Fallback: invoke + JSON parsing
    response = client.invoke(prompt)
    data = _parse_and_fix_menu_json(response.text)
    return MenuOutput.model_validate(data)
```

### 3. Gemini Restituisce Strutture JSON Diverse

**Problema**: Anche con prompt esplicito, Gemini può restituire:
- `{"menu": [...]}` invece di `{"courses": {...}}`
- Lista piatta invece di dizionario categorizzato

**Soluzione Implementata**: Funzione `_fix_menu_structure()` che:
- Converte `menu` → `courses`
- Converte lista piatta → dizionario categorizzato
- Genera placeholder per campi mancanti

### 4. GoogleClient: Parametro `max_tokens` NON Supportato

**Problema**: Il costruttore `GoogleClient` non accetta `max_tokens`.

**Soluzione**: Rimuovere il parametro:
```python
# ❌ SBAGLIATO
client = GoogleClient(api_key=key, model=model, max_tokens=8192)

# ✅ CORRETTO
client = GoogleClient(api_key=key, model=model, temperature=0.7)
```

### 5. Tool Return Types: Solo Stringhe

**Problema**: I tool Datapizza devono restituire **stringhe**, non dict/liste pure.

**Soluzione**:
```python
@tool
def my_tool(param: str) -> str:
    result = {"data": "value"}
    return json.dumps(result)  # Converti in stringa JSON
```

### 6. Python 3.13 Compatibility

**Problema**: Datapizza AI richiede `>=3.10.0,<3.13.0`, ma Python 3.13 è installato.

**Sintomo**: Warning durante l'import, ma funziona comunque.

**Raccomandazione**: Usare Python 3.12 per evitare warning.

### 7. TypeScript Import: Usare `type` per Interfacce

**Problema**: React/Vite con TypeScript può fallire con:
```
does not provide an export named 'Course'
```

**Causa**: Gli export di tipi/interfacce richiedono `import type` in alcuni setup.

**Soluzione**:
```typescript
// ❌ SBAGLIATO (può fallire)
import { UserInput, MenuOutput, Course } from '../types';

// ✅ CORRETTO
import type { UserInput, MenuOutput, Course } from '../types';
```

### 8. React: onKeyPress Deprecato

**Problema**: `onKeyPress` è deprecato in React moderno.

**Soluzione**: Usare `onKeyDown`:
```typescript
// ❌ SBAGLIATO
onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}

// ✅ CORRETTO
onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
```

### 9. Creazione File con Notepad su Windows

**Problema**: VS Code a volte non salva correttamente i file o li mette nella posizione sbagliata.

**Soluzione Affidabile**: Usare Notepad da PowerShell:
```powershell
notepad "D:\GitHubRepos\Christmas-World-Menu\frontend\src\types\index.ts"
```
Poi incollare il contenuto, File → Salva, e chiudere.

### 10. 🔴 CRITICO: Mismatch Tipi Frontend/Backend (Errore 422)

**Problema**: Il frontend inviava valori non validi per le enum del backend, causando errore HTTP 422 "Unprocessable Entity".

**Causa**: I tipi TypeScript nel frontend non erano allineati con i modelli Pydantic del backend.

**Mismatch trovati e corretti:**

| Campo | Frontend (SBAGLIATO) | Backend (CORRETTO) |
|-------|---------------------|-------------------|
| **Cuisines** | `messicana`, `giapponese`, `mediterranea` | Solo: `italiana`, `spagnola`, `francese`, `tedesca`, `inglese`, `polacca`, `greca`, `americana`, `scandinava` |
| **Difficulty** | `difficile` | `avanzato` |
| **Dietary** | `kosher`, `halal` | Solo: `vegetariano`, `vegano`, `senza_glutine`, `senza_lattosio` |

**Soluzione**: Aggiornato `frontend/src/types/index.ts` per matchare esattamente `backend/models/input_models.py`.

**REGOLA D'ORO**: Il file `backend/models/input_models.py` è la **FONTE DI VERITÀ**. Ogni modifica alle enum deve partire dal backend, poi propagarsi al frontend.

### 11. Struttura Dati Backend: recipe.steps vs recipe.instructions

**Problema**: Il frontend cercava `recipe.instructions` ma il backend restituisce `recipe.steps`.

**Sintomo**: `Cannot read properties of undefined (reading 'map')` su array inesistente.

**Soluzione**: Aggiornato i tipi TypeScript per usare `steps` invece di `instructions`.

### 12. Layout Non Centrato (Conflitto CSS index.css)

**Problema**: Il modulo frontend appariva spostato a sinistra invece che centrato.

**Causa**: Il file `frontend/src/index.css` (default Vite) aveva `body { display: flex; place-items: center; }` che entrava in conflitto con gli stili di `App.css`. Inoltre mancava la configurazione per `#root`.

**Soluzione**: Modificato `index.css`:
```css
/* ❌ SBAGLIATO (default Vite) */
body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

/* ✅ CORRETTO */
body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  width: 100%;
  min-height: 100vh;
}
```

### 13. Errore 500 Non Descrittivo nel Frontend

**Problema**: Quando il backend restituiva un errore 500, il frontend mostrava solo "Request failed with status code 500" senza dettagli utili per il debug.

**Causa**: Il client Axios non estraeva il messaggio `detail` dalla risposta di errore FastAPI.

**Soluzione Implementata** in `frontend/src/services/api.ts`:
1. Funzione `extractErrorMessage()` che estrae il campo `detail` dalle risposte FastAPI
2. Messaggi user-friendly per codici HTTP comuni (400, 422, 429, 500, 502, 503)
3. Supporto per errori di validazione Pydantic (array in `detail`)
4. Box informativo espandibile nel form con lista codici errore

**UI Aggiunta**: Sopra al pulsante "Genera" ora appare un box con:
- Messaggio di errore completo con codice `[500] Errore durante la generazione...`
- Sezione espandibile "ℹ️ Codici di errore comuni" con spiegazioni

### 14. Bug Rigenerazione Portate (v0.15.1)

**Problema**: La rigenerazione di singole portate falliva con errore 500, mostrando nel terminale:
```
⚠️ Fallback a metodo standard: 'str' object has no attribute 'google_role'
❌ Errore rigenerazione: 1 validation error for RegenerateCourseResponse
new_course
  Input should be a valid dictionary or instance of Course
```

**Causa Duplice**:
1. **API Memory errata**: In `memory_manager.py`, il codice usava `memory.add_message()` che non esiste nell'API Datapizza Memory. L'API corretta è `memory.add_turn(blocks=TextBlock(...), role="...")`.

2. **Pydantic v2 Validation**: Quando si passava un oggetto `Course` esistente a `RegenerateCourseResponse`, Pydantic v2 non riusciva a validarlo correttamente, richiedendo invece un dict o una nuova istanza.

**Soluzione Implementata**:

1. **Fix Memory API** in `backend/services/memory_manager.py`:
```python
# ❌ SBAGLIATO (API inesistente)
memory.add_message(role="user", content="...")

# ✅ CORRETTO (API Datapizza Memory)
user_block = TextBlock(f"[RIGENERAZIONE] Ho sostituito {course_type}...")
memory.add_turn(blocks=user_block, role="user")
```

2. **Fix Pydantic Validation** in `backend/api/menu_routes.py`:
```python
# ❌ SBAGLIATO (Pydantic v2 non valida l'oggetto esistente)
return RegenerateCourseResponse(new_course=new_course)

# ✅ CORRETTO (converti in dict e ricrea)
return RegenerateCourseResponse(
    new_course=Course.model_validate(new_course.model_dump())
)
```

### 15. User Feedback Ignorato nella Rigenerazione (v0.15.2)

**Problema**: Quando l'utente inseriva un feedback specifico (es. "Vorrei più pistacchio"), il sistema lo ignorava e generava un piatto senza considerare la richiesta.

**Causa Duplice**:
1. **Template mancante**: Il `COURSE_REGENERATION_TEMPLATE` non aveva una sezione per il `user_feedback`
2. **Parametro non passato**: La funzione `build_course_regeneration_prompt()` non accettava il parametro `user_feedback` e il fallback in `structured_generation.py` non lo passava

**Soluzione Implementata**:

1. **Aggiornato template** in `backend/services/prompt_templates.py`:
   - Aggiunta sezione "🎯 FEEDBACK UTENTE (PRIORITÀ MASSIMA)"
   - Aggiunta regola #5: "SE C'È UN FEEDBACK UTENTE, DEVI SEGUIRLO CON PRIORITÀ MASSIMA"

2. **Aggiornata funzione** `build_course_regeneration_prompt()`:
   - Nuovo parametro `user_feedback: str = ""`
   - Costruzione dinamica della sezione feedback con enfasi sulla priorità

3. **Aggiornato fallback** in `structured_generation.py`:
   - Passaggio di `user_feedback` a `build_course_regeneration_prompt()`

4. **Migliorato prompt Memory** in `memory_manager.py`:
   - Feedback evidenziato con 🎯 e istruzioni esplicite
   - Istruzione #3: "SE C'È UN FEEDBACK, SEGUILO CON PRIORITÀ MASSIMA"

---

## 🎄 Funzionalità Frontend Implementate

### Form Input
- ✅ Contatore ospiti (1-50)
- ✅ Selezione cucine multiple (9 opzioni - allineate al backend)
- ✅ Ingredienti preferiti (aggiungi/rimuovi)
- ✅ Ingredienti da evitare (aggiungi/rimuovi)
- ✅ Restrizioni alimentari (4 opzioni - allineate al backend)
- ✅ Selezione difficoltà (facile/medio/avanzato)
- ✅ Selezione budget (economico/medio/premium)

### Visualizzazione Risultati
- ✅ Tab Menù: tutte le portate con ricette espandibili
- ✅ Tab Lista Spesa: ingredienti per categoria
- ✅ Tab Timeline: preparazione su 3 giorni

### Rigenerazione Portate (NEW v0.15.0)
- ✅ Pulsante 🔄 (rigenerazione rapida) su ogni portata
- ✅ Pulsante 💬 (rigenerazione con feedback) su ogni portata
- ✅ Modal per inserire feedback opzionale
- ✅ Loading spinner sulla singola portata durante rigenerazione
- ✅ Effetto flash verde dopo rigenerazione completata
- ✅ Aggiornamento automatico shopping list e timeline
- ✅ Gestione errori con banner dismissibile

### Design e UX
- ✅ Layout centrato (max-width 900px) - **FIX v0.12.1**: rimosso conflitto CSS index.css
- ✅ Tema natalizio (rosso/verde/oro)
- ✅ Indicatore stato backend (online/offline)
- ✅ Spinner durante generazione
- ✅ Stampa/PDF via browser (window.print)
- ✅ Box errori dettagliato con codici HTTP - **NEW v0.12.1**
- ❌ Neve animata (RIMOSSA per scelta stilistica)

### Cucine Disponibili (dal backend)
```
italiana, spagnola, francese, tedesca, inglese, polacca, greca, americana, scandinava
```

### Restrizioni Alimentari Disponibili (dal backend)
```
vegetariano, vegano, senza_glutine, senza_lattosio
```

---

## 🔧 Valori Enum Backend (FONTE DI VERITÀ)

Questi sono i valori accettati dal backend. **Il frontend DEVE matchare esattamente questi valori**.

### DifficultyLevel (backend/models/input_models.py)
```python
class DifficultyLevel(str, Enum):
    FACILE = "facile"
    MEDIO = "medio"
    AVANZATO = "avanzato"  # ⚠️ NON "difficile"!
```

### BudgetLevel (backend/models/input_models.py)
```python
class BudgetLevel(str, Enum):
    ECONOMICO = "economico"
    MEDIO = "medio"
    PREMIUM = "premium"
```

### Cuisine (backend/models/input_models.py)
```python
class Cuisine(str, Enum):
    ITALIANA = "italiana"
    SPAGNOLA = "spagnola"
    FRANCESE = "francese"
    TEDESCA = "tedesca"
    INGLESE = "inglese"
    POLACCA = "polacca"
    GRECA = "greca"
    AMERICANA = "americana"
    SCANDINAVA = "scandinava"
    # ⚠️ NON esistono: giapponese, messicana, mediterranea, cinese, etc.
```

### DietaryRestriction (backend/models/input_models.py)
```python
class DietaryRestriction(str, Enum):
    VEGETARIANO = "vegetariano"
    VEGANO = "vegano"
    SENZA_GLUTINE = "senza_glutine"
    SENZA_LATTOSIO = "senza_lattosio"
    # ⚠️ NON esistono: kosher, halal
```

---

## 🚀 Prossimi Passi Consigliati

### PRIORITÀ ALTA: Preparazione per Sfida Datapizza

#### 1. Validazione Finale (30 min)
```powershell
# Verifica che tutto funzioni insieme
# 1. Backend attivo su :8000
# 2. Frontend attivo su :5173
# 3. Genera un menù con combinazione valida:
#    - Cucine: italiana, spagnola, greca (OK)
#    - Difficoltà: avanzato (NON difficile!)
#    - Restrizioni: vegetariano (OK)
# 4. Verifica tutte le tab (Menu, Shopping, Timeline)
# 5. Testa la stampa PDF (bottone "Stampa PDF")
```

#### 2. Deployment (2-3h)

**Opzione A: Railway.app (Consigliata)**
```yaml
# railway.yaml per backend
services:
  backend:
    build:
      dockerfile: Dockerfile
    envVars:
      - GOOGLE_API_KEY: ${{secrets.GOOGLE_API_KEY}}
```

**Opzione B: Render.com + Vercel**
- Backend: Render.com (free tier)
- Frontend: Vercel (free tier)

#### 3. README Pubblico (1h)
Creare un README.md pubblico con:
- Screenshot dell'applicazione
- Istruzioni di setup
- Link alla demo live
- Descrizione features

### PRIORITÀ MEDIA: Miglioramenti Opzionali

#### 4. Design più "Videogame" (se richiesto)
L'utente ha menzionato interesse per un design più dinamico/videogame. Possibili aggiunte:
- Effetti particellari (stelle, scintille)
- Animazioni glow/neon
- Transizioni più aggressive
- Suoni di feedback (opzionale)

#### 5. Estensione Cucine (se necessario)
Per aggiungere nuove cucine (es. giapponese, messicana):
1. Modificare `backend/models/input_models.py` → class Cuisine
2. Aggiornare `frontend/src/types/index.ts` → type Cuisine
3. Aggiornare `frontend/src/App.tsx` → array CUISINES
4. Riavviare entrambi i server

---

## Appendice A: Riferimenti Datapizza AI

### Import Principali

```python
# Client
from datapizza.clients.google import GoogleClient

# Agenti
from datapizza.agents import Agent

# Tools
from datapizza.tools import tool

# Memory
from datapizza.memory import Memory
from datapizza.type import ROLE, TextBlock

# Pipeline
from datapizza.pipeline import DagPipeline, FunctionalPipeline, Dependency
from datapizza.core.models import PipelineComponent

# Tracing
from datapizza.tracing import ContextTracing

# Modules
from datapizza.modules.prompt import ChatPromptTemplate
```

### Pattern Ricorrenti

```python
# Pattern 1: Creazione client (SENZA max_tokens!)
client = GoogleClient(
    api_key="...",
    model="gemini-2.5-flash",
    system_prompt="...",
    temperature=0.7
)

# Pattern 2: Definizione tool (restituisce STRINGA!)
@tool
def my_tool(param: str) -> str:
    """Docstring diventa descrizione per l'LLM."""
    result = {"data": "value"}
    return json.dumps(result)  # IMPORTANTE: stringa!

# Pattern 3: Creazione agente con tools
agent = Agent(
    name="my_agent",
    client=client,
    tools=[my_tool],
    memory=Memory(),
    max_steps=10
)

# Pattern 4: Esecuzione agente
response = agent.run("Task description")
print(response.text)

# Pattern 5: Structured response CON FALLBACK
try:
    response = client.structured_response(input=prompt, output_cls=Model)
    result = response.structured_data[0]
except Exception:
    # Fallback per modelli complessi
    response = client.invoke(prompt)
    result = parse_json_manually(response.text)
```

---

## 🧪 Test Suite (120 Test - ✅ COMPLETATO)

### Panoramica Test
La test suite è stata implementata con **pytest** e copre tutti i layer dell'applicazione:

| File | Test | Copertura |
|------|------|-----------|
| `tests/test_models.py` | 36 | Tutti i modelli Pydantic, enum, validatori (incluso test 1 ospite) |
| `tests/test_tools.py` | 23 | Agent tools: validate_ingredients, calculate_portions, aggregate_ingredients |
| `tests/test_api.py` | 27 | Tutti gli endpoint FastAPI, error handling, CORS |
| `tests/test_services.py` | 24 | MenuService, in-memory storage, business logic |
| `tests/test_memory.py` | 10 | Memory manager: CRUD, context save, summary builders |
| **Totale** | **120** | **100% pass rate** |

### Struttura Test
```
tests/
├── conftest.py           # Fixtures condivise
│   ├── sample_user_input()      # UserInput di esempio
│   ├── sample_menu_output()     # MenuOutput completo mock
│   ├── mock_google_client()     # Mock per Google Gemini
│   └── test_client()            # FastAPI TestClient
├── pytest.ini            # Configurazione pytest + asyncio
├── test_models.py        # Test modelli Pydantic
├── test_tools.py         # Test agent tools
├── test_api.py           # Test endpoint FastAPI
├── test_services.py      # Test service layer
└── test_memory.py        # ✅ NEW: Test Memory manager
```

### Comandi Test
```powershell
# Esegui tutti i test
pytest tests/ -v

# Test con output breve
pytest tests/ -v --tb=short

# Test singolo file
pytest tests/test_models.py -v

# Test con coverage (richiede pytest-cov)
pytest tests/ --cov=backend --cov-report=html
```

### Categorie di Test Implementate

#### 1. Test Modelli (`test_models.py`)
- Validazione enum (Cuisine, DifficultyLevel, BudgetLevel, DietaryRestriction)
- Validazione constraints (num_guests 1-50, validated ingredients)
- Test errori per valori invalidi
- Serializzazione/deserializzazione JSON

#### 2. Test Tools (`test_tools.py`)
- `validate_ingredients`: validazione ingredienti validi/invalidi
- `calculate_portions`: calcolo porzioni per numero ospiti
- `aggregate_ingredients`: aggregazione per categoria

#### 3. Test API (`test_api.py`)
- Health check endpoint
- CRUD operations per menù
- Error handling (404, 422)
- Validazione input/output

#### 4. Test Services (`test_services.py`)
- MenuService initialization
- In-memory storage operations
- Business logic validation

#### 5. Test Memory (`test_memory.py`) - ✅ NEW
- Memory CRUD operations (create, get, delete)
- Context saving (user input + menu summary)
- Summary builders (build_user_input_summary, build_menu_summary)
- Memory statistics

---

## Appendice B: Memory Manager - Guida Tecnica

### Cos'è Memory in Datapizza AI
`Memory` è un componente di Datapizza che mantiene il contesto conversazionale tra interazioni. Ogni Memory contiene "turns" (turni) con ruolo (`user`/`assistant`) e contenuto (`TextBlock`).

### Implementazione nel Progetto
```python
# backend/services/memory_manager.py

# Storage in-memory per le Memory associate ai menù
_memory_store: Dict[str, Memory] = {}

# Creazione Memory per un menù
def create_memory_for_menu(menu_id: str) -> Memory:
    memory = Memory()
    _memory_store[menu_id] = memory
    return memory

# Salvataggio contesto dopo generazione menù
def save_menu_context_to_memory(menu_id, user_input_summary, menu_summary):
    memory = get_memory_for_menu(menu_id) or create_memory_for_menu(menu_id)
    
    # Usa TextBlock per il contenuto
    user_block = TextBlock(f"[CONTESTO] Richiesta:\n{user_input_summary}")
    memory.add_turn(blocks=user_block, role="user")
    
    assistant_block = TextBlock(f"[CONTESTO] Menù:\n{menu_summary}")
    memory.add_turn(blocks=assistant_block, role="assistant")
    
    return memory
```

### Flusso di Rigenerazione con Memory
1. **Generazione**: Quando viene generato un menù, il contesto viene salvato in Memory
2. **Richiesta Rigenerazione**: L'utente richiede di rigenerare una portata con feedback opzionale
3. **Recupero Contesto**: Il sistema recupera la Memory associata al menu_id
4. **Generazione Contestualizzata**: L'agente genera la nuova portata con consapevolezza del menù completo

### API Endpoint Aggiornato
```json
POST /api/menu/regenerate-course
{
  "menu_id": "uuid-del-menu",
  "course_type": "primo",
  "course_index": 0,
  "user_feedback": "Vorrei qualcosa di più leggero"  // ✅ NEW
}
```

---

## Appendice C: Comandi Utili

### Avvio Sviluppo
```powershell
# Terminale 1 - Backend
cd D:\GitHubRepos\Christmas-World-Menu
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000

# Terminale 2 - Frontend
cd D:\GitHubRepos\Christmas-World-Menu\frontend
npm run dev
```

### Test Backend
```powershell
cd D:\GitHubRepos\Christmas-World-Menu
.\.venv\Scripts\Activate.ps1

python backend/test_connection.py
python backend/test_models.py
python backend/test_tools.py
python backend/test_agents.py
python backend/test_structured.py
python backend/test_api.py  # Server deve essere attivo
```

### Build Frontend per Produzione
```powershell
cd D:\GitHubRepos\Christmas-World-Menu\frontend
npm run build
# Output in frontend/dist/
```

### Test Manuale via Swagger
```
1. Vai su http://localhost:8000/docs
2. POST /api/menu/generate
3. Usa questo JSON di test:

{
  "num_guests": 4,
  "cuisines": ["italiana", "spagnola"],
  "preferred_ingredients": ["salmone", "zucca"],
  "avoided_ingredients": ["capperi", "olive"],
  "dietary_restrictions": [],
  "difficulty_level": "medio",
  "budget_level": "medio"
}
```

---

## Appendice C: Checklist Finale

### Pre-Submission Checklist
- [x] Python 3.12 installato
- [x] VS Code configurato
- [x] API Key Google Gemini ottenuta
- [x] Virtual environment creato
- [x] Datapizza AI installato
- [x] Test connessione superato
- [x] File `.env` configurato
- [x] Backend funzionante su :8000
- [x] Frontend funzionante su :5173
- [x] Generazione menù testata
- [x] Bug mismatch tipi risolto (errore 422)
- [x] Layout centrato
- [x] Stampa/PDF funzionante
- [x] Test suite pytest (109 test passing)
- [ ] Deployment effettuato
- [ ] README.md pubblico

---

## Appendice D: File Frontend Corretti (Riferimento)

### types/index.ts (DEVE matchare il backend!)
```typescript
export type DietaryRestriction = 
  | "vegetariano" 
  | "vegano" 
  | "senza_glutine" 
  | "senza_lattosio";

export type DifficultyLevel = "facile" | "medio" | "avanzato";

export type Cuisine = 
  | "italiana" 
  | "spagnola" 
  | "francese" 
  | "tedesca" 
  | "inglese" 
  | "polacca" 
  | "greca" 
  | "americana" 
  | "scandinava";

export type BudgetLevel = "economico" | "medio" | "premium";
```

### App.tsx - Costanti (DEVONO matchare il backend!)
```typescript
const CUISINES = [
  'italiana', 'francese', 'spagnola', 'tedesca', 'inglese',
  'americana', 'polacca', 'greca', 'scandinava'
];

const DIETARY_OPTIONS = [
  { value: 'vegetariano', label: '🥬 Vegetariano' },
  { value: 'vegano', label: '🌱 Vegano' },
  { value: 'senza_glutine', label: '🌾 Senza Glutine' },
  { value: 'senza_lattosio', label: '🥛 Senza Lattosio' },
];

// Difficoltà: facile | medio | avanzato (NON "difficile"!)
// Budget: economico | medio | premium
```

---

*Documento generato per lo sviluppo del progetto Christmas Menu Generator con framework Datapizza AI.*
*Versione: 5.0*
*Ultimo aggiornamento: 9 Dicembre 2025*
*Fasi completate: 11/14*
*Target: Senior Software Developer*