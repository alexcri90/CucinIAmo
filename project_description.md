# CucinIAmo - Documento Tecnico di Progetto

> **🍳 Menù personalizzati con l'AI, per ogni pasto e con le calorie sotto controllo**
> Stack: **React 19 + TypeScript + Vite** | Hosting: **Firebase (piano Spark, gratuito)** | LLM: **Google Gemini via Firebase AI Logic (free tier)**

---

## 📊 Stato del Progetto

**Ultimo aggiornamento:** 6 Luglio 2026
**Versione corrente:** 1.5.0
**Stato Roadmap v2:** tutte e 4 le fasi implementate e deployate (Fase 1 verificata manualmente; Fasi 2-4 da provare sul campo). Prossime idee: vedi "Fase 5+"

### 🎯 Cos'è CucinIAmo

CucinIAmo è l'evoluzione completa del vecchio "Christmas Menu Generator": da generatore di menù natalizi a **strumento per creare menù di ogni giorno e tenere sotto controllo le calorie**. La trasformazione (v1.0.0) ha mantenuto tutto ciò che funzionava dell'architettura originale (login Google + allowlist, hosting Firebase gratuito, generazione client-side con Gemini, rigenerazione dei piatti con feedback) e ha rivoluzionato il dominio:

1. **Niente più tema natalizio**: piatti per tutto l'anno, per qualunque occasione
2. **Cucine libere**: ~23 cucine suggerite come chip + campo di testo libero per aggiungerne qualsiasi altra ("vietnamita", "pugliese", "fusion nikkei"...)
3. **Scelta dei pasti**: colazione, pranzo, cena, spuntini, in qualunque combinazione — incluso il preset "Giornata intera"
4. **Limite calorie opzionale**: budget di kcal per persona sull'insieme dei pasti richiesti (es. 1700 kcal per la giornata, 400 per una colazione); ogni piatto riporta kcal e macro stimate per porzione e i totali sono ricalcolati client-side
5. **Design system dedicato** (v1.1.0): gradiente brand viola→magenta→corallo→arancio, logo a pomodoro, font Space Grotesk + Instrument Sans, neutri caldi — definito nella cartella `CucinIAmo design system/` e applicato a tutta l'app

### ✅ Storia delle versioni

| Versione | Contenuto |
|----------|-----------|
| **1.5.0** | **Fase 4 Roadmap v2 — Foto→calorie**: `utils/image.ts` (compressione canvas ≤1024px JPEG), `estimateNutritionFromPhoto` (Gemini multimodale via inlineData), bottone "📸 Analizza una foto" nel modal del diario con stima correggibile e anteprima locale; la foto non viene mai salvata (`source: 'foto'`) |
| **1.4.0** | **Fase 3 Roadmap v2 — Diario alimentare**: `diaryService.ts` (un doc per giorno su `users/{uid}/diary/{YYYY-MM-DD}`), componente `Diario.tsx` con vista giorno/mese, entry per pasto con kcal/macro, stima kcal da testo con Gemini (`estimateNutritionFromText`), budget kcal giornaliero (prefs), aggancio "L'ho cucinata!" → diario |
| **1.3.0** | **Fase 2 Roadmap v2 — Ricettario completo**: componenti `Ricettario.tsx` + `RecipeDetails.tsx`, ricerca/filtri/ordinamento, stelle 1-5 cliccabili, flusso "✅ L'ho cucinata!" (cooked_count + rating + nota), editing della copia personale (dosi, ingredienti, passaggi, note chef, nutrizione) con badge "Modificata", note datate |
| **1.2.0** | **Fase 1 Roadmap v2 — Fondamenta ricettario**: security rules `users/{uid}/**` con controllo allowlist (`isAllowed()`), nuovi tipi `SavedRecipe`/`RecipeNote`, `services/recipeService.ts` (CRUD Firestore), navigazione a tab 🍳 Genera / 📖 Ricettario, bottone 💾 su ogni piatto del menù, vista elenco base del ricettario (con eliminazione) |
| **1.1.0** | **Applicazione del design system CucinIAmo**: gradiente brand viola→magenta→corallo→arancio, font Space Grotesk (titoli) + Instrument Sans (UI), neutri caldi, chip/card/tab ridisegnati, nuovo logo (pomodoro, `frontend/public/logo.png`, anche favicon), login e header rinnovati. Fonte del design: cartella `CucinIAmo design system/` (mock HTML interattivo) |
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
c:\Users\alexc\Local Github\P4B\CucinIAmo\
├── firebase.json                 # Hosting + Firestore rules + predeploy build
├── .firebaserc                   # Project ID Firebase: cuciniamo-ricette
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
        ├── App.css               # Design system: gradiente brand, neutri caldi, token in :root
        ├── index.css             # Reset base + fondamenta (font, sfondo, selection)
        ├── firebase.ts           # Init Firebase (Auth, Firestore, AI Logic, App Check opz.)
        │
        ├── components\
        │   ├── AuthGate.tsx      # Login Google + verifica allowlist
        │   ├── Diario.tsx        # Diario alimentare: giorno/mese, budget, stima AI
        │   ├── RecipeDetails.tsx # Dettaglio ricetta espandibile (menù + ricettario)
        │   └── Ricettario.tsx    # Vista ricettario: filtri, stelle, editing, note
        │
        ├── services\
        │   ├── aiService.ts      # Prompt, chiamate Gemini, parsing/normalizzazione, helper kcal
        │   ├── diaryService.ts   # CRUD diario (users/{uid}/diary/{data}) + prefs
        │   └── recipeService.ts  # CRUD ricettario su Firestore (users/{uid}/recipes)
        │
        ├── types\
        │   └── index.ts          # Modello dati (FONTE DI VERITÀ)
        │
        └── utils\
            └── image.ts          # Compressione foto client-side (per la stima AI)
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
cd "c:\Users\alexc\Local Github\P4B\CucinIAmo\frontend"
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

## 🗺️ Roadmap v2 — Ricettario, Diario, Foto→Calorie

> Definita il 6 Luglio 2026 (rivista lo stesso giorno: **app mobile/PWA rimandata**, si resta web app). Questa sezione è il **piano d'azione ufficiale** per le prossime versioni. Regola invariata: **solo risorse gratuite** (piano Spark, nessuna carta di credito). Ogni fase è deployabile da sola: si rilascia, si usa, si passa alla successiva.

### Vincoli "gratis" verificati (decisioni di architettura)

Due fatti scoperti in fase di pianificazione che modellano tutta la roadmap:

1. **Cloud Storage for Firebase NON è più gratuito** sui nuovi progetti Spark (da ottobre 2024 richiede il piano Blaze anche per il bucket di default). Conseguenza: **le foto dei piatti non vengono mai salvate**. Per la feature foto→calorie l'immagine viene compressa client-side, inviata a Gemini (multimodale, già incluso nel free tier di Firebase AI Logic) e si persiste su Firestore **solo la stima testuale/numerica**. Opzionale: una miniatura molto compressa (~100-200 KB) come stringa base64 dentro il documento Firestore (limite 1 MiB/doc), da valutare solo se davvero utile.
2. **Pubblicare una app "vera" negli store costa** (Apple Developer $99/anno; Google Play $25 una tantum). La strada gratuita per iPhone e Android sarebbe la **PWA** (manifest + service worker, installabile dalla home screen, fotocamera via `<input capture>`). Decisione del 6 Luglio 2026: **per ora si resta web app e basta** — la PWA è spostata tra le idee future (vedi tabella in fondo). Nota bene: tutto il resto della roadmap funziona comunque perfettamente dal browser del telefono, foto comprese.

### Quota Firestore (Spark) vs. uso previsto

Utenti previsti: ~10-20 (amici e parenti). Quote gratuite: 50.000 letture/giorno, 20.000 scritture/giorno, 1 GiB storage. Anche con un uso intenso (ogni utente apre il ricettario e il diario più volte al giorno) si resta sotto il 5% delle quote. Una ricetta salvata pesa ~5-15 KB → 1 GiB ≈ decine di migliaia di ricette. **Nessun rischio concreto**; se mai si superasse una quota, il servizio si ferma fino al giorno dopo senza costi.

### Nuovo modello dati Firestore

Tutti i dati personali vivono sotto `users/{uid}/...` (uid = utente Firebase Auth). L'allowlist resta la porta d'ingresso.

```
users/{uid}/recipes/{recipeId}     ← Ricettario (Fase 1-2)
users/{uid}/diary/{YYYY-MM-DD}     ← Diario alimentare (Fase 4)
allowlist/{email}                  ← invariata
```

Tipi previsti (verranno aggiunti a `frontend/src/types/index.ts`, la fonte di verità):

```typescript
// ── Ricettario ──
interface SavedRecipe {
  recipe_id: string;            // uuid client-side (= ID documento)
  saved_at: string;             // ISO
  updated_at: string;           // ISO
  dish: Dish;                   // SNAPSHOT del piatto generato (modificabile dall'utente)
  source: { menu_id: string; meal_type: MealType } | null;
  rating: number | null;        // 1-5 stelle, solo se cucinata davvero
  cooked_count: number;         // quante volte è stata cucinata
  notes: RecipeNote[];          // commenti alle preparazioni
  is_customized: boolean;       // true se dish è stato modificato rispetto all'originale
}

interface RecipeNote { date: string; text: string; }

// ── Diario alimentare ──
interface DiaryDay {            // ID documento = "YYYY-MM-DD"
  date: string;
  entries: DiaryEntry[];
}

interface DiaryEntry {
  entry_id: string;
  meal_type: MealType;
  description: string;          // "Pasta al pesto", "2 fette di torta"...
  nutrition: NutritionInfo | null;
  recipe_id: string | null;     // link a una SavedRecipe (se si è cucinata una ricetta)
  source: 'manuale' | 'ricettario' | 'foto';
  logged_at: string;            // ISO
}
```

Scelte di design:
- **`dish` è uno snapshot, non un riferimento**: l'utente può modificare dosi, ingredienti e passaggi della SUA copia senza toccare nulla di condiviso. Niente ricette globali, niente problemi di permessi.
- **Il diario è un documento per giorno** (non una collection di entry): una sola lettura carica l'intera giornata, e la vista mensile costa ≤31 letture.
- **`rating` e `cooked_count` separati dalle note**: la valutazione ha senso solo per ricette effettivamente cucinate; la UI proporrà le stelle nel flusso "L'ho cucinata!".

### Nuove Security Rules (sostituiranno `firestore.rules`)

```
function isAllowed() {
  return request.auth != null
    && request.auth.token.email != null
    && exists(/databases/$(database)/documents/allowlist/$(request.auth.token.email.lower()));
}

match /users/{uid}/{document=**} {
  allow read, write: if isAllowed() && request.auth.uid == uid;
}
// allowlist: invariata (get del solo proprio doc, nessuna scrittura client)
```

Ogni utente legge/scrive **solo** i propri dati, e solo se è ancora in allowlist (revocare l'email = revocare anche l'accesso ai dati). Nota: le rules di Firestore non permettono di validare la dimensione in byte di un documento (quella funzione esiste solo in Storage); fa da tetto il limite hard di 1 MiB/doc di Firestore.

### 📦 Fase 1 — Fondamenta: persistenza + navigazione (v1.2.0) ✅ IMPLEMENTATA

L'infrastruttura su cui poggia tutto il resto. Codice completato il 6 Luglio 2026; resta la verifica sul progetto Firebase reale dopo il deploy.

- [x] Nuove security rules `users/{uid}/**` con controllo allowlist (`isAllowed()`) — nota: niente check sulla dimensione in byte (non esiste nelle rules Firestore; fa da tetto il limite hard di 1 MiB/doc)
- [x] Nuovo service `frontend/src/services/recipeService.ts`: CRUD su `users/{uid}/recipes` (save/list/update/delete); `stripUndefined` prima di ogni scrittura perché Firestore rifiuta i campi `undefined` (i piatti hanno campi opzionali)
- [x] Navigazione a schede nell'app (stato React, niente router): **🍳 Genera** | **📖 Ricettario** | (futuro: **📔 Diario**)
- [x] Bottone 💾 su ogni piatto del menù generato (💾 → spinner → ✓ verde; disabilitato se già salvata)
- [x] Nuovi tipi in `types/index.ts` (`SavedRecipe`, `RecipeNote`)
- [x] Vista elenco base del ricettario: card con nome/cucina/kcal/stelle/data, dettaglio ricetta espandibile, stato vuoto, eliminazione con conferma (anticipata dalla Fase 2)
- [x] Deploy su https://cuciniamo-ricette.web.app (6 Luglio 2026: rules + hosting pubblicati, bundle verificato online)
- [x] Test manuale del criterio di completamento — verificato il 6 Luglio 2026 ✅

**Criterio di completamento:** genero un menù, salvo un piatto, ricarico la pagina da un altro browser e lo ritrovo. ✅ Verificato.

### 📖 Fase 2 — Ricettario completo (v1.3.0) ✅ IMPLEMENTATA

La feature vera e propria, sopra le fondamenta della Fase 1. Il ricettario è ora un componente dedicato (`components/Ricettario.tsx`), con `RecipeDetails.tsx` condiviso col menù generato.

- [x] Vista elenco: card ricetta (nome, cucina, kcal, stelle, badge "modificata", contatore 👨‍🍳), ricerca per nome, filtri (pasto, cucina, valutazione/stato), ordinamento (recenti, rating, kcal)
- [x] Vista dettaglio: ricetta completa espandibile riusando `RecipeDetails`
- [x] Flusso "✅ L'ho cucinata!": incrementa `cooked_count`, chiede stelle (1-5, opzionali) e nota opzionale sulla preparazione
- [x] Valutazione modificabile in ogni momento (stelle cliccabili sulla card)
- [x] **Editing della ricetta**: nome, descrizione, dosi/quantità, aggiunta/rimozione ingredienti, passaggi, note dello chef, valori nutrizionali → `is_customized: true` + `updated_at`
- [x] Note/commenti multipli con data (aggiungibili sia dal flusso "cucinata" sia col bottone 📝)
- [x] Eliminazione ricetta (con conferma) — anticipata in v1.2.0

**Criterio di completamento:** salvo una ricetta, la modifico (dosi + un ingrediente), la segno come cucinata con 4 stelle e un commento, e ritrovo tutto dopo il logout/login.

### 📔 Fase 3 — Diario alimentare (v1.4.0) ✅ IMPLEMENTATA

- [x] Nuovi tipi `DiaryDay`/`DiaryEntry`/`UserPrefs`/`NutritionEstimate` + `diaryService.ts` (CRUD su `users/{uid}/diary/{YYYY-MM-DD}`, range query sul documentId per il mese, prefs su `users/{uid}/settings/prefs`)
- [x] Tab **📔 Diario** (`components/Diario.tsx`): vista giorno (default oggi) con entry raggruppate per pasto, totale kcal/macro della giornata (somme client-side), icona origine voce (✍️ manuale / 📖 ricettario / 📸 foto)
- [x] Aggiunta/modifica/eliminazione entry manuale: descrizione + pasto + kcal/macro opzionali, con bottone "✨ Stima kcal con AI" (`estimateNutritionFromText` in aiService, con porzione assunta e confidenza, valori sempre correggibili)
- [x] Aggiunta dal ricettario: "L'ho cucinata!" propone "📔 Aggiungi al diario di oggi" con scelta del pasto, portandosi dietro kcal e macro della ricetta (`source: 'ricettario'` + link `recipe_id`)
- [x] Navigazione tra i giorni (frecce, date picker, "Oggi") + vista mese con kcal/giorno e media (≤31 letture)
- [x] Budget kcal giornaliero opzionale salvato nelle prefs, con confronto verde/arancio nel totale del giorno e nella vista mese

**Criterio di completamento:** registro colazione manuale e una ricetta cucinata, vedo il totale kcal del giorno, e navigando indietro ritrovo i giorni passati.

### 📸 Fase 4 — Foto del piatto → stima calorie (v1.5.0) ✅ IMPLEMENTATA

Integrata nel modal "Aggiungi al diario" (bottone "📸 Analizza una foto" accanto alla stima da testo).

- [x] Cattura foto: `<input type="file" accept="image/*" capture="environment">` (browser iOS/Android senza permessi speciali)
- [x] Compressione client-side (`utils/image.ts`: canvas, lato lungo ≤1024px, JPEG 0.8) prima dell'invio
- [x] `estimateNutritionFromPhoto` in aiService: Gemini multimodale (prompt + `inlineData`) → JSON `{description, assumed_portion, nutrition, confidence}`, stessa pipeline di normalizzazione
- [x] UI risultato correggibile: la stima riempie i campi kcal/macro (modificabili prima di salvare), con nota su porzione assunta e confidenza; la descrizione scritta dall'utente ha la precedenza su quella dell'AI
- [x] Salvataggio come `DiaryEntry` con `source: 'foto'`; **la foto NON viene salvata** (solo anteprima locale nel modal, con avviso esplicito)
- [x] Gestione errori: foto non cibo (confidence bassa, kcal 0), quota esaurita (mapAiError), file non leggibile

**Criterio di completamento:** fotografo un piatto di pasta col telefono, ottengo una stima kcal plausibile, la correggo e la salvo nel diario di oggi.

### Fase 5+ — Oltre la roadmap (non pianificate)

| Idea | Note |
|------|------|
| 📱 **PWA installabile** | `vite-plugin-pwa`, manifest + service worker, icone dal logo, istruzioni installazione iOS/Android; attenzione al login Google in standalone su iOS (eventuale `signInWithRedirect`) — rimandata il 6 Luglio 2026 per restare web-only |
| 🏪 **App negli store (Capacitor)** | Stessa codebase wrappata in nativo; richiede Apple Developer $99/anno e Google Play $25 — fuori dal vincolo "solo gratis" |
| 💾 **Salvataggio menù interi** | Oggi si salvano i singoli piatti; si potrebbe persistere il menù completo con lista spesa e timeline |
| 📊 **Statistiche diario** | Grafici settimanali/mensili kcal e macro |
| 🎨 **Illustrazioni dedicate** | Sostituire le emoji con un set di icone coerente col design system |
| 🌐 **i18n** | Oggi l'app è solo in italiano (UI e prompt) |

---

*Documento tecnico del progetto CucinIAmo.*
*Versione documento: 8.0 — 6 Luglio 2026*
