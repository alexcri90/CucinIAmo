"""Test di connessione con Datapizza AI e Google Gemini."""
import os
from dotenv import load_dotenv
from datapizza.clients.google import GoogleClient

# Carica variabili d'ambiente
load_dotenv()

def test_connection():
    """Test connessione base con Gemini via Datapizza AI."""
    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY non trovata nel file .env!")
    
    print(f"🔍 Testing connessione con {model}...")
    
    # Crea client
    client = GoogleClient(
        api_key=api_key,
        model=model,
        system_prompt="Sei un assistente utile che risponde in italiano.",
        temperature=0.7
    )
    
    # Test invocazione semplice
    response = client.invoke("Ciao! Dimmi in una frase cosa sai fare.")
    
    print(f"\n✅ Connessione riuscita!")
    print(f"📊 Modello: {model}")
    print(f"💬 Risposta: {response.text}")
    print(f"🎫 Token usati: {response.completion_tokens_used}")
    print(f"📝 Token prompt: {response.prompt_tokens_used}")
    
    return True

if __name__ == "__main__":
    try:
        test_connection()
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        raise