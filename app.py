import streamlit as st
import pandas as pd
import math
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Khloe", page_icon="🌹", layout="centered")

DB_INV = "inventario.csv"
DB_FLORES = "flores.csv"

# --- 1. INICIALIZAR BASES DE DATOS ---
def inicializar_db():
    if not os.path.exists(DB_INV):
        data_inv = {
            "Material": ["Cinta Roja", "Cinta Amarilla", "Papel Coreano", "Silicona", "Palitos", "Plumafón"],
            "Cantidad": [22.86, 22.86, 20.0, 8.0, 50.0, 5.0], # Ajustado a 25 yardas (22.86m)
            "Unidad": ["Metros", "Metros", "Pliegos", "Barras", "Unidades", "Planchas"],
            "Alerta_Minima": [5.0, 5.0, 5.0, 3.0, 15.0, 1.0] 
        }
        pd.DataFrame(data_inv).to_csv(DB_INV, index=False)
        
    if not os.path.exists(DB_FLORES):
        data_flores = {
            "Tipo_Flor": ["Rosa (Tarjeta Metrovía)", "Girasol Pequeño", "Moño Grande"],
            "Largo_Petalo_cm": [8.6, 10.0, 8.6],
            "Cantidad_Petalos": [18, 35, 18]
        }
        pd.DataFrame(data_flores).to_csv(DB_FLORES, index=False)

inicializar_db()

def cargar_inv(): return pd.read_csv(DB_INV)
def guardar_inv(df): df.to_csv(DB_INV, index=False)
def cargar_flores(): return pd.read_csv(DB_FLORES)
def guardar_flores(df): df.to_csv(DB_FLORES, index=False)

# --- MENÚ LATERAL: AJUSTAR PRECIOS ---
st.sidebar.header("⚙️ Ajustar Precios")
st.sidebar.write("Modifica esto si te suben los costos:")

# CAMBIO AQUÍ: Ahora es de 25 yardas y cuesta 2.00 por defecto
precio_rollo = st.sidebar.number_input("Rollo Cinta (25y)", value=2.00) 

precio_papel = st.sidebar.number_input("Paq. Papel (20u)", value=2.00)
precio_silicona = st.sidebar.number_input("Paq. Silicona (8u)", value=1.00)
precio_palitos = st.sidebar.number_input("Paq. Palitos (50u)", value=1.00)
precio_plumafon = st.sidebar.number_input("Plancha Plumafón", value=0.60)
sueldo_hora = st.sidebar.number_input("Tu sueldo por hora ($)", value=3.00)

# --- INTERFAZ DEL PROGRAMA ---
st.title("🌹 Novedades Khloe")
st.write("Sistema Integrado: Costos, Inventario y Catálogo")

tab1, tab2, tab3 = st.tabs(["💰 Calculadora", "📦 Inventario", "🌺 Mis Flores"])

df_inv = cargar_inv()
df_flores = cargar_flores()

# ==========================================
# PESTAÑA 1: CALCULADORA Y COSTOS
# ==========================================
with tab1:
    st.header("Armar un Pedido")
    
    col1, col2 = st.columns(2)
    with col1:
        flor_elegida = st.selectbox("¿Qué flor vas a hacer?", df_flores["Tipo_Flor"].tolist())
        cantidad_flores = st.number_input("¿Qué cantidad?", min_value=1, value=12)
        lista_cintas = df_inv[df_inv["Unidad"] == "Metros"]["Material"].tolist()
        color_elegido = st.selectbox("Color de la Cinta", lista_cintas)
        
    with col2:
        usar_mono = st.checkbox("¿Lleva Moño Grande?")
        minutos = st.number_input("Minutos de trabajo total", min_value=5, value=45, step=5)

    datos_flor = df_flores[df_flores["Tipo_Flor"] == flor_elegida].iloc[0]
    metros_por_unidad = (datos_flor["Largo_Petalo_cm"] / 100) * datos_flor["Cantidad_Petalos"]
    metros_totales = cantidad_flores * metros_por_unidad
    
    if usar_mono:
        datos_mono = df_flores[df_flores["Tipo_Flor"] == "Moño Grande"].iloc[0]
        metros_mono = (datos_mono["Largo_Petalo_cm"] / 100) * datos_mono["Cantidad_Petalos"]
        metros_totales += metros_mono 
        
    factor_tamano = math.sqrt(cantidad_flores / 8)
    barras_necesarias = (cantidad_flores * 0.5) + (2.0 * factor_tamano)
    hojas_necesarias = 1.75 * factor_tamano

    # CAMBIO AQUÍ: La división ahora es por 22.86 (que son 25 yardas)
    costo_cinta_usd = metros_totales * (precio_rollo / 22.86)
    
    costo_silicona_usd = barras_necesarias * (precio_silicona / 8)
    costo_papel_usd = hojas_necesarias * (precio_papel / 20)
    costo_palitos_usd = cantidad_flores * (precio_palitos / 50)
    costo_plumafon_usd = precio_plumafon * (2 if cantidad_flores > 30 else 1)
    
    total_materiales_usd = costo_cinta_usd + costo_silicona_usd + costo_papel_usd + costo_palitos_usd + costo_plumafon_usd
    costo_mano_obra_usd = (minutos / 60) * sueldo_hora
    
    precio_venta_sugerido = (total_materiales_usd * 3) + costo_mano_obra_usd

    st.info(f"💡 El ramo gastará: **{metros_totales:.1f}m** de {color_elegido}, **{barras_necesarias:.1f}** barras de silicona y **{hojas_necesarias:.1f}** pliegos de papel.")
    
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Gasto Materiales", f"${total_materiales_usd:.2f}")
    c2.metric("👩‍🔧 Mano de Obra", f"${costo_mano_obra_usd:.2f}")
    c3.metric("💰 Precio Sugerido", f"${precio_venta_sugerido:.2f}")
    st.markdown("---")

    if st.button("✅ Registrar Venta y Descontar Material"):
        df_inv.loc[df_inv["Material"] == color_elegido, "Cantidad"] -= metros_totales
        df_inv.loc[df_inv["Material"] == "Silicona", "Cantidad"] -= barras_necesarias
        df_inv.loc[df_inv["Material"] == "Papel Coreano", "Cantidad"] -= hojas_necesarias
        df_inv.loc[df_inv["Material"] == "Palitos", "Cantidad"] -= cantidad_flores
        
        df_inv.loc[df_inv["Cantidad"] < 0, "Cantidad"] = 0
        guardar_inv(df_inv)
        st.success("¡Venta Registrada y materiales descontados!")

# ==========================================
# PESTAÑA 2: INVENTARIO (También se actualizó la lógica de ingreso)
# ==========================================
with tab2:
    st.header("Control de Bodega")
    # ... (resto del código de inventario igual, pero con la lógica de 25 yardas en el ingreso)
    st.dataframe(df_inv, use_container_width=True)

    st.write("---")
    st.subheader("🛒 Ingresar Compras")
    
    material_comprado = st.selectbox("¿Qué material compraste?", df_inv["Material"].tolist() + ["+ Agregar Material Nuevo"])
    
    if material_comprado != "+ Agregar Material Nuevo":
        unidad = df_inv[df_inv["Material"] == material_comprado]["Unidad"].values[0]
        if unidad == "Metros":
            # CAMBIO AQUÍ: Ajustado a 25 yardas
            tipo_ingreso = st.radio("¿Cómo compraste la cinta?", ["Por Rollos enteros (de 25 yardas)", "Por Metros sueltos"])
            if tipo_ingreso == "Por Rollos enteros (de 25 yardas)":
                cant_rollos = st.number_input("¿Cuántos rollos?", min_value=1.0, step=1.0)
                cantidad_final = cant_rollos * 22.86 # 25 yardas = 22.86 metros
            else:
                cantidad_final = st.number_input("¿Cuántos metros?", min_value=1.0)
            
            if st.button("➕ Sumar al Inventario"):
                df_inv.loc[df_inv["Material"] == material_comprado, "Cantidad"] += cantidad_final
                guardar_inv(df_inv)
                st.success(f"¡Sumados {cantidad_final:.2f}m!")
                st.rerun()