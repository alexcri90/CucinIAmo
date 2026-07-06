// ═══════════════════════════════════════════════════════════════
// 📖 RICETTARIO - Vista completa delle ricette salvate (Fase 2)
//
// - Ricerca, filtri (pasto, cucina, valutazione) e ordinamento
// - Valutazione 1-5 stelle modificabile in ogni momento
// - Flusso "✅ L'ho cucinata!": cooked_count +1, stelle, nota
// - Editing della propria copia della ricetta (dosi, ingredienti,
//   passaggi, note dello chef) → is_customized
// - Note datate (diario delle preparazioni della singola ricetta)
//
// Lo stato (lista ricette) vive in App.tsx; qui arrivano i dati e
// le callback che scrivono su Firestore via recipeService.
// ═══════════════════════════════════════════════════════════════

import { useMemo, useState } from 'react';
import { MEAL_LABELS } from '../services/aiService';
import RecipeDetails from './RecipeDetails';
import type { Dish, Ingredient, MealType, SavedRecipe } from '../types';

export type RecipePatch = Partial<Omit<SavedRecipe, 'recipe_id' | 'saved_at'>>;

interface RicettarioProps {
  recipes: SavedRecipe[] | null;
  loading: boolean;
  loadError: string | null;
  onDismissLoadError: () => void;
  onGoGenerate: () => void;
  onUpdate: (recipeId: string, patch: RecipePatch) => Promise<void>;
  onDelete: (recipe: SavedRecipe) => Promise<void>;
  /** Registra la ricetta cucinata nel diario di oggi (Fase 3). */
  onLogToDiary: (recipe: SavedRecipe, mealType: MealType) => Promise<void>;
}

const MEAL_EMOJI: Record<MealType, string> = {
  colazione: '🥐',
  pranzo: '🍝',
  cena: '🍽️',
  spuntino: '🍎',
};

type StatusFilter = 'tutte' | 'top' | 'da_valutare' | 'cucinate';
type SortOption = 'recenti' | 'rating' | 'kcal';

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('it-IT', { day: 'numeric', month: 'short', year: 'numeric' });

// ── Stelle 1-5 (cliccabili) ──────────────────────────────────────
const StarRating = ({
  value,
  onChange,
  disabled,
}: {
  value: number | null;
  onChange: (v: number) => void;
  disabled?: boolean;
}) => (
  <span className="star-rating">
    {[1, 2, 3, 4, 5].map((n) => (
      <button
        key={n}
        type="button"
        className={`star-btn ${value !== null && n <= value ? 'filled' : ''}`}
        onClick={() => onChange(n)}
        disabled={disabled}
        title={`${n} stell${n === 1 ? 'a' : 'e'}`}
      >
        {value !== null && n <= value ? '★' : '☆'}
      </button>
    ))}
  </span>
);

// ── Modal "L'ho cucinata!" ───────────────────────────────────────
const CookedModal = ({
  recipe,
  onClose,
  onConfirm,
}: {
  recipe: SavedRecipe;
  onClose: () => void;
  onConfirm: (stars: number, note: string, diaryMeal: MealType | null) => void;
}) => {
  const [stars, setStars] = useState<number>(recipe.rating ?? 0);
  const [note, setNote] = useState('');
  const [addToDiary, setAddToDiary] = useState(false);
  const [diaryMeal, setDiaryMeal] = useState<MealType>(recipe.source?.meal_type ?? 'pranzo');

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>🎉 Hai cucinato "{recipe.dish.name}"!</h3>
        <p className="modal-subtitle">Com'è andata? Dai una valutazione e, se vuoi, lascia una nota.</p>
        <div className="cooked-stars">
          <StarRating value={stars || null} onChange={setStars} />
        </div>
        <textarea
          className="feedback-textarea"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Nota sulla preparazione (opzionale). Es: ottima, ma la prossima volta meno sale..."
          rows={3}
          maxLength={500}
        />
        <div className="diary-log-row">
          <label className="diary-log-check">
            <input
              type="checkbox"
              checked={addToDiary}
              onChange={(e) => setAddToDiary(e.target.checked)}
            />
            📔 Aggiungi al diario di oggi
          </label>
          {addToDiary && (
            <select value={diaryMeal} onChange={(e) => setDiaryMeal(e.target.value as MealType)}>
              {(Object.keys(MEAL_LABELS) as MealType[]).map((m) => (
                <option key={m} value={m}>{MEAL_EMOJI[m]} {MEAL_LABELS[m]}</option>
              ))}
            </select>
          )}
        </div>
        <div className="modal-actions">
          <button className="modal-btn secondary" onClick={onClose}>Annulla</button>
          <button className="modal-btn primary" onClick={() => onConfirm(stars, note, addToDiary ? diaryMeal : null)}>
            ✅ Conferma
          </button>
        </div>
      </div>
    </div>
  );
};

// ── Modal nuova nota ─────────────────────────────────────────────
const NoteModal = ({
  recipe,
  onClose,
  onConfirm,
}: {
  recipe: SavedRecipe;
  onClose: () => void;
  onConfirm: (note: string) => void;
}) => {
  const [note, setNote] = useState('');

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>📝 Nuova nota su "{recipe.dish.name}"</h3>
        <textarea
          className="feedback-textarea"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Es: con il forno ventilato bastano 20 minuti..."
          rows={4}
          maxLength={500}
          autoFocus
        />
        <div className="modal-actions">
          <button className="modal-btn secondary" onClick={onClose}>Annulla</button>
          <button
            className="modal-btn primary"
            onClick={() => note.trim() && onConfirm(note.trim())}
            disabled={!note.trim()}
          >
            Salva nota
          </button>
        </div>
      </div>
    </div>
  );
};

// ── Modal editing ricetta ────────────────────────────────────────
// Modifica la COPIA personale del piatto: dosi/ingredienti,
// passaggi, note dello chef, valori nutrizionali.
const EditModal = ({
  recipe,
  onClose,
  onConfirm,
}: {
  recipe: SavedRecipe;
  onClose: () => void;
  onConfirm: (dish: Dish) => void;
}) => {
  const [name, setName] = useState(recipe.dish.name);
  const [description, setDescription] = useState(recipe.dish.description);
  const [ingredients, setIngredients] = useState<Ingredient[]>(
    recipe.dish.recipe.ingredients.map((i) => ({ ...i }))
  );
  const [steps, setSteps] = useState<string[]>([...recipe.dish.recipe.steps]);
  const [chefNotes, setChefNotes] = useState(recipe.dish.recipe.chef_notes ?? '');
  const [calories, setCalories] = useState(String(recipe.dish.nutrition.calories));
  const [protein, setProtein] = useState(String(recipe.dish.nutrition.protein_g));
  const [carbs, setCarbs] = useState(String(recipe.dish.nutrition.carbs_g));
  const [fat, setFat] = useState(String(recipe.dish.nutrition.fat_g));

  const setIngredient = (idx: number, field: 'quantity' | 'name', value: string) => {
    setIngredients((prev) => prev.map((ing, i) => (i === idx ? { ...ing, [field]: value } : ing)));
  };

  const num = (s: string) => Math.max(0, Math.round(Number(s) || 0));

  const handleSave = () => {
    const cleanedIngredients = ingredients
      .map((i) => ({ ...i, name: i.name.trim(), quantity: i.quantity.trim() || 'q.b.' }))
      .filter((i) => i.name.length > 0);
    const cleanedSteps = steps.map((s) => s.trim()).filter((s) => s.length > 0);

    const dish: Dish = {
      ...recipe.dish,
      name: name.trim() || recipe.dish.name,
      description: description.trim(),
      nutrition: {
        calories: num(calories),
        protein_g: num(protein),
        carbs_g: num(carbs),
        fat_g: num(fat),
      },
      recipe: {
        ...recipe.dish.recipe,
        ingredients: cleanedIngredients,
        steps: cleanedSteps.length > 0 ? cleanedSteps : recipe.dish.recipe.steps,
        chef_notes: chefNotes.trim() || undefined,
      },
    };
    onConfirm(dish);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>✏️ Modifica "{recipe.dish.name}"</h3>
        <p className="modal-subtitle">
          Stai modificando la tua copia personale: dosi, ingredienti, passaggi e note.
        </p>

        <div className="edit-form">
          <label className="edit-label">
            Nome
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} maxLength={120} />
          </label>

          <label className="edit-label">
            Descrizione
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} maxLength={500} />
          </label>

          <div className="edit-section-title">🥕 Ingredienti (dosi e voci)</div>
          {ingredients.map((ing, i) => (
            <div key={i} className="edit-ingredient-row">
              <input
                type="text"
                className="edit-qty"
                value={ing.quantity}
                onChange={(e) => setIngredient(i, 'quantity', e.target.value)}
                placeholder="Dose"
                maxLength={40}
              />
              <input
                type="text"
                className="edit-name"
                value={ing.name}
                onChange={(e) => setIngredient(i, 'name', e.target.value)}
                placeholder="Ingrediente"
                maxLength={80}
              />
              <button
                type="button"
                className="edit-remove-btn"
                onClick={() => setIngredients((prev) => prev.filter((_, idx) => idx !== i))}
                title="Rimuovi ingrediente"
              >
                ×
              </button>
            </div>
          ))}
          <button
            type="button"
            className="edit-add-btn"
            onClick={() => setIngredients((prev) => [...prev, { name: '', quantity: '', category: 'Altro' }])}
          >
            + Aggiungi ingrediente
          </button>

          <div className="edit-section-title">👨‍🍳 Procedimento</div>
          {steps.map((step, i) => (
            <div key={i} className="edit-step-row">
              <span className="edit-step-num">{i + 1}.</span>
              <textarea
                value={step}
                onChange={(e) => setSteps((prev) => prev.map((s, idx) => (idx === i ? e.target.value : s)))}
                rows={2}
                maxLength={600}
              />
              <button
                type="button"
                className="edit-remove-btn"
                onClick={() => setSteps((prev) => prev.filter((_, idx) => idx !== i))}
                title="Rimuovi passaggio"
              >
                ×
              </button>
            </div>
          ))}
          <button type="button" className="edit-add-btn" onClick={() => setSteps((prev) => [...prev, ''])}>
            + Aggiungi passaggio
          </button>

          <label className="edit-label">
            💡 Note dello chef (personali)
            <textarea value={chefNotes} onChange={(e) => setChefNotes(e.target.value)} rows={2} maxLength={500} />
          </label>

          <div className="edit-section-title">🔥 Valori nutrizionali per porzione</div>
          <div className="edit-nutrition-row">
            <label>kcal<input type="number" min={0} value={calories} onChange={(e) => setCalories(e.target.value)} /></label>
            <label>Proteine (g)<input type="number" min={0} value={protein} onChange={(e) => setProtein(e.target.value)} /></label>
            <label>Carboidrati (g)<input type="number" min={0} value={carbs} onChange={(e) => setCarbs(e.target.value)} /></label>
            <label>Grassi (g)<input type="number" min={0} value={fat} onChange={(e) => setFat(e.target.value)} /></label>
          </div>
        </div>

        <div className="modal-actions">
          <button className="modal-btn secondary" onClick={onClose}>Annulla</button>
          <button className="modal-btn primary" onClick={handleSave} disabled={ingredients.every((i) => !i.name.trim())}>
            💾 Salva modifiche
          </button>
        </div>
      </div>
    </div>
  );
};

// ── Componente principale ────────────────────────────────────────
const Ricettario = ({
  recipes,
  loading,
  loadError,
  onDismissLoadError,
  onGoGenerate,
  onUpdate,
  onDelete,
  onLogToDiary,
}: RicettarioProps) => {
  const [search, setSearch] = useState('');
  const [filterMeal, setFilterMeal] = useState<MealType | 'tutti'>('tutti');
  const [filterCuisine, setFilterCuisine] = useState<string>('tutte');
  const [filterStatus, setFilterStatus] = useState<StatusFilter>('tutte');
  const [sort, setSort] = useState<SortOption>('recenti');

  const [actionError, setActionError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [cookedModal, setCookedModal] = useState<SavedRecipe | null>(null);
  const [noteModal, setNoteModal] = useState<SavedRecipe | null>(null);
  const [editModal, setEditModal] = useState<SavedRecipe | null>(null);

  const cuisines = useMemo(() => {
    const set = new Set((recipes ?? []).map((r) => r.dish.cuisine.toLowerCase()));
    return Array.from(set).sort();
  }, [recipes]);

  const visible = useMemo(() => {
    let list = recipes ?? [];
    const q = search.trim().toLowerCase();
    if (q) list = list.filter((r) => r.dish.name.toLowerCase().includes(q));
    if (filterMeal !== 'tutti') list = list.filter((r) => r.source?.meal_type === filterMeal);
    if (filterCuisine !== 'tutte') list = list.filter((r) => r.dish.cuisine.toLowerCase() === filterCuisine);
    if (filterStatus === 'top') list = list.filter((r) => (r.rating ?? 0) >= 4);
    if (filterStatus === 'da_valutare') list = list.filter((r) => r.rating === null);
    if (filterStatus === 'cucinate') list = list.filter((r) => r.cooked_count > 0);

    return [...list].sort((a, b) => {
      if (sort === 'rating') return (b.rating ?? 0) - (a.rating ?? 0);
      if (sort === 'kcal') return a.dish.nutrition.calories - b.dish.nutrition.calories;
      return b.saved_at.localeCompare(a.saved_at);
    });
  }, [recipes, search, filterMeal, filterCuisine, filterStatus, sort]);

  // Applica una patch gestendo spinner ed errori
  const applyPatch = async (recipe: SavedRecipe, patch: RecipePatch) => {
    setActionError(null);
    setBusyId(recipe.recipe_id);
    try {
      await onUpdate(recipe.recipe_id, patch);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Errore nell'aggiornamento della ricetta");
    } finally {
      setBusyId(null);
    }
  };

  const handleRate = (recipe: SavedRecipe, stars: number) => {
    void applyPatch(recipe, { rating: stars });
  };

  const handleCooked = (recipe: SavedRecipe, stars: number, note: string, diaryMeal: MealType | null) => {
    setCookedModal(null);
    const patch: RecipePatch = { cooked_count: recipe.cooked_count + 1 };
    if (stars > 0) patch.rating = stars;
    if (note.trim()) {
      patch.notes = [...recipe.notes, { date: new Date().toISOString(), text: note.trim() }];
    }
    void applyPatch(recipe, patch);
    if (diaryMeal) {
      onLogToDiary(recipe, diaryMeal).catch((err) =>
        setActionError(err instanceof Error ? err.message : 'Errore nella registrazione sul diario')
      );
    }
  };

  const handleAddNote = (recipe: SavedRecipe, text: string) => {
    setNoteModal(null);
    void applyPatch(recipe, { notes: [...recipe.notes, { date: new Date().toISOString(), text }] });
  };

  const handleEdit = (recipe: SavedRecipe, dish: Dish) => {
    setEditModal(null);
    void applyPatch(recipe, { dish, is_customized: true });
  };

  const hasRecipes = (recipes?.length ?? 0) > 0;

  return (
    <div className="ricettario">
      <div className="menu-header">
        <h2>📖 Il tuo ricettario</h2>
        <p>Le ricette che hai salvato: valuta, modifica, annota</p>
      </div>

      {(loadError || actionError) && (
        <div className="error-banner">
          ❌ {loadError ?? actionError}
          <button onClick={() => (loadError ? onDismissLoadError() : setActionError(null))}>×</button>
        </div>
      )}

      {loading && (
        <div className="ricettario-status">
          <span className="spinner"></span>
          <p>Caricamento del ricettario…</p>
        </div>
      )}

      {!loading && recipes !== null && !hasRecipes && (
        <div className="ricettario-empty">
          <p className="ricettario-empty-emoji">🍳</p>
          <h3>Il tuo ricettario è vuoto</h3>
          <p>Genera un menù e salva i piatti che ti piacciono col bottone 💾: li ritroverai qui.</p>
          <button className="action-button primary" onClick={onGoGenerate}>✨ Genera un menù</button>
        </div>
      )}

      {hasRecipes && (
        <div className="ricettario-toolbar">
          <input
            type="search"
            className="ricettario-search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="🔍 Cerca per nome..."
          />
          <select value={filterMeal} onChange={(e) => setFilterMeal(e.target.value as MealType | 'tutti')}>
            <option value="tutti">Tutti i pasti</option>
            {(Object.keys(MEAL_LABELS) as MealType[]).map((m) => (
              <option key={m} value={m}>{MEAL_EMOJI[m]} {MEAL_LABELS[m]}</option>
            ))}
          </select>
          <select value={filterCuisine} onChange={(e) => setFilterCuisine(e.target.value)}>
            <option value="tutte">Tutte le cucine</option>
            {cuisines.map((c) => (
              <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
            ))}
          </select>
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value as StatusFilter)}>
            <option value="tutte">Tutte</option>
            <option value="top">★ 4 o più</option>
            <option value="da_valutare">Da valutare</option>
            <option value="cucinate">Già cucinate</option>
          </select>
          <select value={sort} onChange={(e) => setSort(e.target.value as SortOption)}>
            <option value="recenti">Più recenti</option>
            <option value="rating">Migliori</option>
            <option value="kcal">Meno caloriche</option>
          </select>
        </div>
      )}

      {hasRecipes && visible.length === 0 && (
        <div className="ricettario-empty">
          <p>Nessuna ricetta corrisponde alla ricerca o ai filtri.</p>
        </div>
      )}

      <div className="meals-container">
        {visible.map((recipe) => {
          const busy = busyId === recipe.recipe_id;
          return (
            <div key={recipe.recipe_id} className={`dish-card saved-recipe-card ${busy ? 'regenerating' : ''}`}>
              <div className="dish-header">
                <div className="dish-title">
                  <span className="role-badge">{recipe.dish.role}</span>
                  <h4>{recipe.dish.name}</h4>
                </div>
                <div className="dish-header-actions">
                  <span className="cuisine-badge">{recipe.dish.cuisine}</span>
                  <span className="kcal-badge">🔥 {recipe.dish.nutrition.calories} kcal</span>
                  <button
                    className="regenerate-btn"
                    onClick={() => setEditModal(recipe)}
                    disabled={busy}
                    title="Modifica la tua copia (dosi, ingredienti, passaggi)"
                  >
                    ✏️
                  </button>
                  <button
                    className="regenerate-btn delete"
                    onClick={() => void onDelete(recipe)}
                    disabled={busy}
                    title="Elimina dal ricettario"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              <p className="dish-description">{recipe.dish.description}</p>

              <div className="dish-meta recipe-meta-row">
                <StarRating value={recipe.rating} onChange={(v) => handleRate(recipe, v)} disabled={busy} />
                {recipe.cooked_count > 0 && (
                  <span title="Quante volte l'hai cucinata">👨‍🍳 ×{recipe.cooked_count}</span>
                )}
                {recipe.source && (
                  <span>{MEAL_EMOJI[recipe.source.meal_type]} {MEAL_LABELS[recipe.source.meal_type]}</span>
                )}
                <span>💾 {formatDate(recipe.saved_at)}</span>
                {recipe.is_customized && <span className="prep-ahead">✏️ Modificata</span>}
              </div>

              <div className="recipe-actions">
                <button className="action-button" onClick={() => setCookedModal(recipe)} disabled={busy}>
                  ✅ L'ho cucinata!
                </button>
                <button className="action-button" onClick={() => setNoteModal(recipe)} disabled={busy}>
                  📝 Nuova nota
                </button>
              </div>

              <RecipeDetails dish={recipe.dish} />

              {recipe.notes.length > 0 && (
                <details className="recipe-details recipe-notes">
                  <summary>📝 Note ({recipe.notes.length})</summary>
                  <ul className="recipe-notes-list">
                    {[...recipe.notes].reverse().map((note, i) => (
                      <li key={i}>
                        <span className="recipe-note-date">{formatDate(note.date)}</span> — {note.text}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          );
        })}
      </div>

      {cookedModal && (
        <CookedModal
          recipe={cookedModal}
          onClose={() => setCookedModal(null)}
          onConfirm={(stars, note, diaryMeal) => handleCooked(cookedModal, stars, note, diaryMeal)}
        />
      )}
      {noteModal && (
        <NoteModal
          recipe={noteModal}
          onClose={() => setNoteModal(null)}
          onConfirm={(text) => handleAddNote(noteModal, text)}
        />
      )}
      {editModal && (
        <EditModal
          recipe={editModal}
          onClose={() => setEditModal(null)}
          onConfirm={(dish) => handleEdit(editModal, dish)}
        />
      )}
    </div>
  );
};

export default Ricettario;
