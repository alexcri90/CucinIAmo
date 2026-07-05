"""Recipe Agent - Detailer per ricette dettagliate."""
from datapizza.agents import Agent
from datapizza.memory import Memory

from backend.config import create_google_client
from backend.tools.ingredient_tools import suggest_ingredient_substitution
from backend.tools.calculation_tools import estimate_prep_time

RECIPE_DETAILER_SYSTEM_PROMPT = """
Sei uno chef professionista specializzato nella scrittura di ricette dettagliate.

COMPETENZE:
- Scrivi procedimenti chiari e step-by-step
- Calcoli le quantità con precisione per qualsiasi numero di porzioni
- Conosci i tempi di preparazione e cottura realistici
- Fornisci tips professionali e varianti
- Identifichi cosa può essere preparato in anticipo

FORMATO OUTPUT:
Per ogni ricetta fornisci:
1. Lista ingredienti con quantità esatte
2. Tempo preparazione e cottura separati
3. Procedimento numerato (ogni step max 2 frasi)
4. Note dello chef (tips, varianti, sostituzioni)
5. Indicazione se preparabile in anticipo e quando

STILE:
- Linguaggio chiaro e accessibile
- Terminologia culinaria corretta ma spiegata
- Step logici e sequenziali
- Quantità precise (mai "q.b." senza indicazione)

CATEGORIE INGREDIENTI:
Classifica ogni ingrediente in una di queste categorie:
- Frutta e verdura
- Carne
- Pesce
- Latticini
- Dispensa (farina, zucchero, spezie, olio, etc.)
- Altro
"""


def create_recipe_agent(memory: Memory = None) -> Agent:
    """
    Crea e configura il Recipe Detailer Agent.
    
    Args:
        memory: Oggetto Memory per mantenere il contesto (opzionale)
        
    Returns:
        Agent configurato per dettagli ricette
    """
    client = create_google_client(
        system_prompt=RECIPE_DETAILER_SYSTEM_PROMPT,
        temperature=0.5
    )
    
    agent = Agent(
        name="recipe_detailer",
        client=client,
        tools=[
            suggest_ingredient_substitution,
            estimate_prep_time
        ],
        memory=memory,
        max_steps=5
    )
    
    return agent