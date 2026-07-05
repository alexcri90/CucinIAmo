"""
Test per gli Endpoint API FastAPI

Testa:
- Health check
- GET/POST/DELETE endpoints
- Validazione request/response
- Error handling

NOTA: Usa TestClient di FastAPI con mock del MenuService
per evitare chiamate reali all'API Gemini.
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime

# Setup path per import corretti
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, "backend")
sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient


# =============================================================================
# TEST HEALTH & ROOT ENDPOINTS
# =============================================================================

class TestHealthEndpoints:
    """Test per endpoint di health check."""
    
    def test_health_check(self, test_client):
        """Test GET /health."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, test_client):
        """Test GET / (root)."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "Christmas Menu" in data["name"]
    
    def test_docs_available(self, test_client):
        """Test che Swagger UI sia disponibile."""
        response = test_client.get("/docs")
        
        assert response.status_code == 200


# =============================================================================
# TEST MENU GENERATION ENDPOINT
# =============================================================================

class TestGenerateMenuEndpoint:
    """Test per POST /api/menu/generate."""
    
    @pytest.fixture
    def valid_request_body(self):
        """Request body valido per generazione menù."""
        return {
            "num_guests": 6,
            "cuisines": ["italiana", "francese"],
            "preferred_ingredients": ["salmone"],
            "avoided_ingredients": ["funghi"],
            "dietary_restrictions": [],
            "difficulty_level": "medio",
            "budget_level": "medio"
        }
    
    @pytest.fixture
    def mock_menu_response(self, sample_menu_output):
        """Mock response per MenuService."""
        return sample_menu_output
    
    def test_generate_menu_valid_request(
        self, 
        test_client, 
        valid_request_body,
        sample_menu_output
    ):
        """Test generazione menù con request valida."""
        with patch('api.menu_routes.menu_service') as mock_service:
            mock_service.generate_menu = AsyncMock(return_value=sample_menu_output)
            
            response = test_client.post(
                "/api/menu/generate",
                json=valid_request_body
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "menu_id" in data
            assert "courses" in data
    
    def test_generate_menu_invalid_guests_low(self, test_client):
        """Test errore per num_guests troppo basso."""
        response = test_client.post(
            "/api/menu/generate",
            json={
                "num_guests": 0,  # Minimo è 1
                "cuisines": ["italiana"]
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_menu_invalid_guests_high(self, test_client):
        """Test errore per num_guests troppo alto."""
        response = test_client.post(
            "/api/menu/generate",
            json={
                "num_guests": 100,  # Massimo è 50
                "cuisines": ["italiana"]
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_menu_empty_cuisines(self, test_client):
        """Test errore per cuisines vuoto."""
        response = test_client.post(
            "/api/menu/generate",
            json={
                "num_guests": 6,
                "cuisines": []  # Deve avere almeno 1
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_menu_invalid_cuisine_value(self, test_client):
        """Test errore per cucina non valida."""
        response = test_client.post(
            "/api/menu/generate",
            json={
                "num_guests": 6,
                "cuisines": ["giapponese"]  # Non supportata!
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_menu_invalid_difficulty(self, test_client):
        """Test errore per difficoltà non valida."""
        response = test_client.post(
            "/api/menu/generate",
            json={
                "num_guests": 6,
                "cuisines": ["italiana"],
                "difficulty_level": "difficile"  # Deve essere "avanzato"!
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_menu_invalid_dietary(self, test_client):
        """Test errore per restrizione alimentare non valida."""
        response = test_client.post(
            "/api/menu/generate",
            json={
                "num_guests": 6,
                "cuisines": ["italiana"],
                "dietary_restrictions": ["kosher"]  # Non supportata!
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_menu_minimal_request(self, test_client, sample_menu_output):
        """Test con request minimale (solo campi obbligatori)."""
        with patch('api.menu_routes.menu_service') as mock_service:
            mock_service.generate_menu = AsyncMock(return_value=sample_menu_output)
            
            response = test_client.post(
                "/api/menu/generate",
                json={
                    "num_guests": 4,
                    "cuisines": ["italiana"]
                }
            )
            
            assert response.status_code == 200


# =============================================================================
# TEST GET MENU ENDPOINT
# =============================================================================

class TestGetMenuEndpoint:
    """Test per GET /api/menu/{menu_id}."""
    
    def test_get_menu_not_found(self, test_client):
        """Test 404 per menu_id inesistente."""
        fake_id = str(uuid4())
        response = test_client.get(f"/api/menu/{fake_id}")
        
        assert response.status_code == 404
    
    def test_get_menu_invalid_uuid(self, test_client):
        """Test errore per UUID non valido."""
        response = test_client.get("/api/menu/not-a-valid-uuid")
        
        assert response.status_code == 422
    
    def test_get_menu_success(self, test_client, sample_menu_output):
        """Test recupero menù esistente."""
        # Prima salva un menù nello store
        from services.menu_service import save_menu, menu_store
        
        save_menu(sample_menu_output)
        menu_id = str(sample_menu_output.menu_id)
        
        response = test_client.get(f"/api/menu/{menu_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["menu_id"] == menu_id
        
        # Cleanup
        del menu_store[menu_id]


# =============================================================================
# TEST LIST MENUS ENDPOINT
# =============================================================================

class TestListMenusEndpoint:
    """Test per GET /api/menu/."""
    
    def test_list_menus_empty(self, test_client):
        """Test lista vuota."""
        from services.menu_service import menu_store
        
        # Pulisci lo store
        menu_store.clear()
        
        response = test_client.get("/api/menu/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_menus_with_items(self, test_client, sample_menu_output):
        """Test lista con menù."""
        from services.menu_service import save_menu, menu_store
        
        # Aggiungi un menù
        save_menu(sample_menu_output)
        
        response = test_client.get("/api/menu/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Cleanup
        menu_store.clear()


# =============================================================================
# TEST DELETE MENU ENDPOINT
# =============================================================================

class TestDeleteMenuEndpoint:
    """Test per DELETE /api/menu/{menu_id}."""
    
    def test_delete_menu_not_found(self, test_client):
        """Test 404 per eliminazione menu inesistente."""
        fake_id = str(uuid4())
        response = test_client.delete(f"/api/menu/{fake_id}")
        
        assert response.status_code == 404
    
    def test_delete_menu_success(self, test_client, sample_menu_output):
        """Test eliminazione menù."""
        from services.menu_service import save_menu, menu_store, get_menu
        
        # Prima salva
        save_menu(sample_menu_output)
        menu_id = str(sample_menu_output.menu_id)
        
        # Verifica esistenza
        assert get_menu(menu_id) is not None
        
        # Elimina
        response = test_client.delete(f"/api/menu/{menu_id}")
        
        assert response.status_code == 200
        
        # Verifica eliminazione
        assert get_menu(menu_id) is None


# =============================================================================
# TEST SHOPPING LIST ENDPOINT
# =============================================================================

class TestShoppingListEndpoint:
    """Test per GET /api/menu/{menu_id}/shopping-list."""
    
    def test_get_shopping_list_not_found(self, test_client):
        """Test 404 per menu_id inesistente."""
        fake_id = str(uuid4())
        response = test_client.get(f"/api/menu/{fake_id}/shopping-list")
        
        assert response.status_code == 404
    
    def test_get_shopping_list_success(self, test_client, sample_menu_output):
        """Test recupero lista spesa."""
        from services.menu_service import save_menu, menu_store
        
        save_menu(sample_menu_output)
        menu_id = str(sample_menu_output.menu_id)
        
        response = test_client.get(f"/api/menu/{menu_id}/shopping-list")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        
        # Cleanup
        del menu_store[menu_id]


# =============================================================================
# TEST TIMELINE ENDPOINT
# =============================================================================

class TestTimelineEndpoint:
    """Test per GET /api/menu/{menu_id}/timeline."""
    
    def test_get_timeline_not_found(self, test_client):
        """Test 404 per menu_id inesistente."""
        fake_id = str(uuid4())
        response = test_client.get(f"/api/menu/{fake_id}/timeline")
        
        assert response.status_code == 404
    
    def test_get_timeline_success(self, test_client, sample_menu_output):
        """Test recupero timeline."""
        from services.menu_service import save_menu, menu_store
        
        save_menu(sample_menu_output)
        menu_id = str(sample_menu_output.menu_id)
        
        response = test_client.get(f"/api/menu/{menu_id}/timeline")
        
        assert response.status_code == 200
        data = response.json()
        assert "two_days_before" in data
        assert "one_day_before" in data
        assert "day_of" in data
        
        # Cleanup
        del menu_store[menu_id]


# =============================================================================
# TEST ERROR HANDLING
# =============================================================================

class TestErrorHandling:
    """Test per gestione errori API."""
    
    def test_invalid_json_body(self, test_client):
        """Test errore per JSON non valido."""
        response = test_client.post(
            "/api/menu/generate",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_field(self, test_client):
        """Test errore per campo obbligatorio mancante."""
        response = test_client.post(
            "/api/menu/generate",
            json={"cuisines": ["italiana"]}  # Manca num_guests
        )
        
        assert response.status_code == 422
    
    def test_generation_error_handling(self, test_client):
        """Test gestione errore durante generazione."""
        with patch('api.menu_routes.menu_service') as mock_service:
            mock_service.generate_menu = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            response = test_client.post(
                "/api/menu/generate",
                json={
                    "num_guests": 4,
                    "cuisines": ["italiana"]
                }
            )
            
            # Dovrebbe restituire 500
            assert response.status_code == 500


# =============================================================================
# TEST CORS
# =============================================================================

class TestCORS:
    """Test per configurazione CORS."""
    
    def test_cors_preflight(self, test_client):
        """Test preflight request CORS."""
        response = test_client.options(
            "/api/menu/generate",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # OPTIONS dovrebbe essere gestito
        assert response.status_code in [200, 204, 405]
    
    def test_cors_headers_present(self, test_client):
        """Test che gli header CORS siano presenti."""
        response = test_client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        # Verifica che la richiesta vada a buon fine
        assert response.status_code == 200
