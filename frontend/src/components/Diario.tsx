// ═══════════════════════════════════════════════════════════════
// 📔 DIARIO ALIMENTARE (Fase 3)
//
// - Vista giorno: entry raggruppate per pasto, totali kcal/macro
//   client-side, navigazione tra i giorni
// - Aggiunta/modifica entry manuale, con stima kcal via Gemini
//   dalla descrizione testuale
// - Vista mese: totale kcal per giorno + media (≤31 letture)
// - Budget kcal giornaliero opzionale (users/{uid}/settings/prefs)
//
// Le entry con source 'ricettario' arrivano dal flusso
// "L'ho cucinata!" del Ricettario; quelle 'foto' dalla Fase 4.
// ═══════════════════════════════════════════════════════════════

import { useEffect, useMemo, useState } from 'react';
import { MEAL_LABELS, MEAL_ORDER, estimateNutritionFromText } from '../services/aiService';
import {
  addDiaryEntry,
  deleteDiaryEntry,
  getDiaryDay,
  getDiaryMonth,
  getPrefs,
  savePrefs,
  toISODate,
  updateDiaryEntry,
} from '../services/diaryService';
import type { DiaryDay, DiaryEntry, MealType, NutritionInfo, UserPrefs } from '../types';

interface DiarioProps {
  uid: string;
  selectedModel: string;
}

const MEAL_EMOJI: Record<MealType, string> = {
  colazione: '🥐',
  pranzo: '🍝',
  cena: '🍽️',
  spuntino: '🍎',
};

const SOURCE_ICON: Record<DiaryEntry['source'], string> = {
  manuale: '✍️',
  ricettario: '📖',
  foto: '📸',
};

const formatDayLong = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString('it-IT', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

const formatDayShort = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString('it-IT', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });

const formatMonth = (month: string) =>
  new Date(`${month}-01T12:00:00`).toLocaleDateString('it-IT', { month: 'long', year: 'numeric' });

const shiftDate = (iso: string, days: number): string => {
  const d = new Date(`${iso}T12:00:00`);
  d.setDate(d.getDate() + days);
  return toISODate(d);
};

const shiftMonth = (month: string, delta: number): string => {
  const d = new Date(`${month}-01T12:00:00`);
  d.setMonth(d.getMonth() + delta);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
};

const dayCalories = (day: DiaryDay | null): number =>
  (day?.entries ?? []).reduce((sum, e) => sum + (e.nutrition?.calories ?? 0), 0);

const dayMacros = (day: DiaryDay | null): NutritionInfo =>
  (day?.entries ?? []).reduce(
    (acc, e) => ({
      calories: acc.calories + (e.nutrition?.calories ?? 0),
      protein_g: acc.protein_g + (e.nutrition?.protein_g ?? 0),
      carbs_g: acc.carbs_g + (e.nutrition?.carbs_g ?? 0),
      fat_g: acc.fat_g + (e.nutrition?.fat_g ?? 0),
    }),
    { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 }
  );

// ── Modal entry (nuova o modifica) ───────────────────────────────
const EntryModal = ({
  initial,
  selectedModel,
  onClose,
  onSave,
}: {
  initial: DiaryEntry | null;
  selectedModel: string;
  onClose: () => void;
  onSave: (data: {
    meal_type: MealType;
    description: string;
    nutrition: NutritionInfo | null;
  }) => void;
}) => {
  const [mealType, setMealType] = useState<MealType>(initial?.meal_type ?? 'pranzo');
  const [description, setDescription] = useState(initial?.description ?? '');
  const [calories, setCalories] = useState(initial?.nutrition ? String(initial.nutrition.calories) : '');
  const [protein, setProtein] = useState(initial?.nutrition ? String(initial.nutrition.protein_g) : '');
  const [carbs, setCarbs] = useState(initial?.nutrition ? String(initial.nutrition.carbs_g) : '');
  const [fat, setFat] = useState(initial?.nutrition ? String(initial.nutrition.fat_g) : '');
  const [estimating, setEstimating] = useState(false);
  const [estimateNote, setEstimateNote] = useState<string | null>(null);
  const [estimateError, setEstimateError] = useState<string | null>(null);

  const handleEstimate = async () => {
    if (!description.trim() || estimating) return;
    setEstimating(true);
    setEstimateError(null);
    setEstimateNote(null);
    try {
      const est = await estimateNutritionFromText(description, selectedModel);
      setCalories(String(est.nutrition.calories));
      setProtein(String(est.nutrition.protein_g));
      setCarbs(String(est.nutrition.carbs_g));
      setFat(String(est.nutrition.fat_g));
      setEstimateNote(`Stima AI (confidenza ${est.confidence}) — ${est.assumed_portion}. Correggi pure i valori.`);
    } catch (err) {
      setEstimateError(err instanceof Error ? err.message : 'Errore nella stima');
    } finally {
      setEstimating(false);
    }
  };

  const handleSave = () => {
    if (!description.trim()) return;
    const num = (s: string) => Math.max(0, Math.round(Number(s) || 0));
    const hasNutrition = calories.trim() !== '';
    onSave({
      meal_type: mealType,
      description: description.trim(),
      nutrition: hasNutrition
        ? { calories: num(calories), protein_g: num(protein), carbs_g: num(carbs), fat_g: num(fat) }
        : null,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>{initial ? '✏️ Modifica voce' : '➕ Aggiungi al diario'}</h3>

        <div className="edit-form">
          <label className="edit-label">
            Pasto
            <select value={mealType} onChange={(e) => setMealType(e.target.value as MealType)}>
              {MEAL_ORDER.map((m) => (
                <option key={m} value={m}>{MEAL_EMOJI[m]} {MEAL_LABELS[m]}</option>
              ))}
            </select>
          </label>

          <label className="edit-label">
            Cosa hai mangiato?
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Es: un piatto di lasagne e un'insalata mista"
              rows={2}
              maxLength={300}
              autoFocus={!initial}
            />
          </label>

          <button
            type="button"
            className="action-button estimate-btn"
            onClick={() => void handleEstimate()}
            disabled={!description.trim() || estimating}
          >
            {estimating ? 'Stimo…' : '✨ Stima kcal con AI'}
          </button>
          {estimateNote && <p className="estimate-note">💡 {estimateNote}</p>}
          {estimateError && <p className="estimate-note error">❌ {estimateError}</p>}

          <div className="edit-section-title">🔥 Valori nutrizionali (opzionali)</div>
          <div className="edit-nutrition-row">
            <label>kcal<input type="number" min={0} value={calories} onChange={(e) => setCalories(e.target.value)} placeholder="—" /></label>
            <label>Proteine (g)<input type="number" min={0} value={protein} onChange={(e) => setProtein(e.target.value)} placeholder="—" /></label>
            <label>Carboidrati (g)<input type="number" min={0} value={carbs} onChange={(e) => setCarbs(e.target.value)} placeholder="—" /></label>
            <label>Grassi (g)<input type="number" min={0} value={fat} onChange={(e) => setFat(e.target.value)} placeholder="—" /></label>
          </div>
        </div>

        <div className="modal-actions">
          <button className="modal-btn secondary" onClick={onClose}>Annulla</button>
          <button className="modal-btn primary" onClick={handleSave} disabled={!description.trim()}>
            💾 Salva
          </button>
        </div>
      </div>
    </div>
  );
};

// ── Componente principale ────────────────────────────────────────
const Diario = ({ uid, selectedModel }: DiarioProps) => {
  const today = toISODate(new Date());
  const [date, setDate] = useState(today);
  const [day, setDay] = useState<DiaryDay | null>(null);
  // loading derivato: il giorno mostrato è quello richiesto?
  const [loadedDate, setLoadedDate] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [monthMode, setMonthMode] = useState(false);
  const [month, setMonth] = useState(today.slice(0, 7));
  const [monthDays, setMonthDays] = useState<DiaryDay[] | null>(null);
  const [loadedMonth, setLoadedMonth] = useState<string | null>(null);

  const loading = loadedDate !== date;
  const monthLoading = loadedMonth !== month;

  const [prefs, setPrefs] = useState<UserPrefs | null>(null);
  const [budgetInput, setBudgetInput] = useState('');
  const [entryModal, setEntryModal] = useState<{ initial: DiaryEntry | null } | null>(null);

  // Preferenze (budget kcal): caricate una volta
  useEffect(() => {
    let cancelled = false;
    getPrefs(uid)
      .then((p) => {
        if (cancelled) return;
        setPrefs(p);
        setBudgetInput(p.daily_kcal_budget ? String(p.daily_kcal_budget) : '');
      })
      .catch(() => {
        if (!cancelled) setPrefs({ daily_kcal_budget: null });
      });
    return () => { cancelled = true; };
  }, [uid]);

  // Giorno corrente
  useEffect(() => {
    if (monthMode) return;
    let cancelled = false;
    getDiaryDay(uid, date)
      .then((d) => {
        if (cancelled) return;
        setDay(d);
        setError(null);
        setLoadedDate(date);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Errore nel caricamento del diario');
        setDay(null);
        setLoadedDate(date);
      });
    return () => { cancelled = true; };
  }, [uid, date, monthMode]);

  // Mese (solo in vista mese; si aggiorna anche rientrando nella vista)
  useEffect(() => {
    if (!monthMode) return;
    let cancelled = false;
    getDiaryMonth(uid, month)
      .then((days) => {
        if (cancelled) return;
        setMonthDays(days);
        setError(null);
        setLoadedMonth(month);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Errore nel caricamento del mese');
        setMonthDays([]);
        setLoadedMonth(month);
      });
    return () => { cancelled = true; };
  }, [uid, month, monthMode]);

  const budget = prefs?.daily_kcal_budget ?? null;
  const totals = useMemo(() => dayMacros(day), [day]);
  const overBudget = budget !== null && totals.calories > budget;

  const handleSaveBudget = () => {
    const parsed = parseInt(budgetInput, 10);
    const newPrefs: UserPrefs = { daily_kcal_budget: parsed > 0 ? parsed : null };
    setPrefs(newPrefs);
    savePrefs(uid, newPrefs).catch((err) =>
      setError(err instanceof Error ? err.message : 'Errore nel salvataggio del budget')
    );
  };

  const handleSaveEntry = (data: { meal_type: MealType; description: string; nutrition: NutritionInfo | null }) => {
    const initial = entryModal?.initial ?? null;
    setEntryModal(null);
    const entry: DiaryEntry = {
      entry_id: initial?.entry_id ?? crypto.randomUUID(),
      meal_type: data.meal_type,
      description: data.description,
      nutrition: data.nutrition,
      recipe_id: initial?.recipe_id ?? null,
      source: initial?.source ?? 'manuale',
      logged_at: initial?.logged_at ?? new Date().toISOString(),
    };
    const op = initial ? updateDiaryEntry(uid, date, entry) : addDiaryEntry(uid, date, entry);
    op.then(setDay).catch((err) =>
      setError(err instanceof Error ? err.message : 'Errore nel salvataggio della voce')
    );
  };

  const handleDeleteEntry = (entry: DiaryEntry) => {
    if (!window.confirm(`Eliminare "${entry.description}" dal diario?`)) return;
    deleteDiaryEntry(uid, date, entry.entry_id)
      .then(setDay)
      .catch((err) => setError(err instanceof Error ? err.message : "Errore nell'eliminazione della voce"));
  };

  // ── Vista mese ──────────────────────────────────────────────────
  if (monthMode) {
    const monthTotal = (monthDays ?? []).reduce((sum, d) => sum + dayCalories(d), 0);
    const daysWithData = (monthDays ?? []).length;

    return (
      <div className="diario">
        <div className="menu-header">
          <h2>📔 Diario alimentare</h2>
          <p>Riepilogo del mese</p>
        </div>

        {error && (
          <div className="error-banner">❌ {error}<button onClick={() => setError(null)}>×</button></div>
        )}

        <div className="diario-nav">
          <button className="action-button" onClick={() => setMonth((m) => shiftMonth(m, -1))}>‹</button>
          <span className="diario-current-date">{formatMonth(month)}</span>
          <button
            className="action-button"
            onClick={() => setMonth((m) => shiftMonth(m, 1))}
            disabled={month >= today.slice(0, 7)}
          >›</button>
          <button className="action-button" onClick={() => setMonthMode(false)}>📅 Vista giorno</button>
        </div>

        {monthLoading && (
          <div className="ricettario-status"><span className="spinner"></span><p>Caricamento…</p></div>
        )}

        {!monthLoading && monthDays !== null && (
          daysWithData === 0 ? (
            <div className="ricettario-empty">
              <p className="ricettario-empty-emoji">📔</p>
              <p>Nessuna voce registrata in questo mese.</p>
            </div>
          ) : (
            <>
              <div className="month-summary">
                📊 {daysWithData} giorn{daysWithData === 1 ? 'o' : 'i'} registrat{daysWithData === 1 ? 'o' : 'i'} —
                media <strong>~{Math.round(monthTotal / daysWithData)} kcal/giorno</strong>
              </div>
              <div className="month-list">
                {monthDays.map((d) => {
                  const kcal = dayCalories(d);
                  const over = budget !== null && kcal > budget;
                  return (
                    <button
                      key={d.date}
                      className="month-day-row"
                      onClick={() => { setDate(d.date); setMonthMode(false); }}
                      title="Apri il giorno"
                    >
                      <span className="month-day-date">{formatDayShort(d.date)}</span>
                      <span className="month-day-entries">{d.entries.length} voc{d.entries.length === 1 ? 'e' : 'i'}</span>
                      <span className={`month-day-kcal ${over ? 'over' : ''}`}>🔥 {kcal} kcal</span>
                    </button>
                  );
                })}
              </div>
            </>
          )
        )}
      </div>
    );
  }

  // ── Vista giorno ────────────────────────────────────────────────
  const mealsWithEntries = MEAL_ORDER.map((m) => ({
    meal: m,
    entries: (day?.entries ?? []).filter((e) => e.meal_type === m),
  })).filter((g) => g.entries.length > 0);

  return (
    <div className="diario">
      <div className="menu-header">
        <h2>📔 Diario alimentare</h2>
        <p>Segna cosa hai mangiato, giorno per giorno</p>
      </div>

      {error && (
        <div className="error-banner">❌ {error}<button onClick={() => setError(null)}>×</button></div>
      )}

      <div className="diario-nav">
        <button className="action-button" onClick={() => setDate((d) => shiftDate(d, -1))}>‹</button>
        <input
          type="date"
          className="diario-date-input"
          value={date}
          max={today}
          onChange={(e) => e.target.value && setDate(e.target.value)}
        />
        <button className="action-button" onClick={() => setDate((d) => shiftDate(d, 1))} disabled={date >= today}>›</button>
        {date !== today && (
          <button className="action-button" onClick={() => setDate(today)}>Oggi</button>
        )}
        <button className="action-button" onClick={() => { setMonth(date.slice(0, 7)); setMonthMode(true); }}>
          📊 Vista mese
        </button>
      </div>

      <p className="diario-day-title">{formatDayLong(date)}</p>

      <div className={`kcal-summary ${overBudget ? 'over' : ''}`}>
        🔥 Totale: <strong>~{totals.calories} kcal</strong>
        {budget !== null && (
          <span className="kcal-budget">
            {overBudget ? ` — oltre il budget di ${budget} kcal!` : ` — entro il budget di ${budget} kcal ✓`}
          </span>
        )}
        {totals.calories > 0 && (
          <span className="diario-macros"> · 🥩 P {totals.protein_g}g · 🍞 C {totals.carbs_g}g · 🧈 G {totals.fat_g}g</span>
        )}
      </div>

      <div className="diario-budget-row">
        🎯 Budget giornaliero:
        <input
          type="number"
          className="calorie-input small"
          value={budgetInput}
          onChange={(e) => setBudgetInput(e.target.value)}
          placeholder="—"
          min={0}
          step={50}
        />
        kcal
        <button
          className="action-button"
          onClick={handleSaveBudget}
          disabled={prefs === null || budgetInput === (prefs?.daily_kcal_budget ? String(prefs.daily_kcal_budget) : '')}
        >
          Salva
        </button>
      </div>

      {loading ? (
        <div className="ricettario-status"><span className="spinner"></span><p>Caricamento…</p></div>
      ) : mealsWithEntries.length === 0 ? (
        <div className="ricettario-empty">
          <p className="ricettario-empty-emoji">🍽️</p>
          <p>Nessuna voce per questo giorno.</p>
        </div>
      ) : (
        <div className="meals-container">
          {mealsWithEntries.map(({ meal, entries }) => (
            <div key={meal} className="meal-section">
              <div className="meal-title">
                <h3>{MEAL_EMOJI[meal]} {MEAL_LABELS[meal]}</h3>
                <span className="meal-kcal">
                  ~{entries.reduce((s, e) => s + (e.nutrition?.calories ?? 0), 0)} kcal
                </span>
              </div>
              {entries.map((entry) => (
                <div key={entry.entry_id} className="diary-entry">
                  <span className="diary-entry-source" title={`Origine: ${entry.source}`}>
                    {SOURCE_ICON[entry.source]}
                  </span>
                  <div className="diary-entry-body">
                    <span className="diary-entry-desc">{entry.description}</span>
                    {entry.nutrition && (
                      <span className="diary-entry-macros">
                        🥩 {entry.nutrition.protein_g}g · 🍞 {entry.nutrition.carbs_g}g · 🧈 {entry.nutrition.fat_g}g
                      </span>
                    )}
                  </div>
                  <span className="kcal-badge">
                    {entry.nutrition ? `🔥 ${entry.nutrition.calories} kcal` : '— kcal'}
                  </span>
                  <button
                    className="regenerate-btn"
                    onClick={() => setEntryModal({ initial: entry })}
                    title="Modifica voce"
                  >✏️</button>
                  <button
                    className="regenerate-btn delete"
                    onClick={() => handleDeleteEntry(entry)}
                    title="Elimina voce"
                  >🗑️</button>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      <div className="diario-add-row">
        <button className="action-button primary" onClick={() => setEntryModal({ initial: null })}>
          ➕ Aggiungi voce
        </button>
      </div>

      {entryModal && (
        <EntryModal
          initial={entryModal.initial}
          selectedModel={selectedModel}
          onClose={() => setEntryModal(null)}
          onSave={handleSaveEntry}
        />
      )}
    </div>
  );
};

export default Diario;
