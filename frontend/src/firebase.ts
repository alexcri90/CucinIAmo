// ═══════════════════════════════════════════════════════════════
// 🔥 FIREBASE - Inizializzazione servizi (Spark plan, 100% gratuito)
//
// Servizi usati:
// - Authentication (login Google)
// - Firestore (allowlist email autorizzate)
// - AI Logic con Gemini Developer API (generazione menù, free tier)
//
// La configurazione arriva da frontend/.env (vedi .env.example).
// NOTA: la config web di Firebase NON è un segreto (finisce comunque
// nel bundle JS); la sicurezza è garantita dalle Security Rules.
// ═══════════════════════════════════════════════════════════════

import { initializeApp } from 'firebase/app';
import { getAuth, type Auth } from 'firebase/auth';
import { getFirestore, type Firestore } from 'firebase/firestore';
import { getAI, GoogleAIBackend, type AI } from 'firebase/ai';
import { initializeAppCheck, ReCaptchaV3Provider } from 'firebase/app-check';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string | undefined,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string | undefined,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string | undefined,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET as string | undefined,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string | undefined,
  appId: import.meta.env.VITE_FIREBASE_APP_ID as string | undefined,
};

/** True se frontend/.env contiene la configurazione Firebase. */
export const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey && firebaseConfig.projectId && firebaseConfig.appId
);

interface FirebaseServices {
  auth: Auth;
  db: Firestore;
  ai: AI;
}

function createServices(): FirebaseServices | null {
  if (!isFirebaseConfigured) return null;

  const app = initializeApp(firebaseConfig);

  // App Check (opzionale): protegge la quota gratuita da chiamate esterne
  // che usano la config pubblica del progetto senza passare dalla nostra
  // app. Si attiva solo se VITE_RECAPTCHA_SITE_KEY è impostata (vedi
  // FIREBASE_DEPLOYMENT.md, sezione "App Check"). Senza questa variabile
  // l'app funziona comunque normalmente.
  const recaptchaSiteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY as string | undefined;
  if (recaptchaSiteKey) {
    if (import.meta.env.DEV) {
      // In sviluppo reCAPTCHA v3 non funziona su localhost: genera un
      // debug token in console da registrare in Firebase Console →
      // App Check → Apps → (⋮) → Manage debug tokens.
      (self as unknown as { FIREBASE_APPCHECK_DEBUG_TOKEN?: boolean }).FIREBASE_APPCHECK_DEBUG_TOKEN = true;
    }
    initializeAppCheck(app, {
      provider: new ReCaptchaV3Provider(recaptchaSiteKey),
      isTokenAutoRefreshEnabled: true,
    });
  }

  return {
    auth: getAuth(app),
    db: getFirestore(app),
    // GoogleAIBackend = Gemini Developer API: disponibile sul piano Spark
    // (gratuito). NON usare VertexAIBackend: richiede il piano Blaze.
    ai: getAI(app, { backend: new GoogleAIBackend() }),
  };
}

export const firebase = createServices();
