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

// Portate selezionabili per pranzo e cena (colazione e spuntini
// hanno già una struttura leggera decisa dal modello).
export type CourseType = "antipasto" | "primo" | "secondo" | "contorno" | "dolce";

/** Portate richieste per pasto. Pasto assente (o lista vuota) = decide lo chef. */
export type MealCourses = Partial<Record<MealType, CourseType[]>>;

export interface UserInput {
  num_people: number;
  /** Pasti da generare (almeno uno). Tutti e tre i principali = giornata intera. */
  meal_types: MealType[];
  /** Composizione di pranzo/cena: portate esatte da generare; pasto assente = decide lo chef. */
  courses: MealCourses;
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

// ═══════════════════════════════════════════════════════════════
// 📔 DIARIO ALIMENTARE (Firestore: users/{uid}/diary/{YYYY-MM-DD})
// Un documento per giorno: una lettura carica l'intera giornata.
// ═══════════════════════════════════════════════════════════════

export type DiaryEntrySource = "manuale" | "ricettario" | "foto";

export interface DiaryEntry {
  entry_id: string;              // uuid client-side
  meal_type: MealType;
  description: string;           // "Pasta al pesto", "2 fette di torta"...
  /** Kcal/macro per la porzione consumata; null se non indicate. */
  nutrition: NutritionInfo | null;
  /** Link a una SavedRecipe se si è cucinata una ricetta del ricettario. */
  recipe_id: string | null;
  source: DiaryEntrySource;
  logged_at: string;             // ISO
}

export interface DiaryDay {
  date: string;                  // "YYYY-MM-DD" (= ID documento)
  entries: DiaryEntry[];
}

// Preferenze utente (Firestore: users/{uid}/settings/prefs)
export interface UserPrefs {
  /** Budget kcal giornaliero opzionale per il confronto nel diario. */
  daily_kcal_budget: number | null;
}

// Stima nutrizionale prodotta dall'AI (da testo o da foto)
export interface NutritionEstimate {
  description: string;           // descrizione normalizzata del cibo
  assumed_portion: string;       // porzione assunta per la stima
  nutrition: NutritionInfo;
  confidence: "alta" | "media" | "bassa";
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
