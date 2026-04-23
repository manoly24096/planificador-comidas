# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) al trabajar con el código de este repositorio.

## Ejecutar la aplicación

```bash
pip install -r requirements.txt
streamlit run app.py
```

La aplicación requiere secretos de Streamlit para conectarse a Supabase. Crear `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu-anon-key"
```

## Arquitectura

Es una aplicación Streamlit de un solo archivo (`app.py`) — un planificador de menú semanal (Planificador Pro) enfocado en cocina peruana. Toda la UI, el manejo de estado y el acceso a datos viven en ese único archivo.

**Backend**: Supabase (PostgreSQL). La app usa dos tablas:
- `recetario` — almacena recetas. Columnas clave: `nombre_plato` (PK), `categoria`, `porciones_base`, `ingredientes_texto` (texto libre), `preparacion`, `ingredientes` (campo JSON sin uso, legado)
- `ingredientes_db` — ingredientes con precios (usado en `appold.py` pero no en el `app.py` actual)

**Manejo de estado**: Todos los datos en tiempo de ejecución viven en `st.session_state`:
- `recetario` — dict indexado por nombre de plato, cargado desde Supabase al primer render
- `plan` — lista de dicts `{plato, porciones, categoria}` que representan el menú semanal
- `temp_ing` — dict temporal de ingredientes mientras se crea o edita una receta
- `form_key` — entero que se incrementa para forzar el reseteo de formularios de Streamlit

**Navegación**: Tres secciones controladas por un `st.radio` en el sidebar:
1. **📝 Mi Plan Semanal** — muestra el plan, la lista de compras por plato y las exportaciones (Excel + WhatsApp)
2. **📖 Recetario** — explorador de recetas con filtro por categoría y búsqueda por nombre
3. **🍳 Crear / Editar Platos** — crear o editar recetas; se guarda con `supabase.upsert(on_conflict="nombre_plato")`

## Decisiones de diseño clave

- `app.py` almacena los ingredientes como **texto libre** (`ingredientes_texto`) en lugar de datos estructurados. Simplifica el ingreso de recetas a costa de no poder agregar ni calcular costos automáticamente.
- `appold.py` es la versión anterior con una base de ingredientes estructurada (precios, unidades y cálculo de costos) — se conserva como referencia pero no es la app activa.
- `recetario.json` e `ingredientes_db.json` son archivos locales de datos legados que `app.py` no utiliza.
- Los datos de Supabase se cargan una vez en el session state al iniciar (`cargar_recetario()`). Tras cualquier escritura, se refresca el estado llamando nuevamente a `cargar_recetario()` y luego `st.rerun()`.
- La lista de compras en Mi Plan Semanal **no** agrega ni deduplica ingredientes entre platos — muestra el `ingredientes_texto` crudo de cada plato del plan. Cualquier lógica de agregación requeriría parsear ese campo de texto libre.

## Categorías

La lista fija de categorías de platos (`CATEGORIAS`) está definida a nivel de módulo en `app.py`. Para agregar nuevas categorías, modificar esa lista.
