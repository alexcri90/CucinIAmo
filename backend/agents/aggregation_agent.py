"""Aggregation Agent - Per lista spesa e timeline."""
from datapizza.agents import Agent
from datapizza.memory import Memory

from backend.config import create_google_client
from backend.tools.aggregation_tools import (
    aggregate_ingredients,
    generate_timeline_structure
)

AGGREGATION_SYSTEM_PROMPT = """
Sei un organizzatore esperto di eventi culinari.

COMPETENZE:
- Aggreghi liste ingredienti eliminando duplicati e sommando quantità
- Organizzi gli ingredienti per categoria (reparto del supermercato)
- Crei timeline di preparazione realistiche e ottimizzate
- Consideri i tempi di riposo e le preparazioni anticipate

OBIETTIVI:
1. Lista spesa: aggregata, senza duplicati, organizzata per categoria
2. Timeline: pratica, con orari specifici per il giorno stesso
3. Ottimizzazione: massimizzare le preparazioni anticipate

CATEGORIE INGREDIENTI:
- Frutta e verdura
- Carne
- Pesce
- Latticini
- Dispensa (farina, zucchero, spezie, etc.)
- Surgelati
- Bevande
- Altro

TIMELINE:
Organizza in:
- 2 giorni prima: preparazioni che si conservano bene
- 1 giorno prima (Vigilia): maggior parte della prep
- Giorno stesso: cotture finali e assemblaggio
"""


def create_aggregation_agent(memory: Memory = None) -> Agent:
    """
    Crea e configura l'Aggregation Agent.
    
    Args:
        memory: Oggetto Memory per mantenere il contesto (opzionale)
        
    Returns:
        Agent configurato per aggregazioni
    """
    client = create_google_client(
        system_prompt=AGGREGATION_SYSTEM_PROMPT,
        temperature=0.3
    )
    
    agent = Agent(
        name="aggregation_agent",
        client=client,
        tools=[
            aggregate_ingredients,
            generate_timeline_structure
        ],
        memory=memory,
        max_steps=5
    )
    
    return agent