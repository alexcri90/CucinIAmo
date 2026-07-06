import { useEffect, useState } from 'react';
import { signOut, type User } from 'firebase/auth';
import { firebase } from './firebase';
import {
  generateMenu,
  regenerateDish,
  computeShoppingList,
  mealCalories,
  menuCalories,
  AVAILABLE_MODELS,
  DEFAULT_MODEL,
  MEAL_LABELS,
} from './services/aiService';
import { saveRecipe, listRecipes, updateRecipe, deleteRecipe } from './services/recipeService';
import { addDiaryEntry, toISODate } from './services/diaryService';
import RecipeDetails from './components/RecipeDetails';
import Ricettario, { type RecipePatch } from './components/Ricettario';
import Diario from './components/Diario';
import type {
  UserInput,
  MenuOutput,
  Meal,
  MealType,
  Dish,
  DietaryRestriction,
  DifficultyLevel,
  BudgetLevel,
  SavedRecipe,
} from './types';
import './App.css';

// Viste principali dell'app (navigazione a tab sotto l'header)
type AppView = 'genera' | 'ricettario' | 'diario';

const MODEL_STORAGE_KEY = 'cuciniamo-model';

// Stato per la rigenerazione di un piatto
interface RegeneratingState {
  mealType: MealType;
  dishIndex: number;
}

// Modal per feedback opzionale durante la rigenerazione
const RegenerateModal = ({
  isOpen,
  onClose,
  onConfirm,
  dishName
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (feedback: string) => void;
  dishName: string;
}) => {
  const [feedback, setFeedback] = useState('');

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm(feedback);
    setFeedback('');
  };

  const handleClose = () => {
    setFeedback('');
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={handleClose}>×</button>
        <h3>🔄 Rigenera "{dishName}"</h3>
        <p className="modal-subtitle">
          Vuoi dare un feedback per la nuova versione? (opzionale)
        </p>
        <textarea
          className="feedback-textarea"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Es: Vorrei qualcosa di più leggero, senza formaggio, con più verdure..."
          rows={3}
          maxLength={500}
        />
        <div className="modal-actions">
          <button className="modal-btn secondary" onClick={handleClose}>
            Annulla
          </button>
          <button className="modal-btn primary" onClick={handleConfirm}>
            🔄 Rigenera
          </button>
        </div>
      </div>
    </div>
  );
};

// Cucine popolari proposte come chip; qualsiasi altra si aggiunge
// dal campo di testo libero
const SUGGESTED_CUISINES = [
  'italiana', 'francese', 'spagnola', 'greca', 'mediterranea',
  'cinese', 'giapponese', 'thailandese', 'vietnamita', 'coreana',
  'indiana', 'mediorientale', 'turca', 'marocchina',
  'messicana', 'peruviana', 'brasiliana', 'americana',
  'tedesca', 'inglese', 'scandinava', 'polacca', 'fusion',
];

const MEAL_OPTIONS: { value: MealType; label: string }[] = [
  { value: 'colazione', label: '🥐 Colazione' },
  { value: 'pranzo', label: '🍝 Pranzo' },
  { value: 'cena', label: '🍽️ Cena' },
  { value: 'spuntino', label: '🍎 Spuntini' },
];

const MEAL_EMOJI: Record<MealType, string> = {
  colazione: '🥐',
  pranzo: '🍝',
  cena: '🍽️',
  spuntino: '🍎',
};

const DIETARY_OPTIONS: { value: DietaryRestriction; label: string }[] = [
  { value: 'vegetariano', label: '🥬 Vegetariano' },
  { value: 'vegano', label: '🌱 Vegano' },
  { value: 'senza_glutine', label: '🌾 Senza Glutine' },
  { value: 'senza_lattosio', label: '🥛 Senza Lattosio' },
];

function App({ user }: { user: User }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [menu, setMenu] = useState<MenuOutput | null>(null);
  const [activeTab, setActiveTab] = useState<'menu' | 'shopping' | 'timeline'>('menu');
  const [view, setView] = useState<AppView>('genera');

  // Ricettario: null = non ancora caricato da Firestore
  const [savedRecipes, setSavedRecipes] = useState<SavedRecipe[] | null>(null);
  const [ricettarioLoading, setRicettarioLoading] = useState(false);
  const [ricettarioError, setRicettarioError] = useState<string | null>(null);
  // dish_id dei piatti salvati in questa sessione (per il feedback "✓ Salvata")
  const [savedDishIds, setSavedDishIds] = useState<Record<string, boolean>>({});
  const [savingDishId, setSavingDishId] = useState<string | null>(null);

  // Stati per rigenerazione piatti
  const [regenerating, setRegenerating] = useState<RegeneratingState | null>(null);
  const [regenerateModal, setRegenerateModal] = useState<{
    isOpen: boolean;
    mealType: MealType;
    dishIndex: number;
    dishName: string;
  }>({ isOpen: false, mealType: 'pranzo', dishIndex: 0, dishName: '' });
  const [justRegenerated, setJustRegenerated] = useState<string | null>(null);

  const [formData, setFormData] = useState<UserInput>({
    num_people: 2,
    meal_types: ['cena'],
    cuisines: ['italiana'],
    preferred_ingredients: [],
    avoided_ingredients: [],
    dietary_restrictions: [],
    difficulty_level: 'medio',
    budget_level: 'medio',
    max_calories: null,
  });

  const [ingredientInput, setIngredientInput] = useState('');
  const [avoidedInput, setAvoidedInput] = useState('');
  const [customCuisineInput, setCustomCuisineInput] = useState('');
  const [caloriesEnabled, setCaloriesEnabled] = useState(false);
  const [caloriesInput, setCaloriesInput] = useState('1700');

  // Modello Gemini selezionato (persistito in localStorage)
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    const saved = localStorage.getItem(MODEL_STORAGE_KEY);
    return saved && AVAILABLE_MODELS.some(m => m.id === saved) ? saved : DEFAULT_MODEL;
  });

  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    localStorage.setItem(MODEL_STORAGE_KEY, modelId);
  };

  const handleSignOut = () => {
    if (firebase) void signOut(firebase.auth);
  };

  // Carica il ricettario da Firestore la prima volta che si apre la tab
  useEffect(() => {
    if (view !== 'ricettario' || savedRecipes !== null) return;
    let cancelled = false;
    setRicettarioLoading(true);
    setRicettarioError(null);
    listRecipes(user.uid)
      .then((recipes) => {
        if (!cancelled) setSavedRecipes(recipes);
      })
      .catch((err) => {
        if (!cancelled) {
          setRicettarioError(err instanceof Error ? err.message : 'Errore nel caricamento del ricettario');
        }
      })
      .finally(() => {
        if (!cancelled) setRicettarioLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [view, savedRecipes, user.uid]);

  // Salva un piatto del menù corrente nel ricettario
  const handleSaveDish = async (dish: Dish, mealType: MealType) => {
    if (!menu || savingDishId !== null || savedDishIds[dish.dish_id]) return;
    setSavingDishId(dish.dish_id);
    setError(null);
    try {
      const recipe = await saveRecipe(user.uid, dish, {
        menu_id: menu.menu_id,
        meal_type: mealType,
      });
      setSavedDishIds((prev) => ({ ...prev, [dish.dish_id]: true }));
      // Se il ricettario è già stato caricato, tienilo allineato
      setSavedRecipes((prev) => (prev ? [recipe, ...prev] : prev));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nel salvataggio della ricetta');
    } finally {
      setSavingDishId(null);
    }
  };

  // Elimina una ricetta dal ricettario (con conferma)
  const handleDeleteRecipe = async (recipe: SavedRecipe) => {
    if (!window.confirm(`Eliminare "${recipe.dish.name}" dal ricettario?`)) return;
    setRicettarioError(null);
    try {
      await deleteRecipe(user.uid, recipe.recipe_id);
      setSavedRecipes((prev) => (prev ? prev.filter((r) => r.recipe_id !== recipe.recipe_id) : prev));
    } catch (err) {
      setRicettarioError(err instanceof Error ? err.message : "Errore nell'eliminazione della ricetta");
    }
  };

  // "L'ho cucinata!" → registra la ricetta nel diario di oggi
  const handleLogToDiary = async (recipe: SavedRecipe, mealType: MealType) => {
    await addDiaryEntry(user.uid, toISODate(new Date()), {
      entry_id: crypto.randomUUID(),
      meal_type: mealType,
      description: recipe.dish.name,
      nutrition: recipe.dish.nutrition,
      recipe_id: recipe.recipe_id,
      source: 'ricettario',
      logged_at: new Date().toISOString(),
    });
  };

  // Aggiorna una ricetta (rating, note, editing) su Firestore e nello stato
  const handleUpdateRecipe = async (recipeId: string, patch: RecipePatch) => {
    await updateRecipe(user.uid, recipeId, patch);
    const updated_at = new Date().toISOString();
    setSavedRecipes((prev) =>
      prev ? prev.map((r) => (r.recipe_id === recipeId ? { ...r, ...patch, updated_at } : r)) : prev
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const parsedCalories = parseInt(caloriesInput, 10);
    const input: UserInput = {
      ...formData,
      max_calories: caloriesEnabled && parsedCalories > 0 ? parsedCalories : null,
    };

    try {
      const result = await generateMenu(input, selectedModel);
      setMenu(result);
      setActiveTab('menu');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nella generazione del menù');
    } finally {
      setIsLoading(false);
    }
  };

  const addIngredient = () => {
    if (ingredientInput.trim()) {
      setFormData(prev => ({
        ...prev,
        preferred_ingredients: [...prev.preferred_ingredients, ingredientInput.trim()]
      }));
      setIngredientInput('');
    }
  };

  const removeIngredient = (index: number) => {
    setFormData(prev => ({
      ...prev,
      preferred_ingredients: prev.preferred_ingredients.filter((_, i) => i !== index)
    }));
  };

  const addAvoided = () => {
    if (avoidedInput.trim()) {
      setFormData(prev => ({
        ...prev,
        avoided_ingredients: [...prev.avoided_ingredients, avoidedInput.trim()]
      }));
      setAvoidedInput('');
    }
  };

  const removeAvoided = (index: number) => {
    setFormData(prev => ({
      ...prev,
      avoided_ingredients: prev.avoided_ingredients.filter((_, i) => i !== index)
    }));
  };

  const toggleCuisine = (cuisine: string) => {
    setFormData(prev => ({
      ...prev,
      cuisines: prev.cuisines.includes(cuisine)
        ? prev.cuisines.filter(c => c !== cuisine)
        : [...prev.cuisines, cuisine]
    }));
  };

  const addCustomCuisine = () => {
    const cuisine = customCuisineInput.trim().toLowerCase();
    if (cuisine && !formData.cuisines.includes(cuisine)) {
      setFormData(prev => ({ ...prev, cuisines: [...prev.cuisines, cuisine] }));
    }
    setCustomCuisineInput('');
  };

  // Cucine aggiunte a mano (non presenti tra i suggerimenti)
  const customCuisines = formData.cuisines.filter(c => !SUGGESTED_CUISINES.includes(c));

  const toggleMeal = (meal: MealType) => {
    setFormData(prev => ({
      ...prev,
      meal_types: prev.meal_types.includes(meal)
        ? prev.meal_types.filter(m => m !== meal)
        : [...prev.meal_types, meal]
    }));
  };

  const selectFullDay = () => {
    setFormData(prev => ({ ...prev, meal_types: ['colazione', 'pranzo', 'cena'] }));
  };

  const toggleDietary = (restriction: DietaryRestriction) => {
    setFormData(prev => ({
      ...prev,
      dietary_restrictions: prev.dietary_restrictions.includes(restriction)
        ? prev.dietary_restrictions.filter(r => r !== restriction)
        : [...prev.dietary_restrictions, restriction]
    }));
  };

  // Apri modal per rigenerazione
  const openRegenerateModal = (mealType: MealType, dishIndex: number, dishName: string) => {
    setRegenerateModal({ isOpen: true, mealType, dishIndex, dishName });
  };

  // Chiudi modal
  const closeRegenerateModal = () => {
    setRegenerateModal(prev => ({ ...prev, isOpen: false }));
  };

  // Rigenera un piatto (con o senza feedback) e aggiorna la lista spesa
  const performRegenerate = async (mealType: MealType, dishIndex: number, feedback: string) => {
    if (!menu) return;
    setRegenerating({ mealType, dishIndex });
    setError(null);

    try {
      const newDish = await regenerateDish(menu, mealType, dishIndex, feedback, selectedModel);

      setMenu(prev => {
        if (!prev) return prev;

        const updatedMeals = prev.meals.map(meal => {
          if (meal.meal_type !== mealType) return meal;
          const dishes = [...meal.dishes];
          dishes[dishIndex] = newDish;
          return { ...meal, dishes };
        });

        return {
          ...prev,
          meals: updatedMeals,
          // Ricalcola la lista spesa dagli ingredienti aggiornati;
          // il piano di preparazione resta quello del menù originale
          shopping_list: computeShoppingList(updatedMeals),
        };
      });

      // Effetto flash sul piatto rigenerato
      setJustRegenerated(newDish.dish_id);
      setTimeout(() => setJustRegenerated(null), 2000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nella rigenerazione del piatto');
    } finally {
      setRegenerating(null);
    }
  };

  // Rigenerazione con feedback dal modal
  const handleRegenerate = (feedback: string) => {
    const { mealType, dishIndex } = regenerateModal;
    closeRegenerateModal();
    void performRegenerate(mealType, dishIndex, feedback);
  };

  // Rigenerazione rapida senza modal (click diretto)
  const handleQuickRegenerate = (mealType: MealType, dishIndex: number) => {
    void performRegenerate(mealType, dishIndex, '');
  };

  const downloadPDF = () => {
    if (!menu) return;
    const content = generatePrintableHTML(menu);
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(content);
      printWindow.document.close();
      printWindow.print();
    }
  };

  const generatePrintableHTML = (menuData: MenuOutput): string => {
    let mealsHTML = '';
    for (const meal of menuData.meals) {
      mealsHTML += `<h2>${MEAL_EMOJI[meal.meal_type]} ${MEAL_LABELS[meal.meal_type]} <small>(~${mealCalories(meal)} kcal/persona)</small></h2>`;
      for (const dish of meal.dishes) {
        mealsHTML += `
          <div class="dish">
            <h3>${dish.role} - ${dish.name}</h3>
            <p><em>${dish.description}</em></p>
            <p><strong>Cucina:</strong> ${dish.cuisine} | <strong>Calorie:</strong> ~${dish.nutrition.calories} kcal/porzione (P ${dish.nutrition.protein_g}g · C ${dish.nutrition.carbs_g}g · G ${dish.nutrition.fat_g}g)</p>
            <p><strong>Tempo:</strong> ${dish.recipe.prep_time_minutes} min prep + ${dish.recipe.cook_time_minutes} min cottura</p>
            <h4>Ingredienti:</h4>
            <ul>
              ${dish.recipe.ingredients.map((i) => `<li>${i.quantity} ${i.name}</li>`).join('')}
            </ul>
            <h4>Procedimento:</h4>
            <ol>
              ${dish.recipe.steps.map((s) => `<li>${s}</li>`).join('')}
            </ol>
            ${dish.recipe.chef_notes ? `<p><strong>Note dello Chef:</strong> ${dish.recipe.chef_notes}</p>` : ''}
          </div>
        `;
      }
    }

    const total = menuCalories(menuData.meals);
    const budget = menuData.input.max_calories
      ? ` (limite: ${menuData.input.max_calories} kcal)`
      : '';

    return `<!DOCTYPE html><html><head><title>CucinIAmo - Menù</title><style>body{font-family:Georgia,serif;max-width:800px;margin:0 auto;padding:20px;color:#201A2B}h1{text-align:center;color:#D6349E}h2{color:#B02C8F;border-bottom:1px solid #ECEAF0;padding-bottom:4px}h3{color:#F3704D}.dish{margin-bottom:30px;page-break-inside:avoid}</style></head><body><h1>🍅 CucinIAmo</h1><p style="text-align:center">Per ${menuData.input.num_people} person${menuData.input.num_people === 1 ? 'a' : 'e'} — Totale: ~${total} kcal/persona${budget}</p>${mealsHTML}</body></html>`;
  };

  // Riepilogo calorie del menù corrente
  const renderCaloriesSummary = (menuData: MenuOutput) => {
    const total = menuCalories(menuData.meals);
    const budget = menuData.input.max_calories;
    const overBudget = budget !== null && total > budget;

    return (
      <div className={`kcal-summary ${overBudget ? 'over' : ''}`}>
        🔥 Totale: <strong>~{total} kcal</strong> a persona
        {budget !== null && (
          <span className="kcal-budget">
            {overBudget ? ` — oltre il limite di ${budget} kcal!` : ` — entro il limite di ${budget} kcal ✓`}
          </span>
        )}
      </div>
    );
  };

  const renderDishCard = (meal: Meal, dish: Dish, idx: number) => {
    const isRegenerating = regenerating?.mealType === meal.meal_type && regenerating?.dishIndex === idx;
    const wasJustRegenerated = justRegenerated === dish.dish_id;
    const isSaved = Boolean(savedDishIds[dish.dish_id]);
    const isSaving = savingDishId === dish.dish_id;

    return (
      <div
        key={dish.dish_id}
        className={`dish-card ${isRegenerating ? 'regenerating' : ''} ${wasJustRegenerated ? 'just-regenerated' : ''}`}
      >
        <div className="dish-header">
          <div className="dish-title">
            <span className="role-badge">{dish.role}</span>
            <h4>{dish.name}</h4>
          </div>
          <div className="dish-header-actions">
            <span className="cuisine-badge">{dish.cuisine}</span>
            <span className="kcal-badge">🔥 {dish.nutrition.calories} kcal</span>
            <div className="regenerate-buttons">
              <button
                className={`regenerate-btn save ${isSaved ? 'saved' : ''}`}
                onClick={() => void handleSaveDish(dish, meal.meal_type)}
                disabled={isSaved || isSaving || isRegenerating}
                title={isSaved ? 'Salvata nel ricettario' : 'Salva nel ricettario'}
              >
                {isSaving ? <span className="spinner-small"></span> : isSaved ? '✓' : '💾'}
              </button>
              <button
                className="regenerate-btn quick"
                onClick={() => handleQuickRegenerate(meal.meal_type, idx)}
                disabled={isRegenerating || regenerating !== null}
                title="Rigenera velocemente"
              >
                {isRegenerating ? <span className="spinner-small"></span> : '🔄'}
              </button>
              <button
                className="regenerate-btn with-feedback"
                onClick={() => openRegenerateModal(meal.meal_type, idx, dish.name)}
                disabled={isRegenerating || regenerating !== null}
                title="Rigenera con feedback"
              >
                {isRegenerating ? '...' : '💬'}
              </button>
            </div>
          </div>
        </div>
        <p className="dish-description">{dish.description}</p>
        <div className="dish-meta">
          <span>⏱️ {dish.recipe.prep_time_minutes + dish.recipe.cook_time_minutes} min totali</span>
          <span>📊 {dish.recipe.difficulty}</span>
          <span>🥩 P {dish.nutrition.protein_g}g · 🍞 C {dish.nutrition.carbs_g}g · 🧈 G {dish.nutrition.fat_g}g</span>
          {dish.recipe.can_prep_ahead && <span className="prep-ahead">✅ Preparabile in anticipo</span>}
        </div>
        <RecipeDetails dish={dish} />
      </div>
    );
  };

  return (
    <div className="app">
      <header className="header">
        <img src="/logo.png" alt="" className="header-logo" />
        <div className="header-titles">
          <h1>CucinIAmo</h1>
          <p className="tagline">Il tuo menù, generato con l'AI</p>
        </div>
        <div className="header-spacer" />
        <div className="user-chip">
          {user.photoURL && <img src={user.photoURL} alt="" className="user-avatar" referrerPolicy="no-referrer" />}
          <span className="user-email">{user.email}</span>
          <button type="button" className="logout-btn" onClick={handleSignOut} title="Esci">
            Esci
          </button>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={view === 'genera' ? 'active' : ''}
          onClick={() => setView('genera')}
        >
          🍳 Genera
        </button>
        <button
          className={view === 'ricettario' ? 'active' : ''}
          onClick={() => setView('ricettario')}
        >
          📖 Ricettario
        </button>
        <button
          className={view === 'diario' ? 'active' : ''}
          onClick={() => setView('diario')}
        >
          📔 Diario
        </button>
      </nav>

      <main className="main-content">
        {view === 'diario' ? (
          <Diario uid={user.uid} selectedModel={selectedModel} />
        ) : view === 'ricettario' ? (
          <Ricettario
            recipes={savedRecipes}
            loading={ricettarioLoading}
            loadError={ricettarioError}
            onDismissLoadError={() => setRicettarioError(null)}
            onGoGenerate={() => setView('genera')}
            onUpdate={handleUpdateRecipe}
            onDelete={handleDeleteRecipe}
            onLogToDiary={handleLogToDiary}
          />
        ) : !menu ? (
          <form onSubmit={handleSubmit} className="input-form">
            <div className="form-section people-section">
              <h2>Quanti siete a tavola?</h2>
              <div className="people-counter">
                <button
                  type="button"
                  className="bounce-btn"
                  onClick={() => setFormData(prev => ({ ...prev, num_people: Math.max(1, prev.num_people - 1) }))}
                >−</button>
                <div className="people-number-wrapper">
                  <span className="people-number">{formData.num_people}</span>
                  <span className="people-label">person{formData.num_people === 1 ? 'a' : 'e'}</span>
                </div>
                <button
                  type="button"
                  className="bounce-btn"
                  onClick={() => setFormData(prev => ({ ...prev, num_people: Math.min(50, prev.num_people + 1) }))}
                >+</button>
              </div>
            </div>

            <div className="form-section">
              <h2>Quali pasti prepariamo?</h2>
              <p className="section-hint">Seleziona uno o più pasti, oppure l'intera giornata</p>
              <div className="chip-container centered">
                {MEAL_OPTIONS.map(option => (
                  <button
                    key={option.value}
                    type="button"
                    className={`chip bounce-btn ${formData.meal_types.includes(option.value) ? 'selected' : ''}`}
                    onClick={() => toggleMeal(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
                <button
                  type="button"
                  className="chip bounce-btn preset-chip"
                  onClick={selectFullDay}
                >
                  ☀️ Giornata intera
                </button>
              </div>
            </div>

            <div className="form-section">
              <h2>Che sapori portiamo in tavola?</h2>
              <p className="section-hint">Scegli tra le proposte o aggiungine di tue (es. "pugliese", "etiope", "fusion nikkei")</p>
              <div className="chip-container centered">
                {SUGGESTED_CUISINES.map(cuisine => (
                  <button
                    key={cuisine}
                    type="button"
                    className={`chip bounce-btn ${formData.cuisines.includes(cuisine) ? 'selected' : ''}`}
                    onClick={() => toggleCuisine(cuisine)}
                  >
                    {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)}
                  </button>
                ))}
                {customCuisines.map(cuisine => (
                  <button
                    key={cuisine}
                    type="button"
                    className="chip bounce-btn selected custom"
                    onClick={() => toggleCuisine(cuisine)}
                    title="Rimuovi"
                  >
                    {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)} ×
                  </button>
                ))}
              </div>
              <div className="ingredient-input custom-cuisine-input">
                <input
                  type="text"
                  value={customCuisineInput}
                  onChange={(e) => setCustomCuisineInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomCuisine())}
                  placeholder="Aggiungi un'altra cucina..."
                />
                <button type="button" className="bounce-btn" onClick={addCustomCuisine}>+</button>
              </div>
            </div>

            <div className="form-section ingredients-dual">
              <div className="ingredient-column prefer">
                <h2>💚 Cosa vi piace?</h2>
                <p className="section-hint">Ingredienti che amate</p>
                <div className="ingredient-input">
                  <input
                    type="text"
                    value={ingredientInput}
                    onChange={(e) => setIngredientInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addIngredient())}
                    placeholder="Es: salmone, avocado..."
                  />
                  <button type="button" className="bounce-btn" onClick={addIngredient}>+</button>
                </div>
                <div className="ingredients-list">
                  {formData.preferred_ingredients.map((ing, i) => (
                    <span key={i} className="ingredient-tag">
                      {ing} <button type="button" onClick={() => removeIngredient(i)}>×</button>
                    </span>
                  ))}
                </div>
              </div>
              <div className="ingredient-column avoid">
                <h2>🚫 Cosa evitare?</h2>
                <p className="section-hint">Allergie o preferenze</p>
                <div className="ingredient-input">
                  <input
                    type="text"
                    value={avoidedInput}
                    onChange={(e) => setAvoidedInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addAvoided())}
                    placeholder="Es: piccante, funghi..."
                  />
                  <button type="button" className="bounce-btn" onClick={addAvoided}>+</button>
                </div>
                <div className="ingredients-list">
                  {formData.avoided_ingredients.map((ing, i) => (
                    <span key={i} className="ingredient-tag avoid">
                      {ing} <button type="button" onClick={() => removeAvoided(i)}>×</button>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="form-section">
              <h2>Esigenze speciali?</h2>
              <p className="section-hint">Seleziona se necessario</p>
              <div className="chip-container centered">
                {DIETARY_OPTIONS.map(option => (
                  <button
                    key={option.value}
                    type="button"
                    className={`chip bounce-btn ${formData.dietary_restrictions.includes(option.value) ? 'selected' : ''}`}
                    onClick={() => toggleDietary(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-section">
              <h2>Teniamo d'occhio le calorie?</h2>
              <p className="section-hint">Opzionale: kcal massime a persona sull'insieme dei pasti scelti (es. 1700 per la giornata, 400 per una colazione)</p>
              <div className="calorie-control">
                <button
                  type="button"
                  className={`chip bounce-btn ${caloriesEnabled ? 'selected' : ''}`}
                  onClick={() => setCaloriesEnabled(prev => !prev)}
                >
                  {caloriesEnabled ? '🔥 Limite attivo' : 'Imposta un limite'}
                </button>
                {caloriesEnabled && (
                  <div className="calorie-input-wrapper">
                    <input
                      type="number"
                      className="calorie-input"
                      value={caloriesInput}
                      onChange={(e) => setCaloriesInput(e.target.value)}
                      min={100}
                      max={8000}
                      step={50}
                    />
                    <span className="calorie-unit">kcal / persona</span>
                  </div>
                )}
              </div>
            </div>

            <div className="form-section options-dual">
              <div className="option-column">
                <h2>👨‍🍳 Quanto vi impegnate?</h2>
                <div className="radio-group vertical">
                  {([
                    { value: 'facile', label: 'Relax', desc: 'Poco tempo, zero stress' },
                    { value: 'medio', label: 'Mi piace cucinare', desc: 'Il giusto equilibrio' },
                    { value: 'avanzato', label: 'Sfidami, chef!', desc: 'Piatti ambiziosi' },
                  ] as { value: DifficultyLevel; label: string; desc: string }[]).map(opt => (
                    <label key={opt.value} className={`bounce-btn ${formData.difficulty_level === opt.value ? 'selected' : ''}`}>
                      <input
                        type="radio"
                        name="difficulty"
                        value={opt.value}
                        checked={formData.difficulty_level === opt.value}
                        onChange={(e) => setFormData(prev => ({ ...prev, difficulty_level: e.target.value as DifficultyLevel }))}
                      />
                      <span className="option-label">{opt.label}</span>
                      <span className="option-desc">{opt.desc}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="option-column">
                <h2>💰 Quanto spendete?</h2>
                <div className="radio-group vertical">
                  {([
                    { value: 'economico', label: 'Budget friendly', desc: 'Spesa contenuta' },
                    { value: 'medio', label: 'Il giusto', desc: 'Qualità e prezzo' },
                    { value: 'premium', label: 'Niente limiti!', desc: 'Ingredienti pregiati' },
                  ] as { value: BudgetLevel; label: string; desc: string }[]).map(opt => (
                    <label key={opt.value} className={`bounce-btn ${formData.budget_level === opt.value ? 'selected' : ''}`}>
                      <input
                        type="radio"
                        name="budget"
                        value={opt.value}
                        checked={formData.budget_level === opt.value}
                        onChange={(e) => setFormData(prev => ({ ...prev, budget_level: e.target.value as BudgetLevel }))}
                      />
                      <span className="option-label">{opt.label}</span>
                      <span className="option-desc">{opt.desc}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="form-section">
              <h2>🤖 Quale AI cucinerà per voi?</h2>
              <p className="section-hint">Scegli il modello Gemini che genererà il menù</p>
              <div className="model-select-wrapper">
                <select
                  className="model-select"
                  value={selectedModel}
                  onChange={(e) => handleModelChange(e.target.value)}
                >
                  {AVAILABLE_MODELS.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.label} — {model.description}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {error && (
              <div className="error-box">
                <div className="error-message">❌ {error}</div>
                <details className="error-codes-info">
                  <summary>ℹ️ Problemi comuni</summary>
                  <ul>
                    <li><strong>Quota esaurita</strong> - il free tier di Gemini ha limiti al minuto e al giorno: attendi 1 minuto o cambia modello</li>
                    <li><strong>Modello non disponibile</strong> - i modelli in preview possono essere ritirati: scegline un altro dal menù a tendina</li>
                    <li><strong>JSON non valido</strong> - a volte il modello sbaglia formato: riprova, di solito il secondo tentativo funziona</li>
                    <li><strong>Connessione</strong> - controlla la rete e riprova</li>
                  </ul>
                </details>
              </div>
            )}

            <button
              type="submit"
              className="submit-button bounce-btn"
              disabled={isLoading || formData.cuisines.length === 0 || formData.meal_types.length === 0}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  <span>Lo chef è al lavoro... 👨‍🍳</span>
                </>
              ) : (
                <>
                  <span>✨</span>
                  <span>Crea il nostro menù</span>
                  <span>✨</span>
                </>
              )}
            </button>
          </form>
        ) : (
          <div className="menu-result">
            <div className="menu-header">
              <h2>Il tuo menù</h2>
              <p>
                Per {menu.input.num_people} person{menu.input.num_people === 1 ? 'a' : 'e'} —{' '}
                {menu.meals.map(m => MEAL_LABELS[m.meal_type]).join(', ')}
              </p>
              {renderCaloriesSummary(menu)}
              <div className="menu-actions">
                <button onClick={() => setMenu(null)} className="action-button">← Nuovo menù</button>
                <button onClick={downloadPDF} className="action-button primary">📄 Stampa PDF</button>
              </div>
            </div>

            <div className="tabs">
              <button className={activeTab === 'menu' ? 'active' : ''} onClick={() => setActiveTab('menu')}>📋 Menù</button>
              <button className={activeTab === 'shopping' ? 'active' : ''} onClick={() => setActiveTab('shopping')}>🛒 Lista Spesa</button>
              <button className={activeTab === 'timeline' ? 'active' : ''} onClick={() => setActiveTab('timeline')}>⏰ Timeline</button>
            </div>

            {activeTab === 'menu' && (
              <div className="meals-container">
                {menu.meals.map(meal => (
                  <div key={meal.meal_type} className="meal-section">
                    <div className="meal-title">
                      <h3>{MEAL_EMOJI[meal.meal_type]} {MEAL_LABELS[meal.meal_type]}</h3>
                      <span className="meal-kcal">~{mealCalories(meal)} kcal/persona</span>
                    </div>
                    {meal.dishes.map((dish, idx) => renderDishCard(meal, dish, idx))}
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'shopping' && (
              <div className="shopping-container">
                <h3>🛒 Lista della spesa</h3>
                {menu.shopping_list && menu.shopping_list.categories &&
                  Object.entries(menu.shopping_list.categories).map(([category, items]) => (
                    items && Array.isArray(items) && items.length > 0 && (
                      <div key={category} className="shopping-category">
                        <h4>{category}</h4>
                        <ul>
                          {items.map((item, i) => (
                            <li key={i}>{item.quantity} {item.name}</li>
                          ))}
                        </ul>
                      </div>
                    )
                  ))
                }
              </div>
            )}

            {activeTab === 'timeline' && (
              <div className="timeline-container">
                <h3>⏰ Piano di preparazione</h3>
                {menu.timeline && (
                  <>
                    {menu.timeline.in_advance && menu.timeline.in_advance.length > 0 && (
                      <div className="timeline-section">
                        <h4>📅 In anticipo</h4>
                        <ul>
                          {menu.timeline.in_advance.map((task, i) => (
                            <li key={i}>{task}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {menu.timeline.day_of && Object.keys(menu.timeline.day_of).length > 0 && (
                      <div className="timeline-section">
                        <h4>🍳 Il giorno stesso</h4>
                        <div className="day-schedule">
                          {Object.entries(menu.timeline.day_of)
                            .sort(([a], [b]) => a.localeCompare(b))
                            .map(([time, task]) => (
                              <div key={time} className="schedule-item">
                                <span className="time">{time}</span>
                                <span className="task">{String(task)}</span>
                              </div>
                            ))
                          }
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* Errore rigenerazione/salvataggio */}
        {error && menu && view === 'genera' && (
          <div className="error-banner">
            ❌ {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}
      </main>

      {/* Modal per feedback rigenerazione */}
      <RegenerateModal
        isOpen={regenerateModal.isOpen}
        onClose={closeRegenerateModal}
        onConfirm={handleRegenerate}
        dishName={regenerateModal.dishName}
      />

      <footer className="footer">
        <p>✨ Powered by <strong>Google Gemini</strong> via Firebase AI Logic</p>
      </footer>
    </div>
  );
}

export default App;
