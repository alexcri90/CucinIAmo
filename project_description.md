# CucinIAmo - Documento Tecnico di Progetto

> **🍳 Menù personalizzati con l'AI, per ogni pasto e con le calorie sotto controllo**
> Stack: **React 19 + TypeScript + Vite** | Hosting: **Firebase (piano Spark, gratuito)** | LLM: **Google Gemini via Firebase AI Logic (free tier)**

---

## 📊 Stato del Progetto

**Ultimo aggiornamento:** 5 Luglio 2026
**Versione corrente:** 1.0.0

### 🎯 Cos'è CucinIAmo

CucinIAmo è l'evoluzione completa del vecchio "Christmas Menu Generator": da generatore di menù natalizi a **strumento per creare menù di ogni giorno e tenere sotto controllo le calorie**. La trasformazione (v1.0.0) ha mantenuto tutto ciò che funzionava dell'architettura originale (login Google + allowlist, hosting Firebase gratuito, generazione client-side con Gemini, rigenerazione dei piatti con feedback) e ha rivoluzionato il dominio:

1. **Niente più tema natalizio**: piatti per tutto l'anno, per qualunque occasione
2. **Cucine libere**: ~23 cucine suggerite come chip + campo di testo libero per aggiungerne qualsiasi altra ("vietnamita", "pugliese", "fusion nikkei"...)
3. **Scelta dei pasti**: colazione, pranzo, cena, spuntini, in qualunque combinazione — incluso il preset "Giornata intera"
4. **Limite calorie opzionale**: budget di kcal per persona sull'insieme dei pasti richiesti (es. 1700 kcal per la giornata, 400 per una colazione); ogni piatto riporta kcal e macro stimate per porzione e i totali sono ricalcolati client-side
5. **Asset grafici**: volutamente minimali (emoji), da rifare in una fase successiva

### ✅ Storia delle versioni

| Versione | Contenuto |
|----------|-----------|
| **1.0.0** | **Trasformazione in CucinIAmo**: rimozione backend Python/Datapizza e test (era una demo locale non usata in produzione), nuovo modello dati (Meal/Dish/NutritionInfo), nuovi prompt con budget calorico, form rinnovato (pasti, cucine ibride, limite kcal), nuova palette non natalizia, docs riscritte |
| 0.16.0 | Migrazione a Firebase: hosting Spark, login Google + allowlist Firestore, generazione client-side via Firebase AI Logic, selettore modello Gemini |
| ≤0.15.x | Progetto natalizio originale (backend FastAPI + Datapizza AI multi-agent, 120 test) — vedi la history git per i dettagli |

---

## 🛠️ Stack Tecnologico

**Tutto client-side. Nessun server. Nessun costo possibile** (piano Spark senza carta di credito).

| Componente | Tecnologia | Note |
|---|---|---|
| UI | React 19 + TypeScript 5 + Vite 7 | SPA senza router |
| Hosting | Firebase Hosting (Spark) | Sito statico, `firebase deploy` |
| Login | Firebase Authentication | Solo provider Google |
| Autorizzazione | Cloud Firestore | Collection `allowlist`, un doc per email autorizzata; security rules in `firestore.rules` |
| AI | Firebase AI Logic → Gemini Developer API | Free tier, nessuna API key nel codice |
| Protezione quota | Firebase App Check (opzionale) | reCAPTCHA v3, si attiva con `VITE_RECAPTCHA_SITE_KEY` |

I modelli Gemini selezionabili dalla UI sono definiti in `frontend/src/services/aiService.ts` (costante `AVAILABLE_MODELS`): gemini-2.5-flash (default), flash-lite, 2.5-pro, gemini-3-flash-preview.

---

## 🎯 Architettura

```
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER (React + TypeScript)                 │
│                                                                 │
│  AuthGate ──► Firebase Auth (Google) ──► Firestore allowlist    │
│     │                                                           │
│     ▼                                                           │
│  App.tsx (form + viste) ──► aiService.ts                        │
│                              │  buildMenuPrompt /               │
│                              │  buildRegenerationPrompt         │
│                              ▼                                  │
│                    Firebase AI Logic (proxy)                    │
│                              │                                  │
│                              ▼                                  │
│                 Gemini Developer API (free tier)                │
│                              │                                  │
│                              ▼                                  │
│          parseJsonResponse + normalize* (fallback robusti)      │
│                              │                                  │
│                              ▼                                  │
│    MenuOutput → render (kcal/macro, lista spesa, preparazione)  │
└─────────────────────────────────────────────────────────────────┘
```

Punti chiave:
- **Nessun backend**: i prompt sono costruiti nel browser, la risposta JSON è validata e normalizzata client-side
- **Il menù corrente è il "contesto"**: per la rigenerazione di un piatto, gli altri piatti (con le loro kcal) vengono inclusi nel prompt
- **Non ci fidiamo dell'aritmetica del modello**: i totali kcal per pasto e per menù sono somme client-side (`mealCalories`, `menuCalories`), e la lista spesa può essere ricostruita localmente (`computeShoppingList`) se il modello la omette

---

## 📁 Struttura Progetto

```
D:\GitHubRepos\AI_Recipes\
├── firebase.json                 # Hosting + Firestore rules + predeploy build
├── .firebaserc                   # Project ID Firebase (placeholder da sostituire)
├── firestore.rules               # Security rules: allowlist read-only per il proprio doc
├── firestore.indexes.json
├── FIREBASE_DEPLOYMENT.md        # Guida passo-passo (per chi parte da zero)
├── README.md
├── project_description.md        # ← questo file
│
└── frontend\
    ├── .env                      # Config Firebase (NON committare)
    ├── .env.example              # Template con istruzioni
    ├── package.json              # name: cuciniamo, v1.0.0
    │
    └── src\
        ├── main.tsx              # Entry point: AuthGate → App
        ├── App.tsx               # Form (pasti, cucine, kcal, ...) + viste risultati
        ├── App.css               # Stili (palette: --primary arancio, --secondary verde, --accent ambra)
        ├── index.css             # Reset base Vite
        ├── firebase.ts           # Init Firebase (Auth, Firestore, AI Logic, App Check opz.)
        │
        ├── components\
        │   └── AuthGate.tsx      # Login Google + verifica allowlist
        │
        ├── services\
        │   └── aiService.ts      # Prompt, chiamate Gemini, parsing/normalizzazione, helper kcal
        │
        └── types\
            └── index.ts          # Modello dati (FONTE DI VERITÀ)
```

---

## 🧬 Modello Dati (frontend/src/types/index.ts — FONTE DI VERITÀ)

```typescript
type MealType = "colazione" | "pranzo" | "cena" | "spuntino";
type DietaryRestriction = "vegetariano" | "vegano" | "senza_glutine" | "senza_lattosio";
type DifficultyLevel = "facile" | "medio" | "avanzato";
type BudgetLevel = "economico" | "medio" | "premium";

interface UserInput {
  num_people: number;              // 1-50
  meal_types: MealType[];          // almeno uno; colazione+pranzo+cena = giornata intera
  cuisines: string[];              // TESTO LIBERO (non più enum!)
  preferred_ingredients: string[];
  avoided_ingredients: string[];
  dietary_restrictions: DietaryRestriction[];
  difficulty_level: DifficultyLevel;
  budget_level: BudgetLevel;
  max_calories: number | null;     // kcal PER PERSONA sull'insieme dei pasti (opzionale)
}

interface NutritionInfo {          // stime PER PORZIONE (una persona)
  calories: number; protein_g: number; carbs_g: number; fat_g: number;
}

interface Dish {
  dish_id: string;                 // uuid generato client-side
  name: string;
  cuisine: string;
  role: string;                    // "Antipasto", "Piatto unico", "Bevanda", ... (stringa libera)
  description: string;
  nutrition: NutritionInfo;
  recipe: Recipe;                  // ingredients, tempi, difficulty, steps, chef_notes, prep-ahead
}

interface Meal { meal_type: MealType; dishes: Dish[]; }

interface MenuOutput {
  menu_id: string;
  generated_at: string;
  input: UserInput;
  meals: Meal[];                   // solo i pasti richiesti, in ordine canonico
  shopping_list: ShoppingList;     // categorie → ingredienti
  timeline: Timeline;              // { in_advance: string[], day_of: {"HH:MM": "..."} }
}
```

Note di design:
- **`cuisines` è testo libero**: il vecchio enum di 9 paesi è stato eliminato; la UI propone chip suggerite (`SUGGESTED_CUISINES` in App.tsx) ma accetta qualsiasi stringa
- **`role` è una stringa libera**: la struttura del pasto non è più fissa (antipasto/primo/secondo/contorno/dessert); il prompt dà linee guida per pasto (colazione 2-4 voci, cena 1-4 piatti a seconda del contesto, ecc.) e il modello decide
- **`meal_type` invece è un enum chiuso**: serve per raggruppare, ordinare e rigenerare in modo affidabile

---

## 🔥 Logica Calorie

1. **Input**: il form ha un toggle "Imposta un limite" + campo numerico (kcal/persona). Se disattivato → `max_calories: null`
2. **Prompt di generazione** (`buildCaloriesSection` in aiService.ts):
   - senza limite → si chiede comunque una stima realistica di kcal/macro per ogni piatto
   - con limite → vincolo obbligatorio: somma ≤ max, target 85-100% del budget; se è richiesta la giornata intera si suggerisce la ripartizione (colazione 20-25%, pranzo 35-40%, cena 30-35%, spuntini 5-10%)
3. **Normalizzazione**: `normalizeNutrition` forza numeri ≥ 0 e arrotonda
4. **Visualizzazione**: badge kcal su ogni piatto, totale per pasto (`mealCalories`), riepilogo del menù con confronto rispetto al limite (verde = entro, arancio = oltre) — tutto sommato client-side
5. **Rigenerazione**: il prompt impone al piatto nuovo kcal simili al piatto sostituito (±15% se c'è un budget), salvo diversa richiesta nel feedback utente

⚠️ Le kcal sono **stime dell'LLM**, non valori da database nutrizionale: vanno bene come ordine di grandezza, non per uso medico.

---

## 🔐 Autenticazione e Autorizzazione

Invariata rispetto alla v0.16.0 (funzionava benissimo):

1. Login con Google (Firebase Authentication, popup)
2. `AuthGate` legge `allowlist/{email minuscola}` su Firestore: se il documento esiste → accesso consentito
3. Le security rules permettono a ogni utente autenticato di leggere **solo** il proprio documento; nessuna scrittura dal client
4. L'allowlist si gestisce dalla console Firebase (aggiungi/rimuovi documenti nella collection `allowlist`)

---

## ⚡ Comandi Utili

```powershell
# Sviluppo locale
cd D:\GitHubRepos\AI_Recipes\frontend
npm install
npm run dev          # http://localhost:5173

# Verifica tipi + build di produzione
npm run build        # tsc -b && vite build → frontend/dist/

# Lint
npm run lint

# Deploy (dalla ROOT del repo, dopo aver configurato .firebaserc)
firebase deploy
```

---

## 🔴 Lessons Learned (da conservare!)

Ereditati dal progetto precedente e ancora validi:

### 1. Gemini devia dalla struttura JSON richiesta
Anche con `responseMimeType: 'application/json'` e un esempio esplicito nel prompt, il modello a volte: usa chiavi contenitore diverse, restituisce liste al posto di dizionari, omette campi. Per questo `aiService.ts` ha una pipeline di normalizzazione (`parseJsonResponse` → `normalizeMeals`/`normalizeDish`/`normalizeNutrition`/... ) che corregge gli errori più comuni invece di fallire, con placeholder per i pasti mancanti.

### 2. Il feedback utente va messo in evidenza nel prompt
Se il feedback di rigenerazione è una riga qualunque, il modello lo ignora. Serve una sezione dedicata "🎯 FEEDBACK UTENTE (PRIORITÀ MASSIMA)" + regola esplicita numerata.

### 3. Firebase AI Logic: usare GoogleAIBackend, MAI VertexAIBackend
`VertexAIBackend` richiede il piano Blaze (a pagamento). `GoogleAIBackend` = Gemini Developer API = free tier Spark.

### 4. La config Firebase nel bundle è pubblica per design
Non è un segreto: la sicurezza la fanno Authentication + Security Rules + allowlist. Per proteggere la **quota** gratuita da usi esterni c'è App Check (opzionale, già predisposto in `firebase.ts`).

### 5. Modelli in preview vengono ritirati
`AVAILABLE_MODELS` è volutamente una semplice lista in `aiService.ts`: quando un modello sparisce (errore 404) basta aggiornare la lista.

### 6. TypeScript: `import type` per le interfacce
Con Vite/React usare sempre `import type { ... }` per i tipi, altrimenti in alcuni setup l'import runtime fallisce.

### 7. Non fidarsi dei totali calcolati dall'LLM
Somme di calorie e lista spesa aggregata possono essere sbagliate: si ricalcolano client-side.

---

## 🚀 Possibili Evoluzioni Future

| Idea | Note |
|------|------|
| 🎨 **Asset grafici** | Sostituire le emoji con illustrazioni/logo dedicati (il codice usa solo emoji proprio per rendere facile questo passaggio) |
| 📔 **Diario calorie** | Salvare su Firestore cosa si è mangiato giorno per giorno con totali e storico (richiede nuove security rules per una collection `users/{uid}/diary`) — valutato e rimandato in v1.0.0 |
| 💾 **Salvataggio menù** | Persistere i menù generati (oggi vivono solo nello stato React) |
| 🌐 **i18n** | Oggi l'app è solo in italiano (UI e prompt) |
| 📱 **PWA** | Manifest + service worker per installarla sul telefono |

---

*Documento tecnico del progetto CucinIAmo.*
*Versione documento: 6.0 — 5 Luglio 2026*
