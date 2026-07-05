"""Modelli Pydantic per l'input utente."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DifficultyLevel(str, Enum):
    """Livello di difficoltà delle ricette."""
    FACILE = "facile"
    MEDIO = "medio"
    AVANZATO = "avanzato"


class BudgetLevel(str, Enum):
    """Livello di budget per gli ingredienti."""
    ECONOMICO = "economico"
    MEDIO = "medio"
    PREMIUM = "premium"


class Cuisine(str, Enum):
    """Nazionalità/cucine disponibili."""
    ITALIANA = "italiana"
    SPAGNOLA = "spagnola"
    FRANCESE = "francese"
    TEDESCA = "tedesca"
    INGLESE = "inglese"
    POLACCA = "polacca"
    GRECA = "greca"
    AMERICANA = "americana"
    SCANDINAVA = "scandinava"


class DietaryRestriction(str, Enum):
    """Restrizioni alimentari predefinite."""
    VEGETARIANO = "vegetariano"
    VEGANO = "vegano"
    SENZA_GLUTINE = "senza_glutine"
    SENZA_LATTOSIO = "senza_lattosio"


class UserInput(BaseModel):
    """
    Modello di input utente per la generazione del menù.
    Utilizzato come input principale per il Menu Agent.
    """
    num_guests: int = Field(
        ..., 
        ge=1, 
        le=50, 
        description="Numero di invitati (1-50)"
    )
    preferred_ingredients: List[str] = Field(
        default_factory=list,
        max_length=50,
        description="Ingredienti preferiti da includere"
    )
    avoided_ingredients: List[str] = Field(
        default_factory=list,
        max_length=50,
        description="Ingredienti da evitare"
    )
    cuisines: List[Cuisine] = Field(
        ...,
        min_length=1,
        description="Nazionalità dei piatti desiderati"
    )
    dietary_restrictions: List[DietaryRestriction] = Field(
        default_factory=list,
        description="Restrizioni alimentari"
    )
    other_restrictions: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Altre restrizioni alimentari (testo libero)"
    )
    difficulty_level: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIO,
        description="Livello di difficoltà desiderato"
    )
    budget_level: BudgetLevel = Field(
        default=BudgetLevel.MEDIO,
        description="Livello di budget"
    )

    @field_validator('preferred_ingredients', 'avoided_ingredients')
    @classmethod
    def clean_ingredients(cls, v: List[str]) -> List[str]:
        """Normalizza gli ingredienti: lowercase e trim."""
        return [ing.strip().lower() for ing in v if ing.strip()]

    @field_validator('avoided_ingredients')
    @classmethod
    def check_no_overlap(cls, v: List[str], info) -> List[str]:
        """Verifica che non ci sia overlap tra preferiti ed evitati."""
        preferred = info.data.get('preferred_ingredients', [])
        overlap = set(v) & set(preferred)
        if overlap:
            raise ValueError(
                f"Ingredienti presenti sia in preferiti che evitati: {overlap}"
            )
        return v
    
    class Config:
        """Configurazione Pydantic."""
        json_schema_extra = {
            "example": {
                "num_guests": 6,
                "preferred_ingredients": ["tartufo", "salmone"],
                "avoided_ingredients": ["noci"],
                "cuisines": ["italiana", "francese"],
                "dietary_restrictions": [],
                "other_restrictions": None,
                "difficulty_level": "medio",
                "budget_level": "premium"
            }
        }