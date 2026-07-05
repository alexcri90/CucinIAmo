"""
Menu Routes - Endpoints per la generazione di menù natalizi

Endpoints:
- POST /generate           - Genera un menù completo
- POST /regenerate-course  - Rigenera una singola portata
- GET  /{menu_id}          - Recupera un menù salvato
- GET  /{menu_id}/shopping-list - Solo lista spesa
- GET  /{menu_id}/timeline - Solo timeline
"""

import os
import sys
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Path per import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modelli
from models.input_models import (
    UserInput,
    Cuisine,
    DifficultyLevel,
    BudgetLevel,
    DietaryRestriction
)
from models.output_models import MenuOutput, ShoppingList, Timeline
from models.menu_models import Course

# Import servizi
from services.menu_service import MenuService, menu_store


# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter()

# Istanza del servizio
menu_service = MenuService()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class GenerateMenuRequest(BaseModel):
    """Request body per generare un menù."""
    
    num_guests: int = Field(
        ...,
        ge=1,
        le=50,
        description="Numero di ospiti (1-50)",
        examples=[8]
    )
    
    cuisines: List[Cuisine] = Field(
        ...,
        min_length=1,
        description="Tradizioni culinarie desiderate",
        examples=[["italiana", "francese"]]
    )
    
    preferred_ingredients: List[str] = Field(
        default=[],
        max_length=20,
        description="Ingredienti da includere preferibilmente",
        examples=[["salmone", "tartufo"]]
    )
    
    avoided_ingredients: List[str] = Field(
        default=[],
        max_length=20,
        description="Ingredienti da evitare assolutamente",
        examples=[["piccante", "funghi"]]
    )
    
    dietary_restrictions: List[DietaryRestriction] = Field(
        default=[],
        description="Restrizioni alimentari",
        examples=[["vegetariano", "senza_glutine"]]
    )
    
    other_restrictions: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Altre restrizioni (testo libero)",
        examples=["Niente frutta secca per allergia"]
    )
    
    difficulty_level: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIO,
        description="Livello di difficoltà delle ricette",
        examples=["medio"]
    )
    
    budget_level: BudgetLevel = Field(
        default=BudgetLevel.MEDIO,
        description="Livello di budget",
        examples=["medio"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "num_guests": 8,
                "cuisines": ["italiana"],
                "preferred_ingredients": ["salmone", "gamberi"],
                "avoided_ingredients": ["piccante"],
                "dietary_restrictions": [],
                "difficulty_level": "medio",
                "budget_level": "medio"
            }
        }


class RegenerateCourseRequest(BaseModel):
    """Request body per rigenerare una portata."""
    
    menu_id: UUID = Field(
        ...,
        description="ID del menù da modificare"
    )
    
    course_type: str = Field(
        ...,
        description="Tipo di portata: antipasti, primo, secondo, contorno, dessert",
        examples=["primo"]
    )
    
    course_index: int = Field(
        default=0,
        ge=0,
        description="Indice della portata se ce ne sono multiple (es. 2 antipasti)",
        examples=[0]
    )
    
    user_feedback: Optional[str] = Field(
        default="",
        max_length=500,
        description="Feedback opzionale sul perché la portata non piace",
        examples=["Vorrei qualcosa di meno pesante", "Preferisco un piatto senza carne"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "menu_id": "123e4567-e89b-12d3-a456-426614174000",
                "course_type": "primo",
                "course_index": 0,
                "user_feedback": "Vorrei qualcosa di più leggero"
            }
        }


class RegenerateCourseResponse(BaseModel):
    """Response per rigenerazione portata."""
    
    success: bool
    course_type: str
    new_course: Course
    message: str


class MenuSummary(BaseModel):
    """Riepilogo breve di un menù."""
    
    menu_id: UUID
    generated_at: datetime
    num_guests: int
    cuisines: List[str]
    course_names: List[str]


class ErrorResponse(BaseModel):
    """Risposta di errore standard."""
    
    error: bool = True
    status_code: int
    message: str
    timestamp: datetime


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/generate",
    response_model=MenuOutput,
    summary="Genera un menù natalizio completo",
    description="""
    Genera un menù natalizio personalizzato basato sulle preferenze dell'utente.
    
    Il menù include:
    - 1-2 Antipasti
    - 1 Primo piatto
    - 1 Secondo piatto
    - 1 Contorno
    - 1-2 Dessert
    - Lista della spesa aggregata
    - Timeline di preparazione
    
    **Tempo di risposta**: 30-60 secondi (dipende dalla complessità)
    
    **Rate limit**: 15 richieste/minuto (free tier Gemini)
    """,
    responses={
        200: {"description": "Menù generato con successo"},
        400: {"description": "Input non valido", "model": ErrorResponse},
        500: {"description": "Errore di generazione", "model": ErrorResponse}
    }
)
async def generate_menu(request: GenerateMenuRequest):
    """
    Genera un nuovo menù natalizio completo.
    """
    print(f"\n📥 Richiesta generazione menù:")
    print(f"   Ospiti: {request.num_guests}")
    print(f"   Cucine: {[c.value for c in request.cuisines]}")
    print(f"   Difficoltà: {request.difficulty_level.value}")
    
    try:
        # Converti request in UserInput
        user_input = UserInput(
            num_guests=request.num_guests,
            cuisines=request.cuisines,
            preferred_ingredients=request.preferred_ingredients,
            avoided_ingredients=request.avoided_ingredients,
            dietary_restrictions=request.dietary_restrictions,
            other_restrictions=request.other_restrictions,
            difficulty_level=request.difficulty_level,
            budget_level=request.budget_level
        )
        
        # Genera il menù
        menu = await menu_service.generate_menu(user_input)
        
        print(f"\n✅ Menù generato: {menu.menu_id}")
        
        return menu
        
    except ValueError as e:
        print(f"\n❌ Errore validazione: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        print(f"\n❌ Errore generazione: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la generazione del menù: {str(e)}"
        )


@router.post(
    "/regenerate-course",
    response_model=RegenerateCourseResponse,
    summary="Rigenera una singola portata",
    description="""
    Rigenera una singola portata del menù mantenendo coerenza con le altre.
    
    Utile quando una portata non piace e si vuole una variante.
    
    **MEMORY INTEGRATION**: Usa Memory di Datapizza AI per mantenere
    il contesto del menù originale e generare un piatto coerente.
    
    Puoi opzionalmente fornire un feedback sul perché la portata non piace
    per guidare meglio la rigenerazione.
    """,
    responses={
        200: {"description": "Portata rigenerata con successo"},
        404: {"description": "Menù non trovato"},
        400: {"description": "Tipo portata non valido"}
    }
)
async def regenerate_course(request: RegenerateCourseRequest):
    """
    Rigenera una singola portata del menù.
    """
    print(f"\n🔄 Richiesta rigenerazione:")
    print(f"   Menu ID: {request.menu_id}")
    print(f"   Portata: {request.course_type}[{request.course_index}]")
    if request.user_feedback:
        print(f"   Feedback: {request.user_feedback}")
    
    # Valida tipo portata
    valid_types = ["antipasti", "primo", "secondo", "contorno", "dessert"]
    if request.course_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo portata non valido. Usa uno tra: {valid_types}"
        )
    
    try:
        new_course = await menu_service.regenerate_course(
            menu_id=request.menu_id,
            course_type=request.course_type,
            course_index=request.course_index,
            user_feedback=request.user_feedback or ""
        )
        
        print(f"✅ Nuova portata: {new_course.name}")
        
        # Converti Course in dict per evitare errore Pydantic v2
        # "Input should be a valid dictionary or instance of Course"
        return RegenerateCourseResponse(
            success=True,
            course_type=request.course_type,
            new_course=Course.model_validate(new_course.model_dump()),
            message=f"Portata '{request.course_type}' rigenerata con successo"
        )
        
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Menù con ID {request.menu_id} non trovato"
        )
        
    except IndexError:
        raise HTTPException(
            status_code=400,
            detail=f"Indice {request.course_index} non valido per {request.course_type}"
        )
        
    except Exception as e:
        print(f"❌ Errore rigenerazione: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{menu_id}",
    response_model=MenuOutput,
    summary="Recupera un menù salvato",
    description="Recupera un menù precedentemente generato tramite il suo ID.",
    responses={
        200: {"description": "Menù trovato"},
        404: {"description": "Menù non trovato"}
    }
)
async def get_menu(menu_id: UUID):
    """
    Recupera un menù esistente dal suo ID.
    """
    menu = menu_store.get(str(menu_id))
    
    if not menu:
        raise HTTPException(
            status_code=404,
            detail=f"Menù con ID {menu_id} non trovato. I menù vengono eliminati al riavvio del server."
        )
    
    return menu


@router.get(
    "/{menu_id}/shopping-list",
    response_model=ShoppingList,
    summary="Recupera solo la lista spesa",
    description="Recupera la lista della spesa aggregata di un menù.",
    responses={
        200: {"description": "Lista spesa trovata"},
        404: {"description": "Menù non trovato"}
    }
)
async def get_shopping_list(menu_id: UUID):
    """
    Recupera solo la lista della spesa di un menù.
    """
    menu = menu_store.get(str(menu_id))
    
    if not menu:
        raise HTTPException(
            status_code=404,
            detail=f"Menù con ID {menu_id} non trovato"
        )
    
    return menu.shopping_list


@router.get(
    "/{menu_id}/timeline",
    response_model=Timeline,
    summary="Recupera solo la timeline",
    description="Recupera la timeline di preparazione di un menù.",
    responses={
        200: {"description": "Timeline trovata"},
        404: {"description": "Menù non trovato"}
    }
)
async def get_timeline(menu_id: UUID):
    """
    Recupera solo la timeline di un menù.
    """
    menu = menu_store.get(str(menu_id))
    
    if not menu:
        raise HTTPException(
            status_code=404,
            detail=f"Menù con ID {menu_id} non trovato"
        )
    
    return menu.timeline


@router.get(
    "/",
    response_model=List[MenuSummary],
    summary="Lista menù salvati",
    description="Recupera la lista di tutti i menù generati in questa sessione.",
    responses={
        200: {"description": "Lista menù"}
    }
)
async def list_menus():
    """
    Lista tutti i menù salvati in memoria.
    """
    summaries = []
    
    for menu_id, menu in menu_store.items():
        course_names = []
        for course_type in ["antipasti", "primo", "secondo", "contorno", "dessert"]:
            courses = getattr(menu.courses, course_type, [])
            for c in courses:
                course_names.append(c.name)
        
        summaries.append(MenuSummary(
            menu_id=menu.menu_id,
            generated_at=menu.generated_at,
            num_guests=menu.input.num_guests,
            cuisines=[c.value for c in menu.input.cuisines],
            course_names=course_names
        ))
    
    return summaries


@router.delete(
    "/{menu_id}",
    summary="Elimina un menù",
    description="Elimina un menù salvato.",
    responses={
        200: {"description": "Menù eliminato"},
        404: {"description": "Menù non trovato"}
    }
)
async def delete_menu(menu_id: UUID):
    """
    Elimina un menù dalla memoria.
    """
    if str(menu_id) not in menu_store:
        raise HTTPException(
            status_code=404,
            detail=f"Menù con ID {menu_id} non trovato"
        )
    
    del menu_store[str(menu_id)]
    
    return {"message": f"Menù {menu_id} eliminato con successo"}