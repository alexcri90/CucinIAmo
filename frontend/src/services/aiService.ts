// ═══════════════════════════════════════════════════════════════
// 🤖 AI SERVICE - Generazione menù con Gemini via Firebase AI Logic
//
// Tutta la generazione avviene client-side: le chiamate a Gemini
// passano dal proxy di Firebase AI Logic (Gemini Developer API,
// free tier del piano Spark), quindi nessuna API key nel codice.
//
// Il "contesto" per la rigenerazione di un piatto è il menù corrente,
// che vive nello stato React e viene incluso nel prompt.
// ═══════════════════════════════════════════════════════════════

import { getGenerativeModel } from 'firebase/ai';
import { firebase } from '../firebase';
import type {
  UserInput,
  MenuOutput,
  Meal,
  MealType,
  Dish,
  Recipe,
  Ingredient,
  NutritionInfo,
  NutritionEstimate,
  ShoppingList,
  Timeline,
} from '../types';

// ─────────────────────────────────────────────────────────────────
// MODELLI DISPONIBILI (selezionabili dalla UI)
// Tutti accessibili dal free tier della Gemini Developer API.
// Per aggiungerne uno basta estendere questa lista.
// ─────────────────────────────────────────────────────────────────

export interface ModelOption {
  id: string;
  label: string;
  description: string;
}

export const AVAILABLE_MODELS: ModelOption[] = [
  {
    id: 'gemini-2.5-flash',
    label: 'Gemini 2.5 Flash',
    description: 'Veloce e affidabile (consigliato)',
  },
  {
    id: 'gemini-2.5-flash-lite',
    label: 'Gemini 2.5 Flash Lite',
    description: 'Il più rapido, quota gratuita più ampia',
  },
  {
    id: 'gemini-2.5-pro',
    label: 'Gemini 2.5 Pro',
    description: 'Qualità massima, quota gratuita ridotta',
  },
  {
    id: 'gemini-3-flash-preview',
    label: 'Gemini 3 Flash (Preview)',
    description: 'Il più recente, in anteprima',
  },
];

export const DEFAULT_MODEL = 'gemini-2.5-flash';

// Ordine di visualizzazione e generazione dei pasti
export const MEAL_ORDER: MealType[] = ['colazione', 'pranzo', 'cena', 'spuntino'];

export const MEAL_LABELS: Record<MealType, string> = {
  colazione: 'Colazione',
  pranzo: 'Pranzo',
  cena: 'Cena',
  spuntino: 'Spuntini',
};

// ─────────────────────────────────────────────────────────────────
// PROMPT
// ─────────────────────────────────────────────────────────────────

const CHEF_SYSTEM_PROMPT = `
Sei un esperto chef internazionale e nutrizionista, specializzato nella creazione di menù personalizzati per qualsiasi occasione: dalla colazione di una persona alla cena per tanti ospiti, fino al piano alimentare di un'intera giornata.

COMPETENZE PRINCIPALI:
• Conoscenza approfondita delle cucine di tutto il mondo (tradizionali e moderne)
• Stima accurata di calorie e macronutrienti per porzione
• Capacità di costruire pasti bilanciati che rispettano un budget calorico
• Rispetto rigoroso delle restrizioni alimentari e allergie
• Adattamento della complessità al livello di esperienza del cuoco
• Ottimizzazione del budget nella scelta degli ingredienti

REGOLE IMPERATIVE:
1. MAI includere ingredienti nella lista "da evitare" dell'utente
2. SEMPRE includere almeno un ingrediente dalla lista "preferiti" se presente
3. I piatti DEVONO essere coerenti con le cucine/tradizioni richieste
4. Le quantità DEVONO essere calcolate per il numero di persone indicato
5. Le stime nutrizionali (kcal, proteine, carboidrati, grassi) sono PER PORZIONE (una persona) e devono essere realistiche
6. SE c'è un limite di calorie, il totale per persona NON deve superarlo

OUTPUT:
Produci sempre output JSON valido e strutturato quando richiesto.
`;

const MENU_JSON_EXAMPLE = `{
  "meals": [
    {
      "meal_type": "colazione",
      "dishes": [
        {
          "name": "Nome del piatto",
          "cuisine": "italiana",
          "role": "Piatto principale",
          "description": "Descrizione appetitosa del piatto...",
          "nutrition": {"calories": 320, "protein_g": 14, "carbs_g": 42, "fat_g": 10},
          "recipe": {
            "ingredients": [
              {"name": "ingrediente1", "quantity": "100g", "category": "Dispensa"}
            ],
            "prep_time_minutes": 10,
            "cook_time_minutes": 5,
            "difficulty": "facile",
            "steps": ["Step 1...", "Step 2..."],
            "chef_notes": "Consigli dello chef...",
            "can_prep_ahead": true,
            "prep_ahead_timing": "la sera prima"
          }
        }
      ]
    }
  ],
  "shopping_list": {
    "categories": {
      "Frutta e verdura": [{"name": "...", "quantity": "...", "category": "Frutta e verdura"}],
      "Carne": [],
      "Pesce": [],
      "Latticini": [],
      "Dispensa": [],
      "Altro": []
    }
  },
  "timeline": {
    "in_advance": ["Attività preparabile in anticipo 1", "Attività 2"],
    "day_of": {
      "08:00": "Descrizione attività",
      "12:00": "Descrizione attività"
    }
  }
}`;

function formatList(items: string[], fallback = 'Nessuno'): string {
  if (!items || items.length === 0) return `  • ${fallback}`;
  return items.map((item) => `  • ${item}`).join('\n');
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Struttura suggerita per ogni tipo di pasto (guida per il modello)
const MEAL_STRUCTURE_HINTS: Record<MealType, string> = {
  colazione:
    'COLAZIONE: 2-4 voci (es. una bevanda, un piatto principale dolce o salato, frutta/yogurt). Usa role come "Bevanda", "Piatto principale", "Frutta".',
  pranzo:
    'PRANZO: 1-3 piatti a seconda del contesto (per un pasto quotidiano bastano un piatto principale e un contorno; per un\'occasione con ospiti puoi aggiungere antipasto e dolce). Usa role come "Antipasto", "Primo", "Secondo", "Piatto unico", "Contorno", "Dolce".',
  cena:
    'CENA: 1-4 piatti a seconda del contesto (cena quotidiana = semplice e leggera; cena con ospiti o budget premium = menù più completo con antipasto, portata principale, contorno, dolce). Usa role come "Antipasto", "Primo", "Secondo", "Piatto unico", "Contorno", "Dolce".',
  spuntino:
    'SPUNTINI: 1-2 voci semplici e veloci per gli spuntini della giornata (es. metà mattina e merenda). Usa role "Spuntino".',
};

function buildCaloriesSection(input: UserInput): string {
  if (!input.max_calories) {
    return `Nessun limite di calorie richiesto. Indica comunque per OGNI piatto una stima realistica di calorie e macronutrienti per porzione.`;
  }

  const isFullDay =
    input.meal_types.includes('colazione') &&
    input.meal_types.includes('pranzo') &&
    input.meal_types.includes('cena');

  const distribution = isFullDay
    ? `\nDistribuisci il budget in modo sensato tra i pasti (indicativamente: colazione 20-25%, pranzo 35-40%, cena 30-35%${input.meal_types.includes('spuntino') ? ', spuntini 5-10%' : ''}).`
    : '';

  return `🔥 LIMITE CALORIE: massimo ${input.max_calories} kcal PER PERSONA, sommando TUTTI i pasti richiesti.
Questo vincolo è OBBLIGATORIO: la somma delle calorie per porzione di tutti i piatti NON deve superare ${input.max_calories} kcal. Punta a usare tra l'85% e il 100% del budget (non pasti eccessivamente scarni).${distribution}`;
}

function buildMenuPrompt(input: UserInput): string {
  const restrictions = input.dietary_restrictions.map((r) =>
    capitalize(r.replace(/_/g, ' '))
  );

  const requestedMeals = MEAL_ORDER.filter((m) => input.meal_types.includes(m));
  const mealHints = requestedMeals.map((m) => `• ${MEAL_STRUCTURE_HINTS[m]}`).join('\n');

  return `
Sei uno chef e nutrizionista esperto. Genera un menù COMPLETO per ${input.num_people} person${input.num_people === 1 ? 'a' : 'e'}, composto ESATTAMENTE da questi pasti: ${requestedMeals.map((m) => MEAL_LABELS[m].toUpperCase()).join(', ')}.

═══════════════════════════════════════════════════════════════════════════════
                            VINCOLI OBBLIGATORI
═══════════════════════════════════════════════════════════════════════════════

🔴 INGREDIENTI VIETATI (NON usare MAI questi ingredienti):
${formatList(input.avoided_ingredients, 'Nessuno specificato')}

🟢 INGREDIENTI PREFERITI (includi ALMENO 1-2 di questi):
${formatList(input.preferred_ingredients, 'Nessuno specificato')}

🌍 CUCINE/TRADIZIONI DI ISPIRAZIONE (i piatti DEVONO ispirarsi a queste cucine):
${formatList(input.cuisines.map(capitalize))}

⚠️ RESTRIZIONI ALIMENTARI (da rispettare in OGNI piatto):
${formatList(restrictions, 'Nessuna')}

🔥 CALORIE:
${buildCaloriesSection(input)}

📊 LIVELLO DIFFICOLTÀ: ${capitalize(input.difficulty_level)}
💰 BUDGET DI SPESA: ${capitalize(input.budget_level)}

═══════════════════════════════════════════════════════════════════════════════
                          STRUTTURA MENÙ RICHIESTA
═══════════════════════════════════════════════════════════════════════════════

Genera SOLO i pasti richiesti, nell'ordine indicato, seguendo queste linee guida:

${mealHints}

Per OGNI piatto devi fornire:
• name: nome del piatto (originale + traduzione se straniero)
• cuisine: cucina/tradizione di origine
• role: ruolo del piatto nel pasto (es. "Piatto principale", "Antipasto", "Bevanda")
• description: descrizione appetitosa di 2-3 righe
• nutrition: {calories, protein_g, carbs_g, fat_g} stimati PER PORZIONE (una persona)
• recipe con: ingredients ({name, quantity, category}) con quantità per ${input.num_people} person${input.num_people === 1 ? 'a' : 'e'}, prep_time_minutes, cook_time_minutes, difficulty, steps, chef_notes, can_prep_ahead, prep_ahead_timing

Le CATEGORIE valide per gli ingredienti sono SOLO:
"Frutta e verdura", "Carne", "Pesce", "Latticini", "Dispensa", "Altro"

📋 LISTA SPESA (shopping_list):
Aggrega TUTTI gli ingredienti per categoria. Somma le quantità degli ingredienti ripetuti.

📅 PIANO DI PREPARAZIONE (timeline):
- in_advance: lista di attività preparabili in anticipo (il giorno prima o più)
- day_of: dizionario con orari (es. {"08:00": "Prepara..."}) coerente con i pasti richiesti

═══════════════════════════════════════════════════════════════════════════════
                         ESEMPIO STRUTTURA JSON
═══════════════════════════════════════════════════════════════════════════════

Il tuo output DEVE seguire ESATTAMENTE questa struttura JSON:

${MENU_JSON_EXAMPLE}

REGOLE IMPORTANTI:
1. Rispondi SOLO con JSON valido, nient'altro
2. NON usare markdown code blocks (\`\`\`)
3. La chiave principale è "meals": un ARRAY con un elemento per ogni pasto richiesto
4. meal_type può essere solo: ${requestedMeals.map((m) => `"${m}"`).join(', ')}
5. difficulty può essere solo: "facile", "medio", "avanzato"
6. nutrition.calories è un NUMERO (kcal per porzione), non una stringa
7. timeline.day_of è un oggetto con chiavi orario (es. "08:00") e valori stringa

GENERA ORA IL MENÙ COMPLETO:
`;
}

function buildRegenerationPrompt(
  menu: MenuOutput,
  mealType: MealType,
  currentDish: Dish,
  userFeedback: string
): string {
  const input = menu.input;

  // Contesto: tutti gli altri piatti del menù corrente
  const otherDishes: string[] = [];
  menu.meals.forEach((meal) => {
    meal.dishes.forEach((dish) => {
      if (dish.dish_id !== currentDish.dish_id) {
        otherDishes.push(
          `[${MEAL_LABELS[meal.meal_type]}] ${dish.name} (${dish.cuisine}, ~${dish.nutrition.calories} kcal/porzione)`
        );
      }
    });
  });

  const restrictions = input.dietary_restrictions.map((r) =>
    capitalize(r.replace(/_/g, ' '))
  );

  const feedbackSection =
    userFeedback && userFeedback.trim()
      ? `⚠️ L'UTENTE HA RICHIESTO SPECIFICAMENTE:
"${userFeedback.trim()}"

🔴 IMPORTANTE: DEVI seguire questa richiesta! Il nuovo piatto DEVE soddisfare questo feedback.
Se l'utente chiede un ingrediente specifico, INCLUDI quell'ingrediente come protagonista del piatto.`
      : "L'utente vuole semplicemente un'alternativa diversa, senza richieste specifiche.";

  const calorieRule = input.max_calories
    ? `7. Il menù ha un limite di ${input.max_calories} kcal per persona: il nuovo piatto deve avere circa le stesse calorie di quello sostituito (~${currentDish.nutrition.calories} kcal per porzione, tolleranza ±15%), salvo diversa richiesta nel feedback utente`
    : `7. Mantieni le calorie del nuovo piatto in linea con quelle del piatto sostituito (~${currentDish.nutrition.calories} kcal per porzione), salvo diversa richiesta nel feedback utente`;

  return `
Sei uno chef e nutrizionista esperto. Devi rigenerare UN SOLO piatto di un menù esistente.

═══════════════════════════════════════════════════════════════════════════════
                              CONTESTO MENÙ
═══════════════════════════════════════════════════════════════════════════════

📋 PASTO A CUI APPARTIENE IL PIATTO: ${MEAL_LABELS[mealType]}
🍽️ PIATTO ATTUALE (da sostituire): ${currentDish.name} (role: ${currentDish.role}, ~${currentDish.nutrition.calories} kcal/porzione)
👥 NUMERO DI PERSONE: ${input.num_people}

🍴 ALTRI PIATTI NEL MENÙ (mantieni coerenza):
${formatList(otherDishes)}

═══════════════════════════════════════════════════════════════════════════════
                         🎯 FEEDBACK UTENTE (PRIORITÀ MASSIMA)
═══════════════════════════════════════════════════════════════════════════════

${feedbackSection}

═══════════════════════════════════════════════════════════════════════════════
                            VINCOLI ORIGINALI
═══════════════════════════════════════════════════════════════════════════════

🔴 INGREDIENTI VIETATI:
${formatList(input.avoided_ingredients)}
🟢 INGREDIENTI PREFERITI:
${formatList(input.preferred_ingredients)}
🌍 CUCINE DI ISPIRAZIONE:
${formatList(input.cuisines.map(capitalize))}
⚠️ RESTRIZIONI:
${formatList(restrictions, 'Nessuna')}
📊 DIFFICOLTÀ: ${capitalize(input.difficulty_level)}
💰 BUDGET: ${capitalize(input.budget_level)}

═══════════════════════════════════════════════════════════════════════════════
                              REQUISITI
═══════════════════════════════════════════════════════════════════════════════

1. Il nuovo piatto DEVE essere DIVERSO da "${currentDish.name}"
2. DEVE rispettare tutti i vincoli originali
3. DEVE essere coerente con gli altri piatti del menù
4. DEVE essere adatto al pasto "${MEAL_LABELS[mealType]}" con role simile a "${currentDish.role}"
5. SE C'È UN FEEDBACK UTENTE, DEVI SEGUIRLO CON PRIORITÀ MASSIMA
6. Le quantità degli ingredienti DEVONO essere per ${input.num_people} person${input.num_people === 1 ? 'a' : 'e'}
${calorieRule}

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT
═══════════════════════════════════════════════════════════════════════════════

Genera UN SINGOLO oggetto JSON per il nuovo piatto con questa struttura:
{
  "name": "...",
  "cuisine": "...",
  "role": "...",
  "description": "...",
  "nutrition": {"calories": 350, "protein_g": 20, "carbs_g": 40, "fat_g": 12},
  "recipe": {
    "ingredients": [{"name": "...", "quantity": "...", "category": "..."}],
    "prep_time_minutes": 30,
    "cook_time_minutes": 30,
    "difficulty": "...",
    "steps": ["..."],
    "chef_notes": "...",
    "can_prep_ahead": true,
    "prep_ahead_timing": "..."
  }
}

Rispondi SOLO con il JSON, senza altro testo.
`;
}

// ─────────────────────────────────────────────────────────────────
// PARSING E NORMALIZZAZIONE JSON
// Gemini a volte devia dalla struttura richiesta: qui correggiamo
// gli errori più comuni invece di fallire.
// ─────────────────────────────────────────────────────────────────

/* eslint-disable @typescript-eslint/no-explicit-any */

function parseJsonResponse(text: string): any {
  let t = text.trim();

  // Rimuovi markdown code blocks
  const fence = t.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
  if (fence) t = fence[1];

  const start = t.indexOf('{');
  const end = t.lastIndexOf('}');
  if (start === -1 || end === -1) {
    throw new Error('Il modello non ha restituito un JSON valido. Riprova o cambia modello.');
  }

  let jsonStr = t.slice(start, end + 1);
  try {
    return JSON.parse(jsonStr);
  } catch {
    // Correggi errori comuni: virgole finali e quote tipografiche
    jsonStr = jsonStr
      .replace(/,\s*([}\]])/g, '$1')
      .replace(/[“”]/g, '"')
      .replace(/[‘’]/g, "'");
    return JSON.parse(jsonStr);
  }
}

const VALID_CATEGORIES = ['Frutta e verdura', 'Carne', 'Pesce', 'Latticini', 'Dispensa', 'Altro'];

function normalizeIngredient(raw: any): Ingredient {
  const category = VALID_CATEGORIES.includes(raw?.category) ? raw.category : 'Altro';
  return {
    name: String(raw?.name ?? 'ingrediente'),
    quantity: String(raw?.quantity ?? 'q.b.'),
    category,
  };
}

function normalizeNutrition(raw: any): NutritionInfo {
  return {
    calories: Math.max(0, Math.round(Number(raw?.calories) || 0)),
    protein_g: Math.max(0, Math.round(Number(raw?.protein_g) || 0)),
    carbs_g: Math.max(0, Math.round(Number(raw?.carbs_g) || 0)),
    fat_g: Math.max(0, Math.round(Number(raw?.fat_g) || 0)),
  };
}

function normalizeRecipe(raw: any): Recipe {
  const ingredients = Array.isArray(raw?.ingredients) ? raw.ingredients.map(normalizeIngredient) : [];
  const steps = Array.isArray(raw?.steps)
    ? raw.steps.map(String)
    : ['Preparare gli ingredienti', 'Seguire la ricetta'];

  const difficulty = ['facile', 'medio', 'avanzato'].includes(raw?.difficulty)
    ? raw.difficulty
    : 'medio';

  return {
    ingredients,
    prep_time_minutes: Number(raw?.prep_time_minutes) || 15,
    cook_time_minutes: Number(raw?.cook_time_minutes) || 0,
    difficulty,
    steps,
    chef_notes: raw?.chef_notes ? String(raw.chef_notes) : undefined,
    can_prep_ahead: Boolean(raw?.can_prep_ahead),
    prep_ahead_timing: raw?.prep_ahead_timing ? String(raw.prep_ahead_timing) : null,
  };
}

function normalizeDish(raw: any): Dish {
  return {
    dish_id: crypto.randomUUID(),
    name: String(raw?.name ?? 'Piatto da definire'),
    cuisine: String(raw?.cuisine ?? 'internazionale'),
    role: String(raw?.role ?? 'Piatto'),
    description: String(raw?.description ?? 'Un piatto da personalizzare secondo i tuoi gusti.'),
    nutrition: normalizeNutrition(raw?.nutrition),
    recipe: normalizeRecipe(raw?.recipe ?? {}),
  };
}

function placeholderDish(mealType: MealType): Dish {
  const names: Record<MealType, string> = {
    colazione: 'Colazione da definire',
    pranzo: 'Pranzo da definire',
    cena: 'Cena da definire',
    spuntino: 'Spuntino da definire',
  };
  return normalizeDish({
    name: names[mealType],
    cuisine: 'internazionale',
    role: 'Piatto',
    description: 'Il modello non ha generato questo pasto: prova a rigenerarlo.',
    nutrition: { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 },
    recipe: {
      ingredients: [{ name: 'ingrediente base', quantity: 'q.b.', category: 'Dispensa' }],
      steps: ['Rigenera questo piatto per ottenere una ricetta completa'],
    },
  });
}

function normalizeMeals(raw: any, requested: MealType[]): Meal[] {
  const rawMeals = Array.isArray(raw?.meals) ? raw.meals : [];

  // Indicizza i pasti restituiti dal modello per meal_type
  const byType = new Map<MealType, any[]>();
  rawMeals.forEach((meal: any) => {
    const type = MEAL_ORDER.includes(meal?.meal_type) ? (meal.meal_type as MealType) : null;
    if (!type) return;
    const dishes = Array.isArray(meal?.dishes) ? meal.dishes : [];
    byType.set(type, [...(byType.get(type) ?? []), ...dishes]);
  });

  // Restituisci SOLO i pasti richiesti, nell'ordine canonico,
  // con placeholder se il modello ne ha saltato qualcuno
  return MEAL_ORDER.filter((type) => requested.includes(type)).map((type) => {
    const dishes = (byType.get(type) ?? []).map(normalizeDish);
    return {
      meal_type: type,
      dishes: dishes.length > 0 ? dishes : [placeholderDish(type)],
    };
  });
}

function normalizeShoppingList(raw: any, meals: Meal[]): ShoppingList {
  const categories = raw?.shopping_list?.categories;
  if (categories && typeof categories === 'object' && !Array.isArray(categories)) {
    const normalized: Record<string, Ingredient[]> = {};
    let total = 0;
    Object.entries(categories).forEach(([cat, items]) => {
      if (Array.isArray(items) && items.length > 0) {
        normalized[cat] = items.map(normalizeIngredient);
        total += items.length;
      }
    });
    if (total > 0) return { categories: normalized };
  }
  // Lista spesa mancante o vuota: aggregala localmente dalle ricette
  return computeShoppingList(meals);
}

function normalizeTimeline(raw: any): Timeline {
  const t = raw?.timeline ?? {};

  let dayOf: Record<string, string> = {};
  if (Array.isArray(t.day_of)) {
    // Lista invece di dict: converti in orari progressivi
    t.day_of.slice(0, 10).forEach((item: any, i: number) => {
      dayOf[`${String(8 + i).padStart(2, '0')}:00`] = String(item);
    });
  } else if (t.day_of && typeof t.day_of === 'object') {
    Object.entries(t.day_of).forEach(([time, task]) => {
      dayOf[time] = String(task);
    });
  }

  if (Object.keys(dayOf).length === 0) {
    dayOf = {
      '09:00': 'Controlla la lista della spesa e prepara gli ingredienti',
      '11:00': 'Inizia le preparazioni più lunghe',
      '18:00': 'Ultimi ritocchi e impiattamento',
    };
  }

  // Retrocompatibilità: il modello a volte usa ancora "one_day_before"
  const inAdvance = Array.isArray(t.in_advance)
    ? t.in_advance.map(String)
    : Array.isArray(t.one_day_before)
      ? t.one_day_before.map(String)
      : [];

  return { in_advance: inAdvance, day_of: dayOf };
}

/* eslint-enable @typescript-eslint/no-explicit-any */

// ─────────────────────────────────────────────────────────────────
// HELPER CALORIE E LISTA SPESA (calcolati client-side, non ci
// fidiamo delle somme del modello)
// ─────────────────────────────────────────────────────────────────

/** Kcal totali PER PERSONA di un pasto (somma dei piatti). */
export function mealCalories(meal: Meal): number {
  return meal.dishes.reduce((sum, dish) => sum + (dish.nutrition?.calories ?? 0), 0);
}

/** Kcal totali PER PERSONA dell'intero menù. */
export function menuCalories(meals: Meal[]): number {
  return meals.reduce((sum, meal) => sum + mealCalories(meal), 0);
}

/**
 * Aggrega gli ingredienti di tutti i piatti in una lista spesa per
 * categoria. Usata anche dopo la rigenerazione di un piatto per
 * tenere la lista aggiornata.
 */
export function computeShoppingList(meals: Meal[]): ShoppingList {
  const categories: Record<string, Ingredient[]> = {};
  const seen = new Set<string>();

  meals.forEach((meal) => {
    meal.dishes.forEach((dish) => {
      dish.recipe.ingredients.forEach((ing) => {
        const key = ing.name.toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        const cat = ing.category || 'Altro';
        if (!categories[cat]) categories[cat] = [];
        categories[cat].push(ing);
      });
    });
  });

  return { categories };
}

// ─────────────────────────────────────────────────────────────────
// GESTIONE ERRORI
// ─────────────────────────────────────────────────────────────────

function mapAiError(error: unknown): Error {
  const msg = error instanceof Error ? error.message : String(error);

  if (/429|RESOURCE_EXHAUSTED|quota/i.test(msg)) {
    return new Error(
      'Quota gratuita di Gemini esaurita o troppe richieste ravvicinate. ' +
        'Attendi un minuto e riprova, oppure seleziona un altro modello.'
    );
  }
  if (/404|not found|is not supported/i.test(msg)) {
    return new Error(
      'Il modello selezionato non è al momento disponibile. Prova un altro modello dal menù a tendina.'
    );
  }
  if (/403|PERMISSION_DENIED|API.*not.*enabled|AI Logic/i.test(msg)) {
    return new Error(
      'Firebase AI Logic non risulta attivo per questo progetto. ' +
        'Verifica di aver attivato "AI Logic" con la Gemini Developer API nella console Firebase.'
    );
  }
  if (/SAFETY|blocked/i.test(msg)) {
    return new Error(
      'La risposta è stata bloccata dai filtri di sicurezza. Prova a riformulare le preferenze.'
    );
  }
  if (/network|fetch|Failed to fetch|offline/i.test(msg)) {
    return new Error('Problema di connessione. Controlla la rete e riprova.');
  }
  return new Error(`Errore durante la generazione: ${msg}`);
}

function getModel(modelId: string, systemInstruction: string, temperature: number) {
  if (!firebase) {
    throw new Error('Firebase non è configurato. Crea il file frontend/.env (vedi .env.example).');
  }
  return getGenerativeModel(firebase.ai, {
    model: modelId,
    systemInstruction,
    generationConfig: {
      temperature,
      responseMimeType: 'application/json',
    },
  });
}

// ─────────────────────────────────────────────────────────────────
// API PUBBLICA
// ─────────────────────────────────────────────────────────────────

/**
 * Genera un menù completo (uno o più pasti) con il modello Gemini scelto.
 */
export async function generateMenu(input: UserInput, modelId: string): Promise<MenuOutput> {
  const model = getModel(modelId, CHEF_SYSTEM_PROMPT, 0.7);
  const prompt = buildMenuPrompt(input);

  let text: string;
  try {
    const result = await model.generateContent(prompt);
    text = result.response.text();
  } catch (error) {
    throw mapAiError(error);
  }

  const raw = parseJsonResponse(text);
  const meals = normalizeMeals(raw, input.meal_types);

  return {
    menu_id: crypto.randomUUID(),
    generated_at: new Date().toISOString(),
    input,
    meals,
    shopping_list: normalizeShoppingList(raw, meals),
    timeline: normalizeTimeline(raw),
  };
}

/**
 * Rigenera un singolo piatto mantenendo coerenza con il resto del
 * menù (il menù corrente fa da contesto nel prompt).
 */
export async function regenerateDish(
  menu: MenuOutput,
  mealType: MealType,
  dishIndex: number,
  userFeedback: string,
  modelId: string
): Promise<Dish> {
  const meal = menu.meals.find((m) => m.meal_type === mealType);
  const currentDish = meal?.dishes?.[dishIndex];
  if (!currentDish) {
    throw new Error(`Piatto ${mealType}[${dishIndex}] non trovato nel menù.`);
  }

  const model = getModel(modelId, CHEF_SYSTEM_PROMPT, 0.8);
  const prompt = buildRegenerationPrompt(menu, mealType, currentDish, userFeedback);

  let text: string;
  try {
    const result = await model.generateContent(prompt);
    text = result.response.text();
  } catch (error) {
    throw mapAiError(error);
  }

  const raw = parseJsonResponse(text);
  // A volte il modello incapsula il piatto in una chiave contenitore
  const dishData = raw?.name ? raw : raw?.dish ?? raw?.new_dish ?? raw?.course ?? raw;
  return normalizeDish(dishData);
}

// ─────────────────────────────────────────────────────────────────
// STIMA NUTRIZIONALE (diario alimentare)
// Da descrizione testuale o da foto del piatto. Come per i menù,
// sono STIME dell'LLM: ordine di grandezza, non valori da database.
// ─────────────────────────────────────────────────────────────────

const NUTRITIONIST_SYSTEM_PROMPT = `
Sei un nutrizionista esperto specializzato nella stima di calorie e macronutrienti di cibi e piatti, a partire da descrizioni testuali o fotografie.

REGOLE:
1. Fornisci sempre stime REALISTICHE per la porzione effettivamente descritta/fotografata (non per 100g)
2. Se la porzione non è chiara, assumi una porzione media da adulto e dichiaralo nel campo assumed_portion
3. Sii onesto sulla confidenza: "bassa" se il cibo è ambiguo o la porzione molto incerta
4. Rispondi SOLO con JSON valido, senza markdown né altro testo
`;

const ESTIMATE_JSON_EXAMPLE = `{
  "description": "Piatto di spaghetti alla carbonara",
  "assumed_portion": "porzione media (~120g di pasta cruda)",
  "nutrition": {"calories": 650, "protein_g": 24, "carbs_g": 78, "fat_g": 26},
  "confidence": "media"
}`;

/* eslint-disable @typescript-eslint/no-explicit-any */
function normalizeEstimate(raw: any): NutritionEstimate {
  const confidence = ['alta', 'media', 'bassa'].includes(raw?.confidence) ? raw.confidence : 'media';
  return {
    description: String(raw?.description ?? 'Cibo non identificato'),
    assumed_portion: String(raw?.assumed_portion ?? 'porzione media'),
    nutrition: normalizeNutrition(raw?.nutrition ?? raw),
    confidence,
  };
}
/* eslint-enable @typescript-eslint/no-explicit-any */

/**
 * Stima kcal e macro dalla descrizione testuale di qualcosa che si è
 * mangiato (es. "un piatto di lasagne e una mela").
 */
export async function estimateNutritionFromText(
  description: string,
  modelId: string
): Promise<NutritionEstimate> {
  const model = getModel(modelId, NUTRITIONIST_SYSTEM_PROMPT, 0.3);
  const prompt = `
Stima calorie e macronutrienti di questo cibo/pasto:

"${description.trim()}"

Restituisci SOLO un JSON con questa struttura:
${ESTIMATE_JSON_EXAMPLE}

Le stime si riferiscono alla porzione descritta (campo "nutrition" con numeri, non stringhe).
`;

  let text: string;
  try {
    const result = await model.generateContent(prompt);
    text = result.response.text();
  } catch (error) {
    throw mapAiError(error);
  }

  return normalizeEstimate(parseJsonResponse(text));
}
