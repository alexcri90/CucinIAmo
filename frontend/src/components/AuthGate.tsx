// ═══════════════════════════════════════════════════════════════
// 🔐 AUTH GATE - Login Google + verifica allowlist
//
// Flusso:
// 1. L'utente accede con Google (Firebase Authentication)
// 2. Si verifica che la sua email sia nella collection Firestore
//    "allowlist" (documento con ID = email in minuscolo)
// 3. Solo se autorizzato, viene mostrata l'app
//
// L'allowlist si gestisce dalla console Firebase: il proprietario
// aggiunge/rimuove documenti nella collection "allowlist".
// ═══════════════════════════════════════════════════════════════

import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  type User,
} from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { firebase, isFirebaseConfigured } from '../firebase';

type AuthStatus = 'loading' | 'signed-out' | 'checking' | 'allowed' | 'denied';

interface AuthGateProps {
  children: (user: User) => ReactNode;
}

const AuthGate = ({ children }: AuthGateProps) => {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fb = firebase;
    if (!fb) return;

    const unsubscribe = onAuthStateChanged(fb.auth, async (currentUser) => {
      setUser(currentUser);

      if (!currentUser) {
        setStatus('signed-out');
        return;
      }

      if (!currentUser.email) {
        setStatus('denied');
        return;
      }

      setStatus('checking');
      try {
        const ref = doc(fb.db, 'allowlist', currentUser.email.toLowerCase());
        const snapshot = await getDoc(ref);
        setStatus(snapshot.exists() ? 'allowed' : 'denied');
      } catch {
        // Le security rules negano la lettura se l'email non corrisponde:
        // trattiamo ogni errore come "non autorizzato"
        setStatus('denied');
      }
    });

    return unsubscribe;
  }, []);

  const handleSignIn = async () => {
    if (!firebase) return;
    setError(null);
    try {
      await signInWithPopup(firebase.auth, new GoogleAuthProvider());
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (/popup.*closed/i.test(msg)) return; // utente ha chiuso il popup
      if (/popup.*blocked/i.test(msg)) {
        setError('Il browser ha bloccato il popup di login. Consenti i popup per questo sito e riprova.');
      } else if (/unauthorized.domain/i.test(msg)) {
        setError(
          'Questo dominio non è autorizzato per il login. Aggiungilo in Firebase Console → Authentication → Settings → Authorized domains.'
        );
      } else {
        setError(`Errore durante il login: ${msg}`);
      }
    }
  };

  const handleSignOut = () => {
    if (firebase) void signOut(firebase.auth);
  };

  // ── Configurazione mancante ────────────────────────────────────
  if (!isFirebaseConfigured) {
    return (
      <div className="auth-screen">
        <div className="auth-card">
          <div className="auth-logo-emoji">⚙️</div>
          <h1>Configurazione mancante</h1>
          <p>
            Il file <code>frontend/.env</code> con la configurazione Firebase non è presente.
          </p>
          <p className="auth-hint">
            Copia <code>frontend/.env.example</code> in <code>frontend/.env</code> e inserisci i
            valori della tua web app Firebase, poi riavvia il server di sviluppo.
            Trovi tutti i passaggi in <code>FIREBASE_DEPLOYMENT.md</code>.
          </p>
        </div>
      </div>
    );
  }

  // ── Caricamento / verifica allowlist ───────────────────────────
  if (status === 'loading' || status === 'checking') {
    return (
      <div className="auth-screen">
        <div className="auth-card">
          <img src="/logo.png" alt="CucinIAmo" className="auth-logo" />
          <span className="auth-spinner"></span>
          <p>{status === 'checking' ? 'Verifica autorizzazione…' : 'Caricamento…'}</p>
        </div>
      </div>
    );
  }

  // ── Login ──────────────────────────────────────────────────────
  if (status === 'signed-out') {
    return (
      <div className="auth-screen">
        <div className="auth-card">
          <img src="/logo.png" alt="CucinIAmo" className="auth-logo" />
          <h1>CucinIAmo</h1>
          <p>Genera il tuo menù personalizzato con l'AI, per ogni pasto e con le calorie sotto controllo.</p>
          <button className="google-signin-btn" onClick={handleSignIn}>
            <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
            </svg>
            <span>Accedi con Google</span>
          </button>
          {error && <p className="auth-error">❌ {error}</p>}
          <p className="auth-hint">🔒 L'accesso è riservato agli utenti autorizzati</p>
        </div>
      </div>
    );
  }

  // ── Utente autenticato ma non in allowlist ─────────────────────
  if (status === 'denied') {
    return (
      <div className="auth-screen">
        <div className="auth-card">
          <div className="auth-logo-emoji">🚫</div>
          <h1>Accesso non autorizzato</h1>
          <p>
            L'account <strong>{user?.email ?? 'sconosciuto'}</strong> non è tra gli utenti
            autorizzati.
          </p>
          <p className="auth-hint">
            Chiedi al proprietario del progetto di aggiungere la tua email alla lista degli
            utenti autorizzati.
          </p>
          <button className="modal-btn secondary" onClick={handleSignOut}>
            Esci e cambia account
          </button>
        </div>
      </div>
    );
  }

  // ── Autorizzato ────────────────────────────────────────────────
  return <>{children(user!)}</>;
};

export default AuthGate;
