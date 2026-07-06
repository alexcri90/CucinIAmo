// ═══════════════════════════════════════════════════════════════
// 📖 RECIPE SERVICE - Ricettario personale su Firestore
//
// CRUD sulla collection users/{uid}/recipes/{recipeId}.
// Le security rules garantiscono che ogni utente acceda solo ai
// propri documenti (e solo se è ancora in allowlist).
//
// Nota Firestore: i campi `undefined` non sono ammessi nei
// documenti (fanno fallire la scrittura). I piatti generati hanno
// campi opzionali (chef_notes?, can_prep_ahead?, ...), quindi
// prima di salvare si passa da `stripUndefined`.
// ═══════════════════════════════════════════════════════════════

import {
  collection,
  deleteDoc,
  doc,
  getDocs,
  limit,
  orderBy,
  query,
  setDoc,
  startAfter,
  updateDoc,
  type DocumentData,
  type QueryDocumentSnapshot,
} from 'firebase/firestore';
import { firebase } from '../firebase';
import type { Dish, MealType, SavedRecipe } from '../types';

// Rimuove ricorsivamente i campi undefined (Firestore li rifiuta)
function stripUndefined<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function recipesCollection(uid: string) {
  if (!firebase) throw new Error('Firebase non configurato');
  return collection(firebase.db, 'users', uid, 'recipes');
}

function recipeDoc(uid: string, recipeId: string) {
  if (!firebase) throw new Error('Firebase non configurato');
  return doc(firebase.db, 'users', uid, 'recipes', recipeId);
}

/** Salva un piatto generato nel ricettario. Ritorna la SavedRecipe creata. */
export async function saveRecipe(
  uid: string,
  dish: Dish,
  source: { menu_id: string; meal_type: MealType } | null
): Promise<SavedRecipe> {
  const now = new Date().toISOString();
  const recipe: SavedRecipe = {
    recipe_id: crypto.randomUUID(),
    saved_at: now,
    updated_at: now,
    dish: stripUndefined(dish),
    source,
    rating: null,
    cooked_count: 0,
    notes: [],
    is_customized: false,
  };
  await setDoc(recipeDoc(uid, recipe.recipe_id), recipe);
  return recipe;
}

/** Cursore opaco per la paginazione del ricettario. */
export type RecipeCursor = QueryDocumentSnapshot<DocumentData>;

export interface RecipePage {
  recipes: SavedRecipe[];
  /** Cursore per la pagina successiva; null se non ci sono altre ricette. */
  cursor: RecipeCursor | null;
}

/**
 * Una pagina di ricette, dalla più recente. La paginazione tiene
 * veloci sia il caricamento sia i costi di lettura quando il
 * ricettario cresce (decine/centinaia di ricette).
 */
export async function listRecipesPage(
  uid: string,
  pageSize: number,
  after: RecipeCursor | null = null
): Promise<RecipePage> {
  const q = after
    ? query(recipesCollection(uid), orderBy('saved_at', 'desc'), startAfter(after), limit(pageSize))
    : query(recipesCollection(uid), orderBy('saved_at', 'desc'), limit(pageSize));
  const snapshot = await getDocs(q);
  return {
    recipes: snapshot.docs.map((d) => d.data() as SavedRecipe),
    cursor: snapshot.docs.length === pageSize ? snapshot.docs[snapshot.docs.length - 1] : null,
  };
}

/**
 * Aggiorna una ricetta (rating, note, dish modificato, ...).
 * `updated_at` viene impostato automaticamente.
 */
export async function updateRecipe(
  uid: string,
  recipeId: string,
  patch: Partial<Omit<SavedRecipe, 'recipe_id' | 'saved_at'>>
): Promise<void> {
  await updateDoc(recipeDoc(uid, recipeId), {
    ...stripUndefined(patch),
    updated_at: new Date().toISOString(),
  });
}

/** Elimina definitivamente una ricetta dal ricettario. */
export async function deleteRecipe(uid: string, recipeId: string): Promise<void> {
  await deleteDoc(recipeDoc(uid, recipeId));
}
