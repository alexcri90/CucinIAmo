"""
Memory Manager per Christmas Menu Generator

Gestisce le istanze Memory di Datapizza AI associate ai menù generati.
Permette di mantenere contesto conversazionale per rigenerare portate
con consapevolezza del menù completo.

Utilizzo:
1. Quando un menù viene generato, si salva il contesto in Memory
2. Quando l'utente richiede rigenerazione, si recupera la Memory
3. L'agente può così generare portate coerenti con il resto del menù
"""

from typing import Dict, Optional
from datapizza.memory import Memory
from datapizza.agents import Agent
from datapizza.type import TextBlock

from backend.config import create_google_client


# =============================================================================
# SYSTEM PROMPTS PER AGENTI CON MEMORY
# =============================================================================

MENU_AGENT_SYSTEM_PROMPT_WITH_MEMORY = """
Sei un esperto chef e food consultant specializzato nella creazione di menù natalizi.

COMPETENZE:
- Conosci le tradizioni culinarie natalizie di ogni paese
- Sai bilanciare un menù considerando sapori, consistenze e colori
- Rispetti rigorosamente le restrizioni alimentari
- Adatti la complessità al livello di difficoltà richiesto
- Consideri il budget nella scelta degli ingredienti

REGOLE IMPERATIVE:
1. MAI includere ingredienti nella lista "da evitare"
2. SEMPRE includere almeno un ingrediente dalla lista "preferiti" se presente
3. I piatti DEVONO essere tipicamente natalizi per le culture selezionate
4. Le quantità DEVONO essere calcolate per il numero esatto di ospiti
5. Rispondi SOLO con JSON valido quando richiesto

COMPORTAMENTO CON MEMORY:
Quando ti viene chiesto di rigenerare una portata:
- Leggi dalla memoria il contesto del menù esistente
- Genera un piatto DIVERSO da quello da sostituire
- Mantieni COERENZA con le altre portate del menù
- Rispetta le stesse restrizioni e preferenze dell'utente originale
- Evita di ripetere ingredienti già presenti in abbondanza nel menù

OUTPUT:
Produci sempre JSON valido per la portata richiesta.
"""

REGENERATION_AGENT_SYSTEM_PROMPT = """
Sei uno chef esperto che deve suggerire un'alternativa per una portata del menù.

HAI ACCESSO ALLA MEMORIA DEL MENÙ COMPLETO.
Usa questa informazione per:
1. Proporre un piatto DIVERSO ma COERENTE con il resto del menù
2. Evitare duplicazione di ingredienti principali
3. Mantenere bilanciamento di sapori e consistenze
4. Rispettare le stesse restrizioni alimentari

FORMATO OUTPUT:
Rispondi SOLO con un JSON valido per il nuovo piatto, con questa struttura:
{
    "name": "Nome del piatto",
    "cuisine": "cucina di origine",
    "description": "Descrizione appetitosa",
    "recipe": {
        "ingredients": [{"name": "...", "quantity": "...", "category": "..."}],
        "prep_time_minutes": numero,
        "cook_time_minutes": numero,
        "difficulty": "facile|medio|avanzato",
        "steps": ["Passo 1...", "Passo 2..."],
        "chef_notes": "Note dello chef",
        "can_prep_ahead": true/false,
        "prep_ahead_timing": "quando preparare in anticipo"
    }
}
"""


# =============================================================================
# MEMORY STORE
# =============================================================================

# Storage delle Memory associate ai menù
# Chiave: menu_id (str), Valore: Memory instance
_memory_store: Dict[str, Memory] = {}


def get_memory_for_menu(menu_id: str) -> Optional[Memory]:
    """
    Recupera la Memory associata a un menù.
    
    Args:
        menu_id: ID del menù
        
    Returns:
        Memory instance o None se non esiste
    """
    return _memory_store.get(menu_id)


def create_memory_for_menu(menu_id: str) -> Memory:
    """
    Crea una nuova Memory per un menù.
    
    Args:
        menu_id: ID del menù
        
    Returns:
        Nuova istanza Memory
    """
    memory = Memory()
    _memory_store[menu_id] = memory
    return memory


def delete_memory_for_menu(menu_id: str) -> bool:
    """
    Elimina la Memory associata a un menù.
    
    Args:
        menu_id: ID del menù
        
    Returns:
        True se eliminata, False se non esisteva
    """
    if menu_id in _memory_store:
        del _memory_store[menu_id]
        return True
    return False


def save_menu_context_to_memory(
    menu_id: str,
    user_input_summary: str,
    menu_summary: str
) -> Memory:
    """
    Salva il contesto del menù nella Memory per future rigenerazioni.
    
    Args:
        menu_id: ID del menù
        user_input_summary: Riassunto delle preferenze utente
        menu_summary: Riassunto del menù generato
        
    Returns:
        Memory aggiornata
    """
    memory = get_memory_for_menu(menu_id)
    if memory is None:
        memory = create_memory_for_menu(menu_id)
    
    # Aggiungiamo il contesto come se fosse una "conversazione" precedente
    # Questo permette all'agente di "ricordare" il menù quando rigenera
    
    # Messaggio 1: Richiesta originale dell'utente
    user_block = TextBlock(f"[CONTESTO MENÙ] Richiesta originale:\n{user_input_summary}")
    memory.add_turn(blocks=user_block, role="user")
    
    # Messaggio 2: Menù generato (risposta dell'agente)
    assistant_block = TextBlock(f"[CONTESTO MENÙ] Menù generato:\n{menu_summary}")
    memory.add_turn(blocks=assistant_block, role="assistant")
    
    return memory


def build_user_input_summary(user_input) -> str:
    """
    Costruisce un riassunto testuale delle preferenze utente.
    
    Args:
        user_input: UserInput object
        
    Returns:
        Stringa con riassunto formattato
    """
    lines = [
        f"- Numero ospiti: {user_input.num_guests}",
        f"- Cucine: {', '.join(c.value for c in user_input.cuisines)}",
        f"- Difficoltà: {user_input.difficulty_level.value}",
        f"- Budget: {user_input.budget_level.value}",
    ]
    
    if user_input.preferred_ingredients:
        lines.append(f"- Ingredienti preferiti: {', '.join(user_input.preferred_ingredients)}")
    
    if user_input.avoided_ingredients:
        lines.append(f"- Ingredienti da evitare: {', '.join(user_input.avoided_ingredients)}")
    
    if user_input.dietary_restrictions:
        lines.append(f"- Restrizioni alimentari: {', '.join(r.value for r in user_input.dietary_restrictions)}")
    
    if user_input.other_restrictions:
        lines.append(f"- Note aggiuntive: {user_input.other_restrictions}")
    
    return "\n".join(lines)


def build_menu_summary(menu) -> str:
    """
    Costruisce un riassunto testuale del menù generato.
    
    Args:
        menu: MenuOutput object
        
    Returns:
        Stringa con riassunto formattato
    """
    lines = []
    
    # Antipasti
    if menu.courses.antipasti:
        lines.append("ANTIPASTI:")
        for c in menu.courses.antipasti:
            ingredients = ", ".join(i.name for i in c.recipe.ingredients[:5])
            lines.append(f"  - {c.name} ({c.cuisine}): {ingredients}...")
    
    # Primo
    if menu.courses.primo:
        lines.append("PRIMO:")
        for c in menu.courses.primo:
            ingredients = ", ".join(i.name for i in c.recipe.ingredients[:5])
            lines.append(f"  - {c.name} ({c.cuisine}): {ingredients}...")
    
    # Secondo
    if menu.courses.secondo:
        lines.append("SECONDO:")
        for c in menu.courses.secondo:
            ingredients = ", ".join(i.name for i in c.recipe.ingredients[:5])
            lines.append(f"  - {c.name} ({c.cuisine}): {ingredients}...")
    
    # Contorno
    if menu.courses.contorno:
        lines.append("CONTORNO:")
        for c in menu.courses.contorno:
            ingredients = ", ".join(i.name for i in c.recipe.ingredients[:5])
            lines.append(f"  - {c.name} ({c.cuisine}): {ingredients}...")
    
    # Dessert
    if menu.courses.dessert:
        lines.append("DESSERT:")
        for c in menu.courses.dessert:
            ingredients = ", ".join(i.name for i in c.recipe.ingredients[:5])
            lines.append(f"  - {c.name} ({c.cuisine}): {ingredients}...")
    
    return "\n".join(lines)


# =============================================================================
# AGENT CON MEMORY PER RIGENERAZIONE
# =============================================================================

def create_regeneration_agent_with_memory(memory: Memory) -> Agent:
    """
    Crea un agente per rigenerazione che usa Memory per contesto.
    
    Args:
        memory: Memory contenente il contesto del menù
        
    Returns:
        Agent configurato con Memory
    """
    from backend.tools.ingredient_tools import (
        validate_ingredients,
        get_christmas_dishes_by_cuisine,
        suggest_ingredient_substitution
    )
    from backend.tools.calculation_tools import calculate_portions, estimate_prep_time
    
    client = create_google_client(
        system_prompt=REGENERATION_AGENT_SYSTEM_PROMPT,
        temperature=0.8  # Più creativo per generare alternative
    )
    
    agent = Agent(
        name="regeneration_agent",
        client=client,
        tools=[
            validate_ingredients,
            get_christmas_dishes_by_cuisine,
            suggest_ingredient_substitution,
            calculate_portions,
            estimate_prep_time
        ],
        memory=memory,
        max_steps=5
    )
    
    return agent


def regenerate_course_with_memory(
    menu_id: str,
    course_type: str,
    current_dish_name: str,
    user_feedback: str = ""
) -> dict:
    """
    Rigenera una portata usando Memory per contesto.
    
    Args:
        menu_id: ID del menù
        course_type: Tipo portata (antipasti, primo, secondo, contorno, dessert)
        current_dish_name: Nome del piatto da sostituire
        user_feedback: Feedback opzionale dell'utente sul perché non gli piace
        
    Returns:
        dict con i dati del nuovo piatto
        
    Raises:
        ValueError: Se non esiste Memory per il menù
    """
    import json
    
    memory = get_memory_for_menu(menu_id)
    if memory is None:
        raise ValueError(f"Nessun contesto Memory trovato per menù {menu_id}")
    
    # Crea l'agente con la Memory del menù
    agent = create_regeneration_agent_with_memory(memory)
    
    # Costruisci il prompt per la rigenerazione
    if user_feedback and user_feedback.strip():
        feedback_instruction = f"""\n🎯 FEEDBACK UTENTE (PRIORITÀ MASSIMA):
\"{user_feedback}\"

⚠️ DEVI SEGUIRE QUESTO FEEDBACK! Se l'utente chiede un ingrediente specifico (es. "più pistacchio"),
il nuovo piatto DEVE contenere quell'ingrediente come elemento PRINCIPALE.
"""
    else:
        feedback_instruction = "\nL'utente vuole semplicemente un'alternativa diversa."
    
    prompt = f"""
Devo sostituire il {course_type} "{current_dish_name}" con un'alternativa.
{feedback_instruction}

ISTRUZIONI:
1. Consulta la memoria per vedere il menù completo e le preferenze utente
2. Genera un piatto DIVERSO da "{current_dish_name}"
3. SE C'È UN FEEDBACK, SEGUILO CON PRIORITÀ MASSIMA (es. se chiede "pistacchio", usa pistacchio!)
4. Assicurati che sia COERENTE con le altre portate e regole degli ingredienti
5. Rispetta le restrizioni alimentari e preferenze originali
6. Evita di duplicare ingredienti principali già presenti

Rispondi SOLO con il JSON del nuovo piatto nel formato richiesto.
"""
    
    print(f"\n🔄 Rigenerazione con Memory: {course_type} '{current_dish_name}'")
    
    # Esegui l'agente con Memory
    response = agent.run(prompt)
    
    # Parsa la risposta
    response_text = response.text.strip()
    
    # Estrai JSON dalla risposta
    if "```" in response_text:
        import re
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if match:
            response_text = match.group(1)
    
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}") + 1
    
    if start_idx != -1 and end_idx > 0:
        json_str = response_text[start_idx:end_idx]
        course_data = json.loads(json_str)
    else:
        raise ValueError(f"Impossibile estrarre JSON dalla risposta: {response_text[:200]}")
    
    print(f"   ✅ Nuovo piatto generato: {course_data.get('name', 'N/A')}")
    
    # Aggiorna la Memory con la nuova conversazione
    # Usa add_turn con TextBlock (API corretta di Datapizza Memory)
    user_block = TextBlock(f"[RIGENERAZIONE] Ho sostituito {course_type} '{current_dish_name}'")
    memory.add_turn(blocks=user_block, role="user")
    
    assistant_block = TextBlock(f"[RIGENERAZIONE] Nuovo piatto: {course_data.get('name', 'N/A')}")
    memory.add_turn(blocks=assistant_block, role="assistant")
    
    return course_data


# =============================================================================
# CLEANUP
# =============================================================================

def cleanup_old_memories(max_age_hours: int = 24) -> int:
    """
    Pulisce le Memory più vecchie di max_age_hours.
    
    Nota: Questa è un'implementazione placeholder.
    Per una vera implementazione, dovresti tracciare i timestamp.
    
    Args:
        max_age_hours: Età massima in ore
        
    Returns:
        Numero di Memory eliminate
    """
    # TODO: Implementare cleanup basato su timestamp
    # Per ora, questa funzione è solo un placeholder
    return 0


def get_memory_stats() -> dict:
    """
    Restituisce statistiche sulle Memory salvate.
    
    Returns:
        dict con statistiche
    """
    return {
        "total_memories": len(_memory_store),
        "menu_ids": list(_memory_store.keys())
    }
