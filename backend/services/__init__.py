"""
Services Package per Christmas Menu Generator

Contiene i servizi di business logic:
- prompt_templates: Template di prompt ottimizzati per Gemini
- structured_generation: Logica di generazione con Structured Responses
- menu_service: Business logic per la generazione menù
- memory_manager: Gestione Memory Datapizza AI per rigenerazione contestualizzata
"""

from backend.services.prompt_templates import (
    build_menu_generation_prompt,
    build_course_regeneration_prompt,
    build_recipe_detail_prompt,
    MENU_AGENT_SYSTEM_PROMPT,
    RECIPE_AGENT_SYSTEM_PROMPT,
    AGGREGATION_AGENT_SYSTEM_PROMPT
)

from backend.services.structured_generation import (
    generate_menu_structured,
    generate_recipe_structured,
    regenerate_course_structured,
    validate_menu_output,
    StructuredMenuGenerator
)

from backend.services.menu_service import (
    MenuService,
    menu_store,
    save_menu,
    get_menu,
    delete_menu,
    get_menu_service
)

from backend.services.memory_manager import (
    create_memory_for_menu,
    get_memory_for_menu,
    delete_memory_for_menu,
    save_menu_context_to_memory,
    build_user_input_summary,
    build_menu_summary,
    regenerate_course_with_memory,
    get_memory_stats
)

__all__ = [
    # Prompt templates
    "build_menu_generation_prompt",
    "build_course_regeneration_prompt",
    "build_recipe_detail_prompt",
    "MENU_AGENT_SYSTEM_PROMPT",
    "RECIPE_AGENT_SYSTEM_PROMPT",
    "AGGREGATION_AGENT_SYSTEM_PROMPT",
    # Structured generation
    "generate_menu_structured",
    "generate_recipe_structured",
    "regenerate_course_structured",
    "validate_menu_output",
    "StructuredMenuGenerator",
    # Menu service
    "MenuService",
    "menu_store",
    "save_menu",
    "get_menu",
    "delete_menu",
    "get_menu_service",
    # Memory manager
    "create_memory_for_menu",
    "get_memory_for_menu",
    "delete_memory_for_menu",
    "save_menu_context_to_memory",
    "build_user_input_summary",
    "build_menu_summary",
    "regenerate_course_with_memory",
    "get_memory_stats",
]