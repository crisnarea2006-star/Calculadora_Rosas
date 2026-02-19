import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Novedades Khloe", page_icon="🌹", layout="centered")

st.title("🌹 Novedades Khloe")
st.write("Sistema Profesional conectado a Google Sheets")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    inv = conn.read(worksheet="Inventario")
    flores = conn.read(worksheet="Flores")
    return inv, flores

try:
    df_inv, df_flores = cargar_datos()
except Exception as e:
    st.error("Error: No se pudo conectar a Google Sheets. Revisa los 'Secrets' y los nombres de las pestañas.")
    st.stop()

# --- MENÚ LATERAL: PRECIOS ---
st.sidebar.header("⚙️ Ajustar Precios ($)")
precio_rollo = st.sidebar.number_input("Rollo Cinta (50y)", value=2.50)
precio_papel = st.sidebar.number_input("Paq. Papel (20u)", value=2.00)
precio_silicona = st.sidebar.number_input("Paq. Silicona (8u)", value=1.00)
precio_palitos = st.sidebar.number_input("Paq. Palitos (50u)", value=1.00)
precio_plumafon = st.sidebar.number_input("Plancha Plumafón", value=0.60)
sueldo_hora = st.sidebar.number_input("Tu sueldo por hora", value=3.00)

tab1, tab2, tab3 = st.tabs(["💰 Calculadora", "📦 Inventario", "🌺 Mis Flores"])

# ==========================================
# PESTAÑA 1: CALCULADORA
# ==========================================
with tab1:
    st.header("Armar un Pedido")
    col1, col2 = st.columns(2)
    with col1:
        flor_sel = st.selectbox("Flor:", df_flores["Tipo_Flor"].tolist(), help="Elige el modelo de flor.")
        cant_f = st.number_input("Cantidad de flores:", min_value=1, value=12)
        color_f = st.selectbox("Color de Cinta:", df_inv[df_inv["Unidad"] == "Metros"]["Material"].tolist())
    with col2:
        usar_m = st.checkbox("¿Lleva Moño Grande?")
        t_minutos = st.number_input("Minutos de trabajo:", min_value=5, value=45)

    # Cálculos
    datos_f = df_flores[df_flores["Tipo_Flor"] == flor_sel].iloc[0]
    m_totales = cant_f * ((datos_f["Largo_Petalo_cm"] / 100) * datos_f["Cantidad_Petalos"])
    if usar_m:
        m_totales += 1.55 # Metros extra por moño
    
    barras = (cant_f * 0.5) + 2.0
    hojas = 1.75 * math.sqrt(cant_f / 8)

    # Costos
    c_material = (m_totales * (precio_rollo/45.72)) + (barras * (precio_silicona/8)) + (hojas * (precio_papel/20))
    c_obra = (t_minutos / 60) * sueldo_hora
    p_sugerido = (c_material * 3) + c_obra

    st.info(f"Gasto estimado: {m_totales:.2f}m de cinta, {barras:.1f} barras y {hojas:.1f} pliegos.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Material", f"${c_material:.2f}")
    c2.metric("Mano Obra", f"${c_obra:.2f}")
    c3.metric("Sugerido", f"${p_sugerido:.2f}")

    if st.button("✅ Registrar Venta (Descontar de Google Sheets)"):
        # Lógica para actualizar Google Sheets
        df_inv.loc[df_inv["Material"] == color_f, "Cantidad"] -= m_totales
        df_inv.loc[df_inv["Material"] == "Silicona", "Cantidad"] -= barras
        conn.update(worksheet="Inventario", data=df_inv)
        st.success("¡Venta guardada en Google Sheets!")

# ==========================================
# PESTAÑA 2: INVENTARIO (EDITAR/ELIMINAR)
# ==========================================
with tab2:
    st.header("Control de Bodega")
    st.dataframe(df_inv)

    st.subheader("🛒 Acciones de Inventario")
    accion = st.radio("¿Qué deseas hacer?", ["Sumar Compra", "Editar/Corregir", "Eliminar Material"])

    if accion == "Sumar Compra":
        mat_c = st.selectbox("Material:", df_inv["Material"].tolist())
        und = df_inv[df_inv["Material"] == mat_c]["Unidad"].values[0]
        if und == "Metros":
            modo = st.radio("Compra por:", ["Rollos (50y)", "Metros sueltos"])
            val = st.number_input("Cantidad:", min_value=1.0)
            final = val * 45.72 if modo == "Rollos (50y)" else val
        else:
            final = st.number_input(f"Cantidad ({und}):", min_value=1.0)
        
        if st.button("➕ Actualizar Stock"):
            df_inv.loc[df_inv["Material"] == mat_c, "Cantidad"] += final
            conn.update(worksheet="Inventario", data=df_inv)
            st.success("Inventario actualizado.")
            st.rerun()

    elif accion == "Editar/Corregir":
        mat_e = st.selectbox("Material a editar:", df_inv["Material"].tolist())
        idx = df_inv[df_inv["Material"] == mat_e].index[0]
        nuevo_n = st.text_input("Nombre:", value=df_inv.at[idx, "Material"])
        nueva_c = st.number_input("Cantidad:", value=float(df_inv.at[idx, "Cantidad"]))
        if st.button("💾 Guardar Cambios"):
            df_inv.at[idx, "Material"] = nuevo_n
            df_inv.at[idx, "Cantidad"] = nueva_c
            conn.update(worksheet="Inventario", data=df_inv)
            st.rerun()

# ==========================================
# PESTAÑA 3: MIS FLORES
# ==========================================
with tab3:
    st.header("Catálogo de Diseños")
    st.dataframe(df_flores)
    
    if st.checkbox("➕ Agregar Nueva Flor"):
        n_flor = st.text_input("Nombre:")
        n_largo = st.number_input("Largo pétalo (cm):", value=10.0)
        n_peta = st.number_input("Cant. pétalos:", value=30)
        if st.button("Guardar Flor"):
            nueva_f = pd.DataFrame({"Tipo_Flor": [n_flor], "Largo_Petalo_cm": [n_largo], "Cantidad_Petalos": [n_peta]})
            df_flores = pd.concat([df_flores, nueva_f], ignore_index=True)
            conn.update(worksheet="Flores", data=df_flores)
            st.rerun()