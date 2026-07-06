// ═══════════════════════════════════════════════════════════════
// 📔 DIARY SERVICE - Diario alimentare su Firestore
//
// Struttura: users/{uid}/diary/{YYYY-MM-DD} → DiaryDay
// Un documento per giorno (array di entry): una sola lettura carica
// l'intera giornata, e la vista mensile costa ≤31 letture.
//
// Preferenze: users/{uid}/settings/prefs → UserPrefs
// ═══════════════════════════════════════════════════════════════

import {
  collection,
  deleteDoc,
  doc,
  documentId,
  getDoc,
  getDocs,
  orderBy,
  query,
  setDoc,
  where,
} from 'firebase/firestore';
import { firebase } from '../firebase';
import type { DiaryDay, DiaryEntry, UserPrefs } from '../types';

// Rimuove ricorsivamente i campi undefined (Firestore li rifiuta)
function stripUndefined<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function diaryDoc(uid: string, date: string) {
  if (!firebase) throw new Error('Firebase non configurato');
  return doc(firebase.db, 'users', uid, 'diary', date);
}

/** Data locale in formato "YYYY-MM-DD" (niente UTC: conta il giorno dell'utente). */
export function toISODate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** Il giorno del diario, o null se non esiste ancora. */
export async function getDiaryDay(uid: string, date: string): Promise<DiaryDay | null> {
  const snapshot = await getDoc(diaryDoc(uid, date));
  return snapshot.exists() ? (snapshot.data() as DiaryDay) : null;
}

/** Aggiunge una entry al giorno indicato. Ritorna il giorno aggiornato. */
export async function addDiaryEntry(uid: string, date: string, entry: DiaryEntry): Promise<DiaryDay> {
  const existing = await getDiaryDay(uid, date);
  const day: DiaryDay = {
    date,
    entries: [...(existing?.entries ?? []), stripUndefined(entry)],
  };
  await setDoc(diaryDoc(uid, date), day);
  return day;
}

/** Sostituisce una entry esistente (match per entry_id). Ritorna il giorno aggiornato. */
export async function updateDiaryEntry(uid: string, date: string, entry: DiaryEntry): Promise<DiaryDay> {
  const existing = await getDiaryDay(uid, date);
  const day: DiaryDay = {
    date,
    entries: (existing?.entries ?? []).map((e) =>
      e.entry_id === entry.entry_id ? stripUndefined(entry) : e
    ),
  };
  await setDoc(diaryDoc(uid, date), day);
  return day;
}

/**
 * Elimina una entry. Se il giorno resta vuoto, elimina il documento.
 * Ritorna il giorno aggiornato (o null se il documento è stato rimosso).
 */
export async function deleteDiaryEntry(
  uid: string,
  date: string,
  entryId: string
): Promise<DiaryDay | null> {
  const existing = await getDiaryDay(uid, date);
  const entries = (existing?.entries ?? []).filter((e) => e.entry_id !== entryId);
  if (entries.length === 0) {
    await deleteDoc(diaryDoc(uid, date));
    return null;
  }
  const day: DiaryDay = { date, entries };
  await setDoc(diaryDoc(uid, date), day);
  return day;
}

/**
 * Tutti i giorni registrati di un mese ("YYYY-MM"), in ordine di data.
 * Gli ID documento sono date ISO, quindi basta un range sul documentId.
 */
export async function getDiaryMonth(uid: string, month: string): Promise<DiaryDay[]> {
  if (!firebase) throw new Error('Firebase non configurato');
  const diary = collection(firebase.db, 'users', uid, 'diary');
  const q = query(
    diary,
    where(documentId(), '>=', `${month}-01`),
    where(documentId(), '<=', `${month}-31`),
    orderBy(documentId())
  );
  const snapshot = await getDocs(q);
  return snapshot.docs.map((d) => d.data() as DiaryDay);
}

// ── Preferenze utente ────────────────────────────────────────────

function prefsDoc(uid: string) {
  if (!firebase) throw new Error('Firebase non configurato');
  return doc(firebase.db, 'users', uid, 'settings', 'prefs');
}

export async function getPrefs(uid: string): Promise<UserPrefs> {
  const snapshot = await getDoc(prefsDoc(uid));
  return snapshot.exists() ? (snapshot.data() as UserPrefs) : { daily_kcal_budget: null };
}

export async function savePrefs(uid: string, prefs: UserPrefs): Promise<void> {
  await setDoc(prefsDoc(uid), stripUndefined(prefs));
}
