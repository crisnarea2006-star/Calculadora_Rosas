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
st.sidebar.write("Modifica esto si te suben los costos de los proveedores:")
precio_rollo = st.sidebar.number_input("Rollo Cinta (50y)", value=2.50, help="Precio total de un rollo cerrado.")
precio_papel = st.sidebar.number_input("Paq. Papel (20u)", value=2.00, help="Precio del paquete que trae 20 pliegos.")
precio_silicona = st.sidebar.number_input("Paq. Silicona (8u)", value=1.00, help="Precio de la funda de siliconas gruesas.")
precio_palitos = st.sidebar.number_input("Paq. Palitos (50u)", value=1.00, help="Precio del paquete de palitos de bambú.")
precio_plumafon = st.sidebar.number_input("Plancha Plumafón", value=0.60, help="Precio de una plancha entera.")
sueldo_hora = st.sidebar.number_input("Tu sueldo por hora ($)", value=3.00, help="¿Cuánto quieres ganar por cada hora de tu tiempo?")

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
    
    with st.expander("ℹ️ ¿Cómo usar la calculadora?"):
        st.write("1. Elige qué flor vas a hacer y de qué color.")
        st.write("2. Pon la cantidad y el tiempo que te tomará.")
        st.write("3. Al darle al botón verde, el sistema te dirá cuánto cobrar y restará los materiales de tu bodega automáticamente.")

    col1, col2 = st.columns(2)
    with col1:
        flor_elegida = st.selectbox("¿Qué flor vas a hacer?", df_flores["Tipo_Flor"].tolist(), help="Si la flor no está en la lista, ve a la pestaña 'Mis Flores' para crearla.")
        cantidad_flores = st.number_input("¿Qué cantidad?", min_value=1, value=12, help="Número total de flores que llevará el arreglo.")
        lista_cintas = df_inv[df_inv["Unidad"] == "Metros"]["Material"].tolist()
        color_elegido = st.selectbox("Color de la Cinta", lista_cintas, help="Este color se descontará de tu inventario al registrar la venta.")
        
    with col2:
        usar_mono = st.checkbox("¿Lleva Moño Grande?", help="Marca esta casilla si el ramo lleva un moño de cinta. Gastará material extra.")
        minutos = st.number_input("Minutos de trabajo total", min_value=5, value=45, step=5, help="Suma el tiempo que te toma hacer las flores más el tiempo de armar el ramo.")

    # 1. Calcular consumos físicos
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

    # 2. Calcular COSTOS EN DINERO
    costo_cinta_usd = metros_totales * (precio_rollo / 45.72)
    costo_silicona_usd = barras_necesarias * (precio_silicona / 8)
    costo_papel_usd = hojas_necesarias * (precio_papel / 20)
    costo_palitos_usd = cantidad_flores * (precio_palitos / 50)
    costo_plumafon_usd = precio_plumafon * (2 if cantidad_flores > 30 else 1)
    
    total_materiales_usd = costo_cinta_usd + costo_silicona_usd + costo_papel_usd + costo_palitos_usd + costo_plumafon_usd
    costo_mano_obra_usd = (minutos / 60) * sueldo_hora
    
    precio_venta_sugerido = (total_materiales_usd * 3) + costo_mano_obra_usd

    # 3. Mostrar Resumen al usuario
    st.info(f"💡 El ramo gastará: **{metros_totales:.1f}m** de {color_elegido}, **{barras_necesarias:.1f}** barras de silicona y **{hojas_necesarias:.1f}** pliegos de papel.")
    
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Gasto Materiales", f"${total_materiales_usd:.2f}")
    c2.metric("👩‍🔧 Mano de Obra", f"${costo_mano_obra_usd:.2f}")
    c3.metric("💰 Precio Sugerido", f"${precio_venta_sugerido:.2f}")
    st.markdown("---")

    if st.button("✅ Registrar Venta y Descontar Material", help="Presiona aquí solo cuando ya hayas vendido o armado el ramo para actualizar la bodega."):
        df_inv.loc[df_inv["Material"] == color_elegido, "Cantidad"] -= metros_totales
        df_inv.loc[df_inv["Material"] == "Silicona", "Cantidad"] -= barras_necesarias
        df_inv.loc[df_inv["Material"] == "Papel Coreano", "Cantidad"] -= hojas_necesarias
        df_inv.loc[df_inv["Material"] == "Palitos", "Cantidad"] -= cantidad_flores
        
        guardar_inv(df_inv)
        st.success("¡Venta Registrada! Dinero calculado y materiales descontados de la bodega.")

# ==========================================
# PESTAÑA 2: INVENTARIO Y CONVERSIÓN DE ROLLOS
# ==========================================
with tab2:
    st.header("Control de Bodega")
    
    with st.expander("ℹ️ ¿Cómo funciona la Bodega?"):
        st.write("Aquí ves cuánto material te queda. Si algo está por agotarse, verás una alerta roja. Usa la sección de abajo cada vez que vayas a comprar materiales para mantener tus cuentas al día.")
    
    alertas = 0
    for index, fila in df_inv.iterrows():
        if fila["Cantidad"] <= fila["Alerta_Minima"]:
            st.error(f"⚠️ URGENTE: Queda poco de **{fila['Material']}** ({fila['Cantidad']:.1f} {fila['Unidad']})")
            alertas += 1
            
    st.dataframe(df_inv, use_container_width=True)

    st.write("---")
    st.subheader("🛒 Ingresar Compras de Material")
    
    material_comprado = st.selectbox("¿Qué material compraste?", df_inv["Material"].tolist() + ["+ Agregar Material Nuevo"], help="Elige el material de la lista. Si es un color de cinta nuevo, elige '+ Agregar Material Nuevo'.")
    
    if material_comprado == "+ Agregar Material Nuevo":
        st.info("Vas a crear un material que no existe en tu lista.")
        nuevo_nombre = st.text_input("Nombre", help="Ejemplo: Cinta Negra, Luces LED, Mariposas")
        nueva_unidad = st.selectbox("¿En qué se mide?", ["Metros", "Pliegos", "Barras", "Unidades", "Planchas"], help="¿Cómo cuentas este material?")
        cantidad_inicial = st.number_input("Cantidad inicial", min_value=1.0, help="¿Cuánto compraste para abrir este inventario?")
        
        if st.button("➕ Guardar Material Nuevo"):
            if nuevo_nombre:
                nueva_fila = pd.DataFrame({"Material": [nuevo_nombre], "Cantidad": [cantidad_inicial], "Unidad": [nueva_unidad], "Alerta_Minima": [10.0]})
                df_inv = pd.concat([df_inv, nueva_fila], ignore_index=True)
                guardar_inv(df_inv)
                st.success(f"¡{nuevo_nombre} agregado a tu inventario!")
                st.rerun()
                
    else:
        unidad = df_inv[df_inv["Material"] == material_comprado]["Unidad"].values[0]
        
        if unidad == "Metros":
            tipo_ingreso = st.radio("¿Cómo compraste la cinta?", ["Por Rollos enteros (de 50 yardas)", "Por Metros sueltos"], help="Elige si compraste el rollo sellado o si pediste metros sueltos en la mercería.")
            
            if tipo_ingreso == "Por Rollos enteros (de 50 yardas)":
                cant_rollos = st.number_input("¿Cuántos rollos compraste?", min_value=1.0, step=1.0)
                cantidad_final = cant_rollos * 45.72
                st.info(f"💡 {cant_rollos} rollos se convertirán en **{cantidad_final:.2f} metros** para tu inventario.")
            else:
                cantidad_final = st.number_input("¿Cuántos metros exactos compraste?", min_value=1.0)
        else:
            cantidad_final = st.number_input(f"¿Cuántas {unidad} compraste?", min_value=1.0)
            
        if st.button("➕ Sumar al Inventario"):
            df_inv.loc[df_inv["Material"] == material_comprado, "Cantidad"] += cantidad_final
            guardar_inv(df_inv)
            st.success(f"¡Se sumaron {cantidad_final:.2f} a {material_comprado}!")
            st.rerun()

# ==========================================
# PESTAÑA 3: CATÁLOGO DE FLORES
# ==========================================
with tab3:
    st.header("🌺 Mis Diseños de Flores")
    
    with st.expander("ℹ️ ¿Qué es el catálogo?"):
        st.write("Cada artesana tiene su propio estilo. Aquí guardas la 'receta' de tus flores. Si mañana inventas un Tulipán que usa 5 pétalos de 12cm, lo registras aquí para que la calculadora pueda usarlo.")
        
    st.dataframe(df_flores, use_container_width=True)
    
    st.write("---")
    st.subheader("✨ Agregar Nuevo Modelo")
    nueva_flor = st.text_input("Nombre de la Flor", help="Ej: Girasol Mediano, Rosa Gigante, Tulipán")
    medida_petalo = st.number_input("Largo de 1 pétalo (cm)", min_value=1.0, value=10.0, help="Mide con una regla de qué tamaño cortas la tarjeta o molde para un solo pétalo.")
    cant_petalos = st.number_input("¿Cuántos pétalos lleva 1 flor?", min_value=1, value=30, help="Cuenta cuántos pétalos pegas en total para formar una sola flor terminada.")
    
    if st.button("💾 Guardar Modelo en Catálogo"):
        if nueva_flor:
            nueva_fila_flor = pd.DataFrame({
                "Tipo_Flor": [nueva_flor], 
                "Largo_Petalo_cm": [medida_petalo], 
                "Cantidad_Petalos": [cant_petalos]
            })
            df_flores = pd.concat([df_flores, nueva_fila_flor], ignore_index=True)
            guardar_flores(df_flores)
            st.success(f"¡{nueva_flor} guardado!")
            st.rerun()