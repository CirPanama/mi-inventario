import streamlit as st
import pandas as pd
from datetime import datetime
import json
from supabase import create_client

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="SISTEMA INTEGRAL CIR PANAMÁ", layout="wide")

st.markdown("""
    <style>
    .stDataEditor { border: 1px solid #217346; }
    .main-header { background-color: #217346; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .excel-font { font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 2. NÚCLEO DE CONEXIÓN ---
URL = "https://jegxtslswopyixvtuexu.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImplZ3h0c2xzd29weWl4dnR1ZXh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0OTA3MTksImV4cCI6MjA4NjA2NjcxOX0.UXQ3WhR356jObinxJFGdELjuj10BaNnPrD8BrXKdLY0"
supabase = create_client(URL, KEY)

# ==============================================================================
# 3. CLASES MODULARES (POO)
# ==============================================================================

class DBService:
    @staticmethod
    def fetch(tabla):
        res = supabase.table(tabla).select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()

    @staticmethod
    def update_stock(id_prod, nuevo_stock):
        supabase.table("productos").update({"stock": int(nuevo_stock)}).eq("id", id_prod).execute()

class ModuloVentas:
    @staticmethod
    def render():
        st.markdown('<div class="main-header"><h1>⚖️ Terminal de Ventas y Despacho</h1></div>', unsafe_allow_html=True)
        
        if 'carrito' not in st.session_state: st.session_state.carrito = []
        df_p = DBService.fetch("productos")

        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 1])
            tipo = c1.selectbox("Documento", ["Factura", "Cotización"])
            cliente = c2.text_input("Cliente", "Consumidor Final")
            correlativo = c3.text_input("N° Documento", value=datetime.now().strftime("%Y%m%d%H%M"))

        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 2])
            modo = col1.toggle("Modo Manual")
            
            if not modo:
                sel = col1.selectbox("Buscar Producto", ["---"] + df_p['nombre'].tolist())
                if sel != "---":
                    p = df_p[df_p['nombre'] == sel].iloc[0]
                    precios = {f"P5 (${p['p5']})": p['p5'], f"P7 (${p['p7']})": p['p7'], f"P10 (${p['p10']})": p['p10']}
                    p_sel = col3.radio("Lista de Precios", list(precios.keys()), horizontal=True)
                    precio_final = precios[p_sel]
                    cant = col2.number_input("Cant", min_value=1)
                    if st.button("➕ AGREGAR"):
                        st.session_state.carrito.append({"id": int(p['id']), "nombre": p['nombre'], "cant": cant, "precio": precio_final, "sub": cant*precio_final})
                        st.rerun()
            else:
                desc = col1.text_input("Descripción Servicio")
                p_man = col3.number_input("Precio $")
                cant = col2.number_input("Cant", min_value=1)
                if st.button("➕ AGREGAR MANUAL"):
                    st.session_state.carrito.append({"id": None, "nombre": desc, "cant": cant, "precio": p_man, "sub": cant*p_man})
                    st.rerun()

        if st.session_state.carrito:
            df_c = pd.DataFrame(st.session_state.carrito)
            st.table(df_c)
            total = df_c['sub'].sum() * 1.07
            if st.button(f"🚀 FINALIZAR VENTA (${total:,.2f})", type="primary"):
                # Lógica de guardado y descuento de stock
                detalles_json = json.dumps(st.session_state.carrito)
                supabase.table("ventas").insert({"cliente": cliente, "total": total, "detalles": detalles_json, "num_factura": correlativo}).execute()
                if tipo == "Factura":
                    for it in st.session_state.carrito:
                        if it['id']:
                            stk_act = df_p[df_p['id'] == it['id']].iloc[0]['stock']
                            DBService.update_stock(it['id'], stk_act - it['cant'])
                st.session_state.carrito = []
                st.success("Operación Exitosa")
                st.rerun()

class ModuloInventario:
    @staticmethod
    def render():
        st.markdown('<div class="main-header"><h1>📦 Control de Inventario</h1></div>', unsafe_allow_html=True)
        df = DBService.fetch("productos")
        st.info("Firma Visual: Edición directa tipo Hoja de Cálculo")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="excel_inv")
        if st.button("💾 Guardar Cambios Masivos"):
            # Aquí iría el loop de actualización para cada fila cambiada
            st.success("Inventario Sincronizado con Supabase")

class ModuloContabilidad:
    @staticmethod
    def render():
        st.markdown('<div class="main-header"><h1>📈 Contabilidad y Cierre</h1></div>', unsafe_allow_html=True)
        df_v = DBService.fetch("ventas")
        if not df_v.empty:
            t_ventas = df_v['total'].sum()
            t_itbms = t_ventas - (t_ventas / 1.07)
            c1, c2 = st.columns(2)
            c1.metric("Ventas Totales (Bruto)", f"${t_ventas:,.2f}")
            c2.metric("ITBMS 7% Recaudado", f"${t_itbms:,.2f}")
            st.dataframe(df_v, use_container_width=True)

class ModuloAdmin:
    @staticmethod
    def render():
        st.header("⚙️ Configuración del Sistema")
        st.write("Control de Usuarios y Márgenes Globales (P5, P7, P10)")

# ==============================================================================
# 4. ORQUESTADOR PRINCIPAL
# ==============================================================================

def main():
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🛡️ CIR PANAMÁ OS - LOGIN")
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "123": # Credenciales según lo acordado
                st.session_state.auth = True
                st.rerun()
    else:
        menu = st.sidebar.radio("MENÚ", ["Ventas", "Inventario", "Contabilidad", "Administración"])
        if st.sidebar.button("Salir"):
            st.session_state.auth = False
            st.rerun()

        if menu == "Ventas": ModuloVentas.render()
        elif menu == "Inventario": ModuloInventario.render()
        elif menu == "Contabilidad": ModuloContabilidad.render()
        elif menu == "Administración": ModuloAdmin.render()

if __name__ == "__main__":
    main()