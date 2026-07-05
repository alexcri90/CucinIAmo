"""
Structured Generation Service per Christmas Menu Generator

Questo modulo implementa la generazione di output strutturati usando
Datapizza AI con Google Gemini.

NOTA IMPORTANTE SU GEMINI E STRUCTURED RESPONSES:
L'API Gemini NON supporta "additionalProperties" nello schema JSON.
Per modelli complessi come MenuOutput, usiamo invoke() con parsing manuale
invece di structured_response().

Per modelli semplici (Recipe, Course) structured_response() funziona.

MEMORY INTEGRATION (v0.14.0):
Dopo la generazione del menù, il contesto viene salvato in Memory di Datapizza AI.
Questo permette di rigenerare portate con consapevolezza del menù completo.
"""

import json
import os
import sys
import re
from typing import Optional, Any, Dict, List
from datetime import datetime
from uuid import uuid4

# Aggiungi il path per gli import relativi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Datapizza AI
from datapizza.clients.google import GoogleClient

# Import modelli locali
from backend.models.input_models import UserInput
from backend.models.output_models import MenuOutput, ShoppingList, Timeline
from backend.models.menu_models import Course, Recipe, MenuCourses, Ingredient

# Import templates
from backend.services.prompt_templates import (
    build_menu_generation_prompt,
    build_course_regeneration_prompt,
    build_recipe_detail_prompt,
    MENU_AGENT_SYSTEM_PROMPT,
    RECIPE_AGENT_SYSTEM_PROMPT
)

# Import Memory Manager
from backend.services.memory_manager import (
    save_menu_context_to_memory,
    build_user_input_summary,
    build_menu_summary,
    regenerate_course_with_memory,
    get_memory_for_menu,
    delete_memory_for_menu
)


# =============================================================================
# CONFIGURAZIONE
# =============================================================================

def get_google_client(
    system_prompt: str,
    temperature: float = 0.7
) -> GoogleClient:
    """
    Crea un'istanza di GoogleClient configurata per Gemini 2.5 Flash.
    
    NOTA: GoogleClient NON supporta max_tokens nel costruttore.
    
    Args:
        system_prompt: System prompt per l'agente
        temperature: Creatività del modello (0.0-1.0)
        
    Returns:
        GoogleClient configurato
        
    Raises:
        ValueError: Se GOOGLE_API_KEY non è configurata
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY non trovata! "
            "Assicurati di aver configurato il file .env"
        )
    
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    return GoogleClient(
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature
    )


# =============================================================================
# SCHEMA JSON SEMPLIFICATO PER GEMINI
# =============================================================================

# Schema JSON esplicito che Gemini può seguire (senza additionalProperties)
MENU_JSON_EXAMPLE = '''{
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
    "primo": [
      {
        "name": "Nome Primo",
        "cuisine": "italiana",
        "description": "Descrizione...",
        "recipe": { ... }
      }
    ],
    "secondo": [ ... ],
    "contorno": [ ... ],
    "dessert": [ ... ]
  },
  "shopping_list": {
    "categories": {
      "Frutta e verdura": [{"name": "...", "quantity": "...", "category": "Frutta e verdura"}],
      "Carne": [...],
      "Pesce": [...],
      "Latticini": [...],
      "Dispensa": [...],
      "Altro": [...]
    }
  },
  "timeline": {
    "two_days_before": ["Attività 1", "Attività 2"],
    "one_day_before": ["Attività 1", "Attività 2"],
    "day_of": {
      "09:00": "Descrizione attività",
      "10:00": "Descrizione attività",
      "12:00": "Descrizione attività"
    }
  }
}'''


def build_menu_prompt_with_example(user_input: UserInput) -> str:
    """
    Costruisce un prompt con esempio JSON esplicito.
    
    Questo approccio è più affidabile di structured_response per modelli complessi
    perché mostra a Gemini esattamente la struttura attesa.
    """
    base_prompt = build_menu_generation_prompt(user_input, include_schema=False)
    
    # Aggiungi esempio JSON concreto
    enhanced_prompt = base_prompt + f"""

═══════════════════════════════════════════════════════════════════════════════
                         ESEMPIO STRUTTURA JSON
═══════════════════════════════════════════════════════════════════════════════

Il tuo output DEVE seguire ESATTAMENTE questa struttura JSON:

{MENU_JSON_EXAMPLE}

REGOLE IMPORTANTI:
1. Rispondi SOLO con JSON valido, nient'altro
2. NON usare markdown code blocks (```)
3. La chiave principale è "courses", NON "menu"
4. Ogni portata ha: name, cuisine, description, recipe
5. recipe ha: ingredients, prep_time_minutes, cook_time_minutes, difficulty, steps, chef_notes, can_prep_ahead, prep_ahead_timing
6. Le categorie valide per ingredients sono SOLO: "Frutta e verdura", "Carne", "Pesce", "Latticini", "Dispensa", "Altro"
7. difficulty può essere solo: "facile", "medio", "avanzato"
8. timeline.day_of è un oggetto con chiavi orario (es. "09:00") e valori stringa

GENERA ORA IL MENU COMPLETO:
"""
    
    return enhanced_prompt


# =============================================================================
# GENERAZIONE MENU COMPLETO
# =============================================================================

def generate_menu_structured(user_input: UserInput) -> MenuOutput:
    """
    Genera un menù completo e salva il contesto in Memory per future rigenerazioni.
    
    NOTA: Per modelli complessi come MenuOutput, usiamo invoke() + parsing
    invece di structured_response() per evitare l'errore "additionalProperties".
    
    MEMORY INTEGRATION: Dopo la generazione, il contesto viene salvato in Memory
    di Datapizza AI. Questo permette di rigenerare portate con consapevolezza
    del menù completo.
    
    Args:
        user_input: Input utente validato
        
    Returns:
        MenuOutput: Oggetto Pydantic con menù completo validato
    """
    print(f"\n🎄 Avvio generazione menù per {user_input.num_guests} persone...")
    print(f"   Cucine: {[c.value for c in user_input.cuisines]}")
    print(f"   Difficoltà: {user_input.difficulty_level.value}")
    
    # Crea il client
    client = get_google_client(
        system_prompt=MENU_AGENT_SYSTEM_PROMPT,
        temperature=0.7
    )
    
    # Costruisci il prompt con esempio JSON
    prompt = build_menu_prompt_with_example(user_input)
    
    print("\n📤 Invio richiesta a Gemini...")
    
    # Usa invoke() invece di structured_response() per modelli complessi
    response = client.invoke(prompt)
    
    # Parsa la risposta
    menu_data = _parse_and_fix_menu_json(response.text)
    
    # Aggiungi metadati
    menu_data["menu_id"] = str(uuid4())
    menu_data["generated_at"] = datetime.utcnow().isoformat()
    menu_data["input"] = user_input.model_dump()
    
    # Valida con Pydantic
    try:
        menu = MenuOutput.model_validate(menu_data)
    except Exception as e:
        print(f"   ⚠️ Errore validazione, tentativo correzione struttura...")
        menu_data = _fix_menu_structure(menu_data, user_input)
        menu = MenuOutput.model_validate(menu_data)
    
    print(f"\n✅ Menù generato con successo!")
    print(f"   ID: {menu.menu_id}")
    print(f"   Portate: {_count_courses(menu.courses)}")
    
    # =========================================================================
    # MEMORY INTEGRATION: Salva contesto per future rigenerazioni
    # =========================================================================
    try:
        user_summary = build_user_input_summary(user_input)
        menu_summary = build_menu_summary(menu)
        save_menu_context_to_memory(
            menu_id=str(menu.menu_id),
            user_input_summary=user_summary,
            menu_summary=menu_summary
        )
        print(f"   🧠 Contesto salvato in Memory per rigenerazioni future")
    except Exception as mem_error:
        # Non bloccare la generazione se Memory fallisce
        print(f"   ⚠️ Warning: impossibile salvare in Memory: {mem_error}")
    
    return menu


def _parse_and_fix_menu_json(response_text: str) -> dict:
    """
    Parsa il JSON dalla risposta e corregge problemi comuni.
    """
    text = response_text.strip()
    
    # Rimuovi markdown code blocks
    if "```" in text:
        # Trova il contenuto tra i code blocks
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            text = match.group(1)
        else:
            # Rimuovi solo i delimitatori
            text = text.replace("```json", "").replace("```", "")
    
    # Trova il JSON object
    start_idx = text.find("{")
    end_idx = text.rfind("}") + 1
    
    if start_idx == -1 or end_idx == 0:
        raise ValueError(f"Nessun JSON trovato nella risposta")
    
    json_str = text[start_idx:end_idx]
    
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # Prova a correggere errori comuni
        json_str = _fix_common_json_errors(json_str)
        data = json.loads(json_str)
    
    return data


def _fix_common_json_errors(json_str: str) -> str:
    """Corregge errori JSON comuni."""
    # Rimuovi virgole finali prima di } o ]
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Correggi quotes non standard
    json_str = json_str.replace('"', '"').replace('"', '"')
    json_str = json_str.replace(''', "'").replace(''', "'")
    
    return json_str


def _fix_menu_structure(data: dict, user_input: UserInput) -> dict:
    """
    Corregge la struttura del menù se Gemini ha usato un formato diverso.
    """
    # Se ha usato "menu" invece di "courses"
    if "menu" in data and "courses" not in data:
        print("   Correzione: 'menu' -> 'courses'")
        
        menu_items = data["menu"]
        if isinstance(menu_items, list):
            # Gemini ha restituito una lista piatta, dobbiamo categorizzare
            courses = _categorize_courses(menu_items)
            data["courses"] = courses
            del data["menu"]
    
    # Se courses è una lista invece di un dict
    if "courses" in data and isinstance(data["courses"], list):
        print("   Correzione: courses list -> dict")
        courses = _categorize_courses(data["courses"])
        data["courses"] = courses
    
    # Assicura che ci sia shopping_list
    if "shopping_list" not in data or not data["shopping_list"]:
        print("   Generazione shopping_list mancante...")
        data["shopping_list"] = _generate_shopping_list(data.get("courses", {}))
    
    # Assicura che ci sia timeline
    if "timeline" not in data or not data["timeline"]:
        print("   Generazione timeline mancante...")
        data["timeline"] = _generate_default_timeline()
    
    # Fix timeline.day_of se è una lista invece di dict
    if "timeline" in data:
        if isinstance(data["timeline"].get("day_of"), list):
            day_of_list = data["timeline"]["day_of"]
            data["timeline"]["day_of"] = {
                f"{9+i}:00": item for i, item in enumerate(day_of_list[:8])
            }
    
    return data


def _categorize_courses(items: list) -> dict:
    """
    Categorizza una lista piatta di piatti nelle portate corrette.
    """
    courses = {
        "antipasti": [],
        "primo": [],
        "secondo": [],
        "contorno": [],
        "dessert": []
    }
    
    keywords = {
        "antipasti": ["antipasto", "bruschetta", "carpaccio", "tartare", "insalata", "vol-au-vent", "crostini"],
        "primo": ["primo", "pasta", "risotto", "lasagna", "tortellini", "gnocchi", "ravioli", "zuppa", "minestra", "brodo"],
        "secondo": ["secondo", "arrosto", "brasato", "cotechino", "cappone", "tacchino", "agnello", "maiale", "manzo", "pesce", "baccalà", "salmone"],
        "contorno": ["contorno", "patate", "verdure", "insalata", "spinaci", "lenticchie", "fagioli"],
        "dessert": ["dessert", "dolce", "panettone", "pandoro", "torta", "tiramisù", "budino", "crema", "biscotti", "cioccolato"]
    }
    
    for item in items:
        name = item.get("name", "").lower()
        description = item.get("description", "").lower()
        text = f"{name} {description}"
        
        categorized = False
        for course_type, kws in keywords.items():
            if any(kw in text for kw in kws):
                courses[course_type].append(item)
                categorized = True
                break
        
        if not categorized:
            # Default: metti nel primo slot vuoto
            for course_type in ["antipasti", "primo", "secondo", "contorno", "dessert"]:
                if len(courses[course_type]) == 0:
                    courses[course_type].append(item)
                    break
    
    # Assicura almeno un piatto per categoria
    for course_type in courses:
        if not courses[course_type]:
            courses[course_type] = [_create_placeholder_course(course_type)]
    
    return courses


def _create_placeholder_course(course_type: str) -> dict:
    """Crea un piatto placeholder per le portate mancanti."""
    placeholders = {
        "antipasti": {
            "name": "Antipasto della tradizione",
            "cuisine": "italiana",
            "description": "Un classico antipasto natalizio da personalizzare.",
            "recipe": _create_placeholder_recipe()
        },
        "primo": {
            "name": "Primo natalizio",
            "cuisine": "italiana", 
            "description": "Un primo piatto tradizionale.",
            "recipe": _create_placeholder_recipe()
        },
        "secondo": {
            "name": "Secondo natalizio",
            "cuisine": "italiana",
            "description": "Il piatto forte del pranzo di Natale.",
            "recipe": _create_placeholder_recipe()
        },
        "contorno": {
            "name": "Contorno di stagione",
            "cuisine": "italiana",
            "description": "Un contorno per accompagnare il secondo.",
            "recipe": _create_placeholder_recipe()
        },
        "dessert": {
            "name": "Dolce natalizio",
            "cuisine": "italiana",
            "description": "Il dolce finale per concludere il pranzo.",
            "recipe": _create_placeholder_recipe()
        }
    }
    return placeholders.get(course_type, placeholders["antipasti"])


def _create_placeholder_recipe() -> dict:
    """Crea una ricetta placeholder."""
    return {
        "ingredients": [
            {"name": "ingrediente base", "quantity": "q.b.", "category": "Dispensa"}
        ],
        "prep_time_minutes": 30,
        "cook_time_minutes": 30,
        "difficulty": "medio",
        "steps": ["Preparare gli ingredienti", "Seguire la ricetta tradizionale"],
        "chef_notes": "Personalizza secondo la tua tradizione familiare.",
        "can_prep_ahead": False,
        "prep_ahead_timing": None
    }


def _generate_shopping_list(courses: dict) -> dict:
    """Genera la lista spesa aggregando gli ingredienti."""
    categories: Dict[str, List[dict]] = {
        "Frutta e verdura": [],
        "Carne": [],
        "Pesce": [],
        "Latticini": [],
        "Dispensa": [],
        "Altro": []
    }
    
    seen = set()  # Per evitare duplicati
    
    for course_type, course_list in courses.items():
        if not isinstance(course_list, list):
            continue
        for course in course_list:
            recipe = course.get("recipe", {})
            ingredients = recipe.get("ingredients", [])
            for ing in ingredients:
                if isinstance(ing, dict):
                    name = ing.get("name", "")
                    if name and name not in seen:
                        seen.add(name)
                        cat = ing.get("category", "Altro")
                        if cat not in categories:
                            cat = "Altro"
                        categories[cat].append(ing)
    
    return {"categories": categories}


def _generate_default_timeline() -> dict:
    """Genera una timeline di default."""
    return {
        "two_days_before": [
            "Fare la spesa per gli ingredienti non deperibili",
            "Preparare eventuali dolci che migliorano riposando"
        ],
        "one_day_before": [
            "Fare la spesa per ingredienti freschi",
            "Preparare il brodo se necessario",
            "Preparare antipasti freddi",
            "Organizzare la mise en place"
        ],
        "day_of": {
            "09:00": "Tirare fuori dal frigo ciò che deve tornare a temperatura ambiente",
            "10:00": "Iniziare le preparazioni del secondo",
            "12:00": "Preparare il primo",
            "13:00": "Preparare i contorni",
            "14:00": "Ultimi ritocchi e impiattamento antipasti",
            "19:00": "Riscaldare ciò che serve",
            "20:00": "Servire il pranzo di Natale"
        }
    }


def _count_courses(menu_courses: MenuCourses) -> int:
    """Conta il numero totale di portate."""
    count = 0
    count += len(menu_courses.antipasti)
    count += len(menu_courses.primo)
    count += len(menu_courses.secondo)
    count += len(menu_courses.contorno)
    count += len(menu_courses.dessert)
    return count


# =============================================================================
# GENERAZIONE SINGOLA RICETTA (usa structured_response - funziona per modelli semplici)
# =============================================================================

def generate_recipe_structured(
    dish_name: str,
    cuisine: str,
    num_guests: int,
    difficulty_level: str,
    avoided_ingredients: list = None,
    dietary_restrictions: list = None
) -> Recipe:
    """
    Genera una singola ricetta dettagliata.
    
    Per modelli semplici come Recipe, structured_response funziona bene.
    """
    print(f"\n👨‍🍳 Generazione ricetta per: {dish_name}")
    
    client = get_google_client(
        system_prompt=RECIPE_AGENT_SYSTEM_PROMPT,
        temperature=0.5
    )
    
    prompt = build_recipe_detail_prompt(
        dish_name=dish_name,
        cuisine=cuisine,
        num_guests=num_guests,
        difficulty_level=difficulty_level,
        avoided_ingredients=avoided_ingredients or [],
        dietary_restrictions=dietary_restrictions or []
    )
    
    try:
        # Prova structured_response
        response = client.structured_response(
            input=prompt,
            output_cls=Recipe
        )
        recipe = response.structured_data[0]
        
    except Exception as e:
        print(f"   ⚠️ Fallback a invoke(): {e}")
        # Fallback con parsing manuale
        response = client.invoke(prompt)
        recipe_data = _parse_and_fix_menu_json(response.text)
        recipe = Recipe.model_validate(recipe_data)
    
    print(f"   ✅ Ricetta generata: {len(recipe.ingredients)} ingredienti, {len(recipe.steps)} step")
    return recipe


# =============================================================================
# RIGENERAZIONE PORTATA
# =============================================================================

def regenerate_course_structured(
    course_type: str,
    current_dish_name: str,
    other_dishes: list,
    user_input: UserInput,
    menu_id: str = None,
    user_feedback: str = ""
) -> Course:
    """
    Rigenera una singola portata mantenendo coerenza con il resto del menù.
    
    Se menu_id è fornito e esiste una Memory associata, usa l'agente con Memory
    per una rigenerazione più contestualizzata.
    
    Args:
        course_type: Tipo portata (antipasti, primo, secondo, contorno, dessert)
        current_dish_name: Nome del piatto da sostituire
        other_dishes: Lista nomi altri piatti nel menù
        user_input: UserInput originale
        menu_id: ID del menù (opzionale, per usare Memory)
        user_feedback: Feedback utente sul perché non gli piace (opzionale)
        
    Returns:
        Course: Nuova portata generata
    """
    print(f"\n🔄 Rigenerazione {course_type}: '{current_dish_name}'...")
    
    # =========================================================================
    # MEMORY INTEGRATION: Se abbiamo Memory, usiamo l'agente con contesto
    # =========================================================================
    if menu_id and get_memory_for_menu(menu_id):
        print(f"   🧠 Usando Memory per rigenerazione contestualizzata")
        try:
            course_data = regenerate_course_with_memory(
                menu_id=menu_id,
                course_type=course_type,
                current_dish_name=current_dish_name,
                user_feedback=user_feedback
            )
            new_course = Course.model_validate(course_data)
            print(f"   ✅ Nuova portata (con Memory): {new_course.name}")
            return new_course
        except Exception as mem_error:
            print(f"   ⚠️ Fallback a metodo standard: {mem_error}")
    
    # =========================================================================
    # FALLBACK: Metodo originale senza Memory
    # =========================================================================
    client = get_google_client(
        system_prompt=MENU_AGENT_SYSTEM_PROMPT,
        temperature=0.8
    )
    
    prompt = build_course_regeneration_prompt(
        course_type=course_type,
        current_dish_name=current_dish_name,
        other_dishes=other_dishes,
        user_input=user_input,
        user_feedback=user_feedback
    )
    
    try:
        response = client.structured_response(
            input=prompt,
            output_cls=Course
        )
        new_course = response.structured_data[0]
        
    except Exception as e:
        print(f"   ⚠️ Fallback: {e}")
        response = client.invoke(prompt)
        course_data = _parse_and_fix_menu_json(response.text)
        new_course = Course.model_validate(course_data)
    
    print(f"   ✅ Nuova portata: {new_course.name}")
    return new_course


# =============================================================================
# VALIDAZIONE
# =============================================================================

def validate_menu_output(menu: MenuOutput) -> list:
    """
    Valida un MenuOutput e restituisce eventuali warning.
    """
    warnings = []
    
    # Verifica portate
    if len(menu.courses.antipasti) < 1:
        warnings.append("Manca almeno un antipasto")
    if len(menu.courses.primo) < 1:
        warnings.append("Manca il primo piatto")
    if len(menu.courses.secondo) < 1:
        warnings.append("Manca il secondo piatto")
    if len(menu.courses.contorno) < 1:
        warnings.append("Manca il contorno")
    if len(menu.courses.dessert) < 1:
        warnings.append("Manca il dessert")
    
    # Verifica shopping list
    if not menu.shopping_list.categories:
        warnings.append("Lista spesa vuota")
    
    # Verifica timeline
    if not menu.timeline.day_of:
        warnings.append("Timeline del giorno stesso vuota")
    
    return warnings


# =============================================================================
# CLASSE WRAPPER
# =============================================================================

class StructuredMenuGenerator:
    """Wrapper class per la generazione strutturata di menù."""
    
    def __init__(self, temperature: float = 0.7):
        self.temperature = temperature
    
    def generate(self, user_input: UserInput) -> MenuOutput:
        return generate_menu_structured(user_input)
    
    def regenerate_course(
        self,
        menu: MenuOutput,
        course_type: str,
        course_index: int = 0
    ) -> Course:
        courses = getattr(menu.courses, course_type)
        current_course = courses[course_index]
        
        other_dishes = []
        for ct in ["antipasti", "primo", "secondo", "contorno", "dessert"]:
            for c in getattr(menu.courses, ct):
                if c.name != current_course.name:
                    other_dishes.append(c.name)
        
        return regenerate_course_structured(
            course_type=course_type,
            current_dish_name=current_course.name,
            other_dishes=other_dishes,
            user_input=menu.input
        )
    
    def get_recipe_details(
        self,
        dish_name: str,
        cuisine: str,
        num_guests: int,
        difficulty_level: str
    ) -> Recipe:
        return generate_recipe_structured(
            dish_name=dish_name,
            cuisine=cuisine,
            num_guests=num_guests,
            difficulty_level=difficulty_level
        )


# =============================================================================
# TEST STANDALONE
# =============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 80)
    print("  TEST STRUCTURED GENERATION (versione corretta)")
    print("=" * 80)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ ERRORE: GOOGLE_API_KEY non trovata nel file .env")
        exit(1)
    
    print(f"\n✅ API Key trovata: {api_key[:10]}...")
    
    print("\n📡 Test connessione...")
    try:
        client = get_google_client("Sei un assistente.", 0.5)
        response = client.invoke("Rispondi solo: OK")
        print(f"   Risposta: {response.text.strip()}")
        print("   ✅ Connessione OK!")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        exit(1)
    
    print("\n" + "=" * 80)
    print("  Per test completo: python backend/test_structured.py")
    print("=" * 80)