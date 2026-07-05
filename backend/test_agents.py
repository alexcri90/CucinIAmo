"""Test del sistema di agenti."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents import create_agent_system
from backend.models import UserInput, Cuisine, DifficultyLevel


def test_menu_agent_simple():
    """Test base del menu agent."""
    print("🧪 Test Menu Agent - Invocazione Semplice...\n")
    
    menu_agent, _, _, _ = create_agent_system()
    
    prompt = """
    Suggeriscimi 2 piatti natalizi italiani tradizionali.
    Dimmi solo i nomi dei piatti.
    """
    
    response = menu_agent.run(prompt)
    print(f"✅ Risposta Menu Agent:\n{response.text}\n")
    
    return True


def test_tool_usage():
    """Test uso dei tool."""
    print("🧪 Test Tool Usage...\n")
    
    menu_agent, _, _, _ = create_agent_system()
    
    prompt = """
    Usa il tool get_christmas_dishes_by_cuisine per ottenere 
    i piatti natalizi francesi, poi elencameli.
    """
    
    response = menu_agent.run(prompt)
    print(f"✅ Risposta con Tool:\n{response.text}\n")
    
    return True


def test_validation_tool():
    """Test tool di validazione."""
    print("🧪 Test Validation Tool...\n")
    
    menu_agent, _, _, _ = create_agent_system()
    
    prompt = """
    Usa il tool validate_ingredients per verificare se posso usare 
    tartufo e noci in un piatto, sapendo che:
    - Ingredienti preferiti: ["tartufo"]
    - Ingredienti da evitare: ["noci"]
    - Ingredienti proposti: ["tartufo", "noci", "burro"]
    
    Dimmi il risultato.
    """
    
    response = menu_agent.run(prompt)
    print(f"✅ Risposta Validation:\n{response.text}\n")
    
    return True


if __name__ == "__main__":
    print("🤖 Testing Sistema Agenti Datapizza AI...\n")
    print("=" * 60)
    
    try:
        test_menu_agent_simple()
        print("=" * 60)
        
        test_tool_usage()
        print("=" * 60)
        
        test_validation_tool()
        print("=" * 60)
        
        print("\n✅ Tutti i test degli agenti passati!")
        
    except Exception as e:
        print(f"\n❌ Errore durante i test: {e}")
        raise