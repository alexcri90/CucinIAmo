"""Modelli Pydantic per menù e ricette."""
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """Singolo ingrediente con quantità e categoria."""
    name: str = Field(..., description="Nome dell'ingrediente")
    quantity: str = Field(..., description="Quantità (es. '200g', '2 cucchiai')")
    category: str = Field(
        ..., 
        description="Categoria: Frutta e verdura, Carne, Pesce, Latticini, Dispensa, Altro"
    )


class Recipe(BaseModel):
    """Ricetta dettagliata di un piatto."""
    ingredients: List[Ingredient] = Field(
        ..., 
        description="Lista ingredienti con quantità"
    )
    prep_time_minutes: int = Field(
        ..., 
        ge=5, 
        le=480,
        description="Tempo di preparazione in minuti"
    )
    cook_time_minutes: int = Field(
        default=0,
        ge=0,
        description="Tempo di cottura in minuti"
    )
    difficulty: str = Field(
        ..., 
        description="Livello difficoltà: facile, medio, avanzato"
    )
    steps: List[str] = Field(
        ..., 
        min_length=1,
        description="Procedimento step-by-step"
    )
    chef_notes: Optional[str] = Field(
        default=None,
        description="Note, tips e varianti dello chef"
    )
    can_prep_ahead: bool = Field(
        default=False,
        description="Se può essere preparato in anticipo"
    )
    prep_ahead_timing: Optional[str] = Field(
        default=None,
        description="Quando prepararlo in anticipo (es. '1 giorno prima')"
    )


class Course(BaseModel):
    """Singola portata del menù."""
    course_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Nome del piatto")
    cuisine: str = Field(..., description="Nazionalità/origine del piatto")
    description: str = Field(
        ..., 
        min_length=20,
        max_length=500,
        description="Descrizione del piatto (2-3 righe)"
    )
    recipe: Recipe = Field(..., description="Ricetta dettagliata")


class MenuCourses(BaseModel):
    """Struttura completa delle portate del menù."""
    antipasti: List[Course] = Field(
        ..., 
        min_length=1, 
        max_length=2,
        description="1-2 antipasti"
    )
    primo: List[Course] = Field(
        ..., 
        min_length=1, 
        max_length=1,
        description="1 primo piatto"
    )
    secondo: List[Course] = Field(
        ..., 
        min_length=1, 
        max_length=1,
        description="1 secondo piatto"
    )
    contorno: List[Course] = Field(
        ..., 
        min_length=1, 
        max_length=1,
        description="1 contorno"
    )
    dessert: List[Course] = Field(
        ..., 
        min_length=1, 
        max_length=2,
        description="1-2 dessert"
    )