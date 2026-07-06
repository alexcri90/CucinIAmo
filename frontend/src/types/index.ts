// ═══════════════════════════════════════════════════════════════
// 🍳 CUCINIAMO - TypeScript Types
// Modello dati dell'app: input utente, menù generato, nutrizione.
// Questi tipi sono la FONTE DI VERITÀ per la struttura JSON che
// chiediamo a Gemini (vedi services/aiService.ts).
// ═══════════════════════════════════════════════════════════════

export type DietaryRestriction =
  | "vegetariano"
  | "vegano"
  | "senza_glutine"
  | "senza_lattosio";

export type DifficultyLevel = "facile" | "medio" | "avanzato";

export type BudgetLevel = "economico" | "medio" | "premium";

// Tipi di pasto generabili. "spuntino" raggruppa gli spuntini/merende
// della giornata in un unico blocco.
export type MealType = "colazione" | "pranzo" | "cena" | "spuntino";

export interface UserInput {
  num_people: number;
  /** Pasti da generare (almeno uno). Tutti e tre i principali = giornata intera. */
  meal_types: MealType[];
  /** Cucine di ispirazione: testo libero (es. "thailandese", "pugliese"). */
  cuisines: string[];
  preferred_ingredients: string[];
  avoided_ingredients: string[];
  dietary_restrictions: DietaryRestriction[];
  difficulty_level: DifficultyLevel;
  budget_level: BudgetLevel;
  /** Limite opzionale di kcal PER PERSONA sull'insieme dei pasti richiesti. */
  max_calories: number | null;
}

// Valori nutrizionali stimati PER PORZIONE (una persona)
export interface NutritionInfo {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface Ingredient {
  name: string;
  quantity: string; // es. "400g", "2 cucchiai", "q.b."
  category: string;
}

export interface Recipe {
  ingredients: Ingredient[];
  prep_time_minutes: number;
  cook_time_minutes: number;
  difficulty: DifficultyLevel;
  steps: string[];
  chef_notes?: string;
  can_prep_ahead?: boolean;
  prep_ahead_timing?: string | null;
}

// Un singolo piatto/voce di un pasto
export interface Dish {
  dish_id: string;
  name: string;
  cuisine: string;
  /** Ruolo nel pasto: es. "Antipasto", "Piatto unico", "Bevanda", "Dolce". */
  role: string;
  description: string;
  nutrition: NutritionInfo;
  recipe: Recipe;
}

export interface Meal {
  meal_type: MealType;
  dishes: Dish[];
}

// Lista spesa con categorie dinamiche (nomi in italiano)
export interface ShoppingList {
  categories: Record<string, Ingredient[]>;
}

// Piano di preparazione
export interface Timeline {
  /** Cose preparabili in anticipo (il giorno prima o più). */
  in_advance: string[];
  /** Programma del giorno: "HH:MM" → attività. */
  day_of: Record<string, string>;
}

// Output completo della generazione
export interface MenuOutput {
  menu_id: string;
  generated_at: string;
  input: UserInput;
  meals: Meal[];
  shopping_list: ShoppingList;
  timeline: Timeline;
}

// ═══════════════════════════════════════════════════════════════
// 📖 RICETTARIO (persistito su Firestore: users/{uid}/recipes/{id})
// ═══════════════════════════════════════════════════════════════

// Nota/commento datato su una preparazione della ricetta
export interface RecipeNote {
  date: string; // ISO
  text: string;
}

// Ricetta salvata dall'utente. `dish` è uno SNAPSHOT del piatto
// generato: l'utente può modificare la propria copia (dosi,
// ingredienti, passaggi) senza toccare nulla di condiviso.
export interface SavedRecipe {
  recipe_id: string;            // uuid client-side (= ID documento Firestore)
  saved_at: string;             // ISO
  updated_at: string;           // ISO
  dish: Dish;
  /** Da quale menù generato proviene (null se orfana). */
  source: { menu_id: string; meal_type: MealType } | null;
  /** Valutazione 1-5 stelle; null finché non è stata cucinata/valutata. */
  rating: number | null;
  /** Quante volte è stata cucinata. */
  cooked_count: number;
  notes: RecipeNote[];
  /** True se l'utente ha modificato il piatto rispetto all'originale. */
  is_customized: boolean;
}
