r"""
Test End-to-End per Structured Generation

Questo script testa la generazione completa di un menù natalizio
usando Datapizza AI con Google Gemini 2.5 Flash.

ESECUZIONE:
    cd Christmas-World-Menu
    .\.venv\Scripts\Activate.ps1
    python backend/test_structured.py

NOTA: Richiede GOOGLE_API_KEY configurata nel file .env
"""

import os
import sys
import json
from datetime import datetime

# Aggiungi il path del backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carica variabili d'ambiente
from dotenv import load_dotenv
load_dotenv()

# Import modelli
from models.input_models import (
    UserInput,
    Cuisine,
    DifficultyLevel,
    BudgetLevel,
    DietaryRestriction
)
from models.output_models import MenuOutput

# Import servizi
from services.prompt_templates import build_menu_generation_prompt
from services.structured_generation import (
    generate_menu_structured,
    generate_recipe_structured,
    validate_menu_output,
    StructuredMenuGenerator
)


def print_header(text: str):
    """Stampa un header formattato."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_section(text: str):
    """Stampa una sezione formattata."""
    print(f"\n{'─' * 40}")
    print(f"  {text}")
    print("─" * 40)


def check_python_version():
    """Verifica la versione di Python."""
    version = sys.version_info
    print(f"\n   Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 13:
        print("   ⚠️  WARNING: Python 3.13+ potrebbe avere problemi di compatibilità")
        print("      con Datapizza AI (richiede Python >=3.10.0,<3.13.0)")
        print("      Consigliato: Python 3.12.x")
        return False
    elif version.major == 3 and 10 <= version.minor <= 12:
        print("   ✅ Versione Python compatibile")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} non supportato")
        return False


def test_connection():
    """Test 1: Verifica connessione a Gemini."""
    print_section("TEST 1: Connessione Gemini")
    
    from datapizza.clients.google import GoogleClient
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("   ❌ GOOGLE_API_KEY non trovata!")
        return False
    
    print(f"   API Key: {api_key[:15]}...")
    
    try:
        client = GoogleClient(
            api_key=api_key,
            model="gemini-2.5-flash",
            system_prompt="Sei un assistente di test.",
            temperature=0.5
        )
        
        response = client.invoke("Rispondi solo con la parola: FUNZIONA")
        print(f"   Risposta: {response.text.strip()}")
        print("   ✅ Connessione OK!")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False


def test_prompt_generation():
    """Test 2: Verifica generazione prompt."""
    print_section("TEST 2: Generazione Prompt")
    
    try:
        # Crea input di test
        test_input = UserInput(
            num_guests=6,
            preferred_ingredients=["salmone", "tartufo"],
            avoided_ingredients=["piccante", "funghi porcini"],
            cuisines=[Cuisine.ITALIANA],
            dietary_restrictions=[],
            difficulty_level=DifficultyLevel.MEDIO,
            budget_level=BudgetLevel.MEDIO
        )
        
        # Genera prompt
        prompt = build_menu_generation_prompt(test_input)
        
        print(f"   Input validato: ✅")
        print(f"   Prompt generato: {len(prompt)} caratteri")
        print(f"   Preview:\n{prompt[:500]}...\n")
        print("   ✅ Prompt generation OK!")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False


def test_simple_structured_response():
    """Test 3: Test structured response semplice."""
    print_section("TEST 3: Structured Response Semplice")
    
    from datapizza.clients.google import GoogleClient
    from pydantic import BaseModel
    from typing import List
    
    class SimpleRecipe(BaseModel):
        name: str
        ingredients: List[str]
        prep_time_minutes: int
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        client = GoogleClient(
            api_key=api_key,
            model="gemini-2.5-flash",
            system_prompt="Sei uno chef. Rispondi solo con JSON.",
            temperature=0.5
        )
        
        response = client.structured_response(
            input="Genera una ricetta semplice per pasta al pomodoro per 4 persone.",
            output_cls=SimpleRecipe
        )
        
        recipe = response.structured_data[0]
        print(f"   Nome: {recipe.name}")
        print(f"   Ingredienti: {len(recipe.ingredients)}")
        print(f"   Tempo: {recipe.prep_time_minutes} min")
        print("   ✅ Structured response OK!")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_menu_generation():
    """Test 4: Generazione menù completo."""
    print_section("TEST 4: Generazione Menù Completo")
    
    print("\n   ⚠️  ATTENZIONE: Questo test richiede ~30-60 secondi...")
    print("      Il test genera un menù natalizio completo.\n")
    
    # Input di test
    test_input = UserInput(
        num_guests=4,
        preferred_ingredients=["salmone"],
        avoided_ingredients=["piccante"],
        cuisines=[Cuisine.ITALIANA],
        dietary_restrictions=[],
        difficulty_level=DifficultyLevel.FACILE,
        budget_level=BudgetLevel.ECONOMICO
    )
    
    try:
        start_time = datetime.now()
        
        # Genera il menù
        menu = generate_menu_structured(test_input)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n   ⏱️  Tempo di generazione: {elapsed:.1f} secondi")
        print(f"\n   📋 MENU GENERATO:")
        print(f"      ID: {menu.menu_id}")
        print(f"      Generated at: {menu.generated_at}")
        
        # Mostra le portate
        print(f"\n   🍽️  PORTATE:")
        for antipasto in menu.courses.antipasti:
            print(f"      • Antipasto: {antipasto.name} ({antipasto.cuisine})")
        for primo in menu.courses.primo:
            print(f"      • Primo: {primo.name} ({primo.cuisine})")
        for secondo in menu.courses.secondo:
            print(f"      • Secondo: {secondo.name} ({secondo.cuisine})")
        for contorno in menu.courses.contorno:
            print(f"      • Contorno: {contorno.name} ({contorno.cuisine})")
        for dessert in menu.courses.dessert:
            print(f"      • Dessert: {dessert.name} ({dessert.cuisine})")
        
        # Mostra shopping list summary
        if menu.shopping_list and menu.shopping_list.categories:
            total_items = sum(len(items) for items in menu.shopping_list.categories.values())
            print(f"\n   🛒 LISTA SPESA: {total_items} ingredienti in {len(menu.shopping_list.categories)} categorie")
        
        # Mostra timeline summary
        if menu.timeline:
            print(f"\n   📅 TIMELINE:")
            if menu.timeline.two_days_before:
                print(f"      • 2 giorni prima: {len(menu.timeline.two_days_before)} attività")
            if menu.timeline.one_day_before:
                print(f"      • 1 giorno prima: {len(menu.timeline.one_day_before)} attività")
            if menu.timeline.day_of:
                print(f"      • Giorno stesso: {len(menu.timeline.day_of)} slot orari")
        
        # Valida il menù
        warnings = validate_menu_output(menu)
        if warnings:
            print(f"\n   ⚠️  WARNING: {len(warnings)} avvisi")
            for w in warnings:
                print(f"      - {w}")
        else:
            print(f"\n   ✅ Validazione: nessun warning")
        
        print("\n   ✅ Generazione menù completa OK!")
        return menu
        
    except Exception as e:
        print(f"\n   ❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_recipe_detail():
    """Test 5: Generazione ricetta dettagliata."""
    print_section("TEST 5: Generazione Ricetta Dettagliata")
    
    try:
        recipe = generate_recipe_structured(
            dish_name="Tortellini in brodo",
            cuisine="Italiana (Emilia-Romagna)",
            num_guests=4,
            difficulty_level="medio",
            avoided_ingredients=["piccante"],
            dietary_restrictions=[]
        )
        
        print(f"   Nome piatto: Tortellini in brodo")
        print(f"   Ingredienti: {len(recipe.ingredients)}")
        print(f"   Steps: {len(recipe.steps)}")
        print(f"   Prep time: {recipe.prep_time_minutes} min")
        print(f"   Cook time: {recipe.cook_time_minutes} min")
        print(f"   Difficoltà: {recipe.difficulty}")
        print(f"   Prep ahead: {recipe.can_prep_ahead}")
        
        if recipe.chef_notes:
            print(f"   Note chef: {recipe.chef_notes[:100]}...")
        
        print("\n   ✅ Generazione ricetta OK!")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_menu_to_file(menu: MenuOutput, filename: str = "test_menu_output.json"):
    """Salva il menù generato in un file JSON."""
    try:
        menu_dict = menu.model_dump(mode="json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(menu_dict, f, ensure_ascii=False, indent=2)
        
        print(f"\n   💾 Menù salvato in: {filename}")
        return True
    except Exception as e:
        print(f"   ❌ Errore salvataggio: {e}")
        return False


def run_all_tests():
    """Esegue tutti i test in sequenza."""
    print_header("🎄 CHRISTMAS MENU GENERATOR - TEST SUITE 🎄")
    
    print(f"\nData/Ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    check_python_version()
    
    results = {
        "connection": False,
        "prompt": False,
        "simple_structured": False,
        "full_menu": False,
        "recipe_detail": False
    }
    
    # Test 1: Connessione
    results["connection"] = test_connection()
    if not results["connection"]:
        print("\n❌ Impossibile continuare senza connessione a Gemini.")
        return results
    
    # Test 2: Prompt
    results["prompt"] = test_prompt_generation()
    
    # Test 3: Structured Response semplice
    results["simple_structured"] = test_simple_structured_response()
    
    # Test 4: Menu completo (opzionale)
    print("\n" + "─" * 40)
    run_full = input("  Eseguire test generazione menù completo? (s/n): ").lower().strip()
    
    if run_full == "s":
        menu = test_full_menu_generation()
        results["full_menu"] = menu is not None
        
        if menu:
            save = input("\n  Salvare il menù generato su file JSON? (s/n): ").lower().strip()
            if save == "s":
                save_menu_to_file(menu)
    else:
        print("   ⏭️  Test menù completo saltato")
    
    # Test 5: Ricetta dettagliata (opzionale)
    print("\n" + "─" * 40)
    run_recipe = input("  Eseguire test ricetta dettagliata? (s/n): ").lower().strip()
    
    if run_recipe == "s":
        results["recipe_detail"] = test_recipe_detail()
    else:
        print("   ⏭️  Test ricetta saltato")
    
    # Riepilogo
    print_header("📊 RIEPILOGO TEST")
    
    executed = [k for k, v in results.items() if v is not False or k in ["connection", "prompt", "simple_structured"]]
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n  Test passati: {passed}/{len(executed)}")
    print()
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False and test_name in ["full_menu", "recipe_detail"]:
            status = "⏭️ SKIP/FAIL"
        else:
            status = "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print("\n" + "=" * 80)
    
    if passed >= 3:
        print("  🎉 Test principali passati! Il sistema è pronto.")
    else:
        print("  ⚠️  Alcuni test non sono passati. Verifica gli errori sopra.")
    
    print("=" * 80 + "\n")
    
    return results


def run_quick_test():
    """Esegue solo i test veloci."""
    print_header("🎄 QUICK TEST - Christmas Menu Generator 🎄")
    
    check_python_version()
    
    results = []
    
    results.append(("Connessione", test_connection()))
    results.append(("Prompt Generation", test_prompt_generation()))
    results.append(("Structured Response", test_simple_structured_response()))
    
    print_header("📊 RIEPILOGO")
    
    passed = sum(1 for _, r in results if r)
    print(f"\n  Risultato: {passed}/{len(results)} test passati\n")
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print("\n" + "=" * 80)
    
    return all(r for _, r in results)


def run_full_test():
    """Esegue tutti i test senza chiedere conferma."""
    print_header("🎄 CHRISTMAS MENU GENERATOR - FULL TEST 🎄")
    
    print(f"\nData/Ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    check_python_version()
    
    results = {}
    
    results["connection"] = test_connection()
    if not results["connection"]:
        print("\n❌ Impossibile continuare senza connessione.")
        return results
    
    results["prompt"] = test_prompt_generation()
    results["simple_structured"] = test_simple_structured_response()
    
    menu = test_full_menu_generation()
    results["full_menu"] = menu is not None
    
    if menu:
        save_menu_to_file(menu)
    
    results["recipe_detail"] = test_recipe_detail()
    
    # Riepilogo
    print_header("📊 RIEPILOGO FINALE")
    
    passed = sum(1 for v in results.values() if v)
    print(f"\n  Test passati: {passed}/{len(results)}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print("\n" + "=" * 80)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Structured Generation")
    parser.add_argument("--quick", action="store_true", help="Esegui solo test veloci")
    parser.add_argument("--full", action="store_true", help="Esegui tutti i test")
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_test()
    elif args.full:
        run_full_test()
    else:
        run_all_tests()