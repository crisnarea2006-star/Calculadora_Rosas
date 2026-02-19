import streamlit as st
import pandas as pd
import math
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Khloe", page_icon="🌹", layout="centered")

DB_INV = "inventario.csv"
DB_FLORES = "flores.csv"  # Nueva base de datos para tus medidas

# --- 1. INICIALIZAR BASES DE DATOS ---
def inicializar_db():
    # Inventario
    if not os.path.exists(DB_INV):
        data_inv = {
            "Material": ["Cinta Roja", "Cinta Amarilla", "Papel Coreano", "Silicona", "Palitos", "Plumafón"],
            "Cantidad": [45.0, 45.0, 20.0, 8.0, 50.0, 5.0], 
            "Unidad": ["Metros", "Metros", "Pliegos", "Barras", "Unidades", "Planchas"],
            "Alerta_Minima": [10.0, 10.0, 5.0, 3.0, 15.0, 1.0] 
        }
        pd.DataFrame(data_inv).to_csv(DB_INV, index=False)
        
    # Catálogo de Flores (Las recetas)
    if not os.path.exists(DB_FLORES):
        data_flores = {
            "Tipo_Flor": ["Rosa (Tarjeta Metrovía)", "Girasol Pequeño", "Moño Grande"],
            "Largo_Petalo_cm": [8.6, 10.0, 8.6],
            "Cantidad_Petalos": [18, 35, 18] # Cuántos pétalos o tiras usas para hacer UNA unidad
        }
        pd.DataFrame(data_flores).to_csv(DB_FLORES, index=False)

inicializar_db()

# Cargar y guardar datos
def cargar_inv(): return pd.read_csv(DB_INV)
def guardar_inv(df): df.to_csv(DB_INV, index=False)
def cargar_flores(): return pd.read_csv(DB_FLORES)
def guardar_flores(df): df.to_csv(DB_FLORES, index=False)

# --- INTERFAZ DEL PROGRAMA ---
st.title("🌹 Novedades Khloe")
st.write("Sistema Integrado: Costos, Inventario y Catálogo")

tab1, tab2, tab3 = st.tabs(["💰 Calculadora", "📦 Inventario", "🌺 Mis Flores"])

df_inv = cargar_inv()
df_flores = cargar_flores()

# ==========================================
# PESTAÑA 1: CALCULADORA INTELIGENTE
# ==========================================
with tab1:
    st.header("Armar un Pedido")
    
    col1, col2 = st.columns(2)
    with col1:
        # Elegir la flor desde tu base de datos
        flor_elegida = st.selectbox("¿Qué flor vas a hacer?", df_flores["Tipo_Flor"].tolist())
        cantidad_flores = st.number_input("¿Qué cantidad?", min_value=1, value=12)
        
        lista_cintas = df_inv[df_inv["Unidad"] == "Metros"]["Material"].tolist()
        color_elegido = st.selectbox("Color de la Cinta", lista_cintas)
        
    with col2:
        usar_mono = st.checkbox("¿Lleva Moño Grande?")
        minutos = st.number_input("Minutos de trabajo total", min_value=5, value=45, step=5)

    # Buscar la "receta" de la flor elegida
    datos_flor = df_flores[df_flores["Tipo_Flor"] == flor_elegida].iloc[0]
    largo_cm = datos_flor["Largo_Petalo_cm"]
    petalos_por_flor = datos_flor["Cantidad_Petalos"]
    
    # Cálculos Matemáticos
    # (Largo en cm / 100 para hacer metros) * cantidad de pétalos * cantidad de flores
    metros_por_unidad = (largo_cm / 100) * petalos_por_flor
    metros_totales = cantidad_flores * metros_por_unidad
    
    if usar_mono:
        # Busca cuánto gasta el moño en la base de datos
        datos_mono = df_flores[df_flores["Tipo_Flor"] == "Moño Grande"].iloc[0]
        metros_mono = (datos_mono["Largo_Petalo_cm"] / 100) * datos_mono["Cantidad_Petalos"]
        metros_totales += metros_mono 
        
    factor_tamano = math.sqrt(cantidad_flores / 8)
    barras_necesarias = (cantidad_flores * 0.5) + (2.0 * factor_tamano)
    hojas_necesarias = 1.75 * factor_tamano
    
    st.info(f"💡 El ramo gastará: **{metros_totales:.1f}m** de {color_elegido}, **{barras_necesarias:.1f}** barras de silicona y **{hojas_necesarias:.1f}** pliegos de papel.")

    if st.button("✅ Registrar Venta y Descontar Material"):
        df_inv.loc[df_inv["Material"] == color_elegido, "Cantidad"] -= metros_totales
        df_inv.loc[df_inv["Material"] == "Silicona", "Cantidad"] -= barras_necesarias
        df_inv.loc[df_inv["Material"] == "Papel Coreano", "Cantidad"] -= hojas_necesarias
        df_inv.loc[df_inv["Material"] == "Palitos", "Cantidad"] -= cantidad_flores
        
        guardar_inv(df_inv)
        st.success("¡Materiales descontados del inventario!")

# ==========================================
# PESTAÑA 2: INVENTARIO
# ==========================================
with tab2:
    st.header("Control de Bodega")
    
    alertas = 0
    for index, fila in df_inv.iterrows():
        if fila["Cantidad"] <= fila["Alerta_Minima"]:
            st.error(f"⚠️ URGENTE: Queda poco de **{fila['Material']}** ({fila['Cantidad']:.1f} {fila['Unidad']})")
            alertas += 1
            
    st.dataframe(df_inv, use_container_width=True)

    st.subheader("🛒 Ingresar Compras / Nuevos Materiales")
    with st.form("form_compras"):
        c1, c2, c3 = st.columns(3)
        with c1: material_comprado = st.selectbox("Material", df_inv["Material"].tolist() + ["+ Agregar Nuevo"])
        with c2: cantidad_comprada = st.number_input("Cantidad", min_value=1.0)
        with c3: nuevo_nombre = st.text_input("Si es nuevo, escribe el nombre:")
        
        if st.form_submit_button("➕ Agregar"):
            if material_comprado == "+ Agregar Nuevo" and nuevo_nombre:
                # Agrega un material totalmente nuevo (ej: Cinta Negra)
                nueva_fila = pd.DataFrame({"Material": [nuevo_nombre], "Cantidad": [cantidad_comprada], "Unidad": ["Metros"], "Alerta_Minima": [10.0]})
                df_inv = pd.concat([df_inv, nueva_fila], ignore_index=True)
            else:
                df_inv.loc[df_inv["Material"] == material_comprado, "Cantidad"] += cantidad_comprada
            
            guardar_inv(df_inv)
            st.success("Inventario actualizado")
            st.rerun()

# ==========================================
# PESTAÑA 3: CATÁLOGO DE FLORES (NUEVO)
# ==========================================
with tab3:
    st.header("🌺 Mis Diseños de Flores")
    st.write("Aquí guardas las medidas exactas de cómo TÚ haces cada flor.")
    
    st.dataframe(df_flores, use_container_width=True)
    
    st.subheader("✨ Agregar Nuevo Modelo (Ej: Girasol Gigante)")
    with st.form("form_flores"):
        f1, f2, f3 = st.columns(3)
        with f1: nueva_flor = st.text_input("Nombre de la Flor")
        with f2: medida_petalo = st.number_input("Largo de 1 pétalo (cm)", min_value=1.0, value=10.0)
        with f3: cant_petalos = st.number_input("¿Cuántos pétalos lleva?", min_value=1, value=30)
        
        if st.form_submit_button("💾 Guardar Modelo"):
            if nueva_flor:
                nueva_fila_flor = pd.DataFrame({
                    "Tipo_Flor": [nueva_flor], 
                    "Largo_Petalo_cm": [medida_petalo], 
                    "Cantidad_Petalos": [cant_petalos]
                })
                df_flores = pd.concat([df_flores, nueva_fila_flor], ignore_index=True)
                guardar_flores(df_flores)
                st.success(f"¡{nueva_flor} guardado en tu catálogo!")
                st.rerun()