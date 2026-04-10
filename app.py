import streamlit as st
import pandas as pd
from supabase import create_client
import io

# --- 1. CONEXIÓN SEGURA A SUPABASE ---
# Streamlit leerá esto de los "Secrets" que configuraste
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

CATEGORIAS = ['Abarrotes', 'Carnes', 'Verduras', 'Frutas', 'Lácteos', 'Otros']

# --- 2. FUNCIONES PARA LEER DE LA NUBE ---
def cargar_ingredientes_nube():
    try:
        res = supabase.table("ingredientes_db").select("*").execute()
        db = {}
        for item in res.data:
            db[item['key_name']] = {
                "display_name": item['display_name'],
                "precio_base": item['precio_base'],
                "unidad_precio": item['unidad_precio'],
                "categoria": item['categoria']
            }
        return db
    except:
        return {}

def cargar_recetario_nube():
    try:
        res = supabase.table("recetario").select("*").execute()
        recetas = {}
        for item in res.data:
            recetas[item['nombre_plato']] = {
                "ingredientes": item['ingredientes'],
                "preparacion": item['preparacion']
            }
        return recetas
    except:
        return {}

# --- 3. INICIALIZAR ESTADOS ---
if 'ingredientes_db' not in st.session_state:
    st.session_state.ingredientes_db = cargar_ingredientes_nube()
if 'recetario' not in st.session_state:
    st.session_state.recetario = cargar_recetario_nube()
if 'plan' not in st.session_state:
    st.session_state.plan = []
if 'temp_ingredientes' not in st.session_state:
    st.session_state.temp_ingredientes = {}

# --- 4. INTERFAZ ---
st.set_page_config(page_title="Menú Pro", layout="wide")
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["Mi Plan 📝", "Recetario 📖", "Gestionar Platos 🍳", "Base de Ingredientes 🍅"])

# --- SECCIÓN: INGREDIENTES ---
if opcion == "Base de Ingredientes 🍅":
    st.title("Ingredientes en la Nube ☁️")
    with st.form("nuevo_ing"):
        nom = st.text_input("Nombre del Ingrediente")
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Categoría", CATEGORIAS)
        pre = c2.number_input("Precio S/", min_value=0.0)
        if st.form_submit_button("Guardar Permanente"):
            if nom:
                clave = nom.lower().strip()
                data = {
                    "key_name": clave,
                    "display_name": nom,
                    "precio_base": pre,
                    "unidad_precio": "unidad",
                    "categoria": cat
                }
                supabase.table("ingredientes_db").upsert(data).execute()
                st.session_state.ingredientes_db = cargar_ingredientes_nube() 
                st.success(f"¡{nom} guardado en la nube!")

# --- SECCIÓN: GESTIONAR PLATOS ---
elif opcion == "Gestionar Platos 🍳":
    st.title("Creador de Recetas")
    nombre_p = st.text_input("Nombre del Nuevo Plato")
    
    if st.session_state.ingredientes_db:
        nombres_ing = [i['display_name'] for i in st.session_state.ingredientes_db.values()]
        sel_ing = st.selectbox("Seleccionar ingrediente:", nombres_ing)
        cant = st.number_input("Cantidad", min_value=0.1)
        if st.button("Añadir a receta"):
            st.session_state.temp_ingredientes[sel_ing] = {"cantidad": cant, "unidad": "u"}
            st.rerun()
    
    st.write("Ingredientes actuales en la receta:", st.session_state.temp_ingredientes)
    
    if st.button("💾 GUARDAR PLATO PARA SIEMPRE"):
        if nombre_p and st.session_state.temp_ingredientes:
            data = {
                "nombre_plato": nombre_p,
                "ingredientes": st.session_state.temp_ingredientes,
                "preparacion": "Receta creada desde la web"
            }
            supabase.table("recetario").upsert(data).execute()
            st.session_state.recetario = cargar_recetario_nube()
            st.session_state.temp_ingredientes = {}
            st.success("¡Arroz con Pollo guardado permanentemente!")

# --- SECCIÓN: RECETARIO ---
elif opcion == "Recetario 📖":
    st.title("Tus Recetas Guardadas")
    if st.session_state.recetario:
        plato = st.selectbox("Elegir plato:", list(st.session_state.recetario.keys()))
        if st.button("Agregar al Plan"):
            st.session_state.plan.append(plato)
            st.success("Añadido al plan")
    else:
        st.info("No hay recetas guardadas en Supabase.")

# --- SECCIÓN: MI PLAN ---
elif opcion == "Mi Plan 📝":
    st.title("Plan Semanal")
    if not st.session_state.plan:
        st.info("El plan está vacío.")
    else:
        for p in st.session_state.plan:
            st.write(f"✅ {p}")
