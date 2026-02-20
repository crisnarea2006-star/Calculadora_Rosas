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
            "Cantidad": [45.72, 45.72, 20.0, 8.0, 50.0, 5.0], 
            "Unidad": ["Metros", "Metros", "Pliegos", "Barras", "Unidades", "Planchas"],
            "Alerta_Minima": [10.0, 10.0, 5.0, 3.0, 15.0, 1.0] 
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

# --- MENÚ LATERAL: AJUSTAR PRECIOS EN DÓLARES ---
st.sidebar.header("⚙️ Ajustar Precios")
st.sidebar.write("Modifica esto si te suben los costos:")
precio_rollo = st.sidebar.number_input("Rollo Cinta (50y)", value=2.50)
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

    costo_cinta_usd = metros_totales * (precio_rollo / 45.72)
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
# PESTAÑA 2: INVENTARIO Y CORRECCIONES
# ==========================================
with tab2:
    st.header("Control de Bodega")
    
    alertas = 0
    for index, fila in df_inv.iterrows():
        if fila["Cantidad"] <= fila["Alerta_Minima"]:
            st.error(f"⚠️ URGENTE: Queda poco de **{fila['Material']}** ({fila['Cantidad']:.1f} {fila['Unidad']})")
            alertas += 1
            
    st.dataframe(df_inv, use_container_width=True)

    # --- SECCIÓN: INGRESAR COMPRAS ---
    st.write("---")
    st.subheader("🛒 Ingresar Compras")
    
    material_comprado = st.selectbox("¿Qué material compraste?", df_inv["Material"].tolist() + ["+ Agregar Material Nuevo"])
    
    if material_comprado == "+ Agregar Material Nuevo":
        nuevo_nombre = st.text_input("Nombre (Ej: Cinta Negra)")
        nueva_unidad = st.selectbox("¿En qué se mide?", ["Metros", "Pliegos", "Barras", "Unidades", "Planchas"])
        cantidad_inicial = st.number_input("Cantidad inicial", min_value=1.0)
        
        if st.button("➕ Guardar Material Nuevo"):
            if nuevo_nombre:
                nueva_fila = pd.DataFrame({"Material": [nuevo_nombre], "Cantidad": [cantidad_inicial], "Unidad": [nueva_unidad], "Alerta_Minima": [10.0]})
                df_inv = pd.concat([df_inv, nueva_fila], ignore_index=True)
                guardar_inv(df_inv)
                st.success(f"¡{nuevo_nombre} agregado!")
                st.rerun()
    else:
        unidad = df_inv[df_inv["Material"] == material_comprado]["Unidad"].values[0]
        if unidad == "Metros":
            tipo_ingreso = st.radio("¿Cómo compraste la cinta?", ["Por Rollos enteros (de 50 yardas)", "Por Metros sueltos"])
            if tipo_ingreso == "Por Rollos enteros (de 50 yardas)":
                cant_rollos = st.number_input("¿Cuántos rollos?", min_value=1.0, step=1.0)
                cantidad_final = cant_rollos * 45.72
            else:
                cantidad_final = st.number_input("¿Cuántos metros?", min_value=1.0)
        else:
            cantidad_final = st.number_input(f"¿Cuántas {unidad} compraste?", min_value=1.0)
            
        if st.button("➕ Sumar al Inventario"):
            df_inv.loc[df_inv["Material"] == material_comprado, "Cantidad"] += cantidad_final
            guardar_inv(df_inv)
            st.success(f"¡Sumados {cantidad_final:.2f} a {material_comprado}!")
            st.rerun()

    # --- SECCIÓN: EDITAR Y CORREGIR ERRORES ---
    st.write("---")
    st.subheader("✏️ Corregir, Editar o Eliminar")
    with st.expander("Abre aquí para corregir datos mal registrados"):
        accion_corregir = st.radio("¿Qué necesitas hacer?", [
            "Descontar cantidad (ej. material dañado)", 
            "✏️ EDITAR TODOS LOS DATOS (Nombre, Cantidad, Unidad)",
            "Eliminar un material por completo"
        ])
        
        if accion_corregir == "Descontar cantidad (ej. material dañado)":
            mat_descontar = st.selectbox("Selecciona el material", df_inv["Material"].tolist(), key="desc_mat")
            unidad_mat = df_inv[df_inv["Material"] == mat_descontar]["Unidad"].values[0]
            cant_descontar = st.number_input(f"¿Cuántos {unidad_mat} vas a restar?", min_value=0.1)
            if st.button("📉 Restar"):
                df_inv.loc[df_inv["Material"] == mat_descontar, "Cantidad"] -= cant_descontar
                df_inv.loc[df_inv["Cantidad"] < 0, "Cantidad"] = 0 
                guardar_inv(df_inv)
                st.success("¡Descontado con éxito!")
                st.rerun()
                
        elif accion_corregir == "✏️ EDITAR TODOS LOS DATOS (Nombre, Cantidad, Unidad)":
            mat_editar = st.selectbox("Selecciona el material a arreglar", df_inv["Material"].tolist(), key="edit_mat")
            idx = df_inv[df_inv["Material"] == mat_editar].index[0]
            datos_act = df_inv.iloc[idx]
            
            st.info("Escribe los datos correctos abajo:")
            n_nombre = st.text_input("Corregir Nombre", value=datos_act["Material"])
            n_cant = st.number_input("Corregir Cantidad Actual", value=float(datos_act["Cantidad"]))
            
            lista_und = ["Metros", "Pliegos", "Barras", "Unidades", "Planchas"]
            idx_und = lista_und.index(datos_act["Unidad"]) if datos_act["Unidad"] in lista_und else 0
            n_unidad = st.selectbox("Corregir Unidad", lista_und, index=idx_und)
            
            n_alerta = st.number_input("Corregir Alerta Mínima", value=float(datos_act["Alerta_Minima"]))
            
            if st.button("💾 Guardar Corrección"):
                df_inv.at[idx, "Material"] = n_nombre
                df_inv.at[idx, "Cantidad"] = n_cant
                df_inv.at[idx, "Unidad"] = n_unidad
                df_inv.at[idx, "Alerta_Minima"] = n_alerta
                guardar_inv(df_inv)
                st.success("¡Datos corregidos perfectamente!")
                st.rerun()

        elif accion_corregir == "Eliminar un material por completo":
            mat_eliminar = st.selectbox("Material a borrar", df_inv["Material"].tolist(), key="elim_mat")
            st.warning(f"⚠️ Borrarás '{mat_eliminar}' para siempre.")
            if st.button("🚨 Sí, Eliminar Definitivamente"):
                df_inv = df_inv[df_inv["Material"] != mat_eliminar]
                guardar_inv(df_inv)
                st.success("¡Material eliminado!")
                st.rerun()

# ==========================================
# PESTAÑA 3: CATÁLOGO DE FLORES
# ==========================================
with tab3:
    st.header("🌺 Mis Diseños de Flores")
    st.dataframe(df_flores, use_container_width=True)
    
    st.write("---")
    st.subheader("✨ Agregar Nuevo Modelo")
    nueva_flor = st.text_input("Nombre de la Flor")
    medida_petalo = st.number_input("Largo de 1 pétalo (cm)", min_value=1.0, value=10.0)
    cant_petalos = st.number_input("¿Cuántos pétalos lleva 1 flor?", min_value=1, value=30)
    
    if st.button("💾 Guardar Modelo"):
        if nueva_flor:
            nueva_fila_flor = pd.DataFrame({"Tipo_Flor": [nueva_flor], "Largo_Petalo_cm": [medida_petalo], "Cantidad_Petalos": [cant_petalos]})
            df_flores = pd.concat([df_flores, nueva_fila_flor], ignore_index=True)
            guardar_flores(df_flores)
            st.success("¡Guardado!")
            st.rerun()

    # --- SECCIÓN: EDITAR FLORES ---
    st.write("---")
    with st.expander("✏️ Editar o Eliminar un Diseño Existente"):
        acc_flor = st.radio("Acción:", ["Editar medidas de flor", "Eliminar flor"])
        if acc_flor == "Editar medidas de flor":
            flor_ed = st.selectbox("Flor a corregir", df_flores["Tipo_Flor"].tolist())
            idx_f = df_flores[df_flores["Tipo_Flor"] == flor_ed].index[0]
            datos_f = df_flores.iloc[idx_f]
            
            nf_nombre = st.text_input("Corregir Nombre", value=datos_f["Tipo_Flor"])
            nf_largo = st.number_input("Corregir Largo de pétalo (cm)", value=float(datos_f["Largo_Petalo_cm"]))
            nf_cant = st.number_input("Corregir Cantidad de pétalos", value=int(datos_f["Cantidad_Petalos"]))
            
            if st.button("💾 Actualizar Diseño"):
                df_flores.at[idx_f, "Tipo_Flor"] = nf_nombre
                df_flores.at[idx_f, "Largo_Petalo_cm"] = nf_largo
                df_flores.at[idx_f, "Cantidad_Petalos"] = nf_cant
                guardar_flores(df_flores)
                st.success("¡Diseño corregido!")
                st.rerun()
                
        elif acc_flor == "Eliminar flor":
            flor_el = st.selectbox("Flor a borrar", df_flores["Tipo_Flor"].tolist())
            if st.button("🚨 Eliminar Flor"):
                df_flores = df_flores[df_flores["Tipo_Flor"] != flor_el]
                guardar_flores(df_flores)
                st.success("¡Flor eliminada!")
                st.rerun()