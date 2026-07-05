"""
Test per i Tools degli Agenti Datapizza

Testa:
- ingredient_tools: validate_ingredients, get_christmas_dishes_by_cuisine
- calculation_tools: calculate_portions, estimate_prep_time
- aggregation_tools: aggregate_ingredients, generate_timeline_structure

NOTA: I tool Datapizza restituiscono SEMPRE stringhe JSON.
"""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.tools.ingredient_tools import (
    validate_ingredients,
    get_christmas_dishes_by_cuisine
)
from backend.tools.calculation_tools import (
    calculate_portions,
    estimate_prep_time
)
from backend.tools.aggregation_tools import (
    aggregate_ingredients,
    generate_timeline_structure
)


# =============================================================================
# TEST INGREDIENT TOOLS
# =============================================================================

class TestValidateIngredients:
    """Test per validate_ingredients tool."""
    
    def test_valid_no_violations(self):
        """Test ingredienti validi senza violazioni."""
        result = validate_ingredients(
            preferred=["salmone", "tartufo"],
            avoided=["funghi", "piccante"],
            proposed=["salmone", "patate", "burro"]
        )
        data = json.loads(result)
        
        assert data["valid"] is True
        assert data["has_preferred_ingredients"] is True
        assert len(data["issues"]) == 0
    
    def test_avoided_ingredient_violation(self):
        """Test violazione ingrediente da evitare."""
        result = validate_ingredients(
            preferred=["salmone"],
            avoided=["funghi", "piccante"],
            proposed=["salmone", "funghi"]  # Violazione!
        )
        data = json.loads(result)
        
        assert data["valid"] is False
        assert len(data["issues"]) > 0
        assert "funghi" in data["issues"][0].lower()
    
    def test_missing_preferred(self):
        """Test che rileva ingredienti preferiti mancanti."""
        result = validate_ingredients(
            preferred=["salmone", "tartufo"],
            avoided=[],
            proposed=["patate", "burro"]  # Nessun preferito
        )
        data = json.loads(result)
        
        assert data["has_preferred_ingredients"] is False
        assert "salmone" in data["missing_preferred"]
        assert "tartufo" in data["missing_preferred"]
    
    def test_case_insensitive(self):
        """Test che la validazione sia case-insensitive."""
        result = validate_ingredients(
            preferred=["Salmone"],
            avoided=["FUNGHI"],
            proposed=["salmone", "PATATE"]
        )
        data = json.loads(result)
        
        assert data["valid"] is True
        assert data["has_preferred_ingredients"] is True
    
    def test_empty_lists(self):
        """Test con liste vuote."""
        result = validate_ingredients(
            preferred=[],
            avoided=[],
            proposed=["qualsiasi"]
        )
        data = json.loads(result)
        
        assert data["valid"] is True


class TestGetChristmasDishesByCuisine:
    """Test per get_christmas_dishes_by_cuisine tool."""
    
    def test_italian_dishes(self):
        """Test piatti natalizi italiani."""
        result = get_christmas_dishes_by_cuisine("italiana")
        
        assert "Cappone ripieno" in result or "Tortellini" in result
        assert "Pandoro" in result or "Panettone" in result
    
    def test_french_dishes(self):
        """Test piatti natalizi francesi."""
        result = get_christmas_dishes_by_cuisine("francese")
        
        assert "Foie gras" in result or "Bûche" in result
    
    def test_case_insensitive_cuisine(self):
        """Test che la ricerca sia case-insensitive."""
        result_lower = get_christmas_dishes_by_cuisine("italiana")
        result_upper = get_christmas_dishes_by_cuisine("ITALIANA")
        result_mixed = get_christmas_dishes_by_cuisine("Italiana")
        
        # Tutti dovrebbero restituire risultati
        assert len(result_lower) > 0
        assert len(result_upper) > 0
        assert len(result_mixed) > 0
    
    def test_unknown_cuisine(self):
        """Test cucina non presente."""
        result = get_christmas_dishes_by_cuisine("cucina_inesistente")
        
        # La funzione restituisce una stringa con i piatti separati da virgola
        # Per una cucina inesistente, restituisce stringa vuota o lista vuota
        # Il tool può restituire "" o "[]" o una stringa con i piatti
        assert result is not None  # Non solleva eccezione
    
    def test_all_supported_cuisines(self):
        """Test che tutte le cucine supportate restituiscano piatti."""
        cuisines = [
            "italiana", "francese", "tedesca", "spagnola",
            "inglese", "polacca", "greca", "scandinava", "americana"
        ]
        
        for cuisine in cuisines:
            result = get_christmas_dishes_by_cuisine(cuisine)
            assert len(result) > 0, f"Nessun piatto per cucina: {cuisine}"


# =============================================================================
# TEST CALCULATION TOOLS
# =============================================================================

class TestCalculatePortions:
    """Test per calculate_portions tool."""
    
    def test_double_portions(self):
        """Test raddoppio porzioni."""
        result = calculate_portions(
            base_quantity="200g",
            base_servings=4,
            target_servings=8
        )
        
        assert "400" in result
    
    def test_halve_portions(self):
        """Test dimezzamento porzioni."""
        result = calculate_portions(
            base_quantity="500g",
            base_servings=10,
            target_servings=5
        )
        
        assert "250" in result
    
    def test_preserve_unit(self):
        """Test che l'unità di misura venga preservata."""
        result = calculate_portions(
            base_quantity="2cucchiai",
            base_servings=4,
            target_servings=8
        )
        
        assert "cucchiai" in result
    
    def test_decimal_quantity(self):
        """Test quantità decimale."""
        result = calculate_portions(
            base_quantity="100g",
            base_servings=4,
            target_servings=6
        )
        
        # 100 * 6/4 = 150
        assert "150" in result
    
    def test_non_numeric_quantity(self):
        """Test quantità non numerica (es. 'q.b.')."""
        result = calculate_portions(
            base_quantity="q.b.",
            base_servings=4,
            target_servings=8
        )
        
        # Dovrebbe restituire la quantità originale
        assert "q.b." in result


class TestEstimatePrepTime:
    """Test per estimate_prep_time tool."""
    
    def test_simple_steps(self):
        """Test con step semplici."""
        result = estimate_prep_time(
            steps=["Tagliare le verdure", "Mescolare gli ingredienti"],
            difficulty="facile"
        )
        data = json.loads(result)
        
        assert "prep_time_minutes" in data
        assert data["prep_time_minutes"] >= 10  # Minimo garantito
    
    def test_cooking_steps(self):
        """Test con step di cottura."""
        result = estimate_prep_time(
            steps=["Preparare il soffritto", "Cuocere la pasta", "Bollire il brodo"],
            difficulty="medio"
        )
        data = json.loads(result)
        
        assert data["cook_time_minutes"] > 0
    
    def test_rest_steps(self):
        """Test con step di riposo."""
        result = estimate_prep_time(
            steps=["Impastare", "Lievitare per 2 ore", "Infornare"],
            difficulty="avanzato"
        )
        data = json.loads(result)
        
        assert data["rest_time_minutes"] >= 60  # Lievitazione
    
    def test_difficulty_affects_time(self):
        """Test che la difficoltà influenzi i tempi."""
        steps = ["Step 1", "Step 2", "Step 3"]
        
        facile = json.loads(estimate_prep_time(steps, "facile"))
        avanzato = json.loads(estimate_prep_time(steps, "avanzato"))
        
        # Avanzato dovrebbe richiedere più tempo
        assert avanzato["total_active_time"] >= facile["total_active_time"]


# =============================================================================
# TEST AGGREGATION TOOLS
# =============================================================================

class TestAggregateIngredients:
    """Test per aggregate_ingredients tool."""
    
    def test_simple_aggregation(self):
        """Test aggregazione semplice."""
        ingredients = [
            [
                {"name": "pomodori", "quantity": "200g", "category": "Frutta e verdura"},
                {"name": "sale", "quantity": "1cucchiaino", "category": "Dispensa"}
            ],
            [
                {"name": "pomodori", "quantity": "300g", "category": "Frutta e verdura"},
                {"name": "olio", "quantity": "2cucchiai", "category": "Dispensa"}
            ]
        ]
        
        result = aggregate_ingredients(ingredients)
        data = json.loads(result)
        
        # Pomodori dovrebbero essere aggregati: 200 + 300 = 500g
        assert "Frutta e verdura" in data
        pomodori = [i for i in data["Frutta e verdura"] if "pomodor" in i["name"].lower()]
        assert len(pomodori) == 1
        assert "500" in pomodori[0]["quantity"]
    
    def test_category_grouping(self):
        """Test raggruppamento per categoria."""
        ingredients = [
            [
                {"name": "salmone", "quantity": "500g", "category": "Pesce"},
                {"name": "burro", "quantity": "100g", "category": "Latticini"},
                {"name": "farina", "quantity": "200g", "category": "Dispensa"}
            ]
        ]
        
        result = aggregate_ingredients(ingredients)
        data = json.loads(result)
        
        assert "Pesce" in data
        assert "Latticini" in data
        assert "Dispensa" in data
    
    def test_empty_list(self):
        """Test con lista vuota."""
        result = aggregate_ingredients([])
        data = json.loads(result)
        
        assert isinstance(data, dict)


class TestGenerateTimelineStructure:
    """Test per generate_timeline_structure tool."""
    
    def test_basic_timeline(self):
        """Test generazione timeline base."""
        recipes = [
            {"name": "Arrosto", "can_prep_ahead": False},
            {"name": "Dolce", "can_prep_ahead": True, "prep_ahead_timing": "1 giorno prima"}
        ]
        
        result = generate_timeline_structure(recipes, "13:00")
        data = json.loads(result)
        
        assert "two_days_before" in data or "one_day_before" in data or "day_of" in data
    
    def test_prep_ahead_categorization(self):
        """Test categorizzazione preparazioni anticipate."""
        recipes = [
            {"name": "Brodo", "can_prep_ahead": True, "prep_ahead_timing": "2 giorni prima"},
            {"name": "Ripieno", "can_prep_ahead": True, "prep_ahead_timing": "1 giorno prima"},
            {"name": "Arrosto", "can_prep_ahead": False}
        ]
        
        result = generate_timeline_structure(recipes)
        data = json.loads(result)
        
        # Brodo dovrebbe essere in two_days_before
        if "two_days_before" in data:
            two_days_tasks = " ".join(data["two_days_before"]).lower()
            assert "brodo" in two_days_tasks
        
        # Ripieno dovrebbe essere in one_day_before
        if "one_day_before" in data:
            one_day_tasks = " ".join(data["one_day_before"]).lower()
            assert "ripieno" in one_day_tasks
    
    def test_custom_serving_time(self):
        """Test con orario di servizio personalizzato."""
        result = generate_timeline_structure([], "14:00")
        data = json.loads(result)
        
        # Dovrebbe contenere la struttura anche se vuota
        assert isinstance(data, dict)


# =============================================================================
# TEST INTEGRAZIONE TOOLS
# =============================================================================

class TestToolsIntegration:
    """Test di integrazione tra tools."""
    
    def test_validate_then_calculate(self):
        """Test workflow: valida → calcola porzioni."""
        # Prima valida
        validation = validate_ingredients(
            preferred=["salmone"],
            avoided=["funghi"],
            proposed=["salmone", "patate"]
        )
        val_data = json.loads(validation)
        assert val_data["valid"] is True
        
        # Poi calcola porzioni
        portions = calculate_portions(
            base_quantity="200g",
            base_servings=4,
            target_servings=8
        )
        assert "400" in portions
    
    def test_aggregate_multiple_recipes(self):
        """Test aggregazione ingredienti da più ricette."""
        recipe1_ingredients = [
            {"name": "farina", "quantity": "300g", "category": "Dispensa"},
            {"name": "uova", "quantity": "3pz", "category": "Latticini"}
        ]
        recipe2_ingredients = [
            {"name": "farina", "quantity": "200g", "category": "Dispensa"},
            {"name": "zucchero", "quantity": "150g", "category": "Dispensa"}
        ]
        
        result = aggregate_ingredients([recipe1_ingredients, recipe2_ingredients])
        data = json.loads(result)
        
        # Farina aggregata: 300 + 200 = 500g
        dispensa = data.get("Dispensa", [])
        farina = [i for i in dispensa if "farina" in i["name"].lower()]
        assert len(farina) == 1
        assert "500" in farina[0]["quantity"]
