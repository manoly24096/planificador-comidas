import streamlit as st
from supabase import create_client

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="Planificador Pro", layout="wide")

# Conectamos con las llaves de los Secrets
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- 2. FUNCIONES DE CARGA (NUBE) ---
def cargar_ingredientes():
    try:
        res = supabase.table("ingredientes_db").select("*").execute()
        return {item['display_name']: item for item in res.data}
    except:
        return {}

def cargar_recetario():
    try:
        res = supabase.table("recetario").select("*").execute()
        return {item['nombre_plato']: item for item in res.data}
    except:
        return {}

# --- 3. INICIALIZAR ESTADOS DE SESIÓN ---
if 'ingredientes_db' not in st.session_state:
    st.session_state.ingredientes_db = cargar_ingredientes()
if 'recetario' not in st.session_state:
    st.session_state.recetario = cargar_recetario()
if 'temp_ingredientes' not in st.session_state:
    st.session_state.temp_ingredientes = {}
if 'plan' not in st.session_state:
    st.session_state.plan = []

# --- 4. BARRA LATERAL (NAVEGACIÓN) ---
st.sidebar.title("Menú de Navegación")
opcion = st.sidebar.radio("Ir a:", [
    "Mi Plan 📝", 
    "Recetario 📖", 
    "Gestionar Platos 🍳", 
    "Base de Ingredientes 🍅"
])

# --- SECCIÓN: BASE DE INGREDIENTES ---
if opcion == "Base de Ingredientes 🍅":
    st.title("Gestión de Ingredientes (Nube)")
    with st.form("form_ingrediente"):
        nombre = st.text_input("Nombre del ingrediente (ej. Pollo)")
        categoria = st.selectbox("Categoría", ["Abarrotes", "Carnes", "Verduras", "Lácteos", "Otros"])
        precio = st.number_input("Precio base (S/)", min_value=0.0, step=0.10)
        if st.form_submit_button("💾 Guardar en Supabase"):
            if nombre:
                data = {
                    "key_name": nombre.lower().strip(),
                    "display_name": nombre,
                    "precio_base": precio,
                    "unidad_precio": "unidad/kg",
                    "categoria": categoria
                }
                supabase.table("ingredientes_db").upsert(data).execute()
                st.session_state.ingredientes_db = cargar_ingredientes()
                st.success(f"¡{nombre} guardado correctamente!")
            else:
                st.error("El nombre es obligatorio")

# --- SECCIÓN: GESTIONAR PLATOS ---
elif opcion == "Gestionar Platos 🍳":
    st.title("Creador de Recetas Permanente")
    nombre_plato = st.text_input("Nombre del nuevo plato")
    if st.session_state.ingredientes_db:
        st.subheader("Añadir Ingredientes")
        c1, c2 = st.columns([3, 1])
        lista_nombres = list(st.session_state.ingredientes_db.keys())
        ing_sel = c1.selectbox("Elegir ingrediente:", lista_nombres)
        cantidad = c2.number_input("Cantidad", min_value=0.01, value=1.0)
        if st.button("➕ Añadir a la lista"):
            st.session_state.temp_ingredientes[ing_sel] = cantidad
            st.rerun()
    st.markdown("---")
    st.subheader("Ingredientes seleccionados:")
    if st.session_state.temp_ingredientes:
        for ing, cant in st.session_state.temp_ingredientes.items():
            st.write(f"✅ {ing}: {cant}")
        if st.button("🗑️ Limpiar lista"):
            st.session_state.temp_ingredientes = {}
            st.rerun()
    else:
        st.info("Aún no has añadido ingredientes.")
    if st.button("🔥 GUARDAR TODO EL PLATO EN LA NUBE"):
        if nombre_plato and st.session_state.temp_ingredientes:
            data_plato = {
                "nombre_plato": nombre_plato,
                "ingredientes": st.session_state.temp_ingredientes,
                "preparacion": "Generada desde la app"
            }
            supabase.table("recetario").upsert(data_plato).execute()
            st.session_state.recetario = cargar_recetario()
            st.session_state.temp_ingredientes = {}
            st.success(f"¡{nombre_plato} guardado!")
            st.rerun()

# --- SECCIÓN: RECETARIO ---
elif opcion == "Recetario 📖":
    st.title("Tus Platos Guardados")
    if st.session_state.recetario:
        seleccion = st.selectbox("Selecciona un plato:", list(st.session_state.recetario.keys()))
        info = st.session_state.recetario[seleccion]
        st.write("**Ingredientes:**")
        st.json(info['ingredientes'])
        if st.button("➕ Añadir a Mi Plan"):
            st.session_state.plan.append(seleccion)
            st.success(f"{seleccion} añadido.")
    else:
        st.warning("No hay platos en la nube.")

# --- SECCIÓN: MI PLAN ---
elif opcion == "Mi Plan 📝":
    st.title("Planificación Semanal")
    if st.session_state.plan:
        for plato in st.session_state.plan:
            st.write(f"🍴 **{plato}**")
        if st.button("🗑️ Vaciar Plan"):
            st.session_state.plan = []
            st.rerun()
    else:
        st.info("Tu plan está vacío.")
