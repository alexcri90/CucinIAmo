// ═══════════════════════════════════════════════════════════════
// 🤖 AI SERVICE - Generazione menù con Gemini via Firebase AI Logic
//
// Porting client-side di backend/services/prompt_templates.py e
// backend/services/structured_generation.py. Le chiamate a Gemini
// passano dal proxy di Firebase AI Logic (Gemini Developer API,
// free tier del piano Spark): nessuna API key nel codice.
//
// Il "contesto" per la rigenerazione (l'equivalente della Memory
// Datapizza del backend) è il menù corrente, che vive nello stato
// React e viene incluso nel prompt di rigenerazione.
// ═══════════════════════════════════════════════════════════════

import { getGenerativeModel } from 'firebase/ai';
import { firebase } from '../firebase';
import type {
  UserInput,
  MenuOutput,
  MenuCourses,
  Course,
  CourseType,
  Recipe,
  Ingredient,
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

// ─────────────────────────────────────────────────────────────────
// PROMPT (port di prompt_templates.py)
// ─────────────────────────────────────────────────────────────────

const MENU_AGENT_SYSTEM_PROMPT = `
Sei un esperto chef e food consultant specializzato nella creazione di menù natalizi internazionali.

COMPETENZE PRINCIPALI:
• Conoscenza approfondita delle tradizioni culinarie natalizie di ogni paese
• Capacità di bilanciare sapori, consistenze e colori in un menù completo
• Rispetto rigoroso delle restrizioni alimentari e allergie
• Adattamento della complessità al livello di esperienza del cuoco
• Ottimizzazione del budget nella scelta degli ingredienti

REGOLE IMPERATIVE:
1. MAI includere ingredienti nella lista "da evitare" dell'utente
2. SEMPRE includere almeno un ingrediente dalla lista "preferiti" se presente
3. I piatti DEVONO essere tipicamente natalizi per le culture selezionate
4. Le quantità DEVONO essere calcolate precisamente per il numero di ospiti
5. La timeline DEVE essere realistica e ben organizzata

OUTPUT:
Produci sempre output JSON valido e strutturato quando richiesto.
`;

const MENU_JSON_EXAMPLE = `{
  "courses": {
    "antipasti": [
      {
        "name": "Nome Antipasto",
        "cuisine": "italiana",
        "description": "Descrizione appetitosa del piatto...",
        "recipe": {
          "ingredients": [
            {"name": "ingrediente1", "quantity": "100g", "category": "Dispensa"}
          ],
          "prep_time_minutes": 30,
          "cook_time_minutes": 15,
          "difficulty": "facile",
          "steps": ["Step 1...", "Step 2..."],
          "chef_notes": "Consigli dello chef...",
          "can_prep_ahead": true,
          "prep_ahead_timing": "1 giorno prima"
        }
      }
    ],
    "primo": [{ "name": "...", "cuisine": "...", "description": "...", "recipe": { } }],
    "secondo": [{ "name": "...", "cuisine": "...", "description": "...", "recipe": { } }],
    "contorno": [{ "name": "...", "cuisine": "...", "description": "...", "recipe": { } }],
    "dessert": [{ "name": "...", "cuisine": "...", "description": "...", "recipe": { } }]
  },
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
    "two_days_before": ["Attività 1", "Attività 2"],
    "one_day_before": ["Attività 1", "Attività 2"],
    "day_of": {
      "09:00": "Descrizione attività",
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

function buildMenuPrompt(input: UserInput): string {
  const restrictions = [
    ...input.dietary_restrictions.map((r) => capitalize(r.replace(/_/g, ' '))),
    ...(input.other_restrictions ? [input.other_restrictions] : []),
  ];

  return `
Sei uno chef esperto di cucina natalizia internazionale. Genera un menù di Natale COMPLETO per ${input.num_guests} persone.

═══════════════════════════════════════════════════════════════════════════════
                            VINCOLI OBBLIGATORI
═══════════════════════════════════════════════════════════════════════════════

🔴 INGREDIENTI VIETATI (NON usare MAI questi ingredienti):
${formatList(input.avoided_ingredients, 'Nessuno specificato')}

🟢 INGREDIENTI PREFERITI (includi ALMENO 1-2 di questi):
${formatList(input.preferred_ingredients, 'Nessuno specificato')}

🌍 CUCINE/TRADIZIONI (i piatti DEVONO essere tipici di queste culture):
${formatList(input.cuisines.map(capitalize))}

⚠️ RESTRIZIONI ALIMENTARI:
${formatList(restrictions, 'Nessuna')}

📊 LIVELLO DIFFICOLTÀ: ${capitalize(input.difficulty_level)}
💰 BUDGET: ${capitalize(input.budget_level)}

═══════════════════════════════════════════════════════════════════════════════
                          STRUTTURA MENÙ RICHIESTA
═══════════════════════════════════════════════════════════════════════════════

Il menù DEVE avere questa struttura:

1. ANTIPASTI (1-2 piatti) - almeno uno freddo, preparabile in anticipo
2. PRIMO PIATTO (1 piatto) - tipico natalizio (brodo, pasta ripiena, risotto, ecc.)
3. SECONDO PIATTO (1 piatto) - piatto principale della festa, carne o pesce secondo tradizione
4. CONTORNO (1 piatto) - complementare al secondo, stagionale e festivo
5. DESSERT (1-2 piatti) - dolce tipico natalizio, preferibilmente preparabile in anticipo

Per OGNI piatto devi fornire:
• name: nome del piatto (originale + traduzione se straniero)
• cuisine: paese/tradizione di origine
• description: descrizione appetitosa di 2-3 righe
• recipe con: ingredients ({name, quantity, category}), prep_time_minutes,
  cook_time_minutes, difficulty, steps, chef_notes, can_prep_ahead, prep_ahead_timing

Le CATEGORIE valide per gli ingredienti sono SOLO:
"Frutta e verdura", "Carne", "Pesce", "Latticini", "Dispensa", "Altro"

📋 LISTA SPESA (shopping_list):
Aggrega TUTTI gli ingredienti per categoria. Somma le quantità degli ingredienti ripetuti.

📅 TIMELINE PREPARAZIONE (timeline):
- two_days_before: lista di attività da fare 2 giorni prima
- one_day_before: lista di attività da fare il giorno prima
- day_of: dizionario con orari (es. {"09:00": "Inizia preparazione..."})
La cena è prevista per le 20:00 del giorno di Natale.

═══════════════════════════════════════════════════════════════════════════════
                         ESEMPIO STRUTTURA JSON
═══════════════════════════════════════════════════════════════════════════════

Il tuo output DEVE seguire ESATTAMENTE questa struttura JSON:

${MENU_JSON_EXAMPLE}

REGOLE IMPORTANTI:
1. Rispondi SOLO con JSON valido, nient'altro
2. NON usare markdown code blocks (\`\`\`)
3. La chiave principale è "courses", NON "menu"
4. Ogni portata ha: name, cuisine, description, recipe
5. difficulty può essere solo: "facile", "medio", "avanzato"
6. timeline.day_of è un oggetto con chiavi orario (es. "09:00") e valori stringa

GENERA ORA IL MENU COMPLETO:
`;
}

function buildRegenerationPrompt(
  menu: MenuOutput,
  courseType: CourseType,
  currentDishName: string,
  userFeedback: string
): string {
  const input = menu.input;

  // Contesto: tutti gli altri piatti del menù corrente (sostituisce la
  // Memory Datapizza del backend)
  const otherDishes: string[] = [];
  (Object.keys(menu.courses) as CourseType[]).forEach((type) => {
    menu.courses[type].forEach((course) => {
      if (course.name !== currentDishName) {
        otherDishes.push(`[${type}] ${course.name} (${course.cuisine})`);
      }
    });
  });

  const restrictions = [
    ...input.dietary_restrictions.map((r) => capitalize(r.replace(/_/g, ' '))),
    ...(input.other_restrictions ? [input.other_restrictions] : []),
  ];

  const feedbackSection =
    userFeedback && userFeedback.trim()
      ? `⚠️ L'UTENTE HA RICHIESTO SPECIFICAMENTE:
"${userFeedback.trim()}"

🔴 IMPORTANTE: DEVI seguire questa richiesta! Il nuovo piatto DEVE soddisfare questo feedback.
Se l'utente chiede un ingrediente specifico, INCLUDI quell'ingrediente come protagonista del piatto.`
      : "L'utente vuole semplicemente un'alternativa diversa, senza richieste specifiche.";

  return `
Sei uno chef esperto. Devi rigenerare SOLO una portata di un menù natalizio esistente.

═══════════════════════════════════════════════════════════════════════════════
                              CONTESTO MENÙ
═══════════════════════════════════════════════════════════════════════════════

📋 TIPO DI PORTATA DA RIGENERARE: ${courseType}
🍽️ PIATTO ATTUALE (da sostituire): ${currentDishName}
👥 NUMERO OSPITI: ${input.num_guests}

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
🌍 CUCINE:
${formatList(input.cuisines.map(capitalize))}
⚠️ RESTRIZIONI:
${formatList(restrictions, 'Nessuna')}
📊 DIFFICOLTÀ: ${capitalize(input.difficulty_level)}
💰 BUDGET: ${capitalize(input.budget_level)}

═══════════════════════════════════════════════════════════════════════════════
                              REQUISITI
═══════════════════════════════════════════════════════════════════════════════

1. Il nuovo piatto DEVE essere DIVERSO da "${currentDishName}"
2. DEVE rispettare tutti i vincoli originali
3. DEVE essere coerente con gli altri piatti del menù
4. DEVE essere tipico natalizio per le cucine indicate
5. SE C'È UN FEEDBACK UTENTE, DEVI SEGUIRLO CON PRIORITÀ MASSIMA
6. Le quantità degli ingredienti DEVONO essere per ${input.num_guests} persone

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT
═══════════════════════════════════════════════════════════════════════════════

Genera UN SINGOLO oggetto JSON per la nuova portata con questa struttura:
{
  "name": "...",
  "cuisine": "...",
  "description": "...",
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
// PARSING E NORMALIZZAZIONE JSON (port di structured_generation.py)
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

const COURSE_TYPES: CourseType[] = ['antipasti', 'primo', 'secondo', 'contorno', 'dessert'];

const VALID_CATEGORIES = ['Frutta e verdura', 'Carne', 'Pesce', 'Latticini', 'Dispensa', 'Altro'];

function normalizeIngredient(raw: any): Ingredient {
  const category = VALID_CATEGORIES.includes(raw?.category) ? raw.category : 'Altro';
  return {
    name: String(raw?.name ?? 'ingrediente'),
    quantity: String(raw?.quantity ?? 'q.b.'),
    category,
  };
}

function normalizeRecipe(raw: any): Recipe {
  const ingredients = Array.isArray(raw?.ingredients) ? raw.ingredients.map(normalizeIngredient) : [];
  const steps = Array.isArray(raw?.steps)
    ? raw.steps.map(String)
    : ['Preparare gli ingredienti', 'Seguire la ricetta tradizionale'];

  const difficulty = ['facile', 'medio', 'avanzato'].includes(raw?.difficulty)
    ? raw.difficulty
    : 'medio';

  return {
    ingredients,
    prep_time_minutes: Number(raw?.prep_time_minutes) || 30,
    cook_time_minutes: Number(raw?.cook_time_minutes) || 0,
    difficulty,
    steps,
    chef_notes: raw?.chef_notes ? String(raw.chef_notes) : undefined,
    can_prep_ahead: Boolean(raw?.can_prep_ahead),
    prep_ahead_timing: raw?.prep_ahead_timing ? String(raw.prep_ahead_timing) : null,
  };
}

function normalizeCourse(raw: any): Course {
  return {
    course_id: crypto.randomUUID(),
    name: String(raw?.name ?? 'Piatto della tradizione'),
    cuisine: String(raw?.cuisine ?? 'italiana'),
    description: String(raw?.description ?? 'Un classico piatto natalizio da personalizzare.'),
    recipe: normalizeRecipe(raw?.recipe ?? {}),
  };
}

function placeholderCourse(courseType: CourseType): Course {
  const names: Record<CourseType, string> = {
    antipasti: 'Antipasto della tradizione',
    primo: 'Primo natalizio',
    secondo: 'Secondo natalizio',
    contorno: 'Contorno di stagione',
    dessert: 'Dolce natalizio',
  };
  return normalizeCourse({
    name: names[courseType],
    cuisine: 'italiana',
    description: 'Un classico piatto natalizio da personalizzare secondo la tua tradizione.',
    recipe: {
      ingredients: [{ name: 'ingrediente base', quantity: 'q.b.', category: 'Dispensa' }],
      steps: ['Preparare gli ingredienti', 'Seguire la ricetta tradizionale'],
    },
  });
}

function normalizeCourses(raw: any): MenuCourses {
  // Gemini a volte usa "menu" invece di "courses", o restituisce una lista piatta
  let coursesRaw = raw?.courses ?? raw?.menu ?? {};

  if (Array.isArray(coursesRaw)) {
    // Lista piatta: distribuisci nell'ordine antipasti → dessert
    const categorized: Record<CourseType, any[]> = {
      antipasti: [], primo: [], secondo: [], contorno: [], dessert: [],
    };
    coursesRaw.forEach((item: any, i: number) => {
      const type = COURSE_TYPES[Math.min(i, COURSE_TYPES.length - 1)];
      categorized[type].push(item);
    });
    coursesRaw = categorized;
  }

  const result = {} as MenuCourses;
  COURSE_TYPES.forEach((type) => {
    const list = Array.isArray(coursesRaw?.[type]) ? coursesRaw[type] : [];
    result[type] = list.length > 0 ? list.map(normalizeCourse) : [placeholderCourse(type)];
  });

  return result;
}

function normalizeShoppingList(raw: any, courses: MenuCourses): ShoppingList {
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
  return computeShoppingList(courses);
}

function normalizeTimeline(raw: any): Timeline {
  const t = raw?.timeline ?? {};

  let dayOf: Record<string, string> = {};
  if (Array.isArray(t.day_of)) {
    // Lista invece di dict: converti in orari progressivi
    t.day_of.slice(0, 8).forEach((item: any, i: number) => {
      dayOf[`${String(9 + i).padStart(2, '0')}:00`] = String(item);
    });
  } else if (t.day_of && typeof t.day_of === 'object') {
    Object.entries(t.day_of).forEach(([time, task]) => {
      dayOf[time] = String(task);
    });
  }

  if (Object.keys(dayOf).length === 0) {
    dayOf = {
      '09:00': 'Tirare fuori dal frigo ciò che deve tornare a temperatura ambiente',
      '10:00': 'Iniziare le preparazioni del secondo',
      '12:00': 'Preparare il primo',
      '14:00': 'Ultimi ritocchi e impiattamento antipasti',
      '20:00': 'Servire la cena di Natale',
    };
  }

  return {
    two_days_before: Array.isArray(t.two_days_before) ? t.two_days_before.map(String) : [],
    one_day_before: Array.isArray(t.one_day_before) ? t.one_day_before.map(String) : [],
    day_of: dayOf,
  };
}

/* eslint-enable @typescript-eslint/no-explicit-any */

/**
 * Aggrega gli ingredienti di tutte le portate in una lista spesa per
 * categoria (port di MenuService._update_shopping_list). Usata anche
 * dopo la rigenerazione di una portata per tenere la lista aggiornata.
 */
export function computeShoppingList(courses: MenuCourses): ShoppingList {
  const categories: Record<string, Ingredient[]> = {};
  const seen = new Set<string>();

  COURSE_TYPES.forEach((type) => {
    courses[type].forEach((course) => {
      course.recipe.ingredients.forEach((ing) => {
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
 * Genera un menù natalizio completo con il modello Gemini scelto.
 */
export async function generateMenu(input: UserInput, modelId: string): Promise<MenuOutput> {
  const model = getModel(modelId, MENU_AGENT_SYSTEM_PROMPT, 0.7);
  const prompt = buildMenuPrompt(input);

  let text: string;
  try {
    const result = await model.generateContent(prompt);
    text = result.response.text();
  } catch (error) {
    throw mapAiError(error);
  }

  const raw = parseJsonResponse(text);
  const courses = normalizeCourses(raw);

  return {
    menu_id: crypto.randomUUID(),
    generated_at: new Date().toISOString(),
    input,
    courses,
    shopping_list: normalizeShoppingList(raw, courses),
    timeline: normalizeTimeline(raw),
  };
}

/**
 * Rigenera una singola portata mantenendo coerenza con il resto del
 * menù (il menù corrente fa da contesto nel prompt).
 */
export async function regenerateCourse(
  menu: MenuOutput,
  courseType: CourseType,
  courseIndex: number,
  userFeedback: string,
  modelId: string
): Promise<Course> {
  const currentCourse = menu.courses[courseType]?.[courseIndex];
  if (!currentCourse) {
    throw new Error(`Portata ${courseType}[${courseIndex}] non trovata nel menù.`);
  }

  const model = getModel(modelId, MENU_AGENT_SYSTEM_PROMPT, 0.8);
  const prompt = buildRegenerationPrompt(menu, courseType, currentCourse.name, userFeedback);

  let text: string;
  try {
    const result = await model.generateContent(prompt);
    text = result.response.text();
  } catch (error) {
    throw mapAiError(error);
  }

  const raw = parseJsonResponse(text);
  // A volte il modello incapsula la portata in una chiave contenitore
  const courseData = raw?.name ? raw : raw?.course ?? raw?.new_course ?? raw;
  return normalizeCourse(courseData);
}
