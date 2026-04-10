import streamlit as st
from supabase import create_client

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="Planificador Pro", layout="wide")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- 2. FUNCIONES DE CARGA (NUBE) ---
def cargar_ingredientes():
    try:
        res = supabase.table("ingredientes_db").select("*").execute()
        # Mapeamos usando el nombre para mostrar como clave principal en la app
        return {item['display_name']: item for item in res.data}
    except: return {}

def cargar_recetario():
    try:
        res = supabase.table("recetario").select("*").execute()
        return {item['nombre_plato']: item for item in res.data}
    except: return {}

# --- 3. ESTADOS DE SESIÓN ---
if 'ingredientes_db' not in st.session_state:
    st.session_state.ingredientes_db = cargar_ingredientes()
if 'recetario' not in st.session_state:
    st.session_state.recetario = cargar_recetario()
if 'temp_ing' not in st.session_state:
    st.session_state.temp_ing = {}
if 'plan' not in st.session_state:
    st.session_state.plan = []

# --- 4. BARRA LATERAL ---
st.sidebar.title("Menú Principal")
opcion = st.sidebar.radio("Ir a:", ["Mi Plan 📝", "Recetario 📖", "Añadir/Editar Platos 🍳", "Base de Ingredientes 🍅"])

# --- SECCIÓN: INGREDIENTES (CON AUTO-EDICIÓN) ---
if opcion == "Base de Ingredientes 🍅":
    st.title("Gestión de Ingredientes")
    st.info("Si el nombre ya existe, se actualizará el precio y la categoría.")
    
    with st.form("form_ing"):
        n = st.text_input("Nombre del Ingrediente (ej: Camote)")
        cat = st.selectbox("Categoría", ["Abarrotes", "Carnes", "Verduras", "Frutas", "Otros"])
        p = st.number_input("Precio S/", min_value=0.0, step=0.1)
        if st.form_submit_button("Guardar Permanente"):
            if n:
                datos = {
                    "key_name": n.lower().strip(),
                    "display_name": n,
                    "precio_base": p,
                    "categoria": cat
                }
                # .upsert permite que si ya existe, se actualice en lugar de dar error
                supabase.table("ingredientes_db").upsert(datos, on_conflict="key_name").execute()
                st.session_state.ingredientes_db = cargar_ingredientes()
                st.success(f"¡{n} procesado con éxito!"); st.rerun()

# --- SECCIÓN: AÑADIR/EDITAR PLATOS ---
elif opcion == "Añadir/Editar Platos 🍳":
    st.title("Creador de Recetas")
    modo = st.radio("Acción:", ["Nuevo Plato", "Editar Plato Existente"], horizontal=True)
    
    nombre_p = ""
    if modo == "Editar Plato Existente":
        plato_sel = st.selectbox("Selecciona para editar:", [""] + list(st.session_state.recetario.keys()))
        if plato_sel:
            nombre_p = plato_sel
            # Solo cargamos si la lista temporal está vacía
            if not st.session_state.temp_ing:
                st.session_state.temp_ing = st.session_state.recetario[plato_sel]['ingredientes']
    else:
        nombre_p = st.text_input("Nombre del Plato")

    st.subheader("Ingredientes")
    if st.session_state.ingredientes_db:
        c1, c2 = st.columns([3, 1])
        i_sel = c1.selectbox("Elegir:", list(st.session_state.ingredientes_db.keys()))
        cant = c2.number_input("Cantidad", min_value=0.01)
        if st.button("➕ Añadir"):
            st.session_state.temp_ing[i_sel] = cant
            st.rerun()

    # Visualización de la lista
    if st.session_state.temp_ing:
        st.write("---")
        for ing, c in list(st.session_state.temp_ing.items()):
            col1, col2 = st.columns([4, 1])
            col1.write(f"✅ **{ing}**: {c}")
            if col2.button("❌", key=f"del_{ing}"):
                del st.session_state.temp_ing[ing]
                st.rerun()
        
        if st.button("💾 GUARDAR RECETA EN LA NUBE"):
            if nombre_p:
                supabase.table("recetario").upsert({
                    "nombre_plato": nombre_p, 
                    "ingredientes": st.session_state.temp_ing
                }, on_conflict="nombre_plato").execute()
                st.session_state.recetario = cargar_recetario()
                st.session_state.temp_ing = {}
                st.success("¡Plato guardado!"); st.rerun()
    else:
        st.info("Añade ingredientes para empezar.")

# --- SECCIÓN: RECETARIO (CON ELIMINACIÓN) ---
elif opcion == "Recetario 📖":
    st.title("Tus Platos")
    if st.session_state.recetario:
        p_ver = st.selectbox("Ver:", list(st.session_state.recetario.keys()))
        datos = st.session_state.recetario[p_ver]
        
        costo = 0
        for ing, cant in datos['ingredientes'].items():
            pre_u = st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
            sub = pre_u * cant
            costo += sub
            st.write(f"- {ing}: {cant} (S/ {sub:.2f})")
        
        st.divider()
        st.subheader(f"Costo Total: S/ {costo:.2f}")
        
        c1, c2 = st.columns(2)
        if c1.button("➕ Al Plan"):
            st.session_state.plan.append(p_ver); st.success("Añadido")
        if c2.button("🗑️ Borrar de la Nube"):
            supabase.table("recetario").delete().eq("nombre_plato", p_ver).execute()
            st.session_state.recetario = cargar_recetario()
            st.rerun()

# --- SECCIÓN: MI PLAN ---
elif opcion == "Mi Plan 📝":
    st.title("Menú Semanal")
    if st.session_state.plan:
        for p in st.session_state.plan:
            st.write(f"⭐ {p}")
        if st.button("Limpiar Todo"):
            st.session_state.plan = []; st.rerun()
    else:
        st.write("Tu plan está vacío.")
