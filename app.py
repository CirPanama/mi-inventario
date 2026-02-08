import streamlit as st
from st_supabase_connection import SupabaseConnection

# Configuración de la página
st.set_page_config(page_title="Sistema de Inventario Pro", layout="wide")

# 1. Conexión a la Base de Datos (Supabase)
# Estos datos se configuran en la sección "Secrets" de Streamlit Cloud
conn = st.connection("supabase", type=SupabaseConnection)

st.title("🚀 Punto de Venta & Inventario")

# Inicializar el carrito en la sesión
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- COLUMNA IZQUIERDA: BÚSQUEDA ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🔍 Buscar Producto")
    busqueda = st.text_input("Escanea Código de Barras o escribe Referencia")
    
    if busqueda:
        # Buscamos en Supabase por código de barras O referencia
        query = conn.table("productos").select("*").or_(f"codigo_barras.eq.{busqueda},referencia.eq.{busqueda}").execute()
        
        if query.data:
            prod = query.data[0]
            st.success(f"Producto encontrado: {prod['nombre']}")
            
            # Mostrar Imagen
            if prod['imagen_url']:
                st.image(prod['imagen_url'], width=200)
            
            st.write(f"**Precio:** ${prod['precio_venta']}")
            st.write(f"**Stock disponible:** {prod['stock']}")
            
            if st.button("➕ Añadir al carrito"):
                st.session_state.carrito.append({
                    "id": prod['id'],
                    "nombre": prod['nombre'],
                    "precio": prod['precio_venta'],
                    "cantidad": 1
                })
                st.rerun()
        else:
            st.error("Producto no encontrado.")

# --- COLUMNA DERECHA: CARRITO Y FACTURACIÓN ---
with col2:
    st.subheader("🛒 Carrito de Compras")
    total_factura = 0
    
    if st.session_state.carrito:
        for item in st.session_state.carrito:
            st.write(f"- {item['nombre']} | ${item['precio']} x {item['cantidad']}")
            total_factura += item['precio'] * item['cantidad']
        
        st.divider()
        st.header(f"Total: ${total_factura}")
        
        if st.button("✅ Finalizar Venta"):
            # Aquí iría la lógica para insertar en la tabla 'facturas' y 'detalle_factura'
            # El TRIGGER que creamos en SQL restará el stock automáticamente
            st.balloons()
            st.success("Venta procesada con éxito. El stock se actualizó.")
            st.session_state.carrito = [] # Limpiar carrito
    else:
        st.info("El carrito está vacío")
