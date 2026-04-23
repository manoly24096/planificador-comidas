# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app requires Streamlit secrets for Supabase. Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

## Architecture

This is a single-file Streamlit app (`app.py`) — a weekly meal planner (Planificador Pro) focused on Peruvian cuisine. All UI, state management, and data access live in one file.

**Backend**: Supabase (PostgreSQL). The app uses two tables:
- `recetario` — stores recipes. Key columns: `nombre_plato` (PK), `categoria`, `porciones_base`, `ingredientes_texto` (free-text string), `preparacion`, `ingredientes` (unused JSON field, legacy)
- `ingredientes_db` — ingredients with pricing (used in `appold.py` but not in the current `app.py`)

**State management**: All runtime data lives in `st.session_state`:
- `recetario` — dict keyed by dish name, loaded from Supabase on first render
- `plan` — list of `{plato, porciones, categoria}` dicts representing the weekly menu
- `temp_ing` — temporary ingredient dict while creating/editing a recipe
- `form_key` — integer incremented to force Streamlit form reset

**Navigation**: Three sections controlled by a sidebar `st.radio`:
1. **📝 Mi Plan Semanal** — displays the plan, shopping list per dish, and exports (Excel + WhatsApp)
2. **📖 Recetario** — filterable/searchable recipe browser with add-to-plan button
3. **🍳 Crear / Editar Platos** — create or edit recipes; saves via `supabase.upsert(on_conflict="nombre_plato")`

## Key Design Decisions

- `app.py` stores ingredients as a **free-text string** (`ingredientes_texto`) rather than structured data. This simplifies recipe entry at the cost of not being able to auto-aggregate or price ingredients.
- `appold.py` is the previous version that had a full structured ingredient database with pricing and unit tracking — kept for reference but not the active app.
- `recetario.json` and `ingredientes_db.json` are legacy local data files not used by `app.py`.
- Supabase data is loaded once into session state at startup (`cargar_recetario()`). After any write, the session state is refreshed by calling `cargar_recetario()` again and then `st.rerun()`.
- The shopping list in Mi Plan Semanal does **not** aggregate or deduplicate ingredients across dishes — it displays the raw `ingredientes_texto` for each planned dish. Any aggregation logic would need to parse the free-text field.

## Categories

The fixed list of dish categories (`CATEGORIAS`) is defined at module level in `app.py`. If new categories are needed, add them to that list.
