import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

# --- CONFIGURACIÓN PROFESIONAL ---
st.set_page_config(page_title="Novedades Khloe", page_icon="🌹", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fff5f7; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ffc1cc; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🌹 Novedades Khloe - Control Total")
st.write("Conectado a Google Sheets: **Base_Datos_Khloe**")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_todo():
    inv = conn.read(worksheet="Inventario")
    flores = conn.read(worksheet="Flores")
    return inv, flores

try:
    df_inv, df_flores = cargar_todo()
except Exception as e:
    st.error("⚠️ Error de conexión. Revisa que el Excel esté compartido y los Secrets configurados.")
    st.stop()

# --- PANEL LATERAL DE PRECIOS ---
with st.sidebar:
    st.header("⚙️ Configuración de Costos")
    p_rollo = st.number_input("Precio Rollo Cinta (50y)", value=2.50)
    p_papel = st.number_input("Precio Paquete Papel (20u)", value=2.00)
    p_silic = st.number_input("Precio Paquete Silicona (8u)", value=1.00)
    p_hora = st.number_input("Tu Sueldo por Hora ($)", value=3.00)
    st.info("Estos precios se usan para calcular el sugerido de venta.")

tab1, tab2, tab3 = st.tabs(["💰 CALCULADORA", "📦 BODEGA", "🌺 MODELOS"])

# ==========================================
# PESTAÑA 1: CALCULADORA DE VENTAS
# ==========================================
with tab1:
    st.subheader("Simulador de Pedido")
    c1, c2, c3 = st.columns([2,1,1])
    
    with c1:
        f_tipo = st.selectbox("Modelo de Flor:", df_flores["Tipo_Flor"].tolist())
        f_color = st.selectbox("Color de Cinta (Stock):", df_inv[df_inv["Unidad"] == "Metros"]["Material"].tolist())
    with c2:
        f_cant = st.number_input("¿Cuántas flores?", min_value=1, value=12)
    with c3:
        f_tiempo = st.number_input("Minutos de armado:", min_value=5, value=45)
    
    l_moño = st.checkbox("¿Incluye Moño Grande?")

    # LÓGICA DE CÁLCULO
    datos_f = df_flores[df_flores["Tipo_Flor"] == f_tipo].iloc[0]
    m_cinta = f_cant * ((datos_f["Largo_Petalo_cm"] / 100) * datos_f["Cantidad_Petalos"])
    if l_moño: m_cinta += 1.55
    
    b_silic = (f_cant * 0.5) + 2.0
    p_hojas = 1.75 * math.sqrt(f_cant / 8)

    # COSTOS REALES
    costo_mat = (m_cinta * (p_rollo/45.72)) + (b_silic * (p_silic/8)) + (p_hojas * (p_papel/20))
    costo_mano = (f_tiempo / 60) * p_hora
    # FÓRMULA MAESTRA: (Material x 3) + Mano de Obra
    sugerido = (costo_mat * 3) + costo_mano

    st.markdown("---")
    st.subheader("Resultados del Cálculo")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Cinta (m)", f"{m_cinta:.2f}")
    res2.metric("Silicona (barras)", f"{b_silic:.1f}")
    res3.metric("Papel (pliegos)", f"{p_hojas:.1f}")
    res4.metric("PRECIO SUGERIDO", f"${sugerido:.2f}", delta=f"Costo: ${costo_mat:.2f}")

    if st.button("🚀 REGISTRAR VENTA Y DESCONTAR STOCK"):
        # Actualizamos el DataFrame localmente
        df_inv.loc[df_inv["Material"] == f_color, "Cantidad"] -= m_cinta
        df_inv.loc[df_inv["Material"] == "Silicona", "Cantidad"] -= b_silic
        # Subimos a la nube
        conn.update(worksheet="Inventario", data=df_inv)
        st.success(f"Venta registrada. Se descontaron {m_cinta:.2f}m de {f_color}.")
        st.balloons()

# ==========================================
# PESTAÑA 2: GESTIÓN DE BODEGA
# ==========================================
with tab2:
    st.subheader("Inventario en Tiempo Real")
    st.dataframe(df_inv, use_container_width=True)
    
    # Aquí puedes sumar compras nuevas
    with st.expander("➕ Cargar nueva mercadería"):
        mat_add = st.selectbox("¿Qué compraste?", df_inv["Material"].tolist())
        cant_add = st.number_input("Cantidad:", min_value=0.1)
        if st.button("Actualizar Inventario"):
            df_inv.loc[df_inv["Material"] == mat_add, "Cantidad"] += cant_add
            conn.update(worksheet="Inventario", data=df_inv)
            st.rerun()

# ==========================================
# PESTAÑA 3: CATÁLOGO DE FLORES
# ==========================================
with tab3:
    st.subheader("Configuración de Modelos")
    st.write("Modifica aquí cuántos pétalos usa cada flor de Novedades Khloe.")
    st.table(df_flores)