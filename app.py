import streamlit as st
from supabase import create_client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador Pro", layout="wide")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- 2. FUNCIONES NUBE ---
def cargar_ingredientes():
    try:
        res = supabase.table("ingredientes_db").select("*").execute()
        return {item['display_name']: item for item in res.data}
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
st.sidebar.title("Menú Pro")
opcion = st.sidebar.radio("Ir a:", ["Mi Plan 📝", "Recetario 📖", "Añadir/Editar Platos 🍳", "Base de Ingredientes 🍅"])

# --- SECCIÓN: INGREDIENTES (CON CANTIDAD Y UNIDAD) ---
if opcion == "Base de Ingredientes 🍅":
    st.title("Gestión de Inventario")
    
    with st.form("nuevo_ing"):
        n = st.text_input("Nombre del Ingrediente")
        col1, col2 = st.columns(2)
        cat = col1.selectbox("Categoría", ["Abarrotes", "Carnes", "Verduras", "Frutas", "Otros"])
        p = col2.number_input("Precio S/ (por unidad/kg)", min_value=0.0, step=0.1)
        
        col3, col4 = st.columns(2)
        cant_inv = col3.number_input("Cantidad en Stock", min_value=0.0, step=1.0)
        uni_med = col4.selectbox("Unidad de Medida", ["kg", "g", "unidad", "atado", "litro", "lata"])
        
        if st.form_submit_button("Guardar Permanente"):
            if n:
                datos = {
                    "key_name": n.lower().strip(),
                    "display_name": n,
                    "precio_base": p,
                    "categoria": cat,
                    "cantidad_inventario": cant_inv,
                    "unidad_medida": uni_med
                }
                supabase.table("ingredientes_db").upsert(datos, on_conflict="key_name").execute()
                st.session_state.ingredientes_db = cargar_ingredientes()
                st.success(f"¡{n} actualizado en el inventario!"); st.rerun()

# --- SECCIÓN: AÑADIR/EDITAR PLATOS ---
elif opcion == "Añadir/Editar Platos 🍳":
    st.title("Creador de Recetas")
    modo = st.radio("Acción:", ["Nuevo Plato", "Editar Plato Existente"], horizontal=True)
    
    nombre_p = ""
    if modo == "Editar Plato Existente":
        plato_sel = st.selectbox("Selecciona para editar:", [""] + list(st.session_state.recetario.keys()))
        if plato_sel:
            nombre_p = plato_sel
            if not st.session_state.temp_ing:
                st.session_state.temp_ing = st.session_state.recetario[plato_sel]['ingredientes']
    else:
        nombre_p = st.text_input("Nombre del Plato")

    if st.session_state.ingredientes_db:
        st.subheader("Seleccionar Ingredientes")
        c1, c2, c3 = st.columns([2, 1, 1])
        i_sel = c1.selectbox("Ingrediente:", list(st.session_state.ingredientes_db.keys()))
        
        # Jalamos la unidad guardada para que el usuario sepa qué está sumando
        unidad_actual = st.session_state.ingredientes_db[i_sel].get('unidad_medida', 'u')
        
        cant_receta = c2.number_input(f"Cantidad ({unidad_actual})", min_value=0.01)
        
        if c3.button("➕ Añadir"):
            st.session_state.temp_ing[i_sel] = cant_receta
            st.rerun()

    if st.session_state.temp_ing:
        st.write("---")
        for ing, c in list(st.session_state.temp_ing.items()):
            col_a, col_b = st.columns([4, 1])
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            col_a.write(f"📍 **{ing}**: {c} {u}")
            if col_b.button("❌", key=f"del_{ing}"):
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

# --- SECCIÓN: RECETARIO ---
elif opcion == "Recetario 📖":
    st.title("Tus Recetas")
    if st.session_state.recetario:
        p_ver = st.selectbox("Ver:", list(st.session_state.recetario.keys()))
        datos = st.session_state.recetario[p_ver]
        
        costo = 0
        for ing, cant in datos['ingredientes'].items():
            ing_info = st.session_state.ingredientes_db.get(ing, {})
            pre_u = ing_info.get('precio_base', 0)
            u_m = ing_info.get('unidad_medida', 'u')
            sub = pre_u * cant
            costo += sub
            st.write(f"- {ing}: {cant} {u_m} (S/ {sub:.2f})")
        
        st.divider()
        st.subheader(f"Costo Total: S/ {costo:.2f}")
        
        c1, c2 = st.columns(2)
        if c1.button("➕ Al Plan"):
            st.session_state.plan.append(p_ver); st.success("Añadido")
        if c2.button("🗑️ Borrar Plato"):
            supabase.table("recetario").delete().eq("nombre_plato", p_ver).execute()
            st.session_state.recetario = cargar_recetario()
            st.rerun()

# --- SECCIÓN: MI PLAN ---
elif opcion == "Mi Plan 📝":
    st.title("Menú Semanal")
    if st.session_state.plan:
        for p in st.session_state.plan:
            st.write(f"⭐ {p}")
        if st.button("Vaciar Plan"):
            st.session_state.plan = []; st.rerun()
    else:
        st.write("Tu plan está vacío.")
