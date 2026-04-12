import streamlit as st
import pandas as pd
from supabase import create_client
import io
import urllib.parse

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="🥗 Planificador Pro",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS MODERNO — Verde, Blanco, Limpio
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Playfair+Display:wght@700&display=swap');

  /* Fondo general */
  .stApp {
    background: linear-gradient(135deg, #f0faf4 0%, #ffffff 60%, #e8f5e9 100%);
    font-family: 'Nunito', sans-serif;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 60%, #388e3c 100%) !important;
    border-right: none;
  }
  section[data-testid="stSidebar"] * {
    color: #ffffff !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1.05rem !important;
  }
  section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 10px 16px;
    margin: 4px 0;
    display: block;
    transition: background 0.2s;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
  }
  section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.22);
  }

  /* Título del sidebar */
  .sidebar-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    padding: 18px 0 8px 0;
    letter-spacing: 0.5px;
  }
  .sidebar-subtitle {
    text-align: center;
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.85rem !important;
    margin-bottom: 18px;
  }

  /* Títulos principales */
  h1 {
    font-family: 'Playfair Display', serif !important;
    color: #1b5e20 !important;
    font-size: 2.2rem !important;
    margin-bottom: 4px !important;
  }
  h2, h3 {
    font-family: 'Nunito', sans-serif !important;
    color: #2e7d32 !important;
    font-weight: 800 !important;
  }

  /* Tarjetas / bloques */
  .card {
    background: #ffffff;
    border-radius: 18px;
    padding: 24px 28px;
    box-shadow: 0 4px 24px rgba(46,125,50,0.08);
    border: 1.5px solid #e8f5e9;
    margin-bottom: 18px;
  }

  /* Botones principales */
  .stButton > button {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 28px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.3px;
    box-shadow: 0 4px 15px rgba(46,125,50,0.25) !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(46,125,50,0.35) !important;
  }

  /* Inputs */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div {
    border-radius: 12px !important;
    border: 2px solid #c8e6c9 !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    background: #fafffe !important;
    transition: border 0.2s;
  }
  .stTextInput > div > div > input:focus,
  .stNumberInput > div > div > input:focus {
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 3px rgba(46,125,50,0.12) !important;
  }

  /* Labels de inputs */
  .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: #1b5e20 !important;
    font-size: 1rem !important;
  }

  /* Tags de platos en el plan */
  .plato-tag {
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    border: 1.5px solid #a5d6a7;
    border-radius: 50px;
    padding: 8px 18px;
    margin: 5px 5px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    color: #1b5e20;
    font-size: 1rem;
  }
  .plato-tag .porciones {
    background: #2e7d32;
    color: white;
    border-radius: 50px;
    padding: 2px 10px;
    margin-left: 10px;
    font-size: 0.85rem;
    font-weight: 800;
  }

  /* Ingrediente item */
  .ing-item {
    display: flex;
    align-items: center;
    background: #f1f8e9;
    border-radius: 12px;
    padding: 10px 16px;
    margin: 6px 0;
    border-left: 4px solid #66bb6a;
    font-family: 'Nunito', sans-serif;
    font-size: 1rem;
    color: #1b5e20;
    font-weight: 600;
  }

  /* Compras item */
  .compra-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ffffff;
    border-radius: 14px;
    padding: 12px 20px;
    margin: 7px 0;
    border: 1.5px solid #c8e6c9;
    box-shadow: 0 2px 8px rgba(46,125,50,0.06);
    font-family: 'Nunito', sans-serif;
    font-size: 1.05rem;
  }
  .compra-nombre { font-weight: 700; color: #1b5e20; }
  .compra-cantidad { color: #388e3c; font-weight: 600; }
  .compra-costo {
    background: #e8f5e9;
    color: #2e7d32;
    font-weight: 800;
    border-radius: 8px;
    padding: 3px 12px;
  }

  /* Divider */
  hr { border-color: #c8e6c9 !important; margin: 20px 0 !important; }

  /* Success / info */
  .stSuccess { border-radius: 12px !important; }
  .stInfo { border-radius: 12px !important; }

  /* Dataframe */
  .stDataFrame { border-radius: 14px; overflow: hidden; }

  /* Número grande decorativo */
  .numero-grande {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    color: #c8e6c9;
    font-weight: 700;
    line-height: 1;
  }

  /* Badge categoría */
  .badge {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-left: 8px;
  }

  /* Botón WhatsApp personalizado */
  .btn-ws {
    display: inline-block;
    background: linear-gradient(135deg, #25D366, #128C7E);
    color: white !important;
    text-decoration: none !important;
    border-radius: 14px;
    padding: 12px 28px;
    font-family: 'Nunito', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    box-shadow: 0 4px 15px rgba(37,211,102,0.30);
    transition: all 0.2s;
  }
  .btn-ws:hover { transform: translateY(-2px); }

  /* Ocultar elementos de Streamlit */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN SUPABASE ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- FUNCIONES NUBE ---
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

# --- ESTADOS ---
if 'ingredientes_db' not in st.session_state:
    st.session_state.ingredientes_db = cargar_ingredientes()
if 'recetario' not in st.session_state:
    st.session_state.recetario = cargar_recetario()
if 'temp_ing' not in st.session_state:
    st.session_state.temp_ing = {}
# plan ahora es lista de dicts: {"plato": nombre, "porciones": N}
if 'plan' not in st.session_state:
    st.session_state.plan = []
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

# --- SIDEBAR ---
st.sidebar.markdown('<div class="sidebar-title">🥗 Planificador Pro</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subtitle">Tu menú semanal inteligente</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Navegación:",
    ["📝 Mi Plan Semanal", "📖 Recetario", "🍳 Crear / Editar Platos", "🍅 Ingredientes"],
    label_visibility="collapsed"
)

# Estadísticas rápidas en sidebar
st.sidebar.markdown("---")
n_recetas = len(st.session_state.recetario)
n_ings = len(st.session_state.ingredientes_db)
n_plan = len(st.session_state.plan)
st.sidebar.markdown(f"""
<div style='text-align:center; color:rgba(255,255,255,0.85); font-family:Nunito,sans-serif;'>
  <div style='font-size:0.82rem; margin-bottom:10px; font-weight:600;'>RESUMEN RÁPIDO</div>
  <div style='display:flex; justify-content:space-around;'>
    <div><div style='font-size:1.6rem; font-weight:900;'>{n_recetas}</div><div style='font-size:0.75rem;'>Recetas</div></div>
    <div><div style='font-size:1.6rem; font-weight:900;'>{n_plan}</div><div style='font-size:0.75rem;'>En plan</div></div>
    <div><div style='font-size:1.6rem; font-weight:900;'>{n_ings}</div><div style='font-size:0.75rem;'>Ingredientes</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SECCIÓN: BASE DE INGREDIENTES
# ============================================================
if opcion == "🍅 Ingredientes":
    st.title("🍅 Base de Ingredientes")
    st.markdown("*Registra aquí todos los ingredientes que usas en tus recetas*")
    st.markdown("---")

    col_form, col_tabla = st.columns([1, 1.6], gap="large")

    with col_form:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ Registrar Ingrediente")

        with st.form(key=f"form_ing_{st.session_state.form_key}"):
            n = st.text_input("🏷️ Nombre del ingrediente", placeholder="Ej: Pollo, Arroz, Tomate...")
            cat = st.selectbox("📦 Categoría", ["Carnes y Aves", "Verduras y Hortalizas", "Frutas", "Abarrotes y Granos", "Lácteos y Huevos", "Condimentos y Especias", "Otros"])

            c1, c2 = st.columns(2)
            p = c1.number_input("💰 Precio S/", min_value=0.0, step=0.5, format="%.2f")
            uni_med = c2.selectbox("📏 Unidad", ["kg", "g", "unidad", "atado", "litro", "ml", "taza", "cucharada"])

            cant_inv = st.number_input("📦 Stock actual", min_value=0.0, step=0.5, help="¿Cuánto tienes en casa ahora?")

            enviar = st.form_submit_button("💾 Guardar Ingrediente", use_container_width=True)

            if enviar:
                if n.strip():
                    datos = {
                        "key_name": n.lower().strip(),
                        "display_name": n.strip(),
                        "precio_base": p,
                        "categoria": cat,
                        "cantidad_inventario": cant_inv,
                        "unidad_medida": uni_med
                    }
                    supabase.table("ingredientes_db").upsert(datos, on_conflict="key_name").execute()
                    st.session_state.ingredientes_db = cargar_ingredientes()
                    st.session_state.form_key += 1
                    st.success(f"✅ ¡**{n}** guardado con éxito!")
                    st.rerun()
                else:
                    st.warning("⚠️ Por favor ingresa el nombre del ingrediente.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_tabla:
        st.markdown("### 📋 Ingredientes Registrados")
        if st.session_state.ingredientes_db:
            df_ing = pd.DataFrame(st.session_state.ingredientes_db.values())
            df_show = df_ing[["display_name", "categoria", "precio_base", "unidad_medida", "cantidad_inventario"]].copy()
            df_show.columns = ["🏷️ Nombre", "📦 Categoría", "💰 Precio S/", "📏 Unidad", "📦 Stock"]
            st.dataframe(df_show, hide_index=True, use_container_width=True, height=420)
        else:
            st.info("🌱 Aún no tienes ingredientes. ¡Agrega el primero!")

# ============================================================
# SECCIÓN: CREAR / EDITAR PLATOS
# ============================================================
elif opcion == "🍳 Crear / Editar Platos":
    st.title("🍳 Crear / Editar Platos")
    st.markdown("*Arma tus recetas indicando qué ingredientes lleva cada plato*")
    st.markdown("---")

    if not st.session_state.ingredientes_db:
        st.warning("⚠️ Primero debes registrar ingredientes en la sección **🍅 Ingredientes**")
        st.stop()

    modo = st.radio("¿Qué deseas hacer?", ["✨ Crear nuevo plato", "✏️ Editar plato existente"], horizontal=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if modo == "✨ Crear nuevo plato":
        nombre_p = st.text_input("🍽️ Nombre del plato", placeholder="Ej: Lomo Saltado, Ají de Gallina...")
        if modo == "✨ Crear nuevo plato" and 'ultimo_modo' not in st.session_state:
            st.session_state.temp_ing = {}
        st.session_state.ultimo_modo = modo
    else:
        opciones_editar = ["— Selecciona un plato —"] + list(st.session_state.recetario.keys())
        nombre_p = st.selectbox("🍽️ Plato a editar:", opciones_editar)
        if nombre_p and nombre_p != "— Selecciona un plato —":
            if not st.session_state.temp_ing:
                st.session_state.temp_ing = dict(st.session_state.recetario[nombre_p].get('ingredientes', {}))

    st.markdown("#### 🥕 Agregar Ingredientes")
    c1, c2, c3 = st.columns([2.5, 1.2, 0.8])
    i_sel = c1.selectbox("Ingrediente:", list(st.session_state.ingredientes_db.keys()), label_visibility="collapsed")
    u_m = st.session_state.ingredientes_db[i_sel].get('unidad_medida', 'u')
    cant = c2.number_input(f"Cantidad ({u_m})", min_value=0.01, step=0.1, label_visibility="collapsed")
    if c3.button("➕ Añadir"):
        st.session_state.temp_ing[i_sel] = cant
        st.rerun()

    if st.session_state.temp_ing:
        st.markdown("#### 📋 Ingredientes del plato:")
        for ing, c in list(st.session_state.temp_ing.items()):
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            col_a, col_b = st.columns([5, 1])
            col_a.markdown(f'<div class="ing-item">🥄 <strong>{ing}</strong> — {c} {u}</div>', unsafe_allow_html=True)
            if col_b.button("🗑️", key=f"del_{ing}"):
                del st.session_state.temp_ing[ing]
                st.rerun()
    else:
        st.info("📭 Aún no has añadido ingredientes a este plato.")

    nombre_valido = nombre_p and nombre_p.strip() and nombre_p != "— Selecciona un plato —"
    if nombre_valido and st.session_state.temp_ing:
        if st.button("💾 GUARDAR PLATO", use_container_width=True):
            supabase.table("recetario").upsert(
                {"nombre_plato": nombre_p, "ingredientes": st.session_state.temp_ing},
                on_conflict="nombre_plato"
            ).execute()
            st.session_state.recetario = cargar_recetario()
            st.session_state.temp_ing = {}
            st.success(f"✅ ¡**{nombre_p}** guardado con éxito!")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SECCIÓN: RECETARIO
# ============================================================
elif opcion == "📖 Recetario":
    st.title("📖 Recetario")
    st.markdown("*Todos tus platos en un solo lugar*")
    st.markdown("---")

    if not st.session_state.recetario:
        st.info("🌱 Tu recetario está vacío. Ve a **🍳 Crear / Editar Platos** para agregar tus primeras recetas.")
        st.stop()

    col_lista, col_detalle = st.columns([1, 1.5], gap="large")

    with col_lista:
        st.markdown("### 🍽️ Mis Platos")
        p_ver = st.selectbox("Selecciona un plato:", list(st.session_state.recetario.keys()), label_visibility="collapsed")

    with col_detalle:
        if p_ver:
            st.markdown(f"### 🍽️ {p_ver}")
            receta = st.session_state.recetario[p_ver]
            ingredientes = receta.get('ingredientes', {})

            if ingredientes:
                st.markdown("**Ingredientes:**")
                for ing, cant in ingredientes.items():
                    u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
                    precio_u = st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
                    costo = cant * precio_u
                    st.markdown(f'<div class="ing-item">🥄 <strong>{ing}</strong>: {cant} {u} <span class="badge">S/ {costo:.2f}</span></div>', unsafe_allow_html=True)
            else:
                st.info("Este plato no tiene ingredientes registrados.")

            st.markdown("---")
            porciones_agregar = st.number_input(
                "👨‍👩‍👧 ¿Para cuántas porciones?",
                min_value=1, max_value=20, value=4, step=1,
                help="El número de porciones multiplica las cantidades de ingredientes"
            )

            if st.button(f"➕ Añadir al Plan ({porciones_agregar} porciones)", use_container_width=True):
                st.session_state.plan.append({"plato": p_ver, "porciones": porciones_agregar})
                st.success(f"✅ **{p_ver}** añadido al plan para {porciones_agregar} personas.")

# ============================================================
# SECCIÓN: MI PLAN SEMANAL
# ============================================================
elif opcion == "📝 Mi Plan Semanal":
    st.title("📝 Mi Plan Semanal")
    st.markdown("*Tu menú de la semana con la lista de compras automática*")
    st.markdown("---")

    if not st.session_state.plan:
        st.info("🗓️ Tu plan está vacío. Ve al **📖 Recetario** y agrega platos a tu menú.")
        st.stop()

    # ---- BLOQUE 1: PLATOS DEL PLAN ----
    st.markdown("### 🍽️ Platos en tu Menú")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    cols_platos = st.columns(3)
    for i, item in enumerate(st.session_state.plan):
        with cols_platos[i % 3]:
            st.markdown(f"""
            <div class="plato-tag">
                🍽️ {item['plato']}
                <span class="porciones">👤 {item['porciones']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Modificar porciones
    with st.expander("✏️ Modificar porciones de un plato"):
        nombres_plan = [f"{i['plato']} ({i['porciones']} porc.)" for i in st.session_state.plan]
        sel_mod = st.selectbox("Plato a modificar:", nombres_plan)
        idx_mod = nombres_plan.index(sel_mod)
        nueva_porc = st.number_input("Nuevas porciones:", min_value=1, max_value=20, value=st.session_state.plan[idx_mod]['porciones'])
        c_mod1, c_mod2 = st.columns(2)
        if c_mod1.button("💾 Actualizar porciones"):
            st.session_state.plan[idx_mod]['porciones'] = nueva_porc
            st.success("✅ Porciones actualizadas")
            st.rerun()
        if c_mod2.button("🗑️ Quitar este plato"):
            st.session_state.plan.pop(idx_mod)
            st.success("Plato eliminado del plan")
            st.rerun()

    if st.button("🗑️ Vaciar todo el plan"):
        st.session_state.plan = []
        st.rerun()

    st.markdown("---")

    # ---- BLOQUE 2: LISTA DE COMPRAS ----
    st.markdown("### 🛒 Lista de Compras")

    resumen = {}
    for item in st.session_state.plan:
        plato_nom = item['plato']
        porciones = item['porciones']
        receta = st.session_state.recetario.get(plato_nom, {}).get('ingredientes', {})
        for ing, cant in receta.items():
            resumen[ing] = resumen.get(ing, 0) + (cant * porciones)

    total_general = 0
    datos_export = []

    # Agrupar por categoría
    categorias = {}
    for ing, total in resumen.items():
        cat = st.session_state.ingredientes_db.get(ing, {}).get('categoria', 'Otros')
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(ing)

    for cat, ings_cat in categorias.items():
        st.markdown(f"**📦 {cat}**")
        for ing in ings_cat:
            total = resumen[ing]
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            precio_u = st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
            costo = total * precio_u
            total_general += costo
            st.markdown(f"""
            <div class="compra-item">
                <span class="compra-nombre">🛒 {ing}</span>
                <span class="compra-cantidad">{total:.2f} {u}</span>
                <span class="compra-costo">S/ {costo:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            datos_export.append({
                "Categoría": cat,
                "Ingrediente": ing,
                "Cantidad": round(total, 2),
                "Unidad": u,
                "Costo Estimado (S/)": round(costo, 2)
            })

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#2e7d32,#43a047); color:white; border-radius:16px; padding:16px 24px; margin-top:16px; text-align:right;'>
        <span style='font-family:Nunito,sans-serif; font-size:1.1rem; font-weight:700;'>💰 COSTO TOTAL ESTIMADO</span>
        <span style='font-family:Playfair Display,serif; font-size:1.8rem; font-weight:700; margin-left:16px;'>S/ {total_general:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📤 Exportar")

    # ---- PREPARAR EXCEL ----
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Platos del menú
        datos_platos = []
        for item in st.session_state.plan:
            datos_platos.append({"Plato": item['plato'], "Porciones": item['porciones']})
        df_platos = pd.DataFrame(datos_platos)
        df_platos.to_excel(writer, index=False, sheet_name='Menú Semanal')

        # Hoja 2: Lista de compras
        df_compras = pd.DataFrame(datos_export)
        df_compras.to_excel(writer, index=False, sheet_name='Lista de Compras')

        # Hoja 3: Resumen con total
        resumen_data = datos_export + [{"Categoría": "", "Ingrediente": "TOTAL ESTIMADO", "Cantidad": "", "Unidad": "", "Costo Estimado (S/)": round(total_general, 2)}]
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, index=False, sheet_name='Resumen con Total')

    # ---- PREPARAR WHATSAPP ----
    texto_ws = "🥗 *MI MENÚ SEMANAL*\n"
    texto_ws += "━━━━━━━━━━━━━━━━━━━━\n\n"
    texto_ws += "🍽️ *PLATOS DEL MENÚ:*\n"
    for item in st.session_state.plan:
        texto_ws += f"  ✅ {item['plato']} — {item['porciones']} porciones\n"
    texto_ws += f"\n🛒 *LISTA DE COMPRAS:*\n"
    texto_ws += "━━━━━━━━━━━━━━━━━━━━\n"
    for cat, ings_cat in categorias.items():
        texto_ws += f"\n📦 _{cat}_\n"
        for ing in ings_cat:
            total = resumen[ing]
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            costo = total * st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
            texto_ws += f"  • {ing}: {total:.2f} {u} (S/ {costo:.2f})\n"
    texto_ws += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    texto_ws += f"💰 *TOTAL ESTIMADO: S/ {total_general:.2f}*\n"
    texto_ws += "\n_Enviado desde Planificador Pro 🥗_"

    texto_encoded = urllib.parse.quote(texto_ws)
    url_ws = f"https://wa.me/?text={texto_encoded}"

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📥 Descargar Excel (3 hojas)",
            data=output.getvalue(),
            file_name="mi_menu_semanal.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with c2:
        st.markdown(
            f'<a href="{url_ws}" target="_blank" class="btn-ws">📲 Enviar por WhatsApp</a>',
            unsafe_allow_html=True
        )
