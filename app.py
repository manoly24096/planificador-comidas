import streamlit as st
import pandas as pd
from supabase import create_client
import io
import urllib.parse

st.set_page_config(
    page_title="🥗 Planificador Pro",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Playfair+Display:wght@700&display=swap');
  .stApp { background: linear-gradient(135deg,#f0faf4 0%,#ffffff 60%,#e8f5e9 100%); font-family:'Nunito',sans-serif; }
  section[data-testid="stSidebar"] { background:linear-gradient(180deg,#1b5e20 0%,#2e7d32 60%,#388e3c 100%) !important; }
  section[data-testid="stSidebar"] * { color:#ffffff !important; font-family:'Nunito',sans-serif !important; }
  /* Ocultar texto del ícono de colapsar */
  [data-testid="stSidebarCollapseButton"] span { font-size:0 !important; width:0 !important; overflow:hidden !important; }
  [data-testid="stSidebarCollapseButton"] button { background:#ffffff !important; border-radius:50% !important; border:2px solid #ccc !important; box-shadow:0 2px 8px rgba(0,0,0,0.2) !important; }
  [data-testid="stSidebarCollapseButton"] svg { color:#000000 !important; fill:#000000 !important; }
  section[data-testid="stSidebar"] .stRadio label { background:rgba(255,255,255,0.10); border-radius:12px; padding:10px 16px; margin:4px 0; display:block; font-weight:700 !important; }
  h1 { font-family:'Playfair Display',serif !important; color:#1b5e20 !important; font-size:2.2rem !important; }
  h2,h3 { font-family:'Nunito',sans-serif !important; color:#2e7d32 !important; font-weight:800 !important; }
  .stButton > button { background:linear-gradient(135deg,#2e7d32,#43a047) !important; color:white !important; border:none !important; border-radius:14px !important; padding:12px 28px !important; font-family:'Nunito',sans-serif !important; font-weight:800 !important; font-size:1.05rem !important; box-shadow:0 4px 15px rgba(46,125,50,0.25) !important; }
  .stButton > button:hover { transform:translateY(-2px) !important; }
  .stTextInput > div > div > input, .stNumberInput > div > div > input { border-radius:12px !important; border:2px solid #c8e6c9 !important; font-family:'Nunito',sans-serif !important; }
  .stTextInput label,.stNumberInput label,.stSelectbox label,.stRadio label { font-family:'Nunito',sans-serif !important; font-weight:700 !important; color:#1b5e20 !important; }
  .plato-tag { display:inline-flex; align-items:center; background:linear-gradient(135deg,#e8f5e9,#c8e6c9); border:1.5px solid #a5d6a7; border-radius:50px; padding:8px 18px; margin:5px; font-weight:700; color:#1b5e20; }
  .porciones { background:#2e7d32; color:white; border-radius:50px; padding:2px 10px; margin-left:10px; font-size:0.85rem; font-weight:800; }
  .ing-item { background:#f1f8e9; border-radius:12px; padding:10px 16px; margin:6px 0; border-left:4px solid #66bb6a; font-size:1rem; color:#1b5e20; font-weight:600; }
  .prep-box { background:#fffde7; border-radius:14px; padding:16px 20px; margin:10px 0; border-left:4px solid #fbc02d; font-size:0.95rem; color:#3a3a1a; line-height:1.7; }
  .compra-item { display:flex; justify-content:space-between; align-items:center; background:#ffffff; border-radius:14px; padding:12px 20px; margin:7px 0; border:1.5px solid #c8e6c9; box-shadow:0 2px 8px rgba(46,125,50,0.06); }
  .compra-nombre { font-weight:700; color:#1b5e20; }
  .compra-cantidad { color:#388e3c; font-weight:600; }
  .compra-costo { background:#e8f5e9; color:#2e7d32; font-weight:800; border-radius:8px; padding:3px 12px; }
  .cat-badge { display:inline-block; background:#e8f5e9; color:#2e7d32; border-radius:8px; padding:2px 10px; font-size:0.82rem; font-weight:700; margin-left:8px; }
  .btn-ws { display:inline-block; background:linear-gradient(135deg,#25D366,#128C7E); color:white !important; text-decoration:none !important; border-radius:14px; padding:12px 28px; font-family:'Nunito',sans-serif; font-weight:800; font-size:1.05rem; box-shadow:0 4px 15px rgba(37,211,102,0.30); }
  #MainMenu,footer { visibility:hidden; }
  .block-container { padding-top:2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- FUNCIONES ---
def cargar_recetario():
    try:
        res = supabase.table("recetario").select("*").execute()
        return {item['nombre_plato']: item for item in res.data}
    except:
        return {}

# --- ESTADOS ---
if 'recetario' not in st.session_state:
    st.session_state.recetario = cargar_recetario()
if 'temp_ing' not in st.session_state:
    st.session_state.temp_ing = {}
if 'plan' not in st.session_state:
    st.session_state.plan = []
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

# --- SIDEBAR ---
st.sidebar.markdown("## 🥗 Planificador Pro")
st.sidebar.markdown("*Tu menú semanal inteligente*")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Navegación:",
    ["📝 Mi Plan Semanal", "📖 Recetario", "🍳 Crear / Editar Platos"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
n_recetas = len(st.session_state.recetario)
n_plan = len(st.session_state.plan)
st.sidebar.markdown(f"🍽️ **{n_recetas}** recetas &nbsp; 📝 **{n_plan}** en plan")

# ============================================================
# CATEGORÍAS disponibles
# ============================================================
CATEGORIAS = [
    "Sopas y Caldos", "Arroces", "Aves", "Carnes y Res", "Cerdo",
    "Pescados y Mariscos", "Entradas", "Pastas y Fideos",
    "Verduras y Vegetales", "Ensaladas", "Postres y Dulces",
    "Bebidas y Cócteles", "Platos de Fondo"
]

# ============================================================
# SECCIÓN: CREAR / EDITAR PLATOS
# ============================================================
if opcion == "🍳 Crear / Editar Platos":
    st.title("🍳 Crear / Editar Platos")
    st.markdown("*Crea tus propias recetas con todos los detalles*")
    st.markdown("---")

    modo = st.radio("¿Qué deseas hacer?", ["✨ Crear nuevo plato", "✏️ Editar plato existente"], horizontal=True)

    if modo == "✨ Crear nuevo plato":
        nombre_p = st.text_input("🍽️ Nombre del plato", placeholder="Ej: Lomo Saltado, Ají de Gallina...")
        if 'ultimo_modo' not in st.session_state or st.session_state.ultimo_modo != modo:
            st.session_state.temp_ing = {}
    else:
        mis_recetas = ["— Selecciona —"] + list(st.session_state.recetario.keys())
        nombre_p = st.selectbox("🍽️ Plato a editar:", mis_recetas)
        if nombre_p and nombre_p != "— Selecciona —" and not st.session_state.temp_ing:
            st.session_state.temp_ing = dict(st.session_state.recetario[nombre_p].get('ingredientes_texto', ''))
    st.session_state.ultimo_modo = modo

    c1, c2 = st.columns(2)
    categoria_p = c1.selectbox("📦 Categoría", CATEGORIAS)
    porciones_p = c2.number_input("👨‍👩‍👧 Porciones base", min_value=1, max_value=20, value=4, step=1)

    st.markdown("#### 📝 Ingredientes")
    ingredientes_texto = st.text_area(
        "Escribe los ingredientes",
        placeholder="Ej: 1 kg de pollo, 2 cebollas, 3 cucharadas de ají amarillo, sal y pimienta...",
        height=120,
        help="Escribe todos los ingredientes separados por comas o en líneas separadas"
    )

    st.markdown("#### 👩‍🍳 Preparación")
    preparacion_texto = st.text_area(
        "Pasos de preparación",
        placeholder="Ej: Caliente el aceite, fría la cebolla con el ajo...",
        height=180
    )

    st.markdown("---")
    nombre_ok = nombre_p and nombre_p.strip() and nombre_p != "— Selecciona —"
    if nombre_ok and ingredientes_texto.strip():
        if st.button("💾 GUARDAR PLATO", use_container_width=True):
            datos = {
                "nombre_plato": nombre_p.strip(),
                "categoria": categoria_p,
                "porciones_base": porciones_p,
                "ingredientes_texto": ingredientes_texto.strip(),
                "preparacion": preparacion_texto.strip(),
                "ingredientes": {}
            }
            supabase.table("recetario").upsert(datos, on_conflict="nombre_plato").execute()
            st.session_state.recetario = cargar_recetario()
            st.success(f"✅ ¡**{nombre_p}** guardado con éxito!")
            st.rerun()
    else:
        st.info("📝 Completa el nombre y los ingredientes para guardar.")

# ============================================================
# SECCIÓN: RECETARIO
# ============================================================
elif opcion == "📖 Recetario":
    st.title("📖 Recetario")
    st.markdown("*Explora todas las recetas de La Gran Cocina Peruana*")
    st.markdown("---")

    if not st.session_state.recetario:
        st.info("🌱 Tu recetario está vacío.")
        st.stop()

    # Filtrar por categoría
    cats_disponibles = sorted(set(
        v.get('categoria', 'Platos de Fondo')
        for v in st.session_state.recetario.values()
        if v.get('categoria')
    ))
    cats_disponibles = ["Todas las categorías"] + cats_disponibles

    col_filtro, col_buscar = st.columns([1, 2])
    cat_filtro = col_filtro.selectbox("📦 Categoría:", cats_disponibles)
    buscar = col_buscar.text_input("🔍 Buscar plato:", placeholder="Escribe el nombre...")

    # Filtrar recetas
    recetas_filtradas = {
        k: v for k, v in st.session_state.recetario.items()
        if (cat_filtro == "Todas las categorías" or v.get('categoria') == cat_filtro)
        and (not buscar or buscar.upper() in k.upper())
    }

    st.markdown(f"**{len(recetas_filtradas)} recetas encontradas**")
    st.markdown("---")

    if not recetas_filtradas:
        st.warning("No se encontraron recetas con ese filtro.")
        st.stop()

    col_lista, col_detalle = st.columns([1, 1.6], gap="large")

    with col_lista:
        p_ver = st.selectbox(
            "Selecciona un plato:",
            list(recetas_filtradas.keys()),
            label_visibility="collapsed"
        )

    with col_detalle:
        if p_ver:
            receta = recetas_filtradas[p_ver]
            cat = receta.get('categoria', '')
            porciones_base = receta.get('porciones_base', 4)

            st.markdown(f"### 🍽️ {p_ver}")
            if cat:
                st.markdown(f'<span class="cat-badge">📦 {cat}</span>', unsafe_allow_html=True)

            # Ingredientes
            ing_texto = receta.get('ingredientes_texto', '')
            if ing_texto:
                st.markdown("**🥕 Ingredientes:**")
                st.markdown(f'<div class="ing-item">{ing_texto}</div>', unsafe_allow_html=True)

            # Preparación
            prep = receta.get('preparacion', '')
            if prep:
                st.markdown("**👩‍🍳 Preparación:**")
                st.markdown(f'<div class="prep-box">{prep}</div>', unsafe_allow_html=True)

            st.markdown("---")
            porciones_agregar = st.number_input(
                "👨‍👩‍👧 ¿Para cuántas porciones?",
                min_value=1, max_value=30, value=porciones_base, step=1,
                help="Puedes ajustar las porciones antes de agregar al plan"
            )
            if st.button(f"➕ Añadir al Plan ({porciones_agregar} porciones)", use_container_width=True):
                st.session_state.plan.append({
                    "plato": p_ver,
                    "porciones": porciones_agregar,
                    "categoria": cat
                })
                st.success(f"✅ **{p_ver}** añadido al plan.")

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

    # Platos del plan
    st.markdown("### 🍽️ Platos en tu Menú")
    for item in st.session_state.plan:
        cat_label = f" · {item.get('categoria','')}" if item.get('categoria') else ""
        st.markdown(
            f'<div class="plato-tag">🍽️ {item["plato"]}'
            f'<span class="porciones">👤 {item["porciones"]}</span>'
            f'<span style="font-size:0.75rem;opacity:0.7;margin-left:8px;">{cat_label}</span></div>',
            unsafe_allow_html=True
        )

    st.markdown("")

    with st.expander("✏️ Modificar / quitar un plato"):
        nombres_plan = [f"{i['plato']} ({i['porciones']} porc.)" for i in st.session_state.plan]
        sel_mod = st.selectbox("Plato:", nombres_plan)
        idx_mod = nombres_plan.index(sel_mod)
        nueva_porc = st.number_input("Porciones:", min_value=1, max_value=30,
                                      value=st.session_state.plan[idx_mod]['porciones'])
        cm1, cm2 = st.columns(2)
        if cm1.button("💾 Actualizar"):
            st.session_state.plan[idx_mod]['porciones'] = nueva_porc
            st.success("✅ Actualizado"); st.rerun()
        if cm2.button("🗑️ Quitar"):
            st.session_state.plan.pop(idx_mod); st.rerun()

    if st.button("🗑️ Vaciar todo el plan"):
        st.session_state.plan = []; st.rerun()

    st.markdown("---")

    # Lista de compras — basada en ingredientes_texto
    st.markdown("### 🛒 Lista de Compras")
    st.info("💡 La lista muestra los ingredientes de cada plato seleccionado, multiplicados por porciones.")

    datos_export = []
    total_platos = []

    for item in st.session_state.plan:
        plato_nom = item['plato']
        porciones = item['porciones']
        receta = st.session_state.recetario.get(plato_nom, {})
        ing_texto = receta.get('ingredientes_texto', '')
        cat = item.get('categoria', '')

        total_platos.append({"Plato": plato_nom, "Porciones": porciones, "Categoría": cat})

        st.markdown(f"**🍽️ {plato_nom}** · {porciones} porciones")
        if ing_texto:
            st.markdown(f'<div class="ing-item" style="font-size:0.9rem;">'
                        f'<em>Ingredientes (para {porciones} porc.):</em><br>{ing_texto}'
                        f'</div>', unsafe_allow_html=True)
        datos_export.append({
            "Plato": plato_nom,
            "Porciones": porciones,
            "Categoría": cat,
            "Ingredientes": ing_texto
        })
        st.markdown("")

    st.markdown("---")
    st.markdown("### 📤 Exportar")

    # Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(total_platos).to_excel(writer, index=False, sheet_name='Menú Semanal')
        pd.DataFrame(datos_export).to_excel(writer, index=False, sheet_name='Lista de Compras')

        # Hoja preparación
        prep_data = []
        for item in st.session_state.plan:
            rec = st.session_state.recetario.get(item['plato'], {})
            prep_data.append({
                "Plato": item['plato'],
                "Porciones": item['porciones'],
                "Ingredientes": rec.get('ingredientes_texto', ''),
                "Preparación": rec.get('preparacion', '')
            })
        pd.DataFrame(prep_data).to_excel(writer, index=False, sheet_name='Recetas Completas')

    # WhatsApp
    texto_ws = "🥗 *MI MENÚ SEMANAL*\n━━━━━━━━━━━━━━━━━━━━\n\n🍽️ *PLATOS:*\n"
    for item in st.session_state.plan:
        cat = item.get('categoria', '')
        texto_ws += f"  ✅ {item['plato']} — {item['porciones']} porciones\n"
    texto_ws += "\n🛒 *INGREDIENTES POR PLATO:*\n━━━━━━━━━━━━━━━━━━━━\n"
    for item in st.session_state.plan:
        rec = st.session_state.recetario.get(item['plato'], {})
        ing = rec.get('ingredientes_texto', '')
        texto_ws += f"\n🍽️ *{item['plato']}* ({item['porciones']} porc.)\n{ing}\n"
    texto_ws += "\n_Planificador Pro 🥗_"

    url_ws = f"https://wa.me/?text={urllib.parse.quote(texto_ws)}"

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
