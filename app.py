import streamlit as st
from supabase import create_client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador Pro", layout="wide")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- 2. FUNCIONES NUBE (Nombres corregidos) ---
def cargar_ingredientes():
    try:
        res = supabase.table("ingredientes_db").select("*").execute()
        # Intentamos con 'key_name' que es el estándar de Supabase
        return {item.get('display_name', item.get('key_name')): item for item in res.data}
    except: return {}

def cargar_recetario():
    try:
        res = supabase.table("recetario").select("*").execute()
        return {item['nombre_plato']: item for item in res.data}
    except: return {}

# --- 3. ESTADOS ---
if 'ingredientes_db' not in st.session_state:
    st.session_state.ingredientes_db = cargar_ingredientes()
if 'recetario' not in st.session_state:
    st.session_state.recetario = cargar_recetario()
if 'temp_ing' not in st.session_state:
    st.session_state.temp_ing = {}
if 'plan' not in st.session_state:
    st.session_state.plan = []

# --- 4. NAVEGACIÓN ---
st.sidebar.title(f"Menú Pro")
opcion = st.sidebar.radio("Ir a:", ["Mi Plan 📝", "Recetario 📖", "Añadir/Editar Platos 🍳", "Base de Ingredientes 🍅"])


# --- SECCIÓN: BASE DE INGREDIENTES (Nombres corregidos) ---
if opcion == "Base de Ingredientes 🍅":
    st.title("Ingredientes Disponibles")
    with st.form("nuevo_ing"):
        n = st.text_input("Nombre")
        cat = st.selectbox("Categoría", ["Abarrotes", "Carnes", "Verduras", "Frutas", "Otros"])
        p = st.number_input("Precio S/", min_value=0.0)
        if st.form_submit_button("Guardar"):
            if n:
                # Cambiamos los nombres a inglés para que coincidan con la tabla
                datos_ing = {
                    "key_name": n.lower().strip(), 
                    "display_name": n, 
                    "precio_base": p, 
                    "categoria": cat
                }
                try:
                    supabase.table("ingredientes_db").upsert(datos_ing).execute()
                    st.session_state.ingredientes_db = cargar_ingredientes()
                    st.success(f"¡{n} guardado!"); st.rerun()
                except Exception as e:
                    # Si falla, te mostrará qué columnas SÍ existen
                    st.error(f"Error: {e}")

# --- SECCIÓN: AÑADIR/EDITAR PLATOS ---
elif opcion == "Añadir/Editar Platos 🍳":
    st.title("Gestión de Recetas")
    modo = st.radio("Modo:", ["Nuevo Plato", "Editar Plato Existente"], horizontal=True)
    
    nombre_p = ""
    if modo == "Editar Plato Existente":
        plato_sel = st.selectbox("Selecciona plato a editar:", [""] + list(st.session_state.recetario.keys()))
        if plato_sel:
            nombre_p = plato_sel
            if not st.session_state.temp_ing:
                st.session_state.temp_ing = st.session_state.recetario[plato_sel]['ingredientes']
    else:
        nombre_p = st.text_input("Nombre del Plato")

    st.subheader("Agregar Ingredientes")
    if st.session_state.ingredientes_db:
        c1, c2 = st.columns([3, 1])
        i_sel = c1.selectbox("Ingrediente:", list(st.session_state.ingredientes_db.keys()))
        cant = c2.number_input("Cantidad", min_value=0.01)
        if st.button("➕ Añadir"):
            st.session_state.temp_ing[i_sel] = cant
            st.rerun()

    st.markdown("### Lista actual de la receta:")
    for ing, c in list(st.session_state.temp_ing.items()):
        col_a, col_b = st.columns([4, 1])
        col_a.write(f"📍 **{ing}**: {c}")
        if col_b.button("❌", key=f"del_{ing}"):
            del st.session_state.temp_ing[ing]
            st.rerun()

    if st.button("💾 GUARDAR TODO EN LA NUBE"):
        if nombre_p and st.session_state.temp_ing:
            supabase.table("recetario").upsert({"nombre_plato": nombre_p, "ingredientes": st.session_state.temp_ing}).execute()
            st.session_state.recetario = cargar_recetario()
            st.session_state.temp_ing = {}
            st.success("¡Plato guardado!"); st.rerun()

# --- SECCIÓN: RECETARIO ---
elif opcion == "Recetario 📖":
    st.title("Tus Recetas")
    if st.session_state.recetario:
        p_ver = st.selectbox("Ver plato:", list(st.session_state.recetario.keys()))
        receta = st.session_state.recetario[p_ver]
        
        st.markdown("### Ingredientes requeridos:")
        costo_total = 0
        for ing, cant in receta['ingredientes'].items():
            precio = st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
            subtotal = precio * cant
            costo_total += subtotal
            st.write(f"- {ing}: {cant} (S/ {subtotal:.2f})")
        
        st.info(f"**Costo estimado del plato: S/ {costo_total:.2f}**")
        
        c1, c2 = st.columns(2)
        if c1.button("➕ Añadir a Mi Plan"):
            st.session_state.plan.append(p_ver); st.success("Añadido")
        if c2.button("🗑️ Eliminar Plato de la Nube"):
            supabase.table("recetario").delete().eq("nombre_plato", p_ver).execute()
            st.session_state.recetario = cargar_recetario()
            st.rerun()

# --- SECCIÓN: MI PLAN ---
elif opcion == "Mi Plan 📝":
    st.title("Planificación de la Semana")
    if st.session_state.plan:
        for p in st.session_state.plan:
            st.write(f"🍴 {p}")
        if st.button("Vaciar Plan"):
            st.session_state.plan = []; st.rerun()
    else:
        st.info("Plan vacío.")
