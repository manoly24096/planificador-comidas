import streamlit as st
import json
import pandas as pd
import os
import io

# --- 1. CONFIGURACIÓN DE ARCHIVOS Y RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_RECETAS = os.path.join(BASE_DIR, "recetario.json")
ARCHIVO_INGREDIENTES_DB = os.path.join(BASE_DIR, "ingredientes_db.json")

CATEGORIAS = ['Abarrotes', 'Carnes', 'Verduras', 'Frutas', 'Lácteos', 'Limpieza', 'Otros']
UNIDADES = ['kg', 'g', 'l', 'ml', 'unidad', 'atado', 'lata', 'paquete', 'docena']

# --- 2. FUNCIONES DE LÓGICA ---
def cargar_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_datos(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def calcular_lista_compras(platos, recetario):
    lista_total = {} 
    for plato_nombre in platos:
        if plato_nombre not in recetario: continue
        ingredientes_plato = recetario[plato_nombre].get('ingredientes', {})
        for ing_nombre, ing_data in ingredientes_plato.items():
            ing_nombre_lower = ing_nombre.strip().lower()
            unidad_receta = ing_data['unidad_receta']
            cantidad = ing_data['cantidad']
            if ing_nombre_lower not in lista_total:
                lista_total[ing_nombre_lower] = {
                    'display_name': ing_nombre,
                    'unidades': {unidad_receta: cantidad},
                    'price_info': { 
                        'precio': ing_data.get('precio_base', 0), 
                        'unidad_precio': ing_data.get('unidad_precio', 'u'), 
                        'categoria': ing_data.get('categoria', 'Otros') 
                    }
                }
            else:
                unidades_dict = lista_total[ing_nombre_lower]['unidades']
                if unidad_receta in unidades_dict: unidades_dict[unidad_receta] += cantidad
                else: unidades_dict[unidad_receta] = cantidad
    return lista_total

# --- 3. INICIALIZAR ESTADO DE LA SESIÓN ---
if 'recetario' not in st.session_state:
    st.session_state.recetario = cargar_datos(ARCHIVO_RECETAS)
if 'ingredientes_db' not in st.session_state:
    st.session_state.ingredientes_db = cargar_datos(ARCHIVO_INGREDIENTES_DB)
if 'plan' not in st.session_state:
    st.session_state.plan = []
if 'temp_ingredientes' not in st.session_state:
    st.session_state.temp_ingredientes = {}

# --- 4. INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="Planificador de Comidas", layout="wide")
st.sidebar.title("Menú de Navegación")
opcion = st.sidebar.radio("Ir a:", ["Mi Plan 📝", "Recetario 📖", "Añadir/Editar Platos 🍳", "Base de Ingredientes 🍅"])

# --- SECCIÓN: BASE DE INGREDIENTES ---
if opcion == "Base de Ingredientes 🍅":
    st.title("Gestión de la Base de Ingredientes")
    tab1, tab2 = st.tabs(["➕ Añadir Nuevo", "✏️ Editar Existente"])
    
    with tab1:
        with st.form("nuevo_ing_form"):
            nom = st.text_input("Nombre del Ingrediente")
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox("Categoría", CATEGORIAS)
            pre = c2.number_input("Precio Base (S/)", min_value=0.0, step=0.1)
            uni = c3.selectbox("Unidad", UNIDADES)
            submit_nuevo = st.form_submit_button("Guardar Ingrediente")
            if submit_nuevo:
                if nom:
                    st.session_state.ingredientes_db[nom.lower().strip()] = {
                        "display_name": nom, "precio_base": pre, "unidad_precio": uni, "categoria": cat
                    }
                    guardar_datos(ARCHIVO_INGREDIENTES_DB, st.session_state.ingredientes_db)
                    st.success(f"¡{nom} guardado!")
                    st.rerun()

    with tab2:
        if st.session_state.ingredientes_db:
            nombres_db = sorted([i['display_name'] for i in st.session_state.ingredientes_db.values()])
            sel_ing = st.selectbox("Selecciona para editar:", nombres_db)
            key_edit = sel_ing.lower().strip()
            d = st.session_state.ingredientes_db[key_edit]
            
            with st.form("edit_ing_form"):
                nuevo_nom = st.text_input("Nombre", value=d['display_name'])
                c1, c2 = st.columns(2)
                nueva_cat = c1.selectbox("Categoría", CATEGORIAS, index=CATEGORIAS.index(d['categoria']))
                nuevo_pre = c2.number_input("Precio", value=float(d['precio_base']))
                submit_edit = st.form_submit_button("Actualizar")
                if submit_edit:
                    st.session_state.ingredientes_db[key_edit] = {
                        "display_name": nuevo_nom, "precio_base": nuevo_pre, 
                        "unidad_precio": d['unidad_precio'], "categoria": nueva_cat
                    }
                    guardar_datos(ARCHIVO_INGREDIENTES_DB, st.session_state.ingredientes_db)
                    st.success("Actualizado")
                    st.rerun()

# --- SECCIÓN: AÑADIR/EDITAR PLATOS ---
elif opcion == "Añadir/Editar Platos 🍳":
    st.title("Gestión de Recetas")
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        modo = st.radio("Modo:", ["Nuevo Plato", "Editar Plato Existente"])
    
    if modo == "Editar Plato Existente":
        receta_sel = st.selectbox("Selecciona receta:", sorted(st.session_state.recetario.keys()))
        if st.button("Cargar datos de receta"):
            st.session_state.temp_ingredientes = st.session_state.recetario[receta_sel]['ingredientes'].copy()
            st.session_state.nombre_plato_edit = receta_sel
            st.session_state.prep_edit = st.session_state.recetario[receta_sel].get('preparacion', "")
            st.rerun()

    st.divider()
    nombre_p = st.text_input("Nombre del Plato", value=st.session_state.get('nombre_plato_edit', ""))
    
    st.write("### Agregar Ingredientes a la Receta")
    if st.session_state.ingredientes_db:
        nombres_db = sorted([i['display_name'] for i in st.session_state.ingredientes_db.values()])
        c_ing, c_can, c_btn = st.columns([3, 1, 1])
        ing_r = c_ing.selectbox("Ingrediente", nombres_db)
        can_r = c_can.number_input("Cant.", min_value=0.1, step=0.1)
        if c_btn.button("Añadir"):
            info = next(i for i in st.session_state.ingredientes_db.values() if i['display_name'] == ing_r)
            st.session_state.temp_ingredientes[ing_r] = {
                "cantidad": can_r, "unidad_receta": info['unidad_precio'],
                "precio_base": info['precio_base'], "unidad_precio": info['unidad_precio'], "categoria": info['categoria']
            }
    
    if st.session_state.temp_ingredientes:
        df_temp = pd.DataFrame.from_dict(st.session_state.temp_ingredientes, orient='index')
        st.table(df_temp[['cantidad', 'unidad_receta']])
        if st.button("Limpiar ingredientes de la lista"):
            st.session_state.temp_ingredientes = {}
            st.rerun()

    prep_p = st.text_area("Preparación", value=st.session_state.get('prep_edit', ""))
    
    if st.button("💾 GUARDAR RECETA FINAL"):
        if nombre_p and st.session_state.temp_ingredientes:
            st.session_state.recetario[nombre_p] = {"ingredientes": st.session_state.temp_ingredientes, "preparacion": prep_p}
            guardar_datos(ARCHIVO_RECETAS, st.session_state.recetario)
            st.session_state.temp_ingredientes = {}
            st.session_state.nombre_plato_edit = ""
            st.session_state.prep_edit = ""
            st.success("¡Receta Guardada!")
            st.rerun()

# --- SECCIÓN: RECETARIO ---
elif opcion == "Recetario 📖":
    st.title("Recetario")
    nombres = sorted(list(st.session_state.recetario.keys()))
    if nombres:
        plato = st.selectbox("Selecciona un plato:", nombres)
        datos = st.session_state.recetario[plato]
        st.write(f"**Ingredientes:**")
        df_ver = pd.DataFrame.from_dict(datos['ingredientes'], orient='index')
        st.table(df_ver[['cantidad', 'unidad_receta']])
        st.write(f"**Preparación:** {datos.get('preparacion', 'Sin datos')}")
        if st.button("Añadir al Plan"):
            st.session_state.plan.append(plato)
            st.success("Añadido")
    else:
        st.info("No hay recetas guardadas.")

# --- SECCIÓN: MI PLAN ---
elif opcion == "Mi Plan 📝":
    st.title("Mi Plan de Comidas")
    if not st.session_state.plan:
        st.info("Plan vacío.")
    else:
        for i, p in enumerate(st.session_state.plan):
            c1, c2 = st.columns([4, 1])
            c1.write(f"- {p}")
            if c2.button("Quitar", key=f"del_{i}"):
                st.session_state.plan.pop(i)
                st.rerun()
        
        if st.button("Generar Lista de Compras 🛒"):
            lista = calcular_lista_compras(st.session_state.plan, st.session_state.recetario)
            resumen = []
            for d in lista.values():
                resumen.append({
                    "Producto": d['display_name'],
                    "Cantidad Total": sum(d['unidades'].values()),
                    "Unidad": list(d['unidades'].keys())[0],
                    "Categoría": d['price_info']['categoria']
                })
            df_resumen = pd.DataFrame(resumen)
            st.dataframe(df_resumen)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_resumen.to_excel(writer, index=False)
            st.download_button("Descargar Excel 📥", data=output.getvalue(), file_name="lista_compras.xlsx")