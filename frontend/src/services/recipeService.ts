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
  orderBy,
  query,
  setDoc,
  updateDoc,
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

/** Tutte le ricette salvate, dalla più recente. */
export async function listRecipes(uid: string): Promise<SavedRecipe[]> {
  const q = query(recipesCollection(uid), orderBy('saved_at', 'desc'));
  const snapshot = await getDocs(q);
  return snapshot.docs.map((d) => d.data() as SavedRecipe);
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
