# 🍳 CucinIAmo

> **Menù personalizzati con l'AI, per ogni pasto e con le calorie sotto controllo**

Una web app che genera menù su misura per qualsiasi occasione — una colazione per te, una cena per tanti ospiti o il piano di un'intera giornata — con ricette dettagliate, valori nutrizionali stimati, lista della spesa e piano di preparazione. Tutto ospitato su infrastruttura **100% gratuita** (Firebase piano Spark + Gemini free tier).

![React](https://img.shields.io/badge/React-19-61dafb?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?logo=typescript)
![Firebase](https://img.shields.io/badge/Firebase-Spark%20(free)-FFCA28?logo=firebase)
![Gemini](https://img.shields.io/badge/Google%20Gemini-free%20tier-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🍽️ **Scegli i pasti**: colazione, pranzo, cena, spuntini — o l'intera giornata in un colpo solo
- 🌍 **Cucine dal mondo intero**: chip con le cucine più popolari + campo libero per qualsiasi altra ("vietnamita", "pugliese", "fusion nikkei"...)
- 🔥 **Limite calorie opzionale**: imposta un budget di kcal per persona (es. 1700 per la giornata, 400 per la colazione) e l'AI costruisce il menù rispettandolo
- 📊 **Valori nutrizionali**: kcal e macro (proteine/carboidrati/grassi) stimati per ogni piatto, con totali per pasto e per giornata calcolati client-side
- 💚 **Ingredienti preferiti e da evitare**: l'AI include ciò che ami ed esclude ciò che non vuoi (o non puoi) mangiare
- 🥬 **Restrizioni alimentari**: vegetariano, vegano, senza glutine, senza lattosio
- 🔄 **Rigenerazione intelligente**: non ti piace un piatto? Rigeneralo, anche con feedback specifico, mantenendo coerenza (e calorie) col resto del menù
- 🎛️ **Selezione modello**: scegli dalla UI quale modello Gemini genera il menù
- 🔐 **Accesso riservato**: login con Google + allowlist di email gestita dal proprietario su Firestore
- 🛒 **Lista della spesa**: ingredienti aggregati automaticamente per categoria
- ⏰ **Piano di preparazione**: cosa preparare in anticipo e programma orario del giorno stesso
- 🖨️ **Export PDF**: stampa diretta dal browser

---

## 🛠️ Stack Tecnologico

**Tutto client-side, zero server, zero costi:**

- **React 19 + TypeScript** — UI
- **Vite 7.x** — build tool e dev server
- **Firebase Hosting** — hosting statico (piano Spark, gratuito)
- **Firebase Authentication** — login con Google
- **Cloud Firestore** — allowlist delle email autorizzate
- **Firebase AI Logic** — chiamate a Gemini senza backend e senza API key nel codice (Gemini Developer API, free tier)

---

## 🚀 Quick Start

> 🔥 **Deploy online**: l'app è pensata per essere pubblicata su **Firebase Hosting** (piano Spark, 100% gratuito), con login Google e allowlist di email decisa dal proprietario. Guida completa passo-passo: [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md)

### Prerequisiti

- Node.js 18+ (consigliato v22.x)
- Un account Google (per creare il progetto Firebase gratuito)

### Setup

Serve un progetto Firebase gratuito (piano Spark): segui i passaggi 1-6 di [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md), poi:

```bash
cd frontend
npm install

# Crea frontend/.env con la configurazione della tua web app Firebase
cp .env.example .env   # e compila i valori

npm run dev
```

- 🌐 **App in locale**: http://localhost:5173

---

## 📖 Utilizzo

1. Accedi con Google (la tua email deve essere nell'allowlist su Firestore)
2. Configura il menù:
   - **Persone**: 1-50
   - **Pasti**: colazione, pranzo, cena, spuntini o "giornata intera"
   - **Cucine**: seleziona dalle proposte o scrivi le tue
   - **Ingredienti** preferiti e da evitare
   - **Restrizioni**: vegetariano, vegano, senza glutine, senza lattosio
   - **Limite calorie** (opzionale): kcal massime a persona
   - **Difficoltà** e **budget di spesa**
3. Clicca "Crea il Menù!"
4. Esplora le 3 tab: **Menù** (con kcal e macro), **Lista Spesa**, **Preparazione**
5. Usa "Stampa PDF" per salvare il risultato

### Rigenera un piatto

1. Nella tab **Menù**, trova il piatto da cambiare
2. Clicca **🔄** per una rigenerazione rapida, oppure **💬** per dare un feedback specifico:
   - *"Vorrei qualcosa con più proteine"*
   - *"Preferisco un piatto più leggero"*
   - *"Qualcosa di thailandese"*
3. Il nuovo piatto resterà coerente col resto del menù e, se hai impostato un limite di calorie, manterrà kcal simili a quello sostituito
4. La lista della spesa si aggiorna automaticamente

---

## 🏗️ Architettura

```
┌──────────────────────────────────────────────────────────────┐
│              FIREBASE HOSTING (React + TypeScript)           │
│   Login Google (Authentication) → allowlist (Firestore)     │
│                            │                                 │
│                            ▼                                 │
│        Firebase AI Logic (Gemini Developer API, free)       │
│      generazione menù + rigenerazione piatti client-side    │
└──────────────────────────────────────────────────────────────┘
```

Non esiste un backend: i prompt vengono costruiti nel browser ([aiService.ts](frontend/src/services/aiService.ts)), le chiamate a Gemini passano dal proxy di Firebase AI Logic (nessuna API key nel codice) e le risposte JSON vengono validate e normalizzate client-side. I totali calorici sono ricalcolati localmente sommando i piatti, senza fidarsi dell'aritmetica del modello.

---

## 📁 Struttura Progetto

```
AI_Recipes/
├── firebase.json             # Config hosting + Firestore rules
├── .firebaserc               # Project ID Firebase (da personalizzare)
├── firestore.rules           # Security rules (allowlist)
├── FIREBASE_DEPLOYMENT.md    # Guida deployment passo-passo
├── project_description.md    # Documento tecnico del progetto
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── .env.example          # Template configurazione Firebase
    │
    └── src/
        ├── App.tsx           # Form + viste risultati
        ├── App.css           # Stili
        ├── firebase.ts       # Init Firebase (Auth, Firestore, AI Logic)
        │
        ├── components/
        │   └── AuthGate.tsx  # Login Google + verifica allowlist
        │
        ├── services/
        │   └── aiService.ts  # Prompt, chiamate Gemini, normalizzazione JSON
        │
        └── types/
            └── index.ts      # Modello dati (FONTE DI VERITÀ)
```

---

## ⚠️ Limitazioni Note

- **Nessuna persistenza**: i menù vivono nello stato del browser; ricaricando la pagina si perdono (un diario calorie su Firestore è una possibile evoluzione futura)
- **Le kcal sono stime**: i valori nutrizionali sono stimati dall'AI, non provengono da un database nutrizionale certificato — utili come ordine di grandezza, non per uso medico
- **Rate limit Gemini free tier**: pochi req/min e quota giornaliera per modello; superata la quota si riceve un errore 429, mai un addebito
- **Modelli in preview**: possono essere ritirati da Google; la lista dei modelli è in `frontend/src/services/aiService.ts` (costante `AVAILABLE_MODELS`)

---

## 📄 License

Distribuito sotto licenza MIT.

---

<p align="center">
  Made with ❤️ and 🍳 — powered by Google Gemini via Firebase AI Logic
</p>
