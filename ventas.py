import streamlit as st
import pandas as pd
import json
from datetime import datetime

class ModuloVentas:
    def __init__(self, db):
        self.db = db

    def render(self):
        st.header("⚖️ Terminal de Ventas y Cotizaciones")
        tipo = st.radio("Tipo de Documento", ["Venta", "Cotización"], horizontal=True)
        
        prods = self.db.fetch("productos")
        df_p = pd.DataFrame(prods)

        with st.container(border=True):
            c1, c2, c3 = st.columns([2,1,1])
            cliente = c1.text_input("Cliente")
            n_doc = c2.number_input("N° Correlativo", step=1)
            flete = c3.number_input("Flete $", 0.0)

        # Buscador y Selección
        sel = st.selectbox("Buscar Producto", df_p['nombre'].tolist())
        p_row = df_p[df_p['nombre'] == sel].iloc[0]
        
        c_pre, c_cant = st.columns(2)
        precios = {"P5": p_row['p5'], "P7": p_row['p7'], "P10": p_row['p10']}
        p_sel = c_pre.radio("Precio a Aplicar", list(precios.keys()), horizontal=True)
        cant = c_cant.number_input("Cantidad", 1)

        if st.button("➕ Agregar al Detalle"):
            if 'temp_cart' not in st.session_state: st.session_state.temp_cart = []
            st.session_state.temp_cart.append({
                "id": p_row['id'], "nombre": sel, "cantidad": cant, 
                "precio": precios[p_sel], "subtotal": cant * precios[p_sel]
            })

        if 'temp_cart' in st.session_state and st.session_state.temp_cart:
            df_cart = pd.DataFrame(st.session_state.temp_cart)
            st.table(df_cart)
            
            sub = df_cart['subtotal'].sum()
            itbms = sub * 0.07
            total = sub + itbms + flete

            st.sidebar.metric("Subtotal", f"${sub:.2f}")
            st.sidebar.metric("ITBMS 7%", f"${itbms:.2f}")
            st.sidebar.title(f"TOTAL: ${total:.2f}")

            if st.sidebar.button("🚀 PROCESAR OPERACIÓN"):
                tabla = "ventas" if tipo == "Venta" else "cotizaciones"
                data = {
                    "cliente": cliente, "total": total, "itbms": itbms,
                    "flete": flete, "subtotal": sub, "detalles": json.dumps(st.session_state.temp_cart)
                }
                self.db.insert(tabla, data)
                st.session_state.temp_cart = []
                st.success(f"{tipo} registrada con éxito.")