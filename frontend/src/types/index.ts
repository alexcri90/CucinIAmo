// ═══════════════════════════════════════════════════════════════
// 🎄 CHRISTMAS MENU GENERATOR - TypeScript Types
// Allineati alla struttura reale del backend
// ═══════════════════════════════════════════════════════════════

// Allineato al backend: input_models.py
export type DietaryRestriction = 
  | "vegetariano" 
  | "vegano" 
  | "senza_glutine" 
  | "senza_lattosio";

export type DifficultyLevel = "facile" | "medio" | "avanzato";

export type Cuisine = 
  | "italiana" 
  | "spagnola" 
  | "francese" 
  | "tedesca" 
  | "inglese" 
  | "polacca" 
  | "greca" 
  | "americana" 
  | "scandinava";
export type BudgetLevel = "economico" | "medio" | "premium";
export type CourseType = "antipasti" | "primo" | "secondo" | "contorno" | "dessert";

export interface UserInput {
  num_guests: number;
  cuisines: string[];
  preferred_ingredients: string[];
  avoided_ingredients: string[];
  dietary_restrictions: DietaryRestriction[];
  difficulty_level: DifficultyLevel;
  budget_level: BudgetLevel;
  other_restrictions?: string | null;
}

// Ingrediente come arriva dal backend
export interface Ingredient {
  name: string;
  quantity: string;  // Backend manda string (es. "400g", "q.b.")
  category: string;
}

// Recipe come arriva dal backend
export interface Recipe {
  ingredients: Ingredient[];
  prep_time_minutes: number;
  cook_time_minutes: number;
  difficulty: DifficultyLevel;
  steps: string[];  // Backend manda "steps", non "instructions"
  chef_notes?: string;
  can_prep_ahead?: boolean;
  prep_ahead_timing?: string | null;
}

// Course come arriva dal backend
export interface Course {
  course_id: string;
  name: string;
  cuisine: string;
  description: string;
  recipe: Recipe;
}

// Struttura courses dal backend
export interface MenuCourses {
  antipasti: Course[];
  primo: Course[];
  secondo: Course[];
  contorno: Course[];
  dessert: Course[];
}

// Shopping list con categorie dinamiche (nomi in italiano)
export interface ShoppingList {
  categories: Record<string, Ingredient[]>;
}

// Timeline dal backend
export interface Timeline {
  two_days_before: string[];
  one_day_before: string[];
  day_of: Record<string, string>;
}

// Output completo del menu
export interface MenuOutput {
  menu_id: string;
  generated_at: string;
  input: UserInput;
  courses: MenuCourses;
  shopping_list: ShoppingList;
  timeline: Timeline;
}

// Request per rigenerazione portata
export interface RegenerateCourseRequest {
  menu_id: string;
  course_type: CourseType;
  course_index: number;
  user_feedback?: string;
}

// Response rigenerazione portata
export interface RegenerateCourseResponse {
  course_type: string;
  new_course: Course;
  updated_shopping_list: ShoppingList;
  updated_timeline: Timeline;
}