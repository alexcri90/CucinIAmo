"""
Test per i modelli Pydantic - Input, Menu e Output Models

Testa:
- Validazione campi
- Enum values
- Constraints (min/max)
- Field validators custom
- Serializzazione JSON
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import UUID

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.input_models import (
    UserInput,
    Cuisine,
    DifficultyLevel,
    BudgetLevel,
    DietaryRestriction
)
from backend.models.menu_models import (
    Course,
    Recipe,
    Ingredient,
    MenuCourses
)
from backend.models.output_models import (
    MenuOutput,
    ShoppingList,
    Timeline
)


# =============================================================================
# TEST ENUM VALUES
# =============================================================================

class TestEnums:
    """Test per verificare i valori delle enum."""
    
    def test_cuisine_values(self):
        """Verifica che tutte le cucine siano presenti."""
        expected = {
            "italiana", "spagnola", "francese", "tedesca", 
            "inglese", "polacca", "greca", "americana", "scandinava"
        }
        actual = {c.value for c in Cuisine}
        assert actual == expected, f"Mancanti: {expected - actual}"
    
    def test_difficulty_values(self):
        """Verifica livelli di difficoltà."""
        expected = {"facile", "medio", "avanzato"}
        actual = {d.value for d in DifficultyLevel}
        assert actual == expected
    
    def test_budget_values(self):
        """Verifica livelli di budget."""
        expected = {"economico", "medio", "premium"}
        actual = {b.value for b in BudgetLevel}
        assert actual == expected
    
    def test_dietary_restriction_values(self):
        """Verifica restrizioni alimentari."""
        expected = {"vegetariano", "vegano", "senza_glutine", "senza_lattosio"}
        actual = {d.value for d in DietaryRestriction}
        assert actual == expected


# =============================================================================
# TEST USER INPUT
# =============================================================================

class TestUserInput:
    """Test per il modello UserInput."""
    
    def test_valid_input_minimal(self):
        """Test creazione con campi minimi obbligatori."""
        user_input = UserInput(
            num_guests=4,
            cuisines=[Cuisine.ITALIANA]
        )
        assert user_input.num_guests == 4
        assert len(user_input.cuisines) == 1
        assert user_input.difficulty_level == DifficultyLevel.MEDIO  # default
        assert user_input.budget_level == BudgetLevel.MEDIO  # default
    
    def test_valid_input_full(self, valid_user_input):
        """Test creazione con tutti i campi."""
        assert valid_user_input.num_guests == 6
        assert Cuisine.ITALIANA in valid_user_input.cuisines
        assert "salmone" in valid_user_input.preferred_ingredients
        assert "piccante" in valid_user_input.avoided_ingredients
    
    def test_num_guests_minimum(self):
        """Test vincolo minimo ospiti (1)."""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(num_guests=0, cuisines=[Cuisine.ITALIANA])
        assert "greater than or equal to 1" in str(exc_info.value)
    
    def test_num_guests_one_accepted(self):
        """Test che 1 ospite sia accettato."""
        user_input = UserInput(num_guests=1, cuisines=[Cuisine.ITALIANA])
        assert user_input.num_guests == 1
    
    def test_num_guests_maximum(self):
        """Test vincolo massimo ospiti (50)."""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(num_guests=100, cuisines=[Cuisine.ITALIANA])
        assert "less than or equal to 50" in str(exc_info.value)
    
    def test_cuisines_required(self):
        """Test che almeno una cucina sia richiesta."""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(num_guests=4, cuisines=[])
        assert "at least 1" in str(exc_info.value).lower()
    
    def test_ingredient_overlap_validation(self):
        """Test che preferiti e evitati non si sovrappongano."""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                num_guests=4,
                cuisines=[Cuisine.ITALIANA],
                preferred_ingredients=["tartufo", "salmone"],
                avoided_ingredients=["tartufo"]  # Overlap!
            )
        assert "preferiti che evitati" in str(exc_info.value).lower() or "overlap" in str(exc_info.value).lower()
    
    def test_ingredient_normalization(self):
        """Test che gli ingredienti vengano normalizzati (lowercase, trim)."""
        user_input = UserInput(
            num_guests=4,
            cuisines=[Cuisine.ITALIANA],
            preferred_ingredients=["  SALMONE  ", "Tartufo"]
        )
        assert "salmone" in user_input.preferred_ingredients
        assert "tartufo" in user_input.preferred_ingredients
    
    def test_json_serialization(self, valid_user_input):
        """Test serializzazione JSON."""
        json_str = valid_user_input.model_dump_json()
        assert "num_guests" in json_str
        assert "italiana" in json_str
    
    def test_multiple_cuisines(self):
        """Test input con multiple cucine."""
        user_input = UserInput(
            num_guests=10,
            cuisines=[Cuisine.ITALIANA, Cuisine.FRANCESE, Cuisine.GRECA]
        )
        assert len(user_input.cuisines) == 3


# =============================================================================
# TEST INGREDIENT
# =============================================================================

class TestIngredient:
    """Test per il modello Ingredient."""
    
    def test_valid_ingredient(self, sample_ingredient):
        """Test creazione ingrediente valido."""
        assert sample_ingredient.name == "Salmone affumicato"
        assert sample_ingredient.quantity == "200g"
        assert sample_ingredient.category == "Pesce"
    
    def test_ingredient_required_fields(self):
        """Test che tutti i campi siano obbligatori."""
        with pytest.raises(ValidationError):
            Ingredient(name="Test")  # Manca quantity e category
    
    def test_ingredient_categories(self):
        """Test diverse categorie ingredienti."""
        categories = [
            "Frutta e verdura", "Carne", "Pesce", 
            "Latticini", "Dispensa", "Altro"
        ]
        for cat in categories:
            ing = Ingredient(name="Test", quantity="100g", category=cat)
            assert ing.category == cat


# =============================================================================
# TEST RECIPE
# =============================================================================

class TestRecipe:
    """Test per il modello Recipe."""
    
    def test_valid_recipe(self, sample_recipe):
        """Test creazione ricetta valida."""
        assert len(sample_recipe.ingredients) == 3
        assert sample_recipe.prep_time_minutes == 15
        assert sample_recipe.difficulty == "facile"
        assert len(sample_recipe.steps) == 3
    
    def test_prep_time_minimum(self):
        """Test tempo preparazione minimo (5 min)."""
        with pytest.raises(ValidationError) as exc_info:
            Recipe(
                ingredients=[Ingredient(name="Test", quantity="1", category="Altro")],
                prep_time_minutes=2,  # Troppo basso!
                difficulty="facile",
                steps=["Step 1"]
            )
        assert "greater than or equal to 5" in str(exc_info.value)
    
    def test_steps_required(self):
        """Test che almeno uno step sia richiesto."""
        with pytest.raises(ValidationError) as exc_info:
            Recipe(
                ingredients=[Ingredient(name="Test", quantity="1", category="Altro")],
                prep_time_minutes=10,
                difficulty="facile",
                steps=[]  # Vuoto!
            )
        assert "at least 1" in str(exc_info.value).lower()
    
    def test_prep_ahead_fields(self, sample_recipe):
        """Test campi preparazione anticipata."""
        assert sample_recipe.can_prep_ahead is True
        assert sample_recipe.prep_ahead_timing == "1 giorno prima"


# =============================================================================
# TEST COURSE
# =============================================================================

class TestCourse:
    """Test per il modello Course."""
    
    def test_valid_course(self, sample_course):
        """Test creazione portata valida."""
        assert sample_course.name == "Salmone Norvegese con Aneto"
        assert sample_course.cuisine == "scandinava"
        assert sample_course.recipe is not None
        assert isinstance(sample_course.course_id, UUID)
    
    def test_description_min_length(self, sample_recipe):
        """Test lunghezza minima descrizione (20 char)."""
        with pytest.raises(ValidationError) as exc_info:
            Course(
                name="Test",
                cuisine="italiana",
                description="Troppo corta",  # < 20 caratteri
                recipe=sample_recipe
            )
        assert "at least 20" in str(exc_info.value).lower()
    
    def test_description_max_length(self, sample_recipe):
        """Test lunghezza massima descrizione (500 char)."""
        with pytest.raises(ValidationError) as exc_info:
            Course(
                name="Test",
                cuisine="italiana",
                description="A" * 501,  # > 500 caratteri
                recipe=sample_recipe
            )
        assert "at most 500" in str(exc_info.value).lower()
    
    def test_course_id_auto_generated(self, sample_recipe):
        """Test che course_id venga generato automaticamente."""
        course = Course(
            name="Test Course",
            cuisine="italiana",
            description="Questa è una descrizione valida con più di venti caratteri.",
            recipe=sample_recipe
        )
        assert course.course_id is not None
        assert isinstance(course.course_id, UUID)


# =============================================================================
# TEST MENU COURSES
# =============================================================================

class TestMenuCourses:
    """Test per il modello MenuCourses."""
    
    def test_valid_menu_courses(self, sample_menu_courses):
        """Test struttura menù completa."""
        assert len(sample_menu_courses.antipasti) >= 1
        assert len(sample_menu_courses.primo) == 1
        assert len(sample_menu_courses.secondo) == 1
        assert len(sample_menu_courses.contorno) == 1
        assert len(sample_menu_courses.dessert) >= 1
    
    def test_antipasti_max_two(self, sample_course):
        """Test massimo 2 antipasti."""
        with pytest.raises(ValidationError):
            MenuCourses(
                antipasti=[sample_course, sample_course, sample_course],  # 3!
                primo=[sample_course],
                secondo=[sample_course],
                contorno=[sample_course],
                dessert=[sample_course]
            )


# =============================================================================
# TEST SHOPPING LIST
# =============================================================================

class TestShoppingList:
    """Test per il modello ShoppingList."""
    
    def test_valid_shopping_list(self, sample_shopping_list):
        """Test lista spesa valida."""
        assert "Pesce" in sample_shopping_list.categories
        assert len(sample_shopping_list.categories["Pesce"]) == 1
    
    def test_get_total_items(self, sample_shopping_list):
        """Test conteggio totale ingredienti."""
        total = sample_shopping_list.get_total_items()
        assert total == 3  # 1 pesce + 1 verdura + 1 dispensa
    
    def test_empty_categories(self):
        """Test lista con categorie vuote."""
        shopping = ShoppingList(categories={})
        assert shopping.get_total_items() == 0


# =============================================================================
# TEST TIMELINE
# =============================================================================

class TestTimeline:
    """Test per il modello Timeline."""
    
    def test_valid_timeline(self, sample_timeline):
        """Test timeline valida."""
        assert len(sample_timeline.two_days_before) == 2
        assert len(sample_timeline.one_day_before) == 2
        assert "09:00" in sample_timeline.day_of
    
    def test_empty_timeline(self):
        """Test timeline con sezioni vuote."""
        timeline = Timeline(
            two_days_before=[],
            one_day_before=[],
            day_of={}
        )
        assert len(timeline.two_days_before) == 0


# =============================================================================
# TEST MENU OUTPUT
# =============================================================================

class TestMenuOutput:
    """Test per il modello MenuOutput completo."""
    
    def test_valid_menu_output(self, sample_menu_output):
        """Test output menù completo."""
        assert sample_menu_output.menu_id is not None
        assert sample_menu_output.generated_at is not None
        assert sample_menu_output.input is not None
        assert sample_menu_output.courses is not None
        assert sample_menu_output.shopping_list is not None
        assert sample_menu_output.timeline is not None
    
    def test_menu_id_is_uuid(self, sample_menu_output):
        """Test che menu_id sia UUID."""
        assert isinstance(sample_menu_output.menu_id, UUID)
    
    def test_generated_at_is_datetime(self, sample_menu_output):
        """Test che generated_at sia datetime."""
        assert isinstance(sample_menu_output.generated_at, datetime)
    
    def test_full_json_serialization(self, sample_menu_output):
        """Test serializzazione JSON completa."""
        json_data = sample_menu_output.model_dump_json()
        assert "menu_id" in json_data
        assert "courses" in json_data
        assert "shopping_list" in json_data
        assert "timeline" in json_data
