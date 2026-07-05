"""
Test per l'API FastAPI

Questo script testa gli endpoint dell'API usando requests.

PREREQUISITI:
1. Il server deve essere in esecuzione:
   uvicorn backend.main:app --reload --port 8000

2. Esegui questo script in un altro terminale:
   python backend/test_api.py

NOTA: Puoi anche usare Swagger UI su http://localhost:8000/docs
"""

import requests
import json
import time
from datetime import datetime

# Configurazione
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/menu"


def print_header(text: str):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_response(response, show_body: bool = True):
    print(f"   Status: {response.status_code}")
    if show_body:
        try:
            data = response.json()
            print(f"   Body: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        except:
            print(f"   Body: {response.text[:500]}...")


def test_health():
    """Test 1: Health check."""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_response(response)
        
        if response.status_code == 200:
            print("   ✅ Health check OK!")
            return True
        else:
            print("   ❌ Health check fallito")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Server non raggiungibile!")
        print("   💡 Avvia il server con: uvicorn backend.main:app --reload --port 8000")
        return False


def test_generate_menu():
    """Test 2: Genera un menù."""
    print_header("TEST 2: Genera Menù")
    
    print("   ⏳ Invio richiesta (può richiedere 30-60 secondi)...")
    
    payload = {
        "num_guests": 4,
        "cuisines": ["italiana"],
        "preferred_ingredients": ["salmone"],
        "avoided_ingredients": ["piccante"],
        "dietary_restrictions": [],
        "difficulty_level": "facile",
        "budget_level": "economico"
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json=payload,
            timeout=120  # 2 minuti di timeout
        )
        
        elapsed = time.time() - start_time
        print(f"   ⏱️  Tempo: {elapsed:.1f} secondi")
        
        if response.status_code == 200:
            menu = response.json()
            print(f"\n   ✅ Menù generato con successo!")
            print(f"   📋 Menu ID: {menu.get('menu_id')}")
            
            # Mostra portate
            courses = menu.get('courses', {})
            print(f"\n   🍽️  Portate:")
            for course_type in ['antipasti', 'primo', 'secondo', 'contorno', 'dessert']:
                items = courses.get(course_type, [])
                for item in items:
                    print(f"      • {course_type}: {item.get('name')}")
            
            return menu
        else:
            print(f"   ❌ Errore: {response.status_code}")
            print_response(response)
            return None
            
    except requests.exceptions.Timeout:
        print("   ❌ Timeout! La richiesta ha superato i 2 minuti.")
        return None
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return None


def test_get_menu(menu_id: str):
    """Test 3: Recupera un menù."""
    print_header("TEST 3: Recupera Menù")
    
    try:
        response = requests.get(f"{API_URL}/{menu_id}", timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Menù {menu_id} recuperato!")
            return True
        elif response.status_code == 404:
            print(f"   ⚠️  Menù non trovato (normale se il server è stato riavviato)")
            return False
        else:
            print_response(response)
            return False
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False


def test_list_menus():
    """Test 4: Lista menù."""
    print_header("TEST 4: Lista Menù")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        
        if response.status_code == 200:
            menus = response.json()
            print(f"   ✅ Trovati {len(menus)} menù salvati")
            for m in menus:
                print(f"      • {m.get('menu_id')[:8]}... - {m.get('num_guests')} ospiti")
            return True
        else:
            print_response(response)
            return False
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False


def test_shopping_list(menu_id: str):
    """Test 5: Recupera lista spesa."""
    print_header("TEST 5: Lista Spesa")
    
    try:
        response = requests.get(f"{API_URL}/{menu_id}/shopping-list", timeout=10)
        
        if response.status_code == 200:
            shopping = response.json()
            categories = shopping.get('categories', {})
            total = sum(len(items) for items in categories.values())
            print(f"   ✅ Lista spesa: {total} ingredienti in {len(categories)} categorie")
            return True
        else:
            print_response(response)
            return False
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False


def test_timeline(menu_id: str):
    """Test 6: Recupera timeline."""
    print_header("TEST 6: Timeline")
    
    try:
        response = requests.get(f"{API_URL}/{menu_id}/timeline", timeout=10)
        
        if response.status_code == 200:
            timeline = response.json()
            print(f"   ✅ Timeline recuperata:")
            print(f"      • 2 giorni prima: {len(timeline.get('two_days_before', []))} attività")
            print(f"      • 1 giorno prima: {len(timeline.get('one_day_before', []))} attività")
            print(f"      • Giorno stesso: {len(timeline.get('day_of', {}))} slot orari")
            return True
        else:
            print_response(response)
            return False
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False


def run_all_tests():
    """Esegue tutti i test."""
    print("\n" + "=" * 70)
    print("  🎄 CHRISTMAS MENU GENERATOR - API TEST SUITE 🎄")
    print("=" * 70)
    print(f"\n  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Server: {BASE_URL}")
    
    results = {}
    menu_id = None
    
    # Test 1: Health
    results['health'] = test_health()
    
    if not results['health']:
        print("\n❌ Server non disponibile. Avvialo prima di eseguire i test.")
        return results
    
    # Test 2: Genera menù
    print("\n" + "-" * 70)
    run_generate = input("  Eseguire test generazione menù? (richiede ~60s) [s/n]: ").lower().strip()
    
    if run_generate == 's':
        menu = test_generate_menu()
        results['generate'] = menu is not None
        
        if menu:
            menu_id = menu.get('menu_id')
    else:
        print("   ⏭️  Test generazione saltato")
        results['generate'] = None
    
    # Test 3-6: Solo se abbiamo un menu_id
    if menu_id:
        results['get_menu'] = test_get_menu(menu_id)
        results['list_menus'] = test_list_menus()
        results['shopping_list'] = test_shopping_list(menu_id)
        results['timeline'] = test_timeline(menu_id)
    else:
        print("\n   ⏭️  Test 3-6 saltati (nessun menù generato)")
    
    # Riepilogo
    print_header("📊 RIEPILOGO")
    
    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)
    
    print(f"\n  Test passati: {passed}/{total}")
    
    for name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️ SKIP"
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 70)
    
    return results


def quick_test():
    """Test veloce solo health check."""
    print_header("🎄 QUICK TEST - Health Check")
    
    if test_health():
        print("\n✅ Server operativo!")
        print("📖 Apri http://localhost:8000/docs per Swagger UI")
    else:
        print("\n❌ Server non raggiungibile")
        print("💡 Avvia con: uvicorn backend.main:app --reload --port 8000")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        run_all_tests()