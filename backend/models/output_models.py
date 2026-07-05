"""Modelli Pydantic per output del sistema."""
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from .input_models import UserInput
from .menu_models import MenuCourses, Ingredient, Course


class ShoppingList(BaseModel):
    """Lista spesa aggregata per categorie."""
    categories: Dict[str, List[Ingredient]] = Field(
        ...,
        description="Ingredienti organizzati per categoria"
    )
    
    def get_total_items(self) -> int:
        """Conta totale ingredienti."""
        return sum(len(items) for items in self.categories.values())


class Timeline(BaseModel):
    """Timeline di preparazione completa."""
    two_days_before: List[str] = Field(
        default_factory=list,
        description="Attività 2 giorni prima"
    )
    one_day_before: List[str] = Field(
        default_factory=list,
        description="Attività 1 giorno prima"
    )
    day_of: Dict[str, str] = Field(
        ...,
        description="Timeline oraria del giorno stesso"
    )


class MenuOutput(BaseModel):
    """
    Output completo della generazione menù.
    Questo è il modello principale usato per le Structured Responses.
    """
    menu_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    input: UserInput = Field(..., description="Input originale dell'utente")
    courses: MenuCourses = Field(..., description="Portate del menù")
    shopping_list: ShoppingList = Field(..., description="Lista spesa aggregata")
    timeline: Timeline = Field(..., description="Timeline di preparazione")


class RegenerateCourseRequest(BaseModel):
    """Request per rigenerare una singola portata."""
    menu_id: UUID
    course_type: str = Field(..., description="Tipo portata da rigenerare")
    course_index: int = Field(default=0, ge=0, description="Indice se multipli")


class RegenerateCourseResponse(BaseModel):
    """Response con la nuova portata generata."""
    course_type: str
    new_course: Course
    updated_shopping_list: ShoppingList
    updated_timeline: Timeline