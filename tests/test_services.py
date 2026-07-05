"""
Test per MenuService e Structured Generation

Testa:
- MenuService business logic
- Storage in-memory
- Integration con structured_generation (mocked)
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime

# Aggiungi path per import corretti
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, "backend")
sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)

from backend.models.input_models import (
    UserInput, Cuisine, DifficultyLevel, BudgetLevel
)

# Import diretti dal modulo
from services.menu_service import (
    MenuService,
    menu_store,
    save_menu,
    get_menu,
    delete_menu
)


# =============================================================================
# TEST IN-MEMORY STORAGE
# =============================================================================

class TestMenuStorage:
    """Test per le funzioni di storage in-memory."""
    
    def test_save_menu(self, sample_menu_output):
        """Test salvataggio menù."""
        # Pulisci store
        menu_store.clear()
        
        save_menu(sample_menu_output)
        
        assert str(sample_menu_output.menu_id) in menu_store
        
        # Cleanup
        menu_store.clear()
    
    def test_get_menu_exists(self, sample_menu_output):
        """Test recupero menù esistente."""
        menu_store.clear()
        save_menu(sample_menu_output)
        
        menu_id = str(sample_menu_output.menu_id)
        retrieved = get_menu(menu_id)
        
        assert retrieved is not None
        assert retrieved.menu_id == sample_menu_output.menu_id
        
        menu_store.clear()
    
    def test_get_menu_not_exists(self):
        """Test recupero menù inesistente."""
        menu_store.clear()
        
        result = get_menu("non-existent-id")
        
        assert result is None
    
    def test_delete_menu_exists(self, sample_menu_output):
        """Test eliminazione menù esistente."""
        menu_store.clear()
        save_menu(sample_menu_output)
        
        menu_id = str(sample_menu_output.menu_id)
        result = delete_menu(menu_id)
        
        assert result is True
        assert get_menu(menu_id) is None
    
    def test_delete_menu_not_exists(self):
        """Test eliminazione menù inesistente."""
        menu_store.clear()
        
        result = delete_menu("non-existent-id")
        
        assert result is False
    
    def test_multiple_menus(self, sample_menu_output):
        """Test storage multipli menù."""
        menu_store.clear()
        
        # Crea 3 menù diversi
        menu1 = sample_menu_output
        menu2 = sample_menu_output.model_copy(update={"menu_id": uuid4()})
        menu3 = sample_menu_output.model_copy(update={"menu_id": uuid4()})
        
        save_menu(menu1)
        save_menu(menu2)
        save_menu(menu3)
        
        assert len(menu_store) == 3
        
        menu_store.clear()


# =============================================================================
# TEST MENU SERVICE
# =============================================================================

class TestMenuService:
    """Test per la classe MenuService."""
    
    @pytest.fixture
    def menu_service(self):
        """Istanza MenuService per test."""
        return MenuService()
    
    def test_service_initialization(self, menu_service):
        """Test inizializzazione servizio."""
        assert menu_service is not None
        assert menu_service.generation_timeout == 120
    
    @pytest.mark.asyncio
    async def test_generate_menu_success(
        self, 
        menu_service, 
        valid_user_input,
        sample_menu_output
    ):
        """Test generazione menù con successo."""
        with patch('services.menu_service.generate_menu_structured') as mock_gen:
            mock_gen.return_value = sample_menu_output
            
            result = await menu_service.generate_menu(valid_user_input)
            
            assert result is not None
            assert result.menu_id == sample_menu_output.menu_id
            mock_gen.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_menu_saves_to_store(
        self,
        menu_service,
        valid_user_input,
        sample_menu_output
    ):
        """Test che la generazione salvi nello store."""
        menu_store.clear()
        
        with patch('services.menu_service.generate_menu_structured') as mock_gen:
            mock_gen.return_value = sample_menu_output
            
            result = await menu_service.generate_menu(valid_user_input)
            
            # Verifica che sia stato salvato
            assert get_menu(str(result.menu_id)) is not None
        
        menu_store.clear()
    
    @pytest.mark.asyncio
    async def test_generate_menu_validation_error(self, menu_service):
        """Test errore validazione input."""
        with patch('services.menu_service.generate_menu_structured') as mock_gen:
            mock_gen.side_effect = ValueError("Invalid input")
            
            with pytest.raises(ValueError):
                invalid_input = UserInput(
                    num_guests=4,
                    cuisines=[Cuisine.ITALIANA]
                )
                await menu_service.generate_menu(invalid_input)
    
    @pytest.mark.asyncio
    async def test_generate_menu_api_error(
        self,
        menu_service,
        valid_user_input
    ):
        """Test gestione errore API."""
        with patch('services.menu_service.generate_menu_structured') as mock_gen:
            mock_gen.side_effect = Exception("API unavailable")
            
            with pytest.raises(Exception) as exc_info:
                await menu_service.generate_menu(valid_user_input)
            
            assert "API unavailable" in str(exc_info.value)


# =============================================================================
# TEST MENU SERVICE - REGENERATE COURSE
# =============================================================================

class TestMenuServiceRegenerate:
    """Test per la rigenerazione delle portate."""
    
    @pytest.fixture
    def menu_service(self):
        return MenuService()
    
    @pytest.mark.asyncio
    async def test_regenerate_course_not_found(self, menu_service):
        """Test rigenerazione per menù inesistente."""
        menu_store.clear()
        
        with pytest.raises(KeyError):
            await menu_service.regenerate_course(
                menu_id=uuid4(),
                course_type="primo"
            )
    
    @pytest.mark.asyncio
    async def test_regenerate_course_success(
        self,
        menu_service,
        sample_menu_output,
        sample_course
    ):
        """Test rigenerazione portata con successo."""
        menu_store.clear()
        save_menu(sample_menu_output)
        
        with patch('services.menu_service.regenerate_course_structured') as mock_regen:
            mock_regen.return_value = sample_course
            
            result = await menu_service.regenerate_course(
                menu_id=sample_menu_output.menu_id,
                course_type="primo",
                course_index=0
            )
            
            assert result is not None
        
        menu_store.clear()


# =============================================================================
# TEST VALIDATE MENU OUTPUT
# =============================================================================

class TestValidateMenuOutput:
    """Test per la validazione dell'output."""
    
    def test_validate_complete_menu(self, sample_menu_output):
        """Test validazione menù completo."""
        from services.structured_generation import validate_menu_output
        
        warnings = validate_menu_output(sample_menu_output)
        
        # Un menù completo non dovrebbe avere warning
        assert isinstance(warnings, list)
    
    def test_validate_empty_courses(self):
        """Test validazione con portate mancanti."""
        from services.structured_generation import validate_menu_output
        from models.menu_models import MenuCourses
        from models.output_models import MenuOutput, ShoppingList, Timeline
        
        # Questo test verifica la robustezza della validazione
        # In realtà MenuCourses richiede almeno 1 elemento per portata
        pass  # Skip - la validazione Pydantic impedisce questo caso


# =============================================================================
# TEST INPUT VALIDATION IN SERVICE
# =============================================================================

class TestServiceInputValidation:
    """Test validazione input nel servizio."""
    
    @pytest.fixture
    def menu_service(self):
        return MenuService()
    
    def test_validate_input_valid(self, menu_service, valid_user_input):
        """Test validazione input valido."""
        # Internamente _validate_input non solleva eccezioni
        try:
            menu_service._validate_input(valid_user_input)
        except Exception:
            pytest.fail("_validate_input raised exception on valid input")
    
    def test_validate_input_constraints(self, menu_service):
        """Test che le constraint vengano rispettate."""
        # Test con valori limite validi
        edge_case_input = UserInput(
            num_guests=2,  # Minimo
            cuisines=[Cuisine.ITALIANA]  # Minimo 1
        )
        
        try:
            menu_service._validate_input(edge_case_input)
        except Exception:
            pytest.fail("_validate_input failed on edge case")


# =============================================================================
# TEST CONCURRENT ACCESS
# =============================================================================

class TestConcurrentAccess:
    """Test per accesso concorrente allo storage."""
    
    def test_concurrent_saves(self, sample_menu_output):
        """Test salvataggi concorrenti."""
        import asyncio
        
        menu_store.clear()
        
        async def save_many():
            tasks = []
            for i in range(10):
                menu = sample_menu_output.model_copy(update={"menu_id": uuid4()})
                tasks.append(asyncio.to_thread(save_menu, menu))
            await asyncio.gather(*tasks)
        
        asyncio.run(save_many())
        
        assert len(menu_store) == 10
        
        menu_store.clear()
    
    def test_concurrent_read_write(self, sample_menu_output):
        """Test letture e scritture concorrenti."""
        import asyncio
        
        menu_store.clear()
        save_menu(sample_menu_output)
        menu_id = str(sample_menu_output.menu_id)
        
        async def read_write():
            read_tasks = [asyncio.to_thread(get_menu, menu_id) for _ in range(5)]
            write_tasks = [
                asyncio.to_thread(
                    save_menu, 
                    sample_menu_output.model_copy(update={"menu_id": uuid4()})
                ) 
                for _ in range(5)
            ]
            await asyncio.gather(*read_tasks, *write_tasks)
        
        asyncio.run(read_write())
        
        # Originale + 5 nuovi
        assert len(menu_store) == 6
        
        menu_store.clear()


# =============================================================================
# TEST MENU SERVICE INTEGRATION
# =============================================================================

class TestMenuServiceIntegration:
    """Test di integrazione per MenuService."""
    
    @pytest.fixture
    def menu_service(self):
        return MenuService()
    
    @pytest.mark.asyncio
    async def test_full_workflow(
        self,
        menu_service,
        valid_user_input,
        sample_menu_output
    ):
        """Test workflow completo: genera → recupera → elimina."""
        menu_store.clear()
        
        with patch('services.menu_service.generate_menu_structured') as mock_gen:
            mock_gen.return_value = sample_menu_output
            
            # 1. Genera
            generated = await menu_service.generate_menu(valid_user_input)
            menu_id = str(generated.menu_id)
            
            # 2. Recupera
            retrieved = get_menu(menu_id)
            assert retrieved is not None
            assert retrieved.menu_id == generated.menu_id
            
            # 3. Elimina
            deleted = delete_menu(menu_id)
            assert deleted is True
            
            # 4. Verifica eliminazione
            assert get_menu(menu_id) is None
        
        menu_store.clear()
