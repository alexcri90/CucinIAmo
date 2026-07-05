# CucinIAmo - AI Coding Agent Instructions

## Project Overview

**CucinIAmo** is a client-only web app that generates personalized menus (breakfast, lunch, dinner, snacks or a full day) with estimated calories/macros, a shopping list and a prep plan, using **Google Gemini via Firebase AI Logic**. There is **no backend**: everything runs in the browser and is hosted on Firebase (Spark plan, 100% free — this is a hard constraint, never introduce paid resources).

**Key Stack:** React 19 + TypeScript 5 + Vite 7 | Firebase Hosting/Auth/Firestore/AI Logic (Gemini Developer API, free tier)

---

## Architecture & Data Flow

```
AuthGate (Google login → Firestore allowlist check)
  → App.tsx (form state, tabs: Menù / Lista Spesa / Preparazione)
  → aiService.ts (prompt building → Firebase AI Logic → Gemini → JSON parsing/normalization)
  → MenuOutput rendered with client-side calorie totals
```

| File | Responsibility |
|------|----------------|
| `frontend/src/types/index.ts` | Data model — **SOURCE OF TRUTH** for the JSON structure requested from Gemini (`UserInput`, `Meal`, `Dish`, `NutritionInfo`, `MenuOutput`) |
| `frontend/src/services/aiService.ts` | System prompt, menu/regeneration prompt builders, `AVAILABLE_MODELS` list, JSON parsing with normalization fallbacks, calorie helpers (`mealCalories`, `menuCalories`, `computeShoppingList`) |
| `frontend/src/App.tsx` | Form (people, meal types, free-text cuisines, ingredients, restrictions, optional kcal limit, difficulty, budget, model select) + results views + dish regeneration |
| `frontend/src/components/AuthGate.tsx` | Google sign-in + allowlist verification (`allowlist/{lowercase email}` doc must exist) |
| `frontend/src/firebase.ts` | Firebase init: Auth, Firestore, AI Logic (**GoogleAIBackend only** — VertexAIBackend requires the paid Blaze plan), optional App Check |
| `firestore.rules` | Users may only `get` their own allowlist doc; all writes denied |

---

## Critical Patterns

1. **Never trust Gemini's structure or math.** Responses are normalized (`normalizeMeals`, `normalizeDish`, `normalizeNutrition`, ...) with placeholders for missing meals; calorie totals and the shopping list are recomputed client-side.
2. **`cuisines` is free text** (user can type anything); **`meal_types` is a closed enum** (`colazione | pranzo | cena | spuntino`) used for grouping/ordering/regeneration. `Dish.role` is a free string ("Antipasto", "Piatto unico", ...).
3. **Calorie budget** (`max_calories`, kcal per person over all requested meals, optional): enforced via prompt (target 85-100% of budget, per-meal distribution hints for full days); regenerated dishes must stay within ±15% of the replaced dish's kcal when a budget is set.
4. **User feedback in regeneration prompts must be prominent** (dedicated "PRIORITÀ MASSIMA" section) or the model ignores it.
5. **Italian everywhere**: UI copy and prompts are intentionally in Italian; don't anglicize.
6. **Models list** (`AVAILABLE_MODELS`) is a plain array — preview models get retired by Google; fixing a 404 means editing that list.
7. **Firebase web config is public by design** (it ships in the JS bundle); security comes from Auth + Security Rules + allowlist. App Check (optional, reCAPTCHA v3 via `VITE_RECAPTCHA_SITE_KEY`) protects the free quota.

---

## Developer Workflow

```powershell
cd frontend
npm install
npm run dev      # http://localhost:5173 (needs frontend/.env, see .env.example)
npm run build    # tsc -b && vite build → type-check + production bundle
npm run lint

# Deploy (repo root, after setting the project id in .firebaserc)
firebase deploy
```

No formal test suite: `npm run build` (type-check) + manual verification are the safety net.

Setup from zero (new Firebase project, allowlist, AI Logic): follow `FIREBASE_DEPLOYMENT.md`. Project status and design decisions: `project_description.md`.
