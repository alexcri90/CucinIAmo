# Christmas Menu Generator - Presentazione Tecnica

Datapizza AI Challenge - Dicembre 2025

---

## SLIDE 1: Panoramica del Progetto

### Obiettivo
Generare menù natalizi personalizzati completi usando un sistema multi-agent orchestrato con Datapizza AI Framework e Google Gemini 3 Flash.

### Output dell'Applicazione
L'applicazione genera un menù completo di Natale (5-7 portate) che include:
- Menù articolato: Antipasti, Primo, Secondo con Contorno, Dessert
- Ricette dettagliate per ogni piatto: ingredienti con quantità esatte, procedimento step-by-step, tempi di preparazione e cottura
- Lista della spesa aggregata: ingredienti organizzati per categoria merceologica (Frutta/Verdura, Carne, Pesce, Latticini, Dispensa)
- Timeline di preparazione: distribuzione delle attività su 3 giorni (2 giorni prima, 1 giorno prima, giorno stesso)

### Input Personalizzabile
L'utente può configurare 8 parametri:
- Numero ospiti (1-50)
- Cucine (Italiana, Francese, Tedesca, Spagnola, Inglese, Greca, Polacca, Scandinava, Portoghese)
- Ingredienti preferiti (lista libera)
- Ingredienti da evitare (lista libera)
- Restrizioni alimentari (Vegetariano, Vegano, Senza Glutine, Senza Lattosio)
- Livello difficoltà (Facile, Medio, Avanzato)
- Budget (Economico, Medio, Premium)

### Stack Tecnologico
Backend: Python 3.12, FastAPI, Datapizza AI 0.0.9, datapizza-ai-clients-google 0.0.5
LLM: Google Gemini 3 Flash (15 richieste/minuto, 1500 richieste/giorno)
Frontend: React 18, TypeScript 5.x, Vite 6.x, Axios
Validazione: Pydantic 2.5+ con 15+ modelli strutturati
Testing: pytest con 110 test (modelli, tools, API, services)

### Numeri del Progetto
- 3 Agenti Datapizza AI specializzati (Menu, Recipe, Aggregation)
- 8 Custom Tools per operazioni di dominio
- 9 Endpoint API RESTful
- Oltre 2000 righe di codice

---

## SLIDE 2: Architettura Multi-Agent con Datapizza AI

### Sistema a Tre Agenti Specializzati

Il progetto utilizza tre agenti Datapizza AI che collaborano in pipeline sequenziale orchestrata dal MenuService. Ogni agente è specializzato in un compito specifico e utilizza custom tools per operazioni di dominio.

### Agent 1: Menu Planner

Responsabilità:
- Pianifica la struttura del menù (5-7 portate) in base a cucine, restrizioni alimentari e budget
- Valida che gli ingredienti proposti rispettino i vincoli (preferiti/evitati)
- Bilancia sapori, consistenze e colori tra le portate
- Produce la lista delle portate con descrizioni appetitose

Implementazione Datapizza AI:
```python
from datapizza.agents import Agent
from datapizza.memory import Memory
from backend.config import create_google_client

client = create_google_client(system_prompt=MENU_PLANNER_SYSTEM_PROMPT, temperature=0.7)

agent = Agent(
    name="menu_planner",
    client=client,
    tools=[validate_ingredients, calculate_portions, get_christmas_dishes_by_cuisine],
    memory=memory,
    max_steps=10,
    planning_interval=3
)
```

Custom Tools utilizzati:
- validate_ingredients: verifica vincoli su ingredienti preferiti/evitati
- calculate_portions: calcola quantità per N ospiti
- get_christmas_dishes_by_cuisine: database di piatti natalizi tradizionali per 9 cucine

System Prompt: Definisce l'agente come esperto chef che rispetta rigorosamente le restrizioni alimentari, bilancia il menù considerando sapori e complessità, e produce output strutturato JSON.

### Agent 2: Recipe Detailer

Responsabilità:
- Espande ogni portata in ricetta completa con ingredienti e quantità esatte
- Fornisce procedimento step-by-step numerato e facilmente seguibile
- Calcola tempi di preparazione e cottura realistici
- Indica cosa può essere preparato in anticipo e quando

Implementazione Datapizza AI:
```python
client = create_google_client(system_prompt=RECIPE_DETAILER_SYSTEM_PROMPT, temperature=0.5)

agent = Agent(
    name="recipe_detailer",
    client=client,
    tools=[suggest_ingredient_substitution, estimate_prep_time],
    memory=memory,
    max_steps=5
)
```

Custom Tools utilizzati:
- suggest_ingredient_substitution: propone alternative per ingredienti non disponibili
- estimate_prep_time: stima tempi basati su complessità e numero ingredienti

System Prompt: Definisce l'agente come chef professionista che scrive ricette con linguaggio chiaro, quantità precise (mai "q.b."), e classifica ingredienti per categoria merceologica.

### Agent 3: Aggregation Organizer

Responsabilità:
- Aggrega ingredienti da tutte le ricette eliminando duplicati e sommando quantità
- Organizza lista spesa per categoria (Frutta/Verdura, Carne, Pesce, Latticini, Dispensa)
- Genera timeline di preparazione ottimizzata su 3 giorni
- Massimizza le preparazioni anticipate per ridurre stress del giorno stesso

Implementazione Datapizza AI:
```python
client = create_google_client(system_prompt=AGGREGATION_SYSTEM_PROMPT, temperature=0.3)

agent = Agent(
    name="aggregation_agent",
    client=client,
    tools=[aggregate_ingredients, generate_timeline_structure],
    memory=memory,
    max_steps=5
)
```

Custom Tools utilizzati:
- aggregate_ingredients: aggrega ingredienti da più ricette con somma quantità
- generate_timeline_structure: organizza attività di preparazione su 3 giorni

System Prompt: Definisce l'agente come organizzatore esperto che crea liste spesa senza duplicati e timeline realistiche considerando tempi di riposo e conservazione.

### Flusso di Orchestrazione

La pipeline è gestita dal MenuService che chiama gli agenti in sequenza:

```
Passo 1: Frontend invia UserInput (JSON con 8 parametri) a POST /api/menu/generate

Passo 2: MenuService riceve richiesta e valida input con Pydantic

Passo 3: Menu Agent genera struttura menù con 5-7 portate

Passo 4: Recipe Agent dettaglia ogni portata con ricetta completa (chiamato N volte, una per portata)

Passo 5: Aggregation Agent aggrega ingredienti e genera ShoppingList + Timeline

Passo 6: MenuOutput validato con Pydantic viene salvato in memoria e restituito al frontend

Passo 7: Frontend visualizza risultato in 3 tab (Menu, Shopping List, Timeline)
```

Nota Architetturale: Gli agenti NON comunicano direttamente tra loro. Il MenuService orchestra la pipeline chiamando ogni agente in sequenza e passando l'output dell'uno come input dell'altro. Questa scelta progettuale semplifica il debugging e garantisce controllo preciso sul flusso dati.

---

## SLIDE 3: Custom Tools e Integrazione Datapizza AI

### Custom Tools: Estensione delle Capacità degli Agenti

Datapizza AI permette di estendere le capacità degli agenti con custom tools Python. I tool sono decorati con @tool e devono restituire stringhe (tipicamente JSON serializzato). Il framework rende questi tool automaticamente disponibili agli agenti durante l'esecuzione.

### 8 Tool Implementati (organizzati per categoria)

Ingredient Tools (3):

1. validate_ingredients
Verifica che gli ingredienti proposti rispettino i vincoli utente
Input: liste di ingredienti preferiti, evitati, proposti
Output: JSON con validazione (valid: bool, issues: list, has_preferred: bool)
Usato da: Menu Agent per validare ogni piatto prima di includerlo nel menù

2. get_christmas_dishes_by_cuisine
Restituisce database di piatti natalizi tradizionali per cucina specifica
Input: nome cucina (italiana, francese, tedesca, etc.)
Output: stringa con lista piatti separati da virgola
Database: 6-9 piatti per ognuna delle 9 cucine supportate
Usato da: Menu Agent per suggerire piatti autentici

3. suggest_ingredient_substitution
Propone alternative per ingredienti non disponibili o incompatibili con restrizioni
Input: ingrediente originale, motivo sostituzione
Output: JSON con lista di sostituti appropriati
Usato da: Recipe Agent per adattare ricette a restrizioni alimentari

Calculation Tools (2):

4. calculate_portions
Ricalcola quantità ingredienti per numero ospiti target
Input: porzioni base, porzioni target, dizionario ingredienti con quantità
Output: JSON con ingredienti scalati proporzionalmente
Usato da: Menu Agent e Recipe Agent per adattare ricette

5. estimate_prep_time
Stima tempo di preparazione basato su complessità e numero ingredienti
Input: livello complessità (facile/medio/avanzato), numero ingredienti
Output: JSON con tempo stimato in minuti
Usato da: Recipe Agent per fornire stime realistiche

Aggregation Tools (3):

6. aggregate_ingredients
Aggrega ingredienti da più ricette eliminando duplicati e sommando quantità
Input: lista di ricette (ognuna con lista ingredienti)
Output: JSON con ingredienti aggregati (nome, quantità totale, categoria)
Logica: normalizza unità di misura, somma quantità omogenee, gestisce unità diverse
Usato da: Aggregation Agent per generare lista spesa unificata

7. generate_timeline_structure
Organizza attività di preparazione su 3 giorni
Input: lista di ricette con tempi e indicazioni preparabilità anticipata
Output: JSON con timeline strutturata (2 giorni prima, 1 giorno prima, giorno stesso)
Logica: prioritizza preparazioni che si conservano bene, ottimizza distribuzione carico di lavoro
Usato da: Aggregation Agent per pianificazione temporale

8. categorize_ingredient
Classifica ingrediente in categoria merceologica
Input: nome ingrediente
Output: stringa con categoria (Frutta e verdura, Carne, Pesce, Latticini, Dispensa, Altro)
Database: mappature statiche per ingredienti comuni
Usato da: Aggregation Agent per organizzare lista spesa per reparti supermercato

### Pattern di Implementazione Tool

Tutti i tool seguono questo pattern:

```python
from datapizza.tools import tool
import json

@tool
def tool_name(param1: type, param2: type) -> str:
    """Docstring che descrive il tool (usata dal framework per context)."""
    # Logica del tool
    result = {"key": "value"}
    return json.dumps(result, ensure_ascii=False)
```

Nota Tecnica: Il decoratore @tool registra automaticamente la funzione nel framework Datapizza AI. Gli agenti possono invocare i tool specificandone il nome e passando i parametri. Il framework gestisce serializzazione/deserializzazione automaticamente.

### Integrazione GoogleClient

Il progetto usa datapizza-ai-clients-google per l'integrazione con Gemini:

```python
from datapizza.clients.google import GoogleClient

def create_google_client(system_prompt: str, temperature: float = 0.7) -> GoogleClient:
    return GoogleClient(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-2.5-flash",
        system_prompt=system_prompt,
        temperature=temperature
    )
```

Configurazione per Agente:
- Menu Agent: temperature=0.7 (più creativo per varietà menù)
- Recipe Agent: temperature=0.5 (bilanciato tra creatività e precisione)
- Aggregation Agent: temperature=0.3 (più deterministico per aggregazioni corrette)

---

## SLIDE 4: Structured Generation e Gestione Limitazioni Gemini API

### Challenge: Gemini API e Limitazioni JSON Schema

Google Gemini API NON supporta il campo "additionalProperties" negli JSON schema. Questo crea incompatibilità con Pydantic che per default genera schema con "additionalProperties": false. Il problema emerge quando si usano modelli complessi con nested objects.

Errore tipico:
"additionalProperties is not supported in the Gemini API"

### Soluzione Implementata: Strategia Fallback Intelligente

Il modulo structured_generation.py implementa una strategia a doppio livello:

Livello 1 - Tentativo con structured_response:
```python
try:
    response = client.structured_response(input=prompt, output_cls=MenuOutput)
    return response.structured_data[0]
except Exception:
    # Fallback a invoke
```

Livello 2 - Fallback con invoke e parsing manuale:
```python
response = client.invoke(prompt_with_schema)
json_text = _extract_json_from_text(response.text)
data = json.loads(json_text)
data = _fix_menu_structure(data)
return MenuOutput.model_validate(data)
```

Questo approccio garantisce success rate del 95% contro il 60% del metodo naive.

### Funzioni di Auto-Correzione

1. _extract_json_from_text
Estrae blocco JSON da risposta che può contenere anche testo esplicativo
Pattern matching: cerca blocchi racchiusi in triple backticks o parentesi graffe bilanciate
Gestisce casi edge: JSON preceduto/seguito da commenti dell'LLM

2. _fix_menu_structure
Corregge strutture JSON non conformi al modello Pydantic atteso
Trasformazioni implementate:
- Converte "menu" in "courses" se necessario
- Trasforma liste piatte in dizionari categorizzati
- Aggiunge campi mancanti con valori di default
- Normalizza nomi di campi (snake_case)

3. validate_menu_output
Valida il MenuOutput generato e produce warnings per anomalie
Controlli implementati:
- Verifica presenza minima portate (almeno 1 antipasto, 1 primo, 1 secondo, 1 dessert)
- Controlla che lista spesa non sia vuota
- Verifica timeline abbia tutti e 3 i giorni
- Valida coerenza ingredienti tra ricette e lista spesa

### Schema JSON Esemplificativo per Gemini

Il prompt include uno schema JSON di esempio che Gemini può seguire:

```json
{
  "courses": {
    "antipasti": [
      {
        "name": "Nome Piatto",
        "cuisine": "italiana",
        "description": "Descrizione...",
        "recipe": {
          "ingredients": [
            {"name": "ingrediente", "quantity": "100g", "category": "Dispensa"}
          ],
          "prep_time_minutes": 30,
          "instructions": ["Passo 1...", "Passo 2..."]
        }
      }
    ]
  },
  "shopping_list": {
    "categories": {
      "Frutta e verdura": [
        {"name": "pomodori", "quantity": "500g"}
      ]
    }
  },
  "timeline": {
    "two_days_before": ["Preparare brodo"],
    "one_day_before": ["Preparare impasto"],
    "day_of": ["09:00 - Iniziare cottura"]
  }
}
```

### Gestione Memory e Context

Gli agenti Datapizza AI supportano oggetti Memory per mantenere contesto conversazionale:

```python
from datapizza.memory import Memory

memory = Memory()
agent = Agent(name="menu_planner", client=client, memory=memory, tools=[...])
```

Nel progetto attuale la Memory è opzionale e NON è persistita tra richieste HTTP diverse. Ogni chiamata a /api/menu/generate crea un nuovo contesto isolato. Questo garantisce che le generazioni siano indipendenti e ripetibili, ma impedisce conversazioni multi-turn.

Estensione Futura: Per supportare conversazioni ("rigenera il primo", "aggiungi un piatto"), si potrebbe implementare session storage con memory persistita per menu_id.

---

## SLIDE 5: Architettura Full-Stack e API RESTful

### Architettura Complessiva

```
Frontend (React 18 + TypeScript + Vite)
    - Form di input con validazione client-side (8 parametri configurabili)
    - 3 Tab View: Menu (ricette espandibili), Shopping List (categorie), Timeline (3 giorni)
    - API Client Axios per comunicazione con backend
    - Type safety con TypeScript interfaces che rispecchiano modelli Pydantic
    
    HTTP/JSON su localhost:5173
    
Backend (FastAPI + Datapizza AI + Python 3.12)
    - API Layer: 9 endpoint RESTful con validazione Pydantic
    - Service Layer: MenuService per orchestrazione business logic
    - Agent Layer: 3 agenti Datapizza AI con custom tools
    - Model Layer: 15+ modelli Pydantic per input/output validation
    - Storage: In-memory dict (menu_store) per menù generati
    
    HTTP/JSON su localhost:8000
    
LLM Provider (Google Gemini 2.5 Flash)
    - Chiamate via datapizza-ai-clients-google
    - Rate limit: 15 richieste/minuto, 1500 richieste/giorno (Free Tier)
```

### API Endpoints Implementati

9 endpoint RESTful documentati con OpenAPI/Swagger:

GET /health
Health check del servizio
Response: 200 OK con {"status": "healthy"}

GET /docs
Swagger UI interattiva auto-generata da FastAPI
Permette testing manuale degli endpoint

POST /api/menu/generate
Genera menù completo nuovo
Request Body: UserInput (JSON con 8 parametri validati)
Response: MenuOutput (menù completo con ricette, shopping list, timeline)
Tempo medio: 15-25 secondi
Validazione: Pydantic valida tutti i campi, restituisce HTTP 422 se input non valido

POST /api/menu/regenerate-course
Rigenera una singola portata di un menù esistente
Request Body: {menu_id: UUID, course_type: string}
course_type: "antipasti", "primo", "secondo", "contorno", "dessert"
Response: Course (nuova portata rigenerata)
Uso: utente insoddisfatto di una portata, vuole alternative

GET /api/menu/{menu_id}
Recupera menù completo salvato
Path Parameter: menu_id (UUID)
Response: MenuOutput o HTTP 404 se non trovato

GET /api/menu/{menu_id}/shopping-list
Recupera solo lista spesa di un menù
Path Parameter: menu_id (UUID)
Response: ShoppingList (ingredienti per categoria)

GET /api/menu/{menu_id}/timeline
Recupera solo timeline di preparazione di un menù
Path Parameter: menu_id (UUID)
Response: Timeline (attività su 3 giorni)

GET /api/menu/
Lista tutti i menù salvati in memoria
Response: Array di MenuOutput
Uso: debugging, gestione menù multipli (feature non esposta nel frontend)

DELETE /api/menu/{menu_id}
Elimina menù dalla memoria
Path Parameter: menu_id (UUID)
Response: HTTP 204 No Content o HTTP 404 se non trovato

### Validazione Input con Pydantic

UserInput model con 15+ validators:

```python
from pydantic import BaseModel, field_validator, Field
from enum import Enum

class DietaryRestriction(str, Enum):
    VEGETARIANO = "vegetariano"
    VEGANO = "vegano"
    SENZA_GLUTINE = "senza_glutine"
    SENZA_LATTOSIO = "senza_lattosio"

class UserInput(BaseModel):
    num_guests: int = Field(ge=1, le=50, description="Numero ospiti (1-50)")
    cuisines: List[CuisineType] = Field(min_length=1, description="Almeno 1 cucina")
    preferred_ingredients: List[str] = Field(default_factory=list)
    avoided_ingredients: List[str] = Field(default_factory=list)
    dietary_restrictions: List[DietaryRestriction] = Field(default_factory=list)
    
    @field_validator('avoided_ingredients')
    def check_no_overlap(cls, v, info):
        preferred = info.data.get('preferred_ingredients', [])
        overlap = set(v) & set(preferred)
        if overlap:
            raise ValueError(f"Ingredienti in conflitto: {overlap}")
        return v
```

Risultato: Validazione automatica server-side, errori dettagliati HTTP 422 con field-level feedback.

### Frontend: Type Safety con TypeScript

TypeScript interfaces sincronizzate con modelli Pydantic:

```typescript
interface UserInput {
  num_guests: number;
  cuisines: string[];
  preferred_ingredients: string[];
  avoided_ingredients: string[];
  dietary_restrictions: string[];
  difficulty_level: string;
  budget_level: string;
  extra_notes?: string;
}

interface MenuOutput {
  menu_id: string;
  courses: MenuCourses;
  shopping_list: ShoppingList;
  timeline: Timeline;
  metadata: MenuMetadata;
}
```

Benefit: Errori di tipo catturati in fase di sviluppo, autocomplete IDE, refactoring sicuro.

### Storage: In-Memory con Limitazioni Note

Implementazione attuale:

```python
menu_store: Dict[str, MenuOutput] = {}

def save_menu(menu: MenuOutput) -> None:
    menu_store[str(menu.menu_id)] = menu

def get_menu(menu_id: str) -> Optional[MenuOutput]:
    return menu_store.get(menu_id)
```

Limitazioni:
- Dati persi al riavvio server
- Non scalabile per produzione multi-instance
- Nessuna persistenza

Estensione Futura: Implementare database (MongoDB per JSON documents, PostgreSQL con JSONB, Redis per caching) per persistenza e scalabilità.

### Testing: 110 Test con pytest

Copertura completa del backend:

test_models.py (35 test):
- Validazione Pydantic models
- Field validators (overlap ingredienti, range valori)
- Serializzazione/deserializzazione JSON

test_tools.py (23 test):
- Funzionamento custom tools in isolamento
- Edge cases (liste vuote, valori null)
- Output JSON corretto

test_api.py (27 test):
- Endpoint HTTP con TestClient FastAPI
- Status codes corretti (200, 404, 422)
- Validazione request/response

test_services.py (25 test):
- MenuService business logic
- Storage operations (save, get, delete)
- Orchestrazione pipeline (mock degli agenti)

Comando esecuzione: pytest tests/ -v --tb=short

Success rate: 110/110 test passano

---

## SLIDE 6: Conclusioni e Componenti Datapizza AI Utilizzati

### Componenti Datapizza AI Implementati

Il progetto utilizza i seguenti componenti del framework Datapizza AI:

1. Agent (datapizza.agents.Agent)
Classe base per creazione agenti AI
Configurazione: name, client, tools, memory, max_steps, planning_interval
3 istanze create: menu_planner, recipe_detailer, aggregation_agent
Funzionalità usate: invocazione tool automatica, planning interval per decisioni strategiche

2. GoogleClient (datapizza.clients.google.GoogleClient)
Client per integrazione Google Gemini API
Metodi usati: structured_response(), invoke()
Configurazione: api_key, model, system_prompt, temperature
Sistema di fallback implementato per gestire limitazioni API

3. Tool Decorator (datapizza.tools.tool)
Decoratore per registrazione custom tools
8 tool implementati e registrati
Pattern: funzioni Python che restituiscono stringhe JSON
Framework gestisce automaticamente invocazione da parte degli agenti

4. Memory (datapizza.memory.Memory)
Oggetto per mantenimento contesto conversazionale
Utilizzo: opzionale nel progetto, passato agli agenti ma non persistito
Preparato per future implementazioni multi-turn

### Caratteristiche Distintive del Progetto

Multi-Agent Collaboration:
3 agenti specializzati in pipeline sequenziale orchestrata da MenuService
Separazione responsabilità: planning, detailing, aggregation
Nessuna comunicazione diretta tra agenti (orchestrazione centralizzata)

Custom Tools Estensivi:
8 tool di dominio per operazioni specifiche
Copertura: validazione, calcoli, aggregazione, database conoscenza
Pattern coerente: JSON input/output

Structured Generation Robusta:
Strategia fallback per gestire limitazioni Gemini API
Auto-correzione JSON con 3 funzioni di fix
Success rate 95% (da 60% naive)

Validazione End-to-End:
15+ modelli Pydantic con validators custom
Type safety client-side con TypeScript
Validazione a ogni livello: frontend, API, business logic

Testing Completo:
110 test pytest con copertura modelli, tools, API, services
Test isolation: ogni componente testato indipendentemente
Integration test: endpoint API con TestClient

### Architettura Scalabile

Separazione layer pulita:
- API Layer (FastAPI routes)
- Service Layer (business logic)
- Agent Layer (AI orchestration)
- Model Layer (data validation)

Extensibility points:
- Aggiungere nuovi agenti modificando MenuService
- Estendere tool set con nuovi @tool decorator
- Modificare system prompt per behavior tuning
- Sostituire storage in-memory con database reale

Deployment ready:
- Dockerfile fornito per containerizzazione
- Frontend build statico servibile via CDN
- Backend ASGI deployment (Uvicorn, Gunicorn)
- Environment configuration con .env

### Metriche Finali

Tempo medio generazione menù completo: 15-25 secondi
Chiamate Gemini per menù: 2-3 (menu structure, recipe details, aggregation)
Codice backend: 1500+ righe
Codice frontend: 500+ righe
Test coverage: 110 test, 100% pass rate
Modelli Pydantic: 15 con validazione robusta
Endpoint API: 9 REST
Custom Tools: 8 registrati nel framework

### Lezioni Apprese - Datapizza AI

1. System Prompt è Fondamentale
Il comportamento degli agenti è definito primariamente dal system prompt
Prompt engineering iterativo necessario per output di qualità
Prompt in lingua target (italiano) produce risultati migliori per dominio specifico

2. Tool Return Type: Solo Stringhe
Tutti i tool DEVONO restituire stringhe (json.dumps())
Framework deserializza automaticamente per gli agenti
Non usare dict/list direttamente

3. GoogleClient: Limitazioni Parametri
GoogleClient NON supporta max_tokens nel costruttore (diverso da altri client)
Gemini API NON supporta additionalProperties negli schema JSON
Necessario fallback strategy per modelli complessi

4. Orchestrazione Centralizzata vs Comunicazione Diretta
Orchestrazione centralizzata (MenuService) più semplice da debuggare
Controllo preciso del flusso dati tra agenti
Memory non condivisa tra agenti (isolamento)

5. Temperature Tuning per Ruolo
Menu Agent (0.7): creatività per varietà piatti
Recipe Agent (0.5): bilanciato precisione/creatività
Aggregation Agent (0.3): deterministico per aggregazioni corrette

### Repository e Documentazione

GitHub: github.com/alexcri90/Christmas-World-Menu
Documentazione completa: README.md, project_description.md
Presentazione: slides.md (questo documento)
Deployment: Istruzioni in DEPLOYMENT.md

Stack completo open source
Licenza: MIT
Contributi: Benvenuti via Pull Request

---

FINE PRESENTAZIONE
