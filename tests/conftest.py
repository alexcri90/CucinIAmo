"""
Pytest Configuration e Fixtures per Christmas Menu Generator

Questo file contiene:
- Configurazione pytest
- Fixtures condivise per tutti i test
- Mock objects per testing isolato
"""

import os
import sys
from datetime import datetime
from uuid import uuid4
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Aggiungi path per import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modelli
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
# FIXTURES: INPUT MODELS
# =============================================================================

@pytest.fixture
def valid_user_input() -> UserInput:
    """UserInput valido per test standard."""
    return UserInput(
        num_guests=6,
        cuisines=[Cuisine.ITALIANA, Cuisine.FRANCESE],
        preferred_ingredients=["salmone", "tartufo"],
        avoided_ingredients=["piccante", "funghi"],
        dietary_restrictions=[],
        difficulty_level=DifficultyLevel.MEDIO,
        budget_level=BudgetLevel.MEDIO
    )


@pytest.fixture
def minimal_user_input() -> UserInput:
    """UserInput minimale (solo campi obbligatori)."""
    return UserInput(
        num_guests=4,
        cuisines=[Cuisine.ITALIANA]
    )


@pytest.fixture
def vegetarian_user_input() -> UserInput:
    """UserInput con restrizioni alimentari."""
    return UserInput(
        num_guests=8,
        cuisines=[Cuisine.ITALIANA, Cuisine.GRECA],
        dietary_restrictions=[DietaryRestriction.VEGETARIANO],
        difficulty_level=DifficultyLevel.FACILE,
        budget_level=BudgetLevel.ECONOMICO
    )


# =============================================================================
# FIXTURES: MENU MODELS
# =============================================================================

@pytest.fixture
def sample_ingredient() -> Ingredient:
    """Singolo ingrediente per test."""
    return Ingredient(
        name="Salmone affumicato",
        quantity="200g",
        category="Pesce"
    )


@pytest.fixture
def sample_recipe(sample_ingredient) -> Recipe:
    """Ricetta di esempio per test."""
    return Recipe(
        ingredients=[
            sample_ingredient,
            Ingredient(name="Limone", quantity="1", category="Frutta e verdura"),
            Ingredient(name="Aneto", quantity="q.b.", category="Dispensa")
        ],
        prep_time_minutes=15,
        cook_time_minutes=0,
        difficulty="facile",
        steps=[
            "Disporre il salmone su un piatto da portata",
            "Guarnire con fette di limone",
            "Spolverare con aneto fresco"
        ],
        chef_notes="Servire ben freddo",
        can_prep_ahead=True,
        prep_ahead_timing="1 giorno prima"
    )


@pytest.fixture
def sample_course(sample_recipe) -> Course:
    """Portata di esempio per test."""
    return Course(
        name="Salmone Norvegese con Aneto",
        cuisine="scandinava",
        description="Delicato salmone affumicato servito con limone fresco e aneto, "
                   "perfetto come antipasto leggero per la cena di Natale.",
        recipe=sample_recipe
    )


@pytest.fixture
def sample_menu_courses(sample_course) -> MenuCourses:
    """MenuCourses completo per test."""
    # Crea portate diverse
    antipasto = sample_course.model_copy(update={"name": "Antipasto Test"})
    primo = sample_course.model_copy(update={"name": "Primo Test", "cuisine": "italiana"})
    secondo = sample_course.model_copy(update={"name": "Secondo Test", "cuisine": "francese"})
    contorno = sample_course.model_copy(update={"name": "Contorno Test"})
    dessert = sample_course.model_copy(update={"name": "Dessert Test"})
    
    return MenuCourses(
        antipasti=[antipasto],
        primo=[primo],
        secondo=[secondo],
        contorno=[contorno],
        dessert=[dessert]
    )


# =============================================================================
# FIXTURES: OUTPUT MODELS
# =============================================================================

@pytest.fixture
def sample_shopping_list(sample_ingredient) -> ShoppingList:
    """Lista spesa di esempio."""
    return ShoppingList(
        categories={
            "Pesce": [sample_ingredient],
            "Frutta e verdura": [
                Ingredient(name="Limone", quantity="2", category="Frutta e verdura")
            ],
            "Dispensa": [
                Ingredient(name="Sale", quantity="q.b.", category="Dispensa")
            ]
        }
    )


@pytest.fixture
def sample_timeline() -> Timeline:
    """Timeline di preparazione di esempio."""
    return Timeline(
        two_days_before=[
            "Fare la spesa per ingredienti non deperibili",
            "Preparare il brodo"
        ],
        one_day_before=[
            "Preparare i ripieni",
            "Marinare il salmone"
        ],
        day_of={
            "09:00": "Iniziare la preparazione del primo",
            "11:00": "Preparare il secondo",
            "12:30": "Cottura finale e impiattamento"
        }
    )


@pytest.fixture
def sample_menu_output(
    valid_user_input,
    sample_menu_courses,
    sample_shopping_list,
    sample_timeline
) -> MenuOutput:
    """MenuOutput completo per test."""
    return MenuOutput(
        menu_id=uuid4(),
        generated_at=datetime.utcnow(),
        input=valid_user_input,
        courses=sample_menu_courses,
        shopping_list=sample_shopping_list,
        timeline=sample_timeline
    )


# =============================================================================
# FIXTURES: FASTAPI TEST CLIENT
# =============================================================================

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Client FastAPI per test API."""
    from backend.main import app
    with TestClient(app) as client:
        yield client


# =============================================================================
# FIXTURES: MOCKS
# =============================================================================

@pytest.fixture
def mock_google_client():
    """Mock del GoogleClient per test senza API reale."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"test": "response"}'
    mock_response.completion_tokens_used = 100
    mock_response.prompt_tokens_used = 50
    mock_client.invoke.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_menu_service(sample_menu_output):
    """Mock del MenuService per test API isolati."""
    with patch('backend.api.menu_routes.menu_service') as mock:
        mock.generate_menu.return_value = sample_menu_output
        mock.get_menu.return_value = sample_menu_output
        yield mock


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configurazione pytest personalizzata."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests that require external services"
    )


@pytest.fixture(autouse=True)
def set_test_env():
    """Imposta variabili d'ambiente per test."""
    os.environ.setdefault("GOOGLE_API_KEY", "test_key_not_real")
    os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")
    os.environ.setdefault("APP_ENV", "testing")
