"""
Christmas Menu Generator - Backend API

Entry point per l'applicazione FastAPI.
Avvia con: uvicorn backend.main:app --reload --port 8000

Endpoints disponibili:
- GET  /health              - Health check
- POST /api/menu/generate   - Genera menù completo
- POST /api/menu/regenerate - Rigenera una portata
- GET  /api/menu/{menu_id}  - Recupera menù salvato
- GET  /docs                - Documentazione Swagger UI
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Aggiungi il path per import relativi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import routes
from api.menu_routes import router as menu_router

# Carica variabili d'ambiente
from dotenv import load_dotenv
load_dotenv()


# =============================================================================
# LIFECYCLE MANAGEMENT
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestione del ciclo di vita dell'applicazione.
    
    Startup: Inizializza risorse
    Shutdown: Pulisce risorse
    """
    # === STARTUP ===
    print("\n" + "=" * 60)
    print("🎄 Christmas Menu Generator API - Starting...")
    print("=" * 60)
    
    # Verifica API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  WARNING: GOOGLE_API_KEY non configurata!")
    else:
        print(f"✅ Google API Key configurata: {api_key[:10]}...")
    
    # Imposta log level Datapizza
    log_level = os.getenv("DATAPIZZA_AGENT_LOG_LEVEL", "INFO")
    os.environ["DATAPIZZA_AGENT_LOG_LEVEL"] = log_level
    print(f"✅ Datapizza log level: {log_level}")
    
    print("\n🚀 Server pronto!")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   Health check: http://localhost:8000/health")
    print("=" * 60 + "\n")
    
    yield  # L'applicazione gira qui
    
    # === SHUTDOWN ===
    print("\n🛑 Shutting down Christmas Menu Generator API...")


# =============================================================================
# APP CONFIGURATION
# =============================================================================

app = FastAPI(
    title="Christmas Menu Generator API",
    description="""
    🎄 **API per generare menù natalizi personalizzati con AI**
    
    Utilizza **Datapizza AI** con **Google Gemini 2.5 Flash** per creare:
    - Menù completi con antipasti, primo, secondo, contorno e dessert
    - Ricette dettagliate con ingredienti e procedimento
    - Lista della spesa aggregata per categorie
    - Timeline di preparazione (2 giorni prima → giorno stesso)
    
    ## Come usare
    
    1. Chiama `POST /api/menu/generate` con le tue preferenze
    2. Ricevi un menù completo in formato JSON
    3. Se non ti piace una portata, usa `POST /api/menu/regenerate`
    4. Recupera menù salvati con `GET /api/menu/{menu_id}`
    
    ## Rate Limits
    
    - Free tier Gemini: 15 richieste/minuto, 1500/giorno
    - Generazione menù: ~30-60 secondi per richiesta
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# =============================================================================
# CORS MIDDLEWARE
# =============================================================================

# Origini permesse per CORS
# In produzione, aggiungiamo automaticamente l'URL del frontend su Render
ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React dev server
    "http://localhost:5173",      # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Aggiungi origini di produzione da variabile d'ambiente
# Formato: "https://christmas-menu-app.onrender.com,https://altro-dominio.com"
production_origins = os.getenv("ALLOWED_ORIGINS", "")
if production_origins:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in production_origins.split(",")])

# Se siamo in produzione su Render, permetti anche il dominio .onrender.com
if os.getenv("RENDER"):
    # Permetti qualsiasi sottodominio di onrender.com per semplicità
    ALLOWED_ORIGINS.append("https://christmas-menu-app.onrender.com")

# Configura CORS per permettere richieste dal frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handler per HTTPException con formato consistente."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handler per eccezioni generiche."""
    print(f"❌ Errore non gestito: {exc}")
    import traceback
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Errore interno del server. Riprova più tardi.",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# =============================================================================
# ROUTES
# =============================================================================

# Include router per i menù
app.include_router(menu_router, prefix="/api/menu", tags=["Menu"])


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint con info sull'API."""
    return {
        "name": "Christmas Menu Generator API",
        "version": "1.0.0",
        "description": "API per generare menù natalizi con AI",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Verifica che l'API sia operativa e che le dipendenze siano configurate.
    """
    # Verifica API key
    api_key = os.getenv("GOOGLE_API_KEY")
    api_key_status = "configured" if api_key else "missing"
    
    # Verifica connessione Gemini (opzionale, commentato per velocità)
    gemini_status = "not_tested"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "operational",
            "google_api_key": api_key_status,
            "gemini": gemini_status
        },
        "version": "1.0.0"
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configurazione sviluppo
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )