"""Package agenti Datapizza AI."""
from datapizza.memory import Memory

from .menu_agent import create_menu_agent
from .recipe_agent import create_recipe_agent
from .aggregation_agent import create_aggregation_agent


def create_agent_system():
    """
    Crea il sistema di agenti interconnessi.
    
    Il Menu Agent può chiamare gli altri agenti per delegare task specifici.
    
    Returns:
        Tuple di (menu_agent, recipe_agent, aggregation_agent, shared_memory)
    """
    # Memory condivisa tra gli agenti per mantenere contesto
    shared_memory = Memory()
    
    # Crea gli agenti
    menu_agent = create_menu_agent(memory=shared_memory)
    recipe_agent = create_recipe_agent(memory=shared_memory)
    aggregation_agent = create_aggregation_agent(memory=shared_memory)
    
    # Configura le relazioni di chiamata
    # Il menu_agent può chiamare gli altri due agenti
    menu_agent.can_call([recipe_agent, aggregation_agent])
    
    return menu_agent, recipe_agent, aggregation_agent, shared_memory


__all__ = [
    "create_menu_agent",
    "create_recipe_agent", 
    "create_aggregation_agent",
    "create_agent_system",
]