"""Test dei custom tools."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.tools.ingredient_tools import (
    validate_ingredients,
    get_christmas_dishes_by_cuisine,
    suggest_ingredient_substitution
)
from backend.tools.calculation_tools import (
    calculate_portions,
    estimate_prep_time
)


def test_validate_ingredients():
    """Test validazione ingredienti."""
    print("🧪 Test validate_ingredients...")
    
    result = validate_ingredients(
        preferred=["tartufo", "salmone"],
        avoided=["noci"],
        proposed=["tartufo", "burro", "parmigiano"]
    )
    
    assert result["valid"] == True
    assert result["has_preferred_ingredients"] == True
    print("✅ Ingredienti validi - OK")
    
    result = validate_ingredients(
        preferred=["tartufo"],
        avoided=["noci"],
        proposed=["noci", "burro"]
    )
    
    assert result["valid"] == False
    print("✅ Ingredienti vietati rilevati - OK")


def test_christmas_dishes():
    """Test piatti natalizi."""
    print("\n🧪 Test get_christmas_dishes_by_cuisine...")
    
    dishes = get_christmas_dishes_by_cuisine("italiana")
    assert "Panettone" in dishes
    print(f"✅ Piatti italiani: {len(dishes)} trovati")
    
    dishes = get_christmas_dishes_by_cuisine("francese")
    assert "Bûche de Noël" in dishes
    print(f"✅ Piatti francesi: {len(dishes)} trovati")


def test_calculate_portions():
    """Test calcolo porzioni."""
    print("\n🧪 Test calculate_portions...")
    
    result = calculate_portions("200g", 4, 8)
    assert result == "400g"
    print(f"✅ Scaling up: 200g x2 = {result}")
    
    result = calculate_portions("500g", 10, 5)
    assert result == "250g"
    print(f"✅ Scaling down: 500g /2 = {result}")


def test_estimate_prep_time():
    """Test stima tempi."""
    print("\n🧪 Test estimate_prep_time...")
    
    steps = [
        "Tagliare le verdure",
        "Far bollire l'acqua",
        "Cuocere la pasta",
        "Lasciar riposare"
    ]
    
    result = estimate_prep_time(steps, "medio")
    print(f"✅ Prep: {result['prep_time_minutes']}min, Cook: {result['cook_time_minutes']}min")
    assert result["prep_time_minutes"] > 0


def test_substitutions():
    """Test sostituzioni."""
    print("\n🧪 Test suggest_ingredient_substitution...")
    
    result = suggest_ingredient_substitution("burro", "vegano")
    assert len(result["alternatives"]) > 0
    print(f"✅ Alternative vegane per burro: {result['alternatives']}")


if __name__ == "__main__":
    print("🧪 Testing Custom Tools...\n")
    test_validate_ingredients()
    test_christmas_dishes()
    test_calculate_portions()
    test_estimate_prep_time()
    test_substitutions()
    print("\n✅ Tutti i test passati!")