import streamlit as st
import pandas as pd
from supabase import create_client
import io
import urllib.parse

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
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

# --- SECCIÓN: INGREDIENTES ---
if opcion == "Base de Ingredientes 🍅":
    st.title("Gestión de Inventario")
    with st.form("nuevo_ing"):
        n = st.text_input("Nombre del Ingrediente")
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Categoría", ["Abarrotes", "Carnes", "Verduras", "Frutas", "Otros"])
        p = c2.number_input("Precio S/ (por unidad/kg)", min_value=0.0)
        c3, c4 = st.columns(2)
        cant_inv = c3.number_input("Stock Actual", min_value=0.0)
        uni_med = c4.selectbox("Unidad", ["kg", "g", "unidad", "atado", "litro"])
        if st.form_submit_button("Guardar"):
            datos = {"key_name": n.lower().strip(), "display_name": n, "precio_base": p, "categoria": cat, "cantidad_inventario": cant_inv, "unidad_medida": uni_med}
            supabase.table("ingredientes_db").upsert(datos, on_conflict="key_name").execute()
            st.session_state.ingredientes_db = cargar_ingredientes()
            st.success(f"¡{n} guardado!"); st.rerun()

# --- SECCIÓN: AÑADIR/EDITAR PLATOS ---
elif opcion == "Añadir/Editar Platos 🍳":
    st.title("Creador de Recetas")
    modo = st.radio("Acción:", ["Nuevo", "Editar"], horizontal=True)
    nombre_p = st.selectbox("Selecciona:", [""] + list(st.session_state.recetario.keys())) if modo == "Editar" else st.text_input("Nombre")
    
    if modo == "Editar" and nombre_p and not st.session_state.temp_ing:
        st.session_state.temp_ing = st.session_state.recetario[nombre_p]['ingredientes']

    if st.session_state.ingredientes_db:
        c1, c2, c3 = st.columns([2,1,1])
        i_sel = c1.selectbox("Ingrediente:", list(st.session_state.ingredientes_db.keys()))
        u_m = st.session_state.ingredientes_db[i_sel].get('unidad_medida', 'u')
        cant = c2.number_input(f"Cant ({u_m})", min_value=0.01)
        if c3.button("➕"):
            st.session_state.temp_ing[i_sel] = cant
            st.rerun()

    for ing, c in list(st.session_state.temp_ing.items()):
        col_a, col_b = st.columns([4, 1])
        col_a.write(f"📍 {ing}: {c}")
        if col_b.button("❌", key=f"d_{ing}"):
            del st.session_state.temp_ing[ing]; st.rerun()
            
    if st.button("💾 GUARDAR PLATO"):
        supabase.table("recetario").upsert({"nombre_plato": nombre_p, "ingredientes": st.session_state.temp_ing}, on_conflict="nombre_plato").execute()
        st.session_state.recetario = cargar_recetario(); st.session_state.temp_ing = {}; st.success("¡Listo!"); st.rerun()

# --- SECCIÓN: RECETARIO ---
elif opcion == "Recetario 📖":
    st.title("Tus Recetas")
    if st.session_state.recetario:
        p_ver = st.selectbox("Ver:", list(st.session_state.recetario.keys()))
        receta = st.session_state.recetario[p_ver]
        for ing, cant in receta['ingredientes'].items():
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            st.write(f"- {ing}: {cant} {u}")
        if st.button("➕ Al Plan"):
            st.session_state.plan.append(p_ver); st.success("Añadido")

# --- SECCIÓN: MI PLAN (RESUMEN + EXPORTAR) ---
elif opcion == "Mi Plan 📝":
    st.title("Menú Semanal")
    if st.session_state.plan:
        for p in st.session_state.plan:
            st.write(f"⭐ {p}")
        
        if st.button("Vaciar Plan"):
            st.session_state.plan = []; st.rerun()
            
        st.divider()
        st.subheader("🛒 Lista de Compras Acumulada")
        
        # Lógica para sumar ingredientes
        resumen = {}
        for plato_nom in st.session_state.plan:
            receta = st.session_state.recetario.get(plato_nom, {}).get('ingredientes', {})
            for ing, cant in receta.items():
                resumen[ing] = resumen.get(ing, 0) + cant
        
        # Mostrar resumen y preparar datos para Excel
        datos_excel = []
        texto_whatsapp = "Mi Lista de Compras:\n"
        
        for ing, total in resumen.items():
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            precio_u = st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
            costo = total * precio_u
            st.write(f"• **{ing}**: {total} {u} (Est. S/ {costo:.2f})")
            
            datos_excel.append({"Ingrediente": ing, "Cantidad": total, "Unidad": u, "Costo Est.": costo})
            texto_whatsapp += f"- {ing}: {total} {u}\n"

        st.divider()
        c1, c2 = st.columns(2)
        
        # 1. BOTÓN EXCEL
        df = pd.DataFrame(datos_excel)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Compras')
        c1.download_button(label="📥 Descargar Excel", data=output.getvalue(), file_name="lista_compras.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # 2. BOTÓN WHATSAPP
        texto_encoded = urllib.parse.quote(texto_whatsapp)
        url_ws = f"https://wa.me/?text={texto_encoded}"
        c2.markdown(f'''<a href="{url_ws}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">📲 Enviar a WhatsApp</button></a>''', unsafe_allow_html=True)
    else:
        st.info("Plan vacío.")
