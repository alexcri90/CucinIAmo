"""
API Package per Christmas Menu Generator

Contiene i router FastAPI per gli endpoint dell'applicazione.
"""

from api.menu_routes import router as menu_router

__all__ = ["menu_router"]