"""
Test per Memory Manager di Datapizza AI

Verifica l'integrazione di Memory per:
- Salvataggio contesto menù
- Recupero Memory per rigenerazione
- Cleanup Memory
"""

import pytest
import sys
from pathlib import Path

# Aggiungi path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.memory_manager import (
    create_memory_for_menu,
    get_memory_for_menu,
    delete_memory_for_menu,
    save_menu_context_to_memory,
    build_user_input_summary,
    build_menu_summary,
    get_memory_stats
)


class TestMemoryStore:
    """Test per lo storage delle Memory."""
    
    def test_create_memory_for_menu(self):
        """Test creazione Memory per un menù."""
        menu_id = "test-menu-123"
        memory = create_memory_for_menu(menu_id)
        
        assert memory is not None
        
        # Cleanup
        delete_memory_for_menu(menu_id)
    
    def test_get_memory_for_menu_exists(self):
        """Test recupero Memory esistente."""
        menu_id = "test-menu-456"
        create_memory_for_menu(menu_id)
        
        memory = get_memory_for_menu(menu_id)
        assert memory is not None
        
        # Cleanup
        delete_memory_for_menu(menu_id)
    
    def test_get_memory_for_menu_not_exists(self):
        """Test recupero Memory non esistente."""
        memory = get_memory_for_menu("non-existent-menu")
        assert memory is None
    
    def test_delete_memory_for_menu_exists(self):
        """Test eliminazione Memory esistente."""
        menu_id = "test-menu-789"
        create_memory_for_menu(menu_id)
        
        result = delete_memory_for_menu(menu_id)
        assert result is True
        assert get_memory_for_menu(menu_id) is None
    
    def test_delete_memory_for_menu_not_exists(self):
        """Test eliminazione Memory non esistente."""
        result = delete_memory_for_menu("non-existent")
        assert result is False


class TestMemoryContext:
    """Test per il salvataggio del contesto."""
    
    def test_save_menu_context(self):
        """Test salvataggio contesto menù in Memory."""
        menu_id = "context-test-123"
        user_summary = "- Ospiti: 8\n- Cucine: italiana\n- Budget: medio"
        menu_summary = "ANTIPASTI:\n- Bruschette (italiana)\nPRIMO:\n- Lasagne (italiana)"
        
        memory = save_menu_context_to_memory(
            menu_id=menu_id,
            user_input_summary=user_summary,
            menu_summary=menu_summary
        )
        
        assert memory is not None
        
        # Verifica che la Memory contenga messaggi
        # (dipende dall'implementazione di Memory.messages o similar)
        
        # Cleanup
        delete_memory_for_menu(menu_id)
    
    def test_save_context_creates_memory_if_not_exists(self):
        """Test che save_context crei Memory se non esiste."""
        menu_id = "new-context-456"
        
        # Assicurati che non esista
        delete_memory_for_menu(menu_id)
        assert get_memory_for_menu(menu_id) is None
        
        # Salva contesto
        memory = save_menu_context_to_memory(
            menu_id=menu_id,
            user_input_summary="Test summary",
            menu_summary="Test menu"
        )
        
        # Verifica che sia stata creata
        assert get_memory_for_menu(menu_id) is not None
        
        # Cleanup
        delete_memory_for_menu(menu_id)


class TestSummaryBuilders:
    """Test per le funzioni di costruzione summary."""
    
    def test_build_user_input_summary(self):
        """Test costruzione summary preferenze utente."""
        # Import locale per evitare problemi di path
        from backend.models.input_models import (
            UserInput, Cuisine, DifficultyLevel, BudgetLevel, DietaryRestriction
        )
        
        user_input = UserInput(
            num_guests=6,
            cuisines=[Cuisine.ITALIANA, Cuisine.FRANCESE],
            preferred_ingredients=["salmone", "tartufo"],
            avoided_ingredients=["piccante"],
            dietary_restrictions=[DietaryRestriction.SENZA_GLUTINE],
            difficulty_level=DifficultyLevel.MEDIO,
            budget_level=BudgetLevel.PREMIUM
        )
        
        summary = build_user_input_summary(user_input)
        
        assert "6" in summary  # num_guests
        assert "italiana" in summary.lower()
        assert "francese" in summary.lower()
        assert "salmone" in summary
        assert "piccante" in summary
        assert "senza_glutine" in summary
        assert "medio" in summary.lower()
        assert "premium" in summary.lower()
    
    def test_build_menu_summary(self):
        """Test costruzione summary menù."""
        from backend.models.output_models import MenuOutput, ShoppingList, Timeline
        from backend.models.menu_models import MenuCourses, Course, Recipe, Ingredient
        from backend.models.input_models import UserInput, Cuisine, DifficultyLevel, BudgetLevel
        from uuid import uuid4
        from datetime import datetime
        
        # Crea un menù di test con tutti i corsi
        test_recipe = Recipe(
            ingredients=[
                Ingredient(name="pomodoro", quantity="500g", category="Frutta e verdura"),
                Ingredient(name="mozzarella", quantity="200g", category="Latticini")
            ],
            prep_time_minutes=30,
            cook_time_minutes=20,
            difficulty="facile",
            steps=["Passo 1", "Passo 2"],
            chef_notes="Note dello chef per preparare al meglio questo piatto festivo",
            can_prep_ahead=True,
            prep_ahead_timing="1 giorno prima"
        )
        
        test_course = Course(
            name="Caprese di Natale",
            cuisine="italiana",
            description="Una caprese festiva con mozzarella di bufala campana, pomodori freschi e basilico",
            recipe=test_recipe
        )
        
        # Tutti i corsi con almeno un elemento
        test_courses = MenuCourses(
            antipasti=[test_course],
            primo=[test_course],
            secondo=[test_course],
            contorno=[test_course],
            dessert=[test_course]
        )
        
        test_input = UserInput(
            num_guests=4,
            cuisines=[Cuisine.ITALIANA],
            difficulty_level=DifficultyLevel.FACILE,
            budget_level=BudgetLevel.ECONOMICO
        )
        
        test_shopping = ShoppingList(
            categories={
                "Frutta e verdura": [Ingredient(name="pomodoro", quantity="500g", category="Frutta e verdura")],
                "Latticini": [Ingredient(name="mozzarella", quantity="200g", category="Latticini")]
            }
        )
        
        test_timeline = Timeline(
            two_days_before=["Comprare gli ingredienti"],
            one_day_before=["Preparare la base"],
            day_of={"12:00": "Assemblare il piatto"}
        )
        
        test_menu = MenuOutput(
            menu_id=uuid4(),
            generated_at=datetime.now(),
            input=test_input,
            courses=test_courses,
            shopping_list=test_shopping,
            timeline=test_timeline
        )
        
        summary = build_menu_summary(test_menu)
        
        assert "ANTIPASTI" in summary
        assert "Caprese di Natale" in summary
        assert "italiana" in summary.lower()


class TestMemoryStats:
    """Test per le statistiche Memory."""
    
    def test_get_memory_stats(self):
        """Test recupero statistiche."""
        # Crea alcune Memory
        create_memory_for_menu("stats-test-1")
        create_memory_for_menu("stats-test-2")
        
        stats = get_memory_stats()
        
        assert "total_memories" in stats
        assert stats["total_memories"] >= 2
        assert "menu_ids" in stats
        assert "stats-test-1" in stats["menu_ids"]
        assert "stats-test-2" in stats["menu_ids"]
        
        # Cleanup
        delete_memory_for_menu("stats-test-1")
        delete_memory_for_menu("stats-test-2")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
