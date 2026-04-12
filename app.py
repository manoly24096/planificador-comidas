import streamlit as st
import pandas as pd
from supabase import create_client
import io
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="🥗 Planificador Pro",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Playfair+Display:wght@700&display=swap');

  .stApp {
    background: linear-gradient(135deg, #f0faf4 0%, #ffffff 60%, #e8f5e9 100%);
    font-family: 'Nunito', sans-serif;
  }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 60%, #388e3c 100%) !important;
  }
  section[data-testid="stSidebar"] * {
    color: #ffffff !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1.05rem !important;
  }

  /* Ocultar el texto "keyboard_double_a" que aparece en el ícono */
  [data-testid="stSidebarCollapseButton"] span {
    display: none !important;
  }
  /* Botón colapsar — fondo blanco, flecha verde oscura */
  [data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    position: absolute !important;
    top: 12px !important;
    right: -18px !important;
    z-index: 999 !important;
  }
  [data-testid="stSidebarCollapseButton"] button {
    background: #ffffff !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    border: 2px solid #2e7d32 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.20) !important;
  }
  [data-testid="stSidebarCollapseButton"] svg {
    color: #1b5e20 !important;
    fill: #1b5e20 !important;
    width: 20px !important;
    height: 20px !important;
  }
  section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 10px 16px;
    margin: 4px 0;
    display: block;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
  }
  h1 {
    font-family: 'Playfair Display', serif !important;
    color: #1b5e20 !important;
    font-size: 2.2rem !important;
  }
  h2, h3 {
    font-family: 'Nunito', sans-serif !important;
    color: #2e7d32 !important;
    font-weight: 800 !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 28px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    box-shadow: 0 4px 15px rgba(46,125,50,0.25) !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(46,125,50,0.35) !important;
  }
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input {
    border-radius: 12px !important;
    border: 2px solid #c8e6c9 !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
  }
  .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: #1b5e20 !important;
    font-size: 1rem !important;
  }
  .plato-tag {
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    border: 1.5px solid #a5d6a7;
    border-radius: 50px;
    padding: 8px 18px;
    margin: 5px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    color: #1b5e20;
    font-size: 1rem;
  }
  .porciones {
    background: #2e7d32;
    color: white;
    border-radius: 50px;
    padding: 2px 10px;
    margin-left: 10px;
    font-size: 0.85rem;
    font-weight: 800;
  }
  .ing-item {
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
  }
  /* Ocultar solo el menú de hamburguesa, NO el header completo */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  /* NO ocultar header porque contiene el botón de colapsar */
  .block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN SUPABASE ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- FUNCIONES ---
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
    ["📝 Mi Plan Semanal", "📖 Recetario", "🍳 Crear / Editar Platos", "🍅 Ingredientes"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
n_recetas = len(st.session_state.recetario)
n_ings = len(st.session_state.ingredientes_db)
n_plan = len(st.session_state.plan)
st.sidebar.markdown(f"🍽️ **{n_recetas}** recetas &nbsp; 📝 **{n_plan}** en plan &nbsp; 🥕 **{n_ings}** ingredientes")

# ============================================================
# SECCIÓN: INGREDIENTES
# ============================================================
if opcion == "🍅 Ingredientes":
    st.title("🍅 Base de Ingredientes")
    st.markdown("*Registra aquí todos los ingredientes que usas en tus recetas*")
    st.markdown("---")

    col_form, col_tabla = st.columns([1, 1.6], gap="large")

    with col_form:
        st.markdown("### ➕ Registrar Ingrediente")
        with st.form(key=f"form_ing_{st.session_state.form_key}"):
            n = st.text_input("🏷️ Nombre del ingrediente", placeholder="Ej: Pollo, Arroz, Tomate...")
            cat = st.selectbox("📦 Categoría", ["Carnes y Aves", "Verduras y Hortalizas", "Frutas", "Abarrotes y Granos", "Lácteos y Huevos", "Condimentos y Especias", "Pescados y Mariscos", "Otros"])
            c1, c2 = st.columns(2)
            p = c1.number_input("💰 Precio S/", min_value=0.0, step=0.5, format="%.2f")
            uni_med = c2.selectbox("📏 Unidad", ["kg", "g", "unidad", "atado", "litro", "ml", "taza", "cucharada"])
            cant_inv = st.number_input("📦 Stock actual", min_value=0.0, step=0.5)
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
                    st.success(f"✅ {n} guardado con éxito!")
                    st.rerun()
                else:
                    st.warning("⚠️ Por favor ingresa el nombre del ingrediente.")

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

    if modo == "✨ Crear nuevo plato":
        nombre_p = st.text_input("🍽️ Nombre del plato", placeholder="Ej: Lomo Saltado, Ají de Gallina...")
        if 'ultimo_modo' not in st.session_state or st.session_state.ultimo_modo != modo:
            st.session_state.temp_ing = {}
    else:
        opciones_editar = ["— Selecciona un plato —"] + list(st.session_state.recetario.keys())
        nombre_p = st.selectbox("🍽️ Plato a editar:", opciones_editar)
        if nombre_p and nombre_p != "— Selecciona un plato —":
            if not st.session_state.temp_ing:
                st.session_state.temp_ing = dict(st.session_state.recetario[nombre_p].get('ingredientes', {}))

    st.session_state.ultimo_modo = modo

    st.markdown("---")
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

    st.markdown("---")
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

    # ---- PLATOS DEL PLAN ----
    st.markdown("### 🍽️ Platos en tu Menú")
    for item in st.session_state.plan:
        st.markdown(
            f'<div class="plato-tag">🍽️ {item["plato"]}<span class="porciones">👤 {item["porciones"]}</span></div>',
            unsafe_allow_html=True
        )

    st.markdown("")

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
            st.rerun()

    if st.button("🗑️ Vaciar todo el plan"):
        st.session_state.plan = []
        st.rerun()

    st.markdown("---")

    # ---- LISTA DE COMPRAS ----
    st.markdown("### 🛒 Lista de Compras")

    resumen = {}
    for item in st.session_state.plan:
        receta = st.session_state.recetario.get(item['plato'], {}).get('ingredientes', {})
        for ing, cant in receta.items():
            resumen[ing] = resumen.get(ing, 0) + (cant * item['porciones'])

    total_general = 0
    datos_export = []
    categorias = {}
    for ing in resumen:
        cat = st.session_state.ingredientes_db.get(ing, {}).get('categoria', 'Otros')
        categorias.setdefault(cat, []).append(ing)

    for cat, ings_cat in categorias.items():
        st.markdown(f"**📦 {cat}**")
        for ing in ings_cat:
            total = resumen[ing]
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            precio_u = st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
            costo = total * precio_u
            total_general += costo
            st.markdown(f"""<div class="compra-item">
                <span class="compra-nombre">🛒 {ing}</span>
                <span class="compra-cantidad">{total:.2f} {u}</span>
                <span class="compra-costo">S/ {costo:.2f}</span>
            </div>""", unsafe_allow_html=True)
            datos_export.append({
                "Categoría": cat, "Ingrediente": ing,
                "Cantidad": round(total, 2), "Unidad": u,
                "Costo Estimado (S/)": round(costo, 2)
            })

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#2e7d32,#43a047);color:white;
        border-radius:16px;padding:16px 24px;margin-top:16px;text-align:right;'>
        <span style='font-size:1.1rem;font-weight:700;'>💰 COSTO TOTAL ESTIMADO</span>
        <span style='font-size:1.8rem;font-weight:700;margin-left:16px;'>S/ {total_general:.2f}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📤 Exportar")

    # Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame([{"Plato": i["plato"], "Porciones": i["porciones"]} for i in st.session_state.plan]
                     ).to_excel(writer, index=False, sheet_name='Menú Semanal')
        pd.DataFrame(datos_export).to_excel(writer, index=False, sheet_name='Lista de Compras')
        resumen_data = datos_export + [{"Categoría": "", "Ingrediente": "TOTAL ESTIMADO",
                                        "Cantidad": "", "Unidad": "", "Costo Estimado (S/)": round(total_general, 2)}]
        pd.DataFrame(resumen_data).to_excel(writer, index=False, sheet_name='Resumen con Total')

    # WhatsApp
    texto_ws = "🥗 *MI MENÚ SEMANAL*\n━━━━━━━━━━━━━━━━━━━━\n\n🍽️ *PLATOS:*\n"
    for item in st.session_state.plan:
        texto_ws += f"  ✅ {item['plato']} — {item['porciones']} porciones\n"
    texto_ws += "\n🛒 *LISTA DE COMPRAS:*\n━━━━━━━━━━━━━━━━━━━━\n"
    for cat, ings_cat in categorias.items():
        texto_ws += f"\n📦 _{cat}_\n"
        for ing in ings_cat:
            total = resumen[ing]
            u = st.session_state.ingredientes_db.get(ing, {}).get('unidad_medida', 'u')
            costo = total * st.session_state.ingredientes_db.get(ing, {}).get('precio_base', 0)
            texto_ws += f"  • {ing}: {total:.2f} {u} (S/ {costo:.2f})\n"
    texto_ws += f"\n━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL: S/ {total_general:.2f}*\n_Planificador Pro 🥗_"

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
