"""Tool per calcoli e stime."""
import re
import json
from datapizza.tools import tool


@tool
def calculate_portions(
    base_quantity: str, 
    base_servings: int, 
    target_servings: int
) -> str:
    """
    Calcola le quantità scalate per il numero di porzioni.
    
    Args:
        base_quantity: Quantità base (es. "200g", "2 cucchiai")
        base_servings: Numero porzioni della ricetta base
        target_servings: Numero porzioni desiderate
        
    Returns:
        Quantità scalata come stringa
    """
    # Estrai numero e unità
    match = re.match(r'([\d.,]+)\s*(\w+)?', base_quantity)
    if not match:
        return base_quantity
    
    number = float(match.group(1).replace(',', '.'))
    unit = match.group(2) or ''
    
    # Calcola scaling factor
    factor = target_servings / base_servings
    new_quantity = number * factor
    
    # Formatta output
    if new_quantity == int(new_quantity):
        return f"{int(new_quantity)}{unit}"
    else:
        return f"{new_quantity:.1f}{unit}"


@tool
def estimate_prep_time(
    steps: list[str], 
    difficulty: str
) -> str:
    """
    Stima i tempi di preparazione basandosi sugli step.
    
    Args:
        steps: Lista degli step di preparazione
        difficulty: Livello difficoltà (facile, medio, avanzato)
        
    Returns:
        JSON string con stime tempi
    """
    # Tempo base per step in base alla difficoltà
    time_per_step = {
        "facile": 3,
        "medio": 5,
        "avanzato": 8
    }
    
    base_time = time_per_step.get(difficulty.lower(), 5)
    
    # Analisi keywords negli step per aggiustamenti
    cooking_keywords = ["cuocere", "bollire", "friggere", "arrostire", "infornare"]
    rest_keywords = ["riposare", "lievitare", "marinare", "raffreddare"]
    
    prep_minutes = 0
    cook_minutes = 0
    rest_minutes = 0
    
    for step in steps:
        step_lower = step.lower()
        
        if any(kw in step_lower for kw in rest_keywords):
            if "lievitare" in step_lower:
                rest_minutes += 60
            elif "marinare" in step_lower:
                rest_minutes += 30
            else:
                rest_minutes += 15
        elif any(kw in step_lower for kw in cooking_keywords):
            cook_minutes += 15
        else:
            prep_minutes += base_time
    
    result = {
        "prep_time_minutes": max(prep_minutes, 10),
        "cook_time_minutes": cook_minutes,
        "rest_time_minutes": rest_minutes,
        "total_active_time": prep_minutes + cook_minutes,
        "total_time_with_rest": prep_minutes + cook_minutes + rest_minutes
    }
    
    return json.dumps(result, ensure_ascii=False)