# 🔥 Guida al Deployment su Firebase (100% GRATUITO)

Questa guida ti porta da zero all'app **CucinIAmo** online su Firebase, **senza spendere un centesimo e senza rischio di costi nascosti**. È pensata per chi non ha mai usato Firebase o Google Cloud.

> 💡 CucinIAmo va pubblicato in un **nuovo progetto Google Cloud/Firebase**, separato da quello del vecchio menù natalizio: segui questa guida dall'inizio.

---

## 💰 Perché è impossibile pagare qualcosa

Prima di tutto, la cosa che ti interessa di più:

1. **Il piano gratuito di Firebase si chiama "Spark"** ed è quello con cui nasce ogni nuovo progetto. **Non richiede carta di credito.**
2. **Senza carta di credito registrata, Google non può addebitarti nulla.** Se un giorno superassi le quote gratuite, i servizi semplicemente smettono di rispondere (errori tipo 429) fino al giorno dopo. Non scatta MAI un pagamento.
3. **Regola d'oro**: se in qualsiasi schermata vedi le parole **"Upgrade"**, **"Blaze"**, **"billing"** o ti viene chiesta una **carta di credito** → chiudi quella schermata. Per questo progetto **non serve mai**.
4. In questa architettura **non ci sono server** (niente Cloud Functions, niente Cloud Run): il sito è statico e le chiamate all'AI passano dal servizio gratuito "Firebase AI Logic". Sono esattamente i servizi disponibili sul piano Spark.

### Servizi usati e relative quote gratuite

| Servizio | A cosa serve | Quota gratuita (Spark) | Cosa succede se la superi |
|---|---|---|---|
| **Hosting** | Serve il sito web | 10 GB storage, 360 MB/giorno di traffico | Sito non raggiungibile fino al reset. Nessun costo |
| **Authentication** | Login con Google | Illimitato per il provider Google | — |
| **Firestore** | Lista email autorizzate | 50.000 letture/giorno (noi ne usiamo 1 per login) | Errore di permesso. Nessun costo |
| **AI Logic (Gemini Developer API)** | Generazione dei menù | Free tier Gemini: ~10-15 richieste/minuto e alcune centinaia al giorno (varia per modello) | Errore 429 "quota esaurita". Nessun costo |

---

## ✅ Prerequisiti

- Un account Google (quello che usi per Gmail va benissimo)
- Node.js installato (ce l'hai già: v22)
- Questo repository sul tuo PC

---

## Parte 1 — Creare il progetto Firebase (solo console web, ~10 minuti)

### 1️⃣ Crea il progetto

1. Vai su [console.firebase.google.com](https://console.firebase.google.com) e accedi col tuo account Google
2. Clicca **"Crea un progetto"** (o "Add project")
3. Nome progetto: es. `cuciniamo` → prendi nota del **Project ID** che appare sotto il nome (es. `cuciniamo` o `cuciniamo-a1b2c`): ti servirà dopo
4. Quando chiede **Google Analytics**: **disattivalo** (non serve e semplifica tutto)
5. Clicca **"Crea progetto"** e attendi

> ✅ Verifica: in basso a sinistra nella console deve esserci scritto **"Spark"** (il piano gratuito). Non toccare mai il pulsante "Upgrade".

### 2️⃣ Registra la Web App e ottieni la configurazione

1. Nella pagina principale del progetto, clicca sull'icona **`</>`** (Web)
2. Nickname: `cuciniamo-web`
3. **NON** spuntare "Also set up Firebase Hosting" (lo faremo con la CLI)
4. Clicca **"Registra app"**
5. Ti verrà mostrato un blocco di codice `firebaseConfig` con 6 valori (`apiKey`, `authDomain`, `projectId`, `storageBucket`, `messagingSenderId`, `appId`). **Tienili sotto mano** (li ritrovi comunque sempre in ⚙️ *Impostazioni progetto → Le tue app*)
6. Clicca "Continue to console" ignorando le istruzioni npm mostrate

### 3️⃣ Crea il file `frontend/.env`

Nel repository, copia `frontend/.env.example` in `frontend/.env` e incolla i tuoi valori:

```powershell
cd D:\GitHubRepos\AI_Recipes
Copy-Item frontend\.env.example frontend\.env
notepad frontend\.env
```

Esempio di com'è fatto una volta compilato:

```env
VITE_FIREBASE_API_KEY=AIzaSyB...
# ⚠️ come AUTH_DOMAIN usa il dominio del sito (PROJECT-ID.web.app), NON
# quello .firebaseapp.com proposto dalla console: serve al login della
# PWA installata su iPhone (vedi project_description.md, lesson 8)
VITE_FIREBASE_AUTH_DOMAIN=cuciniamo.web.app
VITE_FIREBASE_PROJECT_ID=cuciniamo
VITE_FIREBASE_STORAGE_BUCKET=cuciniamo.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abc123def456
```

> 💡 Questi valori **non sono segreti** (finiscono comunque nel sito pubblico) ma il file `.env` è nel `.gitignore` per buona pratica. La sicurezza vera la fanno il login Google, l'allowlist e le Security Rules.

> ⚠️ **Passaggio obbligatorio se usi il dominio `.web.app` come AUTH_DOMAIN** (come sopra): il client OAuth creato automaticamente da Firebase conosce solo il dominio `.firebaseapp.com`, quindi senza questo passaggio ogni login fresco fallisce con **"Errore 400: redirect_uri_mismatch"**. Vai su [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) (stesso account Google, seleziona il progetto), apri **ID client OAuth 2.0 → "Web client (auto created by Google Service)"** e:
> 1. in **URI di reindirizzamento autorizzati** aggiungi `https://IL-TUO-PROJECT-ID.web.app/__/auth/handler`
> 2. in **Origini JavaScript autorizzate** aggiungi `https://IL-TUO-PROJECT-ID.web.app`
> 3. Salva (attivo in pochi minuti). È tutto gratuito: stai solo configurando, non attivando servizi.

### 4️⃣ Attiva l'Authentication con Google

1. Menu laterale: **Build → Authentication** → **"Inizia"** (Get started)
2. Tab **"Sign-in method"** → clicca su **Google**
3. Sposta l'interruttore su **Abilita**
4. "Support email": seleziona la tua email
5. **Salva**

### 5️⃣ Crea il database Firestore (per l'allowlist)

1. Menu laterale: **Build → Firestore Database** → **"Crea database"**
2. Location: scegli **`eur3 (europe-west)`** (o una regione europea) — ⚠️ non si può cambiare dopo
3. Modalità: **"Avvia in modalità di produzione"** (production mode — blocca tutto di default, le regole giuste le carichiamo noi al deploy)
4. **Crea**

### 6️⃣ Attiva Firebase AI Logic (il "motore" Gemini)

1. Menu laterale: **Build → AI Logic** (a volte sotto la sezione "AI")
2. Clicca **"Get started"** / "Inizia"
3. Ti chiederà quale provider API usare: scegli **"Gemini Developer API"** — è quella etichettata come disponibile sul piano gratuito
4. ⚠️ **NON scegliere "Vertex AI Gemini API"**: quella richiede il piano Blaze (a pagamento)
5. Conferma: Firebase crea automaticamente dietro le quinte una chiave API Gemini (non devi copiarla da nessuna parte)

---

## Parte 2 — Deploy dal tuo PC (~5 minuti)

### 7️⃣ Installa la Firebase CLI e fai login

```powershell
npm install -g firebase-tools
firebase login
```

Si aprirà il browser: accedi con lo **stesso account Google** della console.

### 8️⃣ Collega il repository al tuo progetto

Apri il file `.firebaserc` nella root del repository e sostituisci il placeholder con il tuo **Project ID** (quello dello step 1):

```json
{
  "projects": {
    "default": "cuciniamo"
  }
}
```

### 9️⃣ Deploy! 🚀

```powershell
cd D:\GitHubRepos\AI_Recipes
firebase deploy
```

Questo comando, in automatico:
- compila il frontend (`npm run build`)
- carica le **Security Rules** di Firestore (file `firestore.rules`)
- pubblica il sito su **Firebase Hosting**

Alla fine vedrai l'URL del sito:

```
Hosting URL: https://cuciniamo.web.app
```

### 🔟 Aggiungi le email autorizzate (l'allowlist)

Il sito ora chiede il login con Google, ma **nessuno è ancora autorizzato** (nemmeno tu). Aggiungi le email dalla console:

1. Console Firebase → **Build → Firestore Database**
2. Clicca **"+ Avvia raccolta"** (Start collection)
3. ID raccolta: `allowlist` → Avanti
4. **ID documento**: scrivi l'email da autorizzare, **tutta in minuscolo** (es. `alexcri90@gmail.com`)
5. Aggiungi un campo qualsiasi (Firestore richiede almeno un campo), ad esempio:
   - Campo: `allowed` — Tipo: `boolean` — Valore: `true`
6. **Salva**

Per autorizzare altre persone: nella raccolta `allowlist` clicca **"+ Aggiungi documento"** e ripeti con la loro email Google (sempre minuscola).
Per **revocare** un accesso: elimina il documento corrispondente. Fine.

### 1️⃣1️⃣ Verifica finale

1. Apri `https://IL-TUO-PROJECT-ID.web.app`
2. Clicca "Accedi con Google" → login col tuo account
3. Se la tua email è nell'allowlist entri nell'app; altrimenti vedi "Accesso non autorizzato"
4. Genera un menù 🍳 (puoi anche scegliere il modello Gemini dal menù a tendina nel form)

---

## 🔄 Aggiornamenti futuri

Ogni volta che modifichi il codice:

```powershell
cd D:\GitHubRepos\AI_Recipes
firebase deploy
```

Per lo sviluppo in locale (`cd frontend; npm run dev` → http://localhost:5173): funziona con lo stesso progetto Firebase, perché `localhost` è già tra i domini autorizzati.

---

## 🛡️ App Check (opzionale ma consigliato)

Firebase mostra spesso un avviso tipo *"Registra le tue app con Firebase App Check"*. Non riguarda la fatturazione (su Spark è comunque impossibile pagare), ma protegge una cosa diversa: la configurazione Firebase è pubblica nel bundle JS del sito, quindi in teoria uno sconosciuto potrebbe copiarla e chiamare Gemini tramite il tuo progetto, **consumando la tua quota gratuita giornaliera** (il sintomo sarebbe: i tuoi utenti autorizzati vedono "quota esaurita" senza motivo apparente). App Check verifica che le chiamate arrivino davvero dalla tua app pubblicata.

Il codice è già pronto (in `frontend/src/firebase.ts`) e resta disattivato finché non fai questi passaggi:

1. Console Firebase → **Build → App Check**
2. Nella lista delle app, trova la tua web app → **"Registra"**
3. Provider: scegli **reCAPTCHA v3**
4. Firebase ti guida a creare una chiave reCAPTCHA v3 gratuita (sito [google.com/recaptcha/admin](https://www.google.com/recaptcha/admin) se te lo chiede a parte): registra sia il dominio `IL-TUO-PROJECT-ID.web.app` sia `localhost` (per poter testare anche in sviluppo)
5. Copia la **Site key** ottenuta in `frontend/.env`:
   ```env
   VITE_RECAPTCHA_SITE_KEY=6Lc...
   ```
6. `firebase deploy`
7. **Non attivare subito "Applica" (Enforce)**. Per qualche minuto/ora lascia lo stato "Non applicato" (Unenforced) e usa l'app normalmente: nella dashboard di App Check (tab "APIs", righe "Gemini Developer API" e "Cloud Firestore") vedrai comparire richieste **verificate**. Solo quando vedi che la stragrande maggioranza delle richieste sono verificate, passa a **"Applica"** per entrambe. Se attivi "Applica" troppo presto, rischi di bloccare anche te stesso.

Se non vuoi farlo ora: lascia `VITE_RECAPTCHA_SITE_KEY` vuota, l'app funziona lo stesso, semplicemente senza questa protezione extra.

---

## 🔧 Troubleshooting

| Problema | Causa | Soluzione |
|---|---|---|
| Schermata "Configurazione mancante" | Manca `frontend/.env` | Crea il file (step 3) e rifai la build/deploy |
| `auth/unauthorized-domain` al login | Dominio non autorizzato | Authentication → Settings → Authorized domains → aggiungi il dominio. (`localhost`, `*.web.app` e `*.firebaseapp.com` del progetto sono già inclusi) |
| "Errore 400: redirect_uri_mismatch" al login (o PWA bloccata sul caricamento) | AUTH_DOMAIN = `.web.app` ma il redirect URI non è registrato nel client OAuth di Google Cloud | Vedi il riquadro ⚠️ dello step 3: aggiungi `https://PROJECT-ID.web.app/__/auth/handler` agli URI di reindirizzamento autorizzati del "Web client (auto created by Google Service)" |
| `npm run dev` → "Could not read package.json" | Comando lanciato dalla root del repo | Il frontend vive in `frontend/`: esegui `cd frontend` e poi `npm run dev` (invece `firebase deploy` va lanciato dalla root) |
| Popup di login bloccato | Blocco popup del browser | Consenti i popup per il sito |
| "Quota gratuita di Gemini esaurita" | Limite free tier (al minuto o al giorno) | Attendi 1 minuto e riprova, o cambia modello dal menù a tendina. Nessun costo |
| "Il modello selezionato non è disponibile" | Un modello in preview è stato ritirato | Scegli un altro modello. La lista è in `frontend/src/services/aiService.ts` (costante `AVAILABLE_MODELS`) ed è facile da aggiornare |
| "Firebase AI Logic non risulta attivo" | Step 6 saltato | Attiva AI Logic con **Gemini Developer API** |
| `firebase deploy` fallisce con errori di permessi | Login CLI scaduto | `firebase login --reauth` |
| "Not in a Firebase app directory" | Comando lanciato dalla cartella sbagliata | Esegui `firebase deploy` dalla **root** del repository |

---

## 🔐 Note di sicurezza (in breve)

- **Login**: solo account Google, tramite Firebase Authentication
- **Autorizzazione**: l'app mostra i contenuti solo se l'email è nella collection `allowlist`; le Security Rules (`firestore.rules`) permettono a ciascun utente di leggere **solo** il documento corrispondente alla propria email, e vietano qualsiasi scrittura dal client
- **API key Gemini**: non esiste nel codice; la crea e la custodisce Firebase AI Logic lato server
- **La config Firebase nel bundle JS**: è pubblica per design, non è un segreto
- (Opzionale, per i più pignoli) **Firebase App Check** può limitare le chiamate AI alla sola app ufficiale. Richiede piccole modifiche al codice: se ti interessa, chiedi e lo aggiungiamo. Anche senza, il rischio massimo resta "quota gratuita esaurita", mai un costo

---

## 🧹 Pulizia del vecchio progetto natalizio (opzionale)

CucinIAmo vive in un progetto Firebase nuovo. Quando non ti serve più il vecchio "Christmas Menu Generator", puoi eliminare il suo progetto Firebase: console Firebase → progetto vecchio → ⚙️ *Impostazioni progetto* → in fondo, **"Elimina progetto"**. Anche lì era tutto sul piano gratuito, quindi non c'è fretta: non sta costando nulla.

---

## 🏗️ Architettura in breve

**React (su Firebase Hosting) → Firebase AI Logic → Gemini API**, con login Google + allowlist Firestore davanti a tutto. Nessun server, nessun backend: i prompt e la normalizzazione delle risposte vivono in `frontend/src/services/aiService.ts`.
