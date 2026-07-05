"""Tool per gestione ingredienti."""
import json
from datapizza.tools import tool


@tool
def validate_ingredients(
    preferred: list[str], 
    avoided: list[str], 
    proposed: list[str]
) -> str:
    """
    Valida che gli ingredienti proposti rispettino i vincoli.
    
    Args:
        preferred: Ingredienti che devono essere inclusi
        avoided: Ingredienti che devono essere esclusi
        proposed: Ingredienti proposti per un piatto
        
    Returns:
        JSON string con risultato validazione
    """
    proposed_set = {ing.lower() for ing in proposed}
    avoided_set = {ing.lower() for ing in avoided}
    preferred_set = {ing.lower() for ing in preferred}
    
    issues = []
    
    # Check ingredienti vietati
    violations = proposed_set & avoided_set
    if violations:
        issues.append(f"Ingredienti vietati presenti: {', '.join(violations)}")
    
    # Check ingredienti preferiti
    has_preferred = bool(proposed_set & preferred_set)
    missing_preferred = list(preferred_set - proposed_set)
    
    result = {
        "valid": len(issues) == 0,
        "issues": issues,
        "has_preferred_ingredients": has_preferred,
        "missing_preferred": missing_preferred
    }
    
    return json.dumps(result, ensure_ascii=False)


@tool
def get_christmas_dishes_by_cuisine(cuisine: str) -> str:
    """
    Restituisce piatti natalizi tipici per una data cucina.
    
    Args:
        cuisine: Nome della cucina (italiana, francese, etc.)
        
    Returns:
        Stringa con lista di piatti natalizi separati da virgola
    """
    christmas_dishes = {
        "italiana": [
            "Cappone ripieno", "Tortellini in brodo", "Capitone fritto",
            "Pandoro", "Panettone", "Baccalà alla vicentina",
            "Lasagne", "Cotechino con lenticchie", "Struffoli"
        ],
        "francese": [
            "Foie gras", "Bûche de Noël", "Dinde aux marrons",
            "Huîtres", "Saumon fumé", "Chapon rôti"
        ],
        "tedesca": [
            "Gans (oca arrosto)", "Stollen", "Kartoffelsalat",
            "Würstchen", "Lebkuchen", "Glühwein"
        ],
        "spagnola": [
            "Cordero asado", "Turrón", "Polvorones",
            "Cochinillo", "Besugo al horno", "Mazapán"
        ],
        "inglese": [
            "Roast turkey", "Christmas pudding", "Mince pies",
            "Roast beef", "Yorkshire pudding", "Trifle"
        ],
        "polacca": [
            "Barszcz (borscht)", "Pierogi", "Karp smażony",
            "Bigos", "Kutia", "Makowiec"
        ],
        "greca": [
            "Christopsomo", "Melomakarona", "Kourabiedes",
            "Galaktoboureko", "Spanakopita"
        ],
        "scandinava": [
            "Julskinka", "Gravlax", "Janssons frestelse",
            "Risgrynsgröt", "Lussekatter", "Glögg"
        ],
        "americana": [
            "Roast turkey", "Glazed ham", "Pumpkin pie",
            "Pecan pie", "Cranberry sauce", "Eggnog"
        ]
    }
    
    cuisine_lower = cuisine.lower()
    dishes = christmas_dishes.get(cuisine_lower, [])
    
    if dishes:
        return ", ".join(dishes)
    else:
        return f"Nessun piatto natalizio trovato per la cucina: {cuisine}"


@tool
def suggest_ingredient_substitution(
    ingredient: str, 
    reason: str
) -> str:
    """
    Suggerisce sostituzioni per un ingrediente.
    
    Args:
        ingredient: Ingrediente da sostituire
        reason: Motivo (allergia, dieta, disponibilità)
        
    Returns:
        JSON string con alternative suggerite
    """
    substitutions = {
        "burro": {
            "vegano": ["margarina vegetale", "olio di cocco"],
            "lattosio": ["burro chiarificato", "ghee"],
            "default": ["olio extravergine", "strutto"]
        },
        "uova": {
            "vegano": ["aquafaba", "semi di lino macinati", "banana"],
            "default": ["lecitina di soia"]
        },
        "farina": {
            "glutine": ["farina di riso", "farina di mais", "farina di mandorle"],
            "default": ["amido di mais", "fecola"]
        },
        "latte": {
            "vegano": ["latte di soia", "latte di avena", "latte di mandorla"],
            "lattosio": ["latte delattosato", "latte di riso"],
            "default": ["panna diluita"]
        },
        "panna": {
            "vegano": ["panna di soia", "crema di cocco"],
            "lattosio": ["panna delattosata"],
            "default": ["mascarpone diluito", "ricotta frullata"]
        }
    }
    
    ingredient_lower = ingredient.lower()
    reason_lower = reason.lower()
    
    result = {}
    
    if ingredient_lower in substitutions:
        subs = substitutions[ingredient_lower]
        if reason_lower in subs:
            result = {"alternatives": subs[reason_lower], "for_reason": reason}
        else:
            result = {"alternatives": subs.get("default", []), "for_reason": "generale"}
    else:
        result = {"alternatives": [], "note": "Nessuna sostituzione standard disponibile"}
    
    return json.dumps(result, ensure_ascii=False)