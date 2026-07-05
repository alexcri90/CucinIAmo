"""
Menu Service - Business Logic per la generazione di menù

Questo servizio orchestra la generazione di menù usando:
- Structured Generation (Datapizza AI + Gemini)
- In-memory storage per i menù generati

Nota: Lo storage è in-memory, i menù vengono persi al riavvio del server.
Per persistenza, implementare database (MongoDB, PostgreSQL, etc.)
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
import asyncio

# Path per import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modelli
from backend.models.input_models import UserInput
from backend.models.output_models import MenuOutput
from backend.models.menu_models import Course

# Import structured generation
from backend.services.structured_generation import (
    generate_menu_structured,
    regenerate_course_structured,
    validate_menu_output
)


# =============================================================================
# IN-MEMORY STORAGE
# =============================================================================

# Storage semplice in-memory per i menù generati
# In produzione: usare Redis, MongoDB, PostgreSQL, etc.
menu_store: Dict[str, MenuOutput] = {}


def save_menu(menu: MenuOutput) -> None:
    """Salva un menù nello storage."""
    menu_store[str(menu.menu_id)] = menu


def get_menu(menu_id: str) -> Optional[MenuOutput]:
    """Recupera un menù dallo storage."""
    return menu_store.get(menu_id)


def delete_menu(menu_id: str) -> bool:
    """Elimina un menù dallo storage."""
    if menu_id in menu_store:
        del menu_store[menu_id]
        return True
    return False


# =============================================================================
# MENU SERVICE
# =============================================================================

class MenuService:
    """
    Servizio per la gestione della generazione menù.
    
    Responsabilità:
    - Orchestrare la generazione con AI
    - Gestire lo storage dei menù
    - Validare input e output
    """
    
    def __init__(self):
        """Inizializza il servizio."""
        self.generation_timeout = 120  # secondi
    
    async def generate_menu(self, user_input: UserInput) -> MenuOutput:
        """
        Genera un menù completo.
        
        Args:
            user_input: Input utente validato
            
        Returns:
            MenuOutput: Menù completo generato
            
        Raises:
            ValueError: Se l'input non è valido
            TimeoutError: Se la generazione supera il timeout
            Exception: Per altri errori di generazione
        """
        print(f"\n🍽️  MenuService: Avvio generazione...")
        start_time = datetime.now()
        
        # Validazione extra
        self._validate_input(user_input)
        
        try:
            # Esegui generazione in thread separato per non bloccare
            # (generate_menu_structured è sincrono)
            loop = asyncio.get_event_loop()
            menu = await loop.run_in_executor(
                None,
                generate_menu_structured,
                user_input
            )
            
            # Valida output
            warnings = validate_menu_output(menu)
            if warnings:
                print(f"   ⚠️  Warnings: {warnings}")
            
            # Salva nel storage
            save_menu(menu)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"   ✅ Generazione completata in {elapsed:.1f}s")
            print(f"   📦 Salvato con ID: {menu.menu_id}")
            
            return menu
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"   ❌ Errore dopo {elapsed:.1f}s: {e}")
            raise
    
    async def regenerate_course(
        self,
        menu_id: UUID,
        course_type: str,
        course_index: int = 0,
        user_feedback: str = ""
    ) -> Course:
        """
        Rigenera una singola portata di un menù esistente.
        
        MEMORY INTEGRATION: Se esiste una Memory associata al menù,
        la rigenerazione usa il contesto completo per generare un piatto
        coerente con il resto del menù.
        
        Args:
            menu_id: ID del menù
            course_type: Tipo portata (antipasti, primo, secondo, contorno, dessert)
            course_index: Indice se ci sono multiple portate dello stesso tipo
            user_feedback: Feedback opzionale dell'utente sul perché non gli piace
            
        Returns:
            Course: Nuova portata generata
            
        Raises:
            KeyError: Se il menù non esiste
            IndexError: Se l'indice non è valido
        """
        print(f"\n🔄 MenuService: Rigenerazione {course_type}...")
        if user_feedback:
            print(f"   📝 Feedback utente: {user_feedback}")
        
        # Recupera il menù
        menu = menu_store.get(str(menu_id))
        if not menu:
            raise KeyError(f"Menù {menu_id} non trovato")
        
        # Recupera la portata corrente
        courses = getattr(menu.courses, course_type, [])
        if course_index >= len(courses):
            raise IndexError(f"Indice {course_index} non valido per {course_type}")
        
        current_course = courses[course_index]
        
        # Raccogli i nomi degli altri piatti per mantenere coerenza
        other_dishes = []
        for ct in ["antipasti", "primo", "secondo", "contorno", "dessert"]:
            for c in getattr(menu.courses, ct, []):
                if c.name != current_course.name:
                    other_dishes.append(c.name)
        
        # Genera nuova portata (con supporto Memory)
        loop = asyncio.get_event_loop()
        new_course = await loop.run_in_executor(
            None,
            lambda: regenerate_course_structured(
                course_type=course_type,
                current_dish_name=current_course.name,
                other_dishes=other_dishes,
                user_input=menu.input,
                menu_id=str(menu_id),
                user_feedback=user_feedback
            )
        )
        
        # Aggiorna il menù in memoria
        courses[course_index] = new_course
        setattr(menu.courses, course_type, courses)
        
        # Ricalcola shopping list (semplificato)
        self._update_shopping_list(menu)
        
        # Salva aggiornamenti
        save_menu(menu)
        
        print(f"   ✅ Nuova portata: {new_course.name}")
        
        return new_course
    
    def get_menu(self, menu_id: UUID) -> Optional[MenuOutput]:
        """Recupera un menù per ID."""
        return menu_store.get(str(menu_id))
    
    def list_menus(self) -> list:
        """Lista tutti i menù salvati."""
        return list(menu_store.values())
    
    def delete_menu(self, menu_id: UUID) -> bool:
        """Elimina un menù."""
        return delete_menu(str(menu_id))
    
    def _validate_input(self, user_input: UserInput) -> None:
        """
        Validazione extra dell'input.
        
        Pydantic fa già la validazione base, qui aggiungiamo controlli business.
        """
        # Verifica overlap ingredienti
        preferred_set = set(ing.lower() for ing in user_input.preferred_ingredients)
        avoided_set = set(ing.lower() for ing in user_input.avoided_ingredients)
        
        overlap = preferred_set & avoided_set
        if overlap:
            raise ValueError(
                f"Ingredienti presenti sia in preferiti che evitati: {overlap}"
            )
        
        # Verifica combinazioni restrizioni incompatibili
        restrictions = set(r.value for r in user_input.dietary_restrictions)
        
        # Vegano include già vegetariano
        if "vegano" in restrictions and "vegetariano" in restrictions:
            print("   ⚠️  Nota: 'vegano' include già 'vegetariano'")
    
    def _update_shopping_list(self, menu: MenuOutput) -> None:
        """
        Ricalcola la lista della spesa dopo una modifica.
        
        Nota: Implementazione semplificata che aggrega gli ingredienti.
        """
        from collections import defaultdict
        
        categories = defaultdict(list)
        seen = set()
        
        for course_type in ["antipasti", "primo", "secondo", "contorno", "dessert"]:
            courses = getattr(menu.courses, course_type, [])
            for course in courses:
                for ing in course.recipe.ingredients:
                    key = ing.name.lower()
                    if key not in seen:
                        seen.add(key)
                        cat = ing.category if ing.category else "Altro"
                        categories[cat].append({
                            "name": ing.name,
                            "quantity": ing.quantity,
                            "category": cat
                        })
        
        # Aggiorna lo shopping list nel menù
        menu.shopping_list.categories = dict(categories)


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Istanza singleton del servizio
_menu_service_instance: Optional[MenuService] = None


def get_menu_service() -> MenuService:
    """
    Factory per ottenere l'istanza del MenuService.
    
    Implementa pattern singleton per riusare la stessa istanza.
    """
    global _menu_service_instance
    
    if _menu_service_instance is None:
        _menu_service_instance = MenuService()
    
    return _menu_service_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_service():
        print("=" * 60)
        print("  TEST MENU SERVICE")
        print("=" * 60)
        
        service = MenuService()
        
        # Test input
        test_input = UserInput(
            num_guests=4,
            cuisines=[Cuisine.ITALIANA],
            preferred_ingredients=["salmone"],
            avoided_ingredients=["piccante"],
            dietary_restrictions=[],
            difficulty_level=DifficultyLevel.FACILE,
            budget_level=BudgetLevel.ECONOMICO
        )
        
        print("\n📝 Generazione menù di test...")
        
        try:
            menu = await service.generate_menu(test_input)
            print(f"\n✅ Menù generato: {menu.menu_id}")
            print(f"   Portate: {len(menu.courses.antipasti) + len(menu.courses.primo) + len(menu.courses.secondo) + len(menu.courses.contorno) + len(menu.courses.dessert)}")
        except Exception as e:
            print(f"\n❌ Errore: {e}")
    
    # Import per test
    from models.input_models import Cuisine, DifficultyLevel, BudgetLevel
    
    asyncio.run(test_service())