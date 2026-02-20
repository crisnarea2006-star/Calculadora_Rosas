import streamlit as st
import pandas as pd
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Novedades Khloe", page_icon="🌹", layout="centered")

# Estilo personalizado (Colores de Novedades Khloe)
st.markdown("""
    <style>
    .main { background-color: #fff5f7; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ffc1cc; }
    .stButton>button { width: 100%; background-color: #ffc1cc; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌹 Novedades Khloe - Calculadora")
st.write("Versión de uso personal (Sin conexión externa)")

# --- BASE DE DATOS INTERNA (Sin Excel) ---
# Aquí definimos tus flores y materiales directamente
if 'inventario' not in st.session_state:
    st.session_state.inventario = {
        "Cinta Roja": 45.72,
        "Cinta Rosada": 91.44,
        "Cinta Azul": 45.72,
        "Silicona": 20.0,
        "Papel Coreano": 20.0
    }

datos_flores = {
    "Rosa Eterna": {"petalos": 15, "largo": 8.5},
    "Rosa Premium": {"petalos": 24, "largo": 10.0},
    "Girasol": {"petalos": 12, "largo": 12.0}
}

# --- MENÚ LATERAL: COSTOS ---
st.sidebar.header("⚙️ Ajustes de Precios")
p_rollo = st.sidebar.number_input("Precio Rollo (50y)", value=2.50)
p_papel = st.sidebar.number_input("Precio Papel (20u)", value=2.00)
p_silic = st.sidebar.number_input("Precio Silicona (8u)", value=1.00)
p_hora = st.sidebar.number_input("Tu Sueldo por Hora", value=3.00)

tab1, tab2 = st.tabs(["💰 CALCULADORA", "📦 MI BODEGA"])

# ==========================================
# PESTAÑA 1: CALCULADORA
# ==========================================
with tab1:
    st.header("Simulador de Ramo")
    col1, col2 = st.columns(2)
    
    with col1:
        flor_sel = st.selectbox("Modelo de Flor:", list(datos_flores.keys()))
        cant_f = st.number_input("¿Cuántas flores?", min_value=1, value=12)
    
    with col2:
        color_cinta = st.selectbox("Color de Cinta:", ["Cinta Roja", "Cinta Rosada", "Cinta Azul"])
        t_minutos = st.number_input("Minutos de trabajo:", min_value=5, value=45)
    
    usar_moño = st.checkbox("¿Lleva Moño Grande? (+1.55m)")

    # LÓGICA MATEMÁTICA
    info = datos_flores[flor_sel]
    # Metros de cinta
    m_necesarios = cant_f * ((info['largo'] / 100) * info['petalos'])
    if usar_moño: m_necesarios += 1.55
    
    # Otros materiales
    b_silic = (cant_f * 0.5) + 2.0
    p_hojas = 1.75 * math.sqrt(cant_f / 8)

    # CÁLCULO DE DINERO
    costo_material = (m_necesarios * (p_rollo/45.72)) + (b_silic * (p_silic/8)) + (p_hojas * (p_papel/20))
    costo_obra = (t_minutos / 60) * p_hora
    precio_sugerido = (costo_material * 3) + costo_obra

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cinta", f"{m_necesarios:.2f} m")
    c2.metric("Silicona", f"{b_silic:.1f} bar")
    c3.metric("Papel", f"{p_hojas:.1f} plie")

    st.subheader(f"Precio Sugerido: ${precio_sugerido:.2f}")
    st.caption(f"Costo de materiales: ${costo_material:.2f} | Mano de obra: ${costo_obra:.2f}")

    if st.button("🚀 DESCONTAR DE MI BODEGA"):
        if st.session_state.inventario[color_cinta] >= m_necesarios:
            st.session_state.inventario[color_cinta] -= m_necesarios
            st.session_state.inventario["Silicona"] -= b_silic
            st.success(f"¡Venta realizada! Se descontó material de la bodega local.")
            st.balloons()
        else:
            st.error("No tienes suficiente cinta en bodega para este pedido.")

# ==========================================
# PESTAÑA 2: MI BODEGA
# ==========================================
with tab2:
    st.header("Estado de mi Inventario")
    for mat, cant in st.session_state.inventario.items():
        # Mostrar barra de progreso visual
        st.write(f"**{mat}**: {cant:.2f}")
        st.progress(min(cant / 100, 1.0))

    st.divider()
    if st.button("♻️ Recargar Inventario (Valores iniciales)"):
        st.session_state.inventario = {
            "Cinta Roja": 45.72,
            "Cinta Rosada": 91.44,
            "Cinta Azul": 45.72,
            "Silicona": 20.0,
            "Papel Coreano": 20.0
        }
        st.rerun()