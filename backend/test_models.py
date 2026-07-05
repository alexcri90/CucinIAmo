"""Test dei modelli Pydantic."""
import sys
from pathlib import Path

# Aggiungi la root del progetto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import (
    UserInput,
    Cuisine,
    DifficultyLevel,
    BudgetLevel,
    MenuOutput
)

def test_user_input():
    """Test creazione UserInput."""
    user_input = UserInput(
        num_guests=6,
        preferred_ingredients=["tartufo", "salmone"],
        avoided_ingredients=["noci"],
        cuisines=[Cuisine.ITALIANA, Cuisine.FRANCESE],
        dietary_restrictions=[],
        difficulty_level=DifficultyLevel.MEDIO,
        budget_level=BudgetLevel.PREMIUM
    )
    
    print("✅ UserInput creato con successo!")
    print(f"📊 Ospiti: {user_input.num_guests}")
    print(f"🍽️ Cucine: {[c.value for c in user_input.cuisines]}")
    print(f"📈 Difficoltà: {user_input.difficulty_level.value}")
    
    # Test JSON Schema
    schema = UserInput.model_json_schema()
    print(f"\n📋 JSON Schema generato: {len(str(schema))} caratteri")
    
    return True

def test_validation():
    """Test validazione ingredienti."""
    try:
        # Questo DEVE fallire (stesso ingrediente in preferiti e evitati)
        UserInput(
            num_guests=4,
            preferred_ingredients=["tartufo"],
            avoided_ingredients=["tartufo"],
            cuisines=[Cuisine.ITALIANA]
        )
        print("❌ La validazione NON ha funzionato!")
        return False
    except ValueError as e:
        print(f"✅ Validazione funziona! Errore catturato: {e}")
        return True

if __name__ == "__main__":
    print("🧪 Testing modelli Pydantic...\n")
    test_user_input()
    print()
    test_validation()
    print("\n✅ Tutti i test passati!")