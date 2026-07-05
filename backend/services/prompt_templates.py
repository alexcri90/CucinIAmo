"""
Prompt Templates per Christmas Menu Generator

Questo modulo contiene tutti i template di prompt ottimizzati per
la generazione di menù natalizi con Datapizza AI e Google Gemini.

IMPORTANTE: I prompt sono progettati per guidare l'LLM a produrre
output JSON strutturati e coerenti.
"""

from string import Template
from typing import Optional
import json

# Importa i modelli per type hints
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.input_models import UserInput
from backend.models.output_models import MenuOutput


# =============================================================================
# TEMPLATE PRINCIPALE: GENERAZIONE MENU COMPLETO
# =============================================================================

MENU_GENERATION_TEMPLATE = Template("""
Sei uno chef esperto di cucina natalizia internazionale. Genera un menù di Natale COMPLETO per $num_guests persone.

═══════════════════════════════════════════════════════════════════════════════
                            VINCOLI OBBLIGATORI
═══════════════════════════════════════════════════════════════════════════════

🔴 INGREDIENTI VIETATI (NON usare MAI questi ingredienti):
$avoided_ingredients

🟢 INGREDIENTI PREFERITI (includi ALMENO 1-2 di questi):
$preferred_ingredients

🌍 CUCINE/TRADIZIONI (i piatti DEVONO essere tipici di queste culture):
$cuisines

⚠️ RESTRIZIONI ALIMENTARI:
$dietary_restrictions

📊 LIVELLO DIFFICOLTÀ: $difficulty_level
💰 BUDGET: $budget_level

═══════════════════════════════════════════════════════════════════════════════
                          STRUTTURA MENÙ RICHIESTA
═══════════════════════════════════════════════════════════════════════════════

Il menù DEVE avere questa struttura:

1. ANTIPASTI (1-2 piatti)
   - Almeno uno freddo, preparabile in anticipo
   - Tipico della tradizione natalizia delle cucine scelte

2. PRIMO PIATTO (1 piatto)
   - Tipico natalizio (brodo, pasta ripiena, risotto, ecc.)
   - Adatto al livello di difficoltà richiesto

3. SECONDO PIATTO (1 piatto)
   - Piatto principale della festa
   - Carne o pesce secondo tradizione

4. CONTORNO (1 piatto)
   - Complementare al secondo
   - Stagionale e festivo

5. DESSERT (1-2 piatti)
   - Dolce tipico natalizio
   - Preferibilmente preparabile in anticipo

═══════════════════════════════════════════════════════════════════════════════
                         DETTAGLI PER OGNI PIATTO
═══════════════════════════════════════════════════════════════════════════════

Per OGNI piatto devi fornire:

• name: nome del piatto (originale + traduzione se straniero)
• cuisine: paese/tradizione di origine
• description: descrizione appetitosa di 2-3 righe

• recipe con:
  - ingredients: lista di oggetti {name, quantity, category}
    Le CATEGORIE valide sono SOLO:
    - "Frutta e verdura"
    - "Carne"
    - "Pesce"
    - "Latticini"
    - "Dispensa"
    - "Altro"
    
  - prep_time_minutes: tempo preparazione attiva (numero intero)
  - cook_time_minutes: tempo cottura (numero intero, 0 se non serve cottura)
  - difficulty: "facile", "medio" o "avanzato"
  - steps: lista di stringhe con procedimento step-by-step
  - chef_notes: consigli, tips e possibili varianti
  - can_prep_ahead: true se preparabile in anticipo, false altrimenti
  - prep_ahead_timing: se can_prep_ahead è true, quando prepararlo (es. "1 giorno prima")

═══════════════════════════════════════════════════════════════════════════════
                           OUTPUT AGGIUNTIVI
═══════════════════════════════════════════════════════════════════════════════

📋 LISTA SPESA (shopping_list):
Aggrega TUTTI gli ingredienti per categoria. Somma le quantità degli ingredienti ripetuti.
Formato: {"categories": {"NomeCategoria": [{name, quantity, category}, ...]}}

📅 TIMELINE PREPARAZIONE (timeline):
- two_days_before: lista di attività da fare 2 giorni prima
- one_day_before: lista di attività da fare il giorno prima
- day_of: dizionario con orari (es. {"09:00": "Inizia preparazione...", "12:00": "..."})

La cena è prevista per le 20:00 del giorno di Natale.

═══════════════════════════════════════════════════════════════════════════════
                              FORMATO OUTPUT
═══════════════════════════════════════════════════════════════════════════════

RISPONDI ESCLUSIVAMENTE CON JSON VALIDO.
NON aggiungere testo prima o dopo il JSON.
NON usare markdown code blocks (```).
Il JSON deve essere parsabile direttamente.
""")


# =============================================================================
# TEMPLATE: RIGENERAZIONE SINGOLA PORTATA
# =============================================================================

COURSE_REGENERATION_TEMPLATE = Template("""
Sei uno chef esperto. Devi rigenerare SOLO una portata di un menù natalizio esistente.

═══════════════════════════════════════════════════════════════════════════════
                              CONTESTO MENÙ
═══════════════════════════════════════════════════════════════════════════════

📋 TIPO DI PORTATA DA RIGENERARE: $course_type
🍽️ PIATTO ATTUALE (da sostituire): $current_dish_name
👥 NUMERO OSPITI: $num_guests

🍴 ALTRI PIATTI NEL MENÙ (mantieni coerenza):
$other_dishes

═══════════════════════════════════════════════════════════════════════════════
                         🎯 FEEDBACK UTENTE (PRIORITÀ MASSIMA)
═══════════════════════════════════════════════════════════════════════════════

$user_feedback_section

═══════════════════════════════════════════════════════════════════════════════
                            VINCOLI ORIGINALI
═══════════════════════════════════════════════════════════════════════════════

🔴 INGREDIENTI VIETATI: $avoided_ingredients
🟢 INGREDIENTI PREFERITI: $preferred_ingredients
🌍 CUCINE: $cuisines
⚠️ RESTRIZIONI: $dietary_restrictions
📊 DIFFICOLTÀ: $difficulty_level
💰 BUDGET: $budget_level

═══════════════════════════════════════════════════════════════════════════════
                              REQUISITI
═══════════════════════════════════════════════════════════════════════════════

1. Il nuovo piatto DEVE essere DIVERSO da "$current_dish_name"
2. DEVE rispettare tutti i vincoli originali
3. DEVE essere coerente con gli altri piatti del menù
4. DEVE essere tipico natalizio per le cucine indicate
5. SE C'È UN FEEDBACK UTENTE, DEVI SEGUIRLO CON PRIORITÀ MASSIMA

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT
═══════════════════════════════════════════════════════════════════════════════

Genera UN SINGOLO oggetto JSON per la nuova portata con la stessa struttura:
{
  "name": "...",
  "cuisine": "...",
  "description": "...",
  "recipe": {
    "ingredients": [...],
    "prep_time_minutes": ...,
    "cook_time_minutes": ...,
    "difficulty": "...",
    "steps": [...],
    "chef_notes": "...",
    "can_prep_ahead": ...,
    "prep_ahead_timing": "..."
  }
}

Rispondi SOLO con il JSON, senza altro testo.
""")


# =============================================================================
# TEMPLATE: GENERAZIONE SINGOLA RICETTA DETTAGLIATA
# =============================================================================

RECIPE_DETAIL_TEMPLATE = Template("""
Sei uno chef professionista. Genera la ricetta DETTAGLIATA per questo piatto natalizio.

═══════════════════════════════════════════════════════════════════════════════
                            INFORMAZIONI PIATTO
═══════════════════════════════════════════════════════════════════════════════

🍽️ PIATTO: $dish_name
🌍 CUCINA: $cuisine
👥 PORZIONI: $num_guests persone
📊 DIFFICOLTÀ RICHIESTA: $difficulty_level

═══════════════════════════════════════════════════════════════════════════════
                              VINCOLI
═══════════════════════════════════════════════════════════════════════════════

🔴 NON USARE: $avoided_ingredients
⚠️ RESTRIZIONI: $dietary_restrictions

═══════════════════════════════════════════════════════════════════════════════
                              REQUISITI
═══════════════════════════════════════════════════════════════════════════════

Genera una ricetta con:
1. Lista ingredienti COMPLETA con quantità ESATTE per $num_guests persone
2. Ogni ingrediente deve avere: name, quantity, category
3. Le categorie valide: "Frutta e verdura", "Carne", "Pesce", "Latticini", "Dispensa", "Altro"
4. Procedimento DETTAGLIATO step-by-step (ogni step una stringa)
5. Tempo preparazione e cottura in minuti (numeri interi)
6. Note dello chef con tips e varianti
7. Indicare se preparabile in anticipo e quando

Rispondi con JSON valido per l'oggetto recipe.
""")


# =============================================================================
# SYSTEM PROMPTS PER GLI AGENTI
# =============================================================================

MENU_AGENT_SYSTEM_PROMPT = """
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

COLLABORAZIONE:
Puoi delegare task specifici ad altri agenti specializzati quando necessario:
- Recipe Agent: per ricette più dettagliate
- Aggregation Agent: per lista spesa e timeline

OUTPUT:
Produci sempre output JSON valido e strutturato quando richiesto.
"""

RECIPE_AGENT_SYSTEM_PROMPT = """
Sei uno chef professionista specializzato nella scrittura di ricette dettagliate.

COMPETENZE:
• Scrittura chiara e precisa di procedimenti culinari
• Calcolo esatto delle quantità per qualsiasi numero di porzioni
• Conoscenza delle tecniche di base e avanzate
• Suggerimenti per preparazioni anticipate
• Tips per varianti e sostituzioni

REGOLE:
1. Le quantità devono essere SEMPRE specificate (mai "q.b." o "a piacere" da soli)
2. Ogni step deve essere chiaro e eseguibile
3. Includere sempre tempi realistici
4. Segnalare passaggi critici o punti di attenzione

OUTPUT:
Fornisci ricette in formato JSON strutturato.
"""

AGGREGATION_AGENT_SYSTEM_PROMPT = """
Sei un assistente specializzato nell'organizzazione e pianificazione di eventi culinari.

COMPETENZE:
• Aggregazione e organizzazione di liste della spesa
• Pianificazione temporale di preparazioni complesse
• Ottimizzazione dei flussi di lavoro in cucina
• Gestione delle priorità per preparazioni anticipate

REGOLE:
1. Aggregare ingredienti uguali sommando le quantità
2. Organizzare per categoria (Frutta/Verdura, Carne, Pesce, Latticini, Dispensa, Altro)
3. Timeline deve partire da 2 giorni prima fino al giorno stesso
4. Gli orari del giorno stesso devono essere realistici (inizio ore 9, cena ore 20)

OUTPUT:
Fornisci liste e timeline in formato JSON strutturato.
"""


# =============================================================================
# FUNZIONI HELPER
# =============================================================================

def build_menu_generation_prompt(user_input: UserInput, include_schema: bool = False) -> str:
    """
    Costruisce il prompt completo per la generazione del menù.
    
    Args:
        user_input: Input utente validato con Pydantic
        include_schema: Se True, include lo schema JSON nel prompt
        
    Returns:
        Prompt formattato pronto per l'LLM
    """
    # Formatta le liste per il prompt
    avoided = _format_list(user_input.avoided_ingredients, "Nessuno specificato")
    preferred = _format_list(user_input.preferred_ingredients, "Nessuno specificato")
    cuisines = _format_list([c.value.title() for c in user_input.cuisines])
    
    # Formatta restrizioni alimentari
    restrictions_list = [r.value.replace("_", " ").title() for r in user_input.dietary_restrictions]
    if user_input.other_restrictions:
        restrictions_list.append(user_input.other_restrictions)
    restrictions = _format_list(restrictions_list, "Nessuna")
    
    # Costruisci il prompt
    prompt = MENU_GENERATION_TEMPLATE.substitute(
        num_guests=user_input.num_guests,
        avoided_ingredients=avoided,
        preferred_ingredients=preferred,
        cuisines=cuisines,
        dietary_restrictions=restrictions,
        difficulty_level=user_input.difficulty_level.value.title(),
        budget_level=user_input.budget_level.value.title()
    )
    
    # Aggiungi schema JSON se richiesto
    if include_schema:
        schema = MenuOutput.model_json_schema()
        prompt += f"\n\nSchema JSON da seguire:\n{json.dumps(schema, indent=2, ensure_ascii=False)}"
    
    return prompt


def build_course_regeneration_prompt(
    course_type: str,
    current_dish_name: str,
    other_dishes: list[str],
    user_input: UserInput,
    user_feedback: str = ""
) -> str:
    """
    Costruisce il prompt per rigenerare una singola portata.
    
    Args:
        course_type: Tipo di portata (antipasti, primo, secondo, contorno, dessert)
        current_dish_name: Nome del piatto attuale da sostituire
        other_dishes: Lista dei nomi degli altri piatti nel menù
        user_input: Input originale dell'utente
        user_feedback: Feedback opzionale dell'utente sul perché non gli piace
        
    Returns:
        Prompt formattato per la rigenerazione
    """
    avoided = _format_list(user_input.avoided_ingredients, "Nessuno")
    preferred = _format_list(user_input.preferred_ingredients, "Nessuno")
    cuisines = _format_list([c.value.title() for c in user_input.cuisines])
    
    restrictions_list = [r.value.replace("_", " ").title() for r in user_input.dietary_restrictions]
    if user_input.other_restrictions:
        restrictions_list.append(user_input.other_restrictions)
    restrictions = _format_list(restrictions_list, "Nessuna")
    
    # Costruisci la sezione feedback
    if user_feedback and user_feedback.strip():
        user_feedback_section = f"""⚠️ L'UTENTE HA RICHIESTO SPECIFICAMENTE:
\"{user_feedback}\"

🔴 IMPORTANTE: DEVI seguire questa richiesta! Il nuovo piatto DEVE soddisfare questo feedback.
Se l'utente chiede un ingrediente specifico, INCLUDI quell'ingrediente come protagonista del piatto."""
    else:
        user_feedback_section = "L'utente vuole semplicemente un'alternativa diversa, senza richieste specifiche."
    
    return COURSE_REGENERATION_TEMPLATE.substitute(
        course_type=course_type,
        current_dish_name=current_dish_name,
        num_guests=user_input.num_guests,
        other_dishes=_format_list(other_dishes),
        user_feedback_section=user_feedback_section,
        avoided_ingredients=avoided,
        preferred_ingredients=preferred,
        cuisines=cuisines,
        dietary_restrictions=restrictions,
        difficulty_level=user_input.difficulty_level.value.title(),
        budget_level=user_input.budget_level.value.title()
    )


def build_recipe_detail_prompt(
    dish_name: str,
    cuisine: str,
    num_guests: int,
    difficulty_level: str,
    avoided_ingredients: list[str],
    dietary_restrictions: list[str]
) -> str:
    """
    Costruisce il prompt per generare una ricetta dettagliata.
    
    Args:
        dish_name: Nome del piatto
        cuisine: Cucina/tradizione del piatto
        num_guests: Numero di persone
        difficulty_level: Livello di difficoltà richiesto
        avoided_ingredients: Ingredienti da evitare
        dietary_restrictions: Restrizioni alimentari
        
    Returns:
        Prompt formattato per la ricetta
    """
    return RECIPE_DETAIL_TEMPLATE.substitute(
        dish_name=dish_name,
        cuisine=cuisine,
        num_guests=num_guests,
        difficulty_level=difficulty_level,
        avoided_ingredients=_format_list(avoided_ingredients, "Nessuno"),
        dietary_restrictions=_format_list(dietary_restrictions, "Nessuna")
    )


def _format_list(items: list[str], default: str = "Nessuno") -> str:
    """
    Formatta una lista in stringa bullet point.
    
    Args:
        items: Lista di elementi
        default: Testo da mostrare se la lista è vuota
        
    Returns:
        Stringa formattata con bullet points
    """
    if not items:
        return f"  • {default}"
    return "\n".join(f"  • {item}" for item in items)


# =============================================================================
# ESEMPIO DI UTILIZZO
# =============================================================================

if __name__ == "__main__":
    # Test dei template
    from models.input_models import UserInput, Cuisine, DifficultyLevel, BudgetLevel, DietaryRestriction
    
    # Crea un input di test
    test_input = UserInput(
        num_guests=8,
        preferred_ingredients=["salmone", "gamberi"],
        avoided_ingredients=["piccante", "funghi"],
        cuisines=[Cuisine.ITALIANA, Cuisine.FRANCESE],
        dietary_restrictions=[DietaryRestriction.SENZA_LATTOSIO],
        difficulty_level=DifficultyLevel.MEDIO,
        budget_level=BudgetLevel.MEDIO
    )
    
    # Genera il prompt
    prompt = build_menu_generation_prompt(test_input)
    
    print("=" * 80)
    print("PROMPT GENERATO:")
    print("=" * 80)
    print(prompt[:2000] + "...")  # Mostra solo i primi 2000 caratteri
    print("\n✅ Template di prompt funzionante!")