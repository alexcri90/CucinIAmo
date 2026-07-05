"""Menu Agent - Planner principale per la generazione del menù."""
import os
from datapizza.agents import Agent
from datapizza.memory import Memory

from backend.config import create_google_client
from backend.tools.ingredient_tools import (
    validate_ingredients,
    get_christmas_dishes_by_cuisine
)
from backend.tools.calculation_tools import calculate_portions

# Imposta log level per debugging
os.environ["DATAPIZZA_AGENT_LOG_LEVEL"] = "DEBUG"

MENU_PLANNER_SYSTEM_PROMPT = """
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

STRUTTURA MENÙ:
- 1-2 Antipasti (almeno uno preparabile in anticipo)
- 1 Primo piatto (tipico natalizio)
- 1 Secondo + 1 Contorno
- 1-2 Dessert (tipici natalizi)

Per ogni piatto fornisci:
- Nome (originale + traduzione se necessario)
- Origine/cucina
- Descrizione appetitosa (2-3 righe)
- Ricetta COMPLETA con ingredienti, quantità esatte, tempi, procedimento, note chef
- Info preparazione anticipata

OUTPUT:
Quando richiesto, produci un output strutturato JSON che includa:
- Tutti i piatti con ricette dettagliate
- Lista spesa aggregata per categorie
- Timeline di preparazione (2 giorni prima, 1 giorno prima, giorno stesso)
"""


def create_menu_agent(memory: Memory = None) -> Agent:
    """
    Crea e configura il Menu Planner Agent.
    
    Args:
        memory: Oggetto Memory per mantenere il contesto (opzionale)
        
    Returns:
        Agent configurato per la pianificazione del menù
    """
    client = create_google_client(
        system_prompt=MENU_PLANNER_SYSTEM_PROMPT,
        temperature=0.7
    )
    
    agent = Agent(
        name="menu_planner",
        client=client,
        tools=[
            validate_ingredients,
            calculate_portions,
            get_christmas_dishes_by_cuisine
        ],
        memory=memory,
        max_steps=10,
        planning_interval=3
    )
    
    return agent