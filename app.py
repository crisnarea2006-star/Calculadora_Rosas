import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

# --- CONFIGURACIÓN PROFESIONAL ---
st.set_page_config(page_title="Novedades Khloe", page_icon="🌹", layout="wide")

# CORRECCIÓN DE ERROR TÉCNICO: Se usa 'unsafe_allow_html', no 'stdio'
st.markdown("""
    <style>
    .main { background-color: #fff5f7; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ffc1cc; }
    .stButton>button { width: 100%; background-color: #ffc1cc; color: black; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌹 Novedades Khloe - Sistema de Gestión")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_todo():
    # Asegúrate de que tus pestañas se llamen exactamente así en el Excel
    inv = conn.read(worksheet="Inventario")
    flores = conn.read(worksheet="Flores")
    return inv, flores

try:
    df_inv, df_flores = cargar_todo()
except Exception as e:
    st.error("⚠️ Error de conexión: Revisa los 'Secrets' en Streamlit Cloud y que el Excel esté compartido con el correo del robot.")
    st.stop()

# --- PANEL LATERAL DE PRECIOS ---
with st.sidebar:
    st.header("⚙️ Ajustar Precios ($)")
    p_rollo = st.number_input("Precio Rollo Cinta (50y)", value=2.50)
    p_papel = st.number_input("Precio Paquete Papel (20u)", value=2.00)
    p_silic = st.number_input("Precio Paquete Silicona (8u)", value=1.00)
    p_hora = st.number_input("Tu Sueldo por Hora ($)", value=3.00)
    st.divider()
    st.write("Configuración de Novedades Khloe")

tab1, tab2, tab3 = st.tabs(["💰 CALCULADORA", "📦 BODEGA", "🌺 MODELOS"])

# ==========================================
# PESTAÑA 1: CALCULADORA (LA INTELIGENCIA)
# ==========================================
with tab1:
    st.subheader("Simulador de Pedido")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        f_tipo = st.selectbox("Modelo de Flor:", df_flores["Tipo_Flor"].tolist())
        # Filtramos solo materiales que se miden en Metros para el color de la cinta
        lista_colores = df_inv[df_inv["Unidad"].str.contains("Metros", case=False, na=False)]["Material"].tolist()
        f_color = st.selectbox("Color de Cinta (Stock):", lista_colores)
    
    with col2:
        f_cant = st.number_input("¿Cuántas flores?", min_value=1, value=12)
        f_tiempo = st.number_input("Minutos de armado:", min_value=5, value=45)
    
    l_moño = st.checkbox("¿Lleva Moño Grande? (+1.55m de cinta)")

    # LÓGICA DE CÁLCULO
    # Buscamos los datos del modelo elegido en la pestaña Flores
    datos_f = df_flores[df_flores["Tipo_Flor"] == f_tipo].iloc[0]
    
    # Metros de cinta: cantidad de flores * (largo pétalo en metros * cantidad de pétalos)
    m_cinta = f_cant * ((datos_f["Largo_Petalo_cm"] / 100) * datos_f["Cantidad_Petalos"])
    if l_moño: 
        m_cinta += 1.55
    
    # Cálculo de otros materiales
    b_silic = (f_cant * 0.5) + 2.0  # 0.5 barras por flor + 2 para la base
    p_hojas = 1.75 * math.sqrt(f_cant / 8) # Proporción de papel coreano

    # COSTOS REALES (Fórmula: Material x 3 + Mano de obra)
    costo_mat = (m_cinta * (p_rollo/45.72)) + (b_silic * (p_silic/8)) + (p_hojas * (p_papel/20))
    costo_mano = (f_tiempo / 60) * p_hora
    p_sugerido = (costo_mat * 3) + costo_mano

    st.markdown("---")
    st.subheader("Gastos y Precio de Venta")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Cinta", f"{m_cinta:.2f} m")
    res2.metric("Silicona", f"{b_silic:.1f} bar")
    res3.metric("Papel", f"{p_hojas:.1f} plieg")
    res4.metric("SUGERIDO", f"${p_sugerido:.2f}", delta=f"Costo: ${costo_mat:.2f}")

    if st.button("🚀 REGISTRAR VENTA (DESCONTAR STOCK)"):
        # Actualizamos el inventario localmente
        df_inv.loc[df_inv["Material"] == f_color, "Cantidad"] -= m_cinta
        df_inv.loc[df_inv["Material"] == "Silicona", "Cantidad"] -= b_silic
        
        # Enviamos la actualización a Google Sheets
        conn.update(worksheet="Inventario", data=df_inv)
        st.success(f"✅ Venta registrada: Se descontaron {m_cinta:.2f}m de {f_color} y {b_silic:.1f} barras de silicona.")
        st.balloons()

# ==========================================
# PESTAÑA 2: GESTIÓN DE BODEGA
# ==========================================
with tab2:
    st.subheader("Inventario en Tiempo Real")
    st.dataframe(df_inv, use_container_width=True)
    
    with st.expander("➕ Cargar nueva compra de material"):
        mat_add = st.selectbox("¿Qué compraste?", df_inv["Material"].tolist())
        cant_add = st.number_input("Cantidad nueva:", min_value=0.1)
        if st.button("Actualizar Inventario"):
            df_inv.loc[df_inv["Material"] == mat_add, "Cantidad"] += cant_add
            conn.update(worksheet="Inventario", data=df_inv)
            st.success("¡Inventario actualizado!")
            st.rerun()

# ==========================================
# PESTAÑA 3: CATÁLOGO DE FLORES
# ==========================================
with tab3:
    st.subheader("Modelos Guardados")
    st.table(df_flores)
    
    if st.checkbox("➕ Agregar Modelo Nuevo"):
        n_flor = st.text_input("Nombre de la flor:")
        n_largo = st.number_input("Largo de pétalo (cm):", value=10.0)
        n_peta = st.number_input("Cantidad de pétalos:", value=15)
        if st.button("Guardar Modelo"):
            nueva_f = pd.DataFrame({"Tipo_Flor": [n_flor], "Largo_Petalo_cm": [n_largo], "Cantidad_Petalos": [n_peta]})
            df_flores = pd.concat([df_flores, nueva_f], ignore_index=True)
            conn.update(worksheet="Flores", data=df_flores)
            st.success("Nuevo modelo guardado.")
            st.rerun()