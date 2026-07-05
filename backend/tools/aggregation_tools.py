"""Tool per aggregazione liste spesa e timeline."""
import re
import json
from collections import defaultdict
from datapizza.tools import tool


@tool
def aggregate_ingredients(ingredients_lists: list[list[dict]]) -> str:
    """
    Aggrega liste di ingredienti sommando le quantità.
    
    Args:
        ingredients_lists: Lista di liste di ingredienti
        
    Returns:
        JSON string con ingredienti aggregati per categoria
    """
    aggregated = defaultdict(lambda: defaultdict(lambda: {"quantity": 0, "unit": ""}))
    
    def parse_quantity(qty_str: str) -> tuple:
        """Estrae numero e unità da una stringa quantità."""
        match = re.match(r'([\d.,]+)\s*(\w*)', qty_str)
        if match:
            num = float(match.group(1).replace(',', '.'))
            unit = match.group(2) or 'pz'
            return num, unit
        return 1, 'pz'
    
    for ing_list in ingredients_lists:
        for ing in ing_list:
            name = ing.get('name', '').lower()
            category = ing.get('category', 'Altro')
            qty_str = ing.get('quantity', '1')
            
            num, unit = parse_quantity(qty_str)
            
            current = aggregated[category][name]
            if current["unit"] == "" or current["unit"] == unit:
                current["quantity"] += num
                current["unit"] = unit
            else:
                aggregated[category][f"{name} ({unit})"]["quantity"] += num
                aggregated[category][f"{name} ({unit})"]["unit"] = unit
    
    # Converti in formato output
    result = {}
    for category, items in aggregated.items():
        result[category] = [
            {
                "name": name.title(),
                "quantity": f"{v['quantity']:.0f}{v['unit']}" if v['quantity'] == int(v['quantity']) 
                           else f"{v['quantity']:.1f}{v['unit']}",
                "category": category
            }
            for name, v in items.items()
        ]
    
    return json.dumps(result, ensure_ascii=False)


@tool
def generate_timeline_structure(
    recipes: list[dict], 
    serving_time: str = "13:00"
) -> str:
    """
    Genera la struttura della timeline di preparazione.
    
    Args:
        recipes: Lista ricette con info su prep anticipata
        serving_time: Ora prevista per servire (formato HH:MM)
        
    Returns:
        JSON string con timeline strutturata
    """
    two_days = []
    one_day = []
    day_of = {}
    
    # Analizza le ricette per preparazioni anticipate
    for recipe in recipes:
        name = recipe.get("name", "Piatto")
        can_prep = recipe.get("can_prep_ahead", False)
        prep_timing = recipe.get("prep_ahead_timing", "")
        
        if can_prep:
            if "2 giorni" in prep_timing.lower():
                two_days.append(f"Preparare {name}")
            elif "1 giorno" in prep_timing.lower() or "vigilia" in prep_timing.lower():
                one_day.append(f"Preparare {name}")
    
    # Genera timeline giorno stesso
    try:
        hour, minute = map(int, serving_time.split(':'))
    except:
        hour, minute = 13, 0
    
    day_of = {
        f"{hour-4:02d}:00": "Iniziare preparazioni principali",
        f"{hour-2:02d}:00": "Preparare contorni",
        f"{hour-1:02d}:00": "Cotture finali",
        f"{hour:02d}:30": "Impiattamento antipasti",
        serving_time: "Servire antipasti"
    }
    
    result = {
        "two_days_before": two_days if two_days else ["Nessuna preparazione richiesta"],
        "one_day_before": one_day if one_day else ["Fare la spesa", "Organizzare gli ingredienti"],
        "day_of": day_of
    }
    
    return json.dumps(result, ensure_ascii=False)