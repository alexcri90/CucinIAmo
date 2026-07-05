import { useState } from 'react';
import { signOut, type User } from 'firebase/auth';
import { firebase } from './firebase';
import {
  generateMenu,
  regenerateCourse,
  computeShoppingList,
  AVAILABLE_MODELS,
  DEFAULT_MODEL,
} from './services/aiService';
import type { UserInput, MenuOutput, DietaryRestriction, DifficultyLevel, BudgetLevel, Ingredient, CourseType } from './types';
import './App.css';

const MODEL_STORAGE_KEY = 'christmas-menu-model';

// Stato per la rigenerazione di una portata
interface RegeneratingState {
  courseType: CourseType;
  courseIndex: number;
}

// Modal per feedback opzionale durante la rigenerazione
const RegenerateModal = ({
  isOpen,
  onClose,
  onConfirm,
  courseName
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (feedback: string) => void;
  courseType: string;
  courseName: string;
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
        <h3>🔄 Rigenera "{courseName}"</h3>
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

// Import delle immagini gingerbread
import onePan from './assets/gingerbread/one_pan.png';
import twoPan from './assets/gingerbread/two_pan.png';
import threePan from './assets/gingerbread/three_pan.png';
import fourPan from './assets/gingerbread/four_pan.png';

// Componente Pan di Zenzero dinamico
const GingerbreadGuests = ({ count }: { count: number }) => {
  // Selezione dinamica dell'icona basata sul numero di ospiti
  const getGingerbreadImage = () => {
    if (count === 1) return onePan;
    if (count >= 2 && count <= 3) return twoPan;
    if (count >= 4 && count <= 5) return threePan;
    return fourPan; // 6 o più
  };

  const isCrowded = count >= 6;

  return (
    <div className={`gingerbread-container ${isCrowded ? 'crowded' : ''}`}>
      <img 
        src={getGingerbreadImage()} 
        alt={`${count} ospite${count !== 1 ? 'i' : ''}`}
        className={`gingerbread-image ${isCrowded ? 'shake' : 'sway'}`}
      />
    </div>
  );
};

const CUISINES = [
  'italiana', 'francese', 'spagnola', 'tedesca', 'inglese',
  'americana', 'polacca', 'greca', 'scandinava'
];

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
  
  // Stati per rigenerazione portate
  const [regenerating, setRegenerating] = useState<RegeneratingState | null>(null);
  const [regenerateModal, setRegenerateModal] = useState<{
    isOpen: boolean;
    courseType: CourseType;
    courseIndex: number;
    courseName: string;
  }>({ isOpen: false, courseType: 'antipasti', courseIndex: 0, courseName: '' });
  const [justRegenerated, setJustRegenerated] = useState<string | null>(null);

  const [formData, setFormData] = useState<UserInput>({
    num_guests: 8,
    cuisines: ['italiana'],
    preferred_ingredients: [],
    avoided_ingredients: [],
    dietary_restrictions: [],
    difficulty_level: 'medio',
    budget_level: 'medio',
  });

  const [ingredientInput, setIngredientInput] = useState('');
  const [avoidedInput, setAvoidedInput] = useState('');

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const result = await generateMenu(formData, selectedModel);
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

  const toggleDietary = (restriction: DietaryRestriction) => {
    setFormData(prev => ({
      ...prev,
      dietary_restrictions: prev.dietary_restrictions.includes(restriction)
        ? prev.dietary_restrictions.filter(r => r !== restriction)
        : [...prev.dietary_restrictions, restriction]
    }));
  };

  // Apri modal per rigenerazione
  const openRegenerateModal = (courseType: CourseType, courseIndex: number, courseName: string) => {
    setRegenerateModal({
      isOpen: true,
      courseType,
      courseIndex,
      courseName
    });
  };

  // Chiudi modal
  const closeRegenerateModal = () => {
    setRegenerateModal(prev => ({ ...prev, isOpen: false }));
  };

  // Rigenera una portata (con o senza feedback) e aggiorna la lista spesa
  const performRegenerate = async (courseType: CourseType, courseIndex: number, feedback: string) => {
    if (!menu) return;
    setRegenerating({ courseType, courseIndex });
    setError(null);

    try {
      const newCourse = await regenerateCourse(menu, courseType, courseIndex, feedback, selectedModel);

      setMenu(prev => {
        if (!prev) return prev;

        const updatedCourses = { ...prev.courses };
        const courseArray = [...updatedCourses[courseType]];
        courseArray[courseIndex] = newCourse;
        updatedCourses[courseType] = courseArray;

        return {
          ...prev,
          courses: updatedCourses,
          // Ricalcola la lista spesa dagli ingredienti aggiornati;
          // la timeline resta quella del menù originale
          shopping_list: computeShoppingList(updatedCourses),
        };
      });

      // Effetto flash sulla portata rigenerata
      const courseId = newCourse.course_id || `${courseType}-${courseIndex}`;
      setJustRegenerated(courseId);
      setTimeout(() => setJustRegenerated(null), 2000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nella rigenerazione della portata');
    } finally {
      setRegenerating(null);
    }
  };

  // Rigenerazione con feedback dal modal
  const handleRegenerate = (feedback: string) => {
    const { courseType, courseIndex } = regenerateModal;
    closeRegenerateModal();
    void performRegenerate(courseType, courseIndex, feedback);
  };

  // Rigenerazione rapida senza modal (click diretto)
  const handleQuickRegenerate = (courseType: CourseType, courseIndex: number) => {
    void performRegenerate(courseType, courseIndex, '');
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
    const courseNames: Record<string, string> = {
      antipasti: '🥗 Antipasti',
      primo: '🍝 Primo',
      secondo: '🍖 Secondo',
      contorno: '🥬 Contorno',
      dessert: '🍰 Dessert'
    };

    let coursesHTML = '';
    for (const [type, courses] of Object.entries(menuData.courses)) {
      if (!courses || !Array.isArray(courses)) continue;
      for (const course of courses) {
        coursesHTML += `
          <div class="course">
            <h3>${courseNames[type] || type} - ${course.name}</h3>
            <p><em>${course.description}</em></p>
            <p><strong>Origine:</strong> ${course.cuisine}</p>
            <p><strong>Tempo:</strong> ${course.recipe.prep_time_minutes} min prep + ${course.recipe.cook_time_minutes} min cottura</p>
            <h4>Ingredienti:</h4>
            <ul>
              ${course.recipe.ingredients.map((i: { quantity: string; name: string }) => `<li>${i.quantity} ${i.name}</li>`).join('')}
            </ul>
            <h4>Procedimento:</h4>
            <ol>
              ${course.recipe.steps.map((s: string) => `<li>${s}</li>`).join('')}
            </ol>
            ${course.recipe.chef_notes ? `<p><strong>Note dello Chef:</strong> ${course.recipe.chef_notes}</p>` : ''}
          </div>
        `;
      }
    }

    return `<!DOCTYPE html><html><head><title>Menu di Natale</title><style>body{font-family:Georgia,serif;max-width:800px;margin:0 auto;padding:20px}h1{text-align:center;color:#c41e3a}h3{color:#c41e3a}.course{margin-bottom:30px;page-break-inside:avoid}</style></head><body><h1>🎄 Menu di Natale 🎄</h1><p style="text-align:center">Per ${menuData.input.num_guests} ospiti</p>${coursesHTML}</body></html>`;
  };

  return (
    <div className="app">
      <header className="header">
        <div className="user-chip">
          {user.photoURL && <img src={user.photoURL} alt="" className="user-avatar" referrerPolicy="no-referrer" />}
          <span className="user-email">{user.email}</span>
          <button type="button" className="logout-btn" onClick={handleSignOut} title="Esci">
            Esci
          </button>
        </div>
        <h1>🎄 Christmas Menu Generator 🎄</h1>
        <p>Genera il tuo menù natalizio personalizzato con l'AI</p>
      </header>

      <main className="main-content">
        {!menu ? (
          <form onSubmit={handleSubmit} className="input-form">
            <div className="form-section guests-section">
              <h2>🍪 Quanti siete a tavola?</h2>
              <GingerbreadGuests count={formData.num_guests} />
              <div className="guest-counter">
                <button 
                  type="button" 
                  className="bounce-btn"
                  onClick={() => setFormData(prev => ({ ...prev, num_guests: Math.max(1, prev.num_guests - 1) }))}
                >−</button>
                <div className="guest-number-wrapper">
                  <span className="guest-number">{formData.num_guests}</span>
                  <span className="guest-label">ospiti</span>
                </div>
                <button 
                  type="button" 
                  className="bounce-btn"
                  onClick={() => setFormData(prev => ({ ...prev, num_guests: Math.min(50, prev.num_guests + 1) }))}
                >+</button>
              </div>
            </div>

            <div className="form-section">
              <h2>🌍 Che sapori volete portare in tavola?</h2>
              <p className="section-hint">Seleziona una o più tradizioni culinarie</p>
              <div className="chip-container centered">
                {CUISINES.map(cuisine => (
                  <button
                    key={cuisine}
                    type="button"
                    className={`chip bounce-btn ${formData.cuisines.includes(cuisine) ? 'selected' : ''}`}
                    onClick={() => toggleCuisine(cuisine)}
                  >
                    {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)}
                  </button>
                ))}
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
                    placeholder="Es: salmone, tartufo..."
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
              <h2>🥗 Esigenze speciali?</h2>
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

            <div className="form-section options-dual">
              <div className="option-column">
                <h2>👨‍🍳 Quanto volete impegnarvi?</h2>
                <div className="radio-group vertical">
                  {(['facile', 'medio', 'avanzato'] as DifficultyLevel[]).map(level => (
                    <label key={level} className={`bounce-btn ${formData.difficulty_level === level ? 'selected' : ''}`}>
                      <input
                        type="radio"
                        name="difficulty"
                        value={level}
                        checked={formData.difficulty_level === level}
                        onChange={(e) => setFormData(prev => ({ ...prev, difficulty_level: e.target.value as DifficultyLevel }))}
                      />
                      {level === 'facile' ? '😊 Relax, voglio godermi la festa' : level === 'medio' ? '👨‍🍳 Mi piace cucinare' : '🔥 Sfidami, chef!'}
                    </label>
                  ))}
                </div>
              </div>
              <div className="option-column">
                <h2>💰 Quanto volete spendere?</h2>
                <div className="radio-group vertical">
                  {(['economico', 'medio', 'premium'] as BudgetLevel[]).map(level => (
                    <label key={level} className={`bounce-btn ${formData.budget_level === level ? 'selected' : ''}`}>
                      <input
                        type="radio"
                        name="budget"
                        value={level}
                        checked={formData.budget_level === level}
                        onChange={(e) => setFormData(prev => ({ ...prev, budget_level: e.target.value as BudgetLevel }))}
                      />
                      {level === 'economico' ? '🪙 Budget friendly' : level === 'medio' ? '💵 Il giusto' : '💎 Si festeggia!'}
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

            <button type="submit" className="submit-button bounce-btn" disabled={isLoading || formData.cuisines.length === 0}>
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  <span>Sto creando la magia... 🎅</span>
                </>
              ) : (
                <>
                  <span className="btn-icon">🎄</span>
                  <span>Crea il nostro Menù!</span>
                  <span className="btn-icon">🎄</span>
                </>
              )}
            </button>
          </form>
        ) : (
          <div className="menu-result">
            <div className="menu-header">
              <h2>🎄 Il Tuo Menù di Natale 🎄</h2>
              <p>Per {menu.input.num_guests} ospiti</p>
              <div className="menu-actions">
                <button onClick={() => setMenu(null)} className="action-button">← Nuovo Menù</button>
                <button onClick={downloadPDF} className="action-button primary">📄 Stampa PDF</button>
              </div>
            </div>

            <div className="tabs">
              <button className={activeTab === 'menu' ? 'active' : ''} onClick={() => setActiveTab('menu')}>📋 Menù</button>
              <button className={activeTab === 'shopping' ? 'active' : ''} onClick={() => setActiveTab('shopping')}>🛒 Lista Spesa</button>
              <button className={activeTab === 'timeline' ? 'active' : ''} onClick={() => setActiveTab('timeline')}>⏰ Timeline</button>
            </div>

            {activeTab === 'menu' && (
              <div className="courses-container">
                {Object.entries(menu.courses).map(([type, courses]) => (
                  courses && Array.isArray(courses) && courses.length > 0 && (
                    <div key={type} className="course-section">
                      <h3 className="course-type">
                        {type === 'antipasti' && '🥗 Antipasti'}
                        {type === 'primo' && '🍝 Primo'}
                        {type === 'secondo' && '🍖 Secondo'}
                        {type === 'contorno' && '🥬 Contorno'}
                        {type === 'dessert' && '🍰 Dessert'}
                      </h3>
                      {courses.map((course, idx) => {
                        const courseId = course.course_id || `${type}-${idx}`;
                        const isRegenerating = regenerating?.courseType === type && regenerating?.courseIndex === idx;
                        const wasJustRegenerated = justRegenerated === courseId;
                        
                        return (
                        <div 
                          key={courseId} 
                          className={`course-card ${isRegenerating ? 'regenerating' : ''} ${wasJustRegenerated ? 'just-regenerated' : ''}`}
                        >
                          <div className="course-header">
                            <h4>{course.name}</h4>
                            <div className="course-header-actions">
                              <span className="cuisine-badge">{course.cuisine}</span>
                              <div className="regenerate-buttons">
                                <button
                                  className="regenerate-btn quick"
                                  onClick={() => handleQuickRegenerate(type as CourseType, idx)}
                                  disabled={isRegenerating || regenerating !== null}
                                  title="Rigenera velocemente"
                                >
                                  {isRegenerating ? <span className="spinner-small"></span> : '🔄'}
                                </button>
                                <button
                                  className="regenerate-btn with-feedback"
                                  onClick={() => openRegenerateModal(type as CourseType, idx, course.name)}
                                  disabled={isRegenerating || regenerating !== null}
                                  title="Rigenera con feedback"
                                >
                                  {isRegenerating ? '...' : '💬'}
                                </button>
                              </div>
                            </div>
                          </div>
                          <p className="course-description">{course.description}</p>
                          <div className="course-meta">
                            <span>⏱️ {course.recipe.prep_time_minutes + course.recipe.cook_time_minutes} min totali</span>
                            <span>📊 {course.recipe.difficulty}</span>
                            {course.recipe.can_prep_ahead && <span>✅ Preparabile in anticipo</span>}
                          </div>
                          <details className="recipe-details">
                            <summary>📖 Vedi Ricetta</summary>
                            <div className="recipe-content">
                              <h5>Ingredienti:</h5>
                              <ul>
                                {course.recipe.ingredients.map((ing: Ingredient, i: number) => (
                                  <li key={i}>{ing.quantity} {ing.name}</li>
                                ))}
                              </ul>
                              <h5>Procedimento:</h5>
                              <ol>
                                {course.recipe.steps.map((step: string, i: number) => (
                                  <li key={i}>{step}</li>
                                ))}
                              </ol>
                              {course.recipe.chef_notes && (
                                <>
                                  <h5>💡 Note dello Chef:</h5>
                                  <p>{course.recipe.chef_notes}</p>
                                </>
                              )}
                              {course.recipe.prep_ahead_timing && (
                                <p><strong>⏰ Preparazione anticipata:</strong> {course.recipe.prep_ahead_timing}</p>
                              )}
                            </div>
                          </details>
                        </div>
                        );
                      })}
                    </div>
                  )
                ))}
              </div>
            )}

            {activeTab === 'shopping' && (
              <div className="shopping-container">
                <h3>🛒 Lista della Spesa</h3>
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
                <h3>⏰ Timeline di Preparazione</h3>
                {menu.timeline && (
                  <>
                    {menu.timeline.two_days_before && menu.timeline.two_days_before.length > 0 && (
                      <div className="timeline-section">
                        <h4>📅 Due giorni prima</h4>
                        <ul>
                          {menu.timeline.two_days_before.map((task, i) => (
                            <li key={i}>{task}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {menu.timeline.one_day_before && menu.timeline.one_day_before.length > 0 && (
                      <div className="timeline-section">
                        <h4>📅 Un giorno prima</h4>
                        <ul>
                          {menu.timeline.one_day_before.map((task, i) => (
                            <li key={i}>{task}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {menu.timeline.day_of && Object.keys(menu.timeline.day_of).length > 0 && (
                      <div className="timeline-section">
                        <h4>🎄 Il giorno di Natale</h4>
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

        {/* Errore rigenerazione */}
        {error && menu && (
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
        courseType={regenerateModal.courseType}
        courseName={regenerateModal.courseName}
      />

      <footer className="footer">
        <p>🔥 Powered by <strong>Google Gemini</strong> via Firebase AI Logic</p>
      </footer>
    </div>
  );
}

export default App;