# 🎄 Christmas Menu Generator

> **Generatore di Menù Natalizi Personalizzati con AI Multi-Agent**

Un'applicazione full-stack che utilizza intelligenza artificiale multi-agent per generare menù natalizi completi, personalizzati in base alle preferenze dell'utente, restrizioni alimentari e budget.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🤖 **AI Multi-Agent**: 3 agenti specializzati (Menu, Recipe, Aggregation) che collaborano
- 🍽️ **Menù Personalizzati**: Genera menù completi basati su preferenze, cucine e restrizioni
- 🔄 **Rigenerazione Intelligente**: Non ti piace una portata? Rigenerala con feedback personalizzato
- 🧠 **Contesto del Menù**: Il sistema "ricorda" il menù per generare portate coerenti
- 🎛️ **Selezione Modello**: Scegli dalla UI quale modello Gemini genera il menù
- 🔐 **Accesso Riservato**: Login con Google + allowlist di email gestita dal proprietario
- 📝 **Ricette Dettagliate**: Ogni portata include ingredienti, istruzioni e tempi di preparazione
- 🛒 **Lista della Spesa**: Ingredienti aggregati automaticamente per categoria
- ⏰ **Timeline di Preparazione**: Pianificazione su 3 giorni (2 giorni prima → giorno stesso)
- 🖨️ **Export PDF**: Stampa diretta dal browser

---

## 🛠️ Stack Tecnologico

### Backend
- **Python 3.12** - Linguaggio principale
- **FastAPI** - Framework API REST
- **Datapizza AI 0.0.9** - Framework orchestrazione multi-agent
- **Google Gemini 3 Flash** - LLM per generazione contenuti
- **Pydantic 2.5+** - Validazione dati e structured responses

### Web App (produzione, 100% gratuita)
- **React 19 + TypeScript** - UI
- **Vite 7.x** - Build tool e dev server
- **Firebase Hosting** - Hosting statico (piano Spark, gratuito)
- **Firebase Authentication** - Login con Google
- **Cloud Firestore** - Allowlist delle email autorizzate
- **Firebase AI Logic** - Chiamate a Gemini senza backend (Gemini Developer API, free tier)

### Backend Python (demo multi-agent, solo locale)
- **Python 3.12** + **FastAPI** - API REST
- **Datapizza AI 0.0.9** - Framework orchestrazione multi-agent
- **Pydantic 2.5+** - Validazione dati e structured responses

### Testing
- **pytest 8.x** - Framework test Python
- **120 test totali** - Copertura completa

---

## 🚀 Quick Start

> 🔥 **Deploy online**: l'app è pensata per essere pubblicata su **Firebase Hosting** (piano Spark, 100% gratuito), con login Google e allowlist di email decisa dal proprietario. Guida completa passo-passo: [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md)

### Prerequisiti

- Python 3.12 (3.13 funziona con warning)
- Node.js 18+ (consigliato v22.x)
- Google API Key per Gemini

### 1. Clone Repository

```bash
git clone https://github.com/alexcri90/Christmas-World-Menu.git
cd Christmas-World-Menu
```

### 2. Setup Web App (React + Firebase)

La web app usa Firebase per login, allowlist e chiamate a Gemini. Serve un progetto Firebase gratuito (piano Spark): segui i passaggi 1-6 di [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md), poi:

```bash
cd frontend
npm install

# Crea frontend/.env con la configurazione della tua web app Firebase
cp .env.example .env   # e compila i valori

npm run dev
```

- 🌐 **Frontend**: http://localhost:5173

### 3. (Opzionale) Backend Python Multi-Agent

Il backend FastAPI + Datapizza AI resta nel repository come demo del sistema multi-agent (il sito pubblicato non lo usa più):

```powershell
# Crea virtual environment
python -m venv .venv

# Attiva (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Installa dipendenze
pip install -r requirements.txt
```

Crea un file `.env` nella root del progetto:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
DATAPIZZA_AGENT_LOG_LEVEL=INFO
```

> 💡 Ottieni la tua API Key gratuita su [Google AI Studio](https://aistudio.google.com/)

Avvia il server e esplora gli endpoint da Swagger:

```powershell
uvicorn backend.main:app --reload --port 8000
```

- 📚 **API Docs**: http://localhost:8000/docs

---

## 📖 Utilizzo

### Genera un Menù

1. Apri http://localhost:5173
2. Configura le preferenze:
   - **Numero ospiti**: 1-50 persone
   - **Cucine**: Italiana, Francese, Spagnola, etc.
   - **Ingredienti preferiti**: Aggiungi i tuoi preferiti
   - **Ingredienti da evitare**: Escludi ciò che non vuoi
   - **Restrizioni alimentari**: Vegetariano, Vegano, Senza Glutine, Senza Lattosio
   - **Difficoltà**: Facile, Medio, Avanzato
   - **Budget**: Economico, Medio, Premium
3. Clicca "Genera Menù"
4. Esplora le 3 tab: **Menù**, **Lista Spesa**, **Timeline**
5. Usa "Stampa PDF" per salvare il risultato

### Rigenera una Portata

Non ti piace una portata? Puoi rigenerarla facilmente:

1. Nella tab **Menù**, trova la portata che vuoi cambiare
2. Clicca il pulsante **🔄** per una rigenerazione rapida
3. Oppure clicca **💬** per inserire un feedback specifico:
   - *"Vorrei qualcosa con più pistacchio"*
   - *"Preferisco un piatto più leggero"*
   - *"Qualcosa di vegetariano"*
4. Il sistema rigenererà solo quella portata, mantenendo coerenza con il resto del menù
5. La lista della spesa e la timeline si aggiorneranno automaticamente

> 💡 **Tip**: Il sistema usa AI Memory per "ricordare" il menù completo, così la nuova portata sarà sempre coerente con le altre!

### Esempio di Input

```json
{
  "num_guests": 8,
  "cuisines": ["italiana", "francese"],
  "preferred_ingredients": ["salmone", "gamberi"],
  "avoided_ingredients": ["piccante", "funghi"],
  "dietary_restrictions": ["senza_glutine"],
  "difficulty_level": "medio",
  "budget_level": "medio"
}
```

---

## 🏗️ Architettura

### Web app pubblicata (Firebase, senza server)

```
┌──────────────────────────────────────────────────────────────┐
│              FIREBASE HOSTING (React + TypeScript)           │
│   Login Google (Authentication) → allowlist (Firestore)     │
│                            │                                 │
│                            ▼                                 │
│        Firebase AI Logic (Gemini Developer API, free)       │
│     generazione menù + rigenerazione portate client-side    │
└──────────────────────────────────────────────────────────────┘
```

### Demo multi-agent locale (Python + Datapizza AI)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Input   │  │  Menu    │  │ Shopping │  │     Timeline     │ │
│  │  Form    │  │  View    │  │   List   │  │       View       │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
│       └─────────────┴─────────────┴─────────────────┘           │
│                            │ HTTP/JSON                          │
└────────────────────────────┼────────────────────────────────────┘
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Datapizza AI)             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              MULTI-AGENT ORCHESTRATION                   │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │  │
│  │  │ Menu Agent │→ │Recipe Agent│→ │ Aggregation Agent  │  │  │
│  │  │  (Planner) │  │  (Details) │  │ (Shopping+Timeline)│  │  │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Google Gemini 2.5 Flash API                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Flusso Dati

1. **UserInput** → Frontend raccoglie preferenze utente
2. **Menu Agent** → Pianifica le portate del menù
3. **Recipe Agent** → Dettaglia ogni ricetta con ingredienti e istruzioni
4. **Aggregation Agent** → Genera lista spesa e timeline di preparazione
5. **MenuOutput** → Risposta strutturata al frontend

---

## 🧩 Componenti Datapizza AI Utilizzati

Questo progetto sfrutta diversi componenti del framework **Datapizza AI**:

| Componente | Import | Utilizzo |
|------------|--------|----------|
| **GoogleClient** | `datapizza.clients.google` | Client per Google Gemini API con `invoke()` e `structured_response()` |
| **Agent** | `datapizza.agents` | Agente AI con memoria e tool per rigenerazione contestualizzata |
| **Memory** | `datapizza.memory` | Memoria conversazionale per mantenere contesto tra rigenerazioni |
| **TextBlock** | `datapizza.type` | Blocchi di testo per costruire turni di conversazione in Memory |
| **@tool** | `datapizza.tools` | Decoratore per creare tool callable dagli agenti |

### Tool Implementati

```python
from datapizza.tools import tool

@tool
def validate_ingredients(preferred, avoided, proposed) -> str:
    """Valida ingredienti rispetto a preferenze e restrizioni."""
    
@tool  
def calculate_portions(ingredient, base_qty, num_guests) -> str:
    """Calcola quantità per numero di ospiti."""

@tool
def aggregate_ingredients(ingredients_list) -> str:
    """Aggrega ingredienti per categoria nella lista spesa."""
```

### Memory per Rigenerazione Contestualizzata

```python
from datapizza.memory import Memory
from datapizza.type import TextBlock

# Salva contesto del menù
memory = Memory()
memory.add_turn(blocks=TextBlock("Menù: Antipasto, Primo..."), role="assistant")

# L'agente usa la memory per generare portate coerenti
agent = Agent(name="chef", client=client, memory=memory, tools=[...])
response = agent.run("Rigenera il secondo con più pistacchio")
```

---

## 📁 Struttura Progetto

```
Christmas-World-Menu/
├── .env                    # Variabili d'ambiente (NON committare!)
├── requirements.txt        # Dipendenze Python
├── pytest.ini              # Configurazione pytest
│
├── backend/
│   ├── main.py             # Entry point FastAPI
│   ├── config.py           # Configurazione app
│   │
│   ├── api/
│   │   └── menu_routes.py  # Endpoint REST
│   │
│   ├── models/
│   │   ├── input_models.py # UserInput, Enum (FONTE DI VERITÀ)
│   │   ├── menu_models.py  # Course, Recipe, Ingredient
│   │   └── output_models.py# MenuOutput, ShoppingList, Timeline
│   │
│   ├── agents/
│   │   ├── menu_agent.py       # Pianificazione menù
│   │   ├── recipe_agent.py     # Dettaglio ricette
│   │   └── aggregation_agent.py# Aggregazione dati
│   │
│   ├── tools/
│   │   ├── ingredient_tools.py # Validazione ingredienti
│   │   ├── calculation_tools.py# Calcolo porzioni
│   │   └── aggregation_tools.py# Aggregazione ingredienti
│   │
│   └── services/
│       ├── menu_service.py     # Business logic
│       ├── prompt_templates.py # Template prompt
│       └── structured_generation.py # Generazione strutturata
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   │
│   └── src/
│       ├── App.tsx         # Componente principale
│       ├── App.css         # Stili
│       │
│       ├── types/
│       │   └── index.ts    # TypeScript interfaces
│       │
│       └── services/
│           └── api.ts      # Client API Axios
│
└── tests/
    ├── conftest.py         # Fixtures pytest
    ├── test_models.py      # Test modelli (35)
    ├── test_tools.py       # Test tools (23)
    ├── test_api.py         # Test API (27)
    └── test_services.py    # Test services (24)
```

---

## 📚 API Reference

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/api/menu/generate` | Genera menù completo |
| `POST` | `/api/menu/regenerate-course` | Rigenera una portata |
| `GET` | `/api/menu/{menu_id}` | Recupera un menù |
| `GET` | `/api/menu/{menu_id}/shopping-list` | Solo lista spesa |
| `GET` | `/api/menu/{menu_id}/timeline` | Solo timeline |
| `GET` | `/api/menu/` | Lista tutti i menù |
| `DELETE` | `/api/menu/{menu_id}` | Elimina un menù |

---

## 🧪 Testing

### Esegui tutti i test

```bash
# Attiva virtual environment
.\.venv\Scripts\Activate.ps1

# Esegui test suite completa
pytest tests/ -v --tb=short
```

### Test specifici

```bash
# Solo test modelli
pytest tests/test_models.py -v

# Solo test API
pytest tests/test_api.py -v

# Solo test services
pytest tests/test_services.py -v

# Solo test tools
pytest tests/test_tools.py -v
```

### Coverage Report

```bash
pytest tests/ --cov=backend --cov-report=html
# Report in htmlcov/index.html
```

---

## ⚠️ Limitazioni Note

- **Nessuna persistenza**: i menù vivono nello stato del browser (web app) o in memoria del server (backend locale)
- **Rate Limit Gemini Free Tier**: pochi req/min e quota giornaliera per modello; superata la quota si riceve un errore 429, mai un addebito
- **Modelli in preview**: possono essere ritirati da Google; la lista dei modelli è in `frontend/src/services/aiService.ts`
- **Python 3.13**: funziona ma con warning, consigliato 3.12 (solo per il backend demo)

---

## 🤝 Contributing

1. Fork il repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

---

## 📄 License

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

---

## 🙏 Acknowledgments

- [Datapizza AI](https://datapizza.ai/) - Framework multi-agent
- [Google Gemini](https://deepmind.google/technologies/gemini/) - LLM
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend library

---

<p align="center">
  Made with ❤️ and 🎄 for the Datapizza AI Challenge
</p>
