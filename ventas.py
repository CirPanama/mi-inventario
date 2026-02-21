import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

class ModuloVentas:
    def __init__(self, db):
        self.db = db

    def generar_pdf(self, datos_venta, cliente_info, num_fact):
        pdf = FPDF()
        pdf.add_page()
        
        # --- ENCABEZADO CIR PANAMÁ ---
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 8, "CIR PANAMÁ", ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, "RUC: 3-716-1500 DV. 97", ln=True, align="C")
        pdf.cell(0, 5, "Ciudad de Colón, Calle 1, Paseo Washington, Edificio 13, Ap. 19 b", ln=True, align="C")
        pdf.cell(0, 5, "TEL: (507) 6865-7082 | Email: hola.cirpanama@gmail.com", ln=True, align="C")
        pdf.ln(10)

        # --- INFO CLIENTE Y FACTURA ---
        pdf.set_font("Arial", "B", 10)
        pdf.cell(100, 6, f"CLIENTE: {cliente_info['nombre'].upper()}", 0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, "FACTURA", 0, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(100, 6, f"ID/RUC: {cliente_info.get('identificacion', 'N/A')}", 0)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, f"FACTURA: {datetime.now().year}-{num_fact:03d}", 0, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(100, 6, "", 0)
        pdf.cell(0, 6, f"FECHA: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, "R")
        pdf.ln(8)

        # --- TABLA DE PRODUCTOS ---
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(90, 8, " Descripcion", 1, 0, "L", True)
        pdf.cell(25, 8, " Cant.", 1, 0, "C", True)
        pdf.cell(35, 8, " Precio", 1, 0, "C", True)
        pdf.cell(35, 8, " Total", 1, 1, "C", True)

        pdf.set_font("Arial", "", 10)
        for item in datos_venta['detalle']:
            pdf.cell(90, 7, f" {item['nombre']}", 1)
            pdf.cell(25, 7, f" {item['cantidad']}", 1, 0, "C")
            pdf.cell(35, 7, f" ${item['precio']:.2f}", 1, 0, "C")
            pdf.cell(35, 7, f" ${item['subtotal']:.2f}", 1, 1, "C")
        
        pdf.ln(5)

        # --- TOTALES (DERECHA) ---
        pdf.set_x(120)
        pdf.cell(40, 7, "SUBTOTAL:", 0)
        pdf.cell(30, 7, f"${datos_venta['subtotal']:.2f}", 0, 1, "R")
        
        pdf.set_x(120)
        pdf.cell(40, 7, "DESCUENTO:", 0)
        pdf.cell(30, 7, f"-${datos_venta['descuento']:.2f}", 0, 1, "R")
        
        pdf.set_x(120)
        pdf.cell(40, 7, "ITBMS (7%):", 0)
        pdf.cell(30, 7, f"${datos_venta['itbms']:.2f}", 0, 1, "R")
        
        pdf.set_x(120)
        pdf.cell(40, 7, "FLETE:", 0)
        pdf.cell(30, 7, f"${datos_venta['flete']:.2f}", 0, 1, "R")
        
        pdf.set_font("Arial", "B", 11)
        pdf.set_x(120)
        pdf.cell(40, 10, "TOTAL:", 0)
        pdf.cell(30, 10, f"${datos_venta['total']:.2f}", 0, 1, "R")

        return pdf.output(dest='S').encode('latin-1')

    def render(self):
        st.header("🛒 Facturación CIR PANAMÁ")
        
        if 'carrito' not in st.session_state: st.session_state.carrito = []
        if 'cliente_sel' not in st.session_state: st.session_state.cliente_sel = None

        # 1. CLIENTE
        with st.container(border=True):
            clientes = self.db.fetch("clientes")
            if clientes:
                df_c = pd.DataFrame(clientes)
                cliente_n = st.selectbox("👤 Seleccionar Cliente", ["Buscar..."] + df_c['nombre'].tolist())
                if cliente_n != "Buscar...":
                    st.session_state.cliente_sel = df_c[df_c['nombre'] == cliente_n].iloc[0].to_dict()
                    st.info(f"Cliente: {st.session_state.cliente_sel['nombre']}")

        # 2. PRODUCTOS Y PRECIOS
        with st.container(border=True):
            productos = self.db.fetch("productos")
            if productos:
                df_p = pd.DataFrame(productos)
                df_p = df_p[df_p['stock'] > 0]
                
                prod_n = st.selectbox("📦 Producto", ["Seleccionar producto..."] + df_p['nombre'].tolist())
                
                if prod_n != "Seleccionar producto...":
                    it = df_p[df_p['nombre'] == prod_n].iloc[0]
                    v_p5, v_p7, v_p10 = float(it.get('p5', 0)), float(it.get('p7', 0)), float(it.get('p10', 0))
                    
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        opciones = {f"P5 (${v_p5:.2f})": v_p5, f"P7 (${v_p7:.2f})": v_p7, f"P10 (${v_p10:.2f})": v_p10}
                        sel_p = st.radio("Nivel de Precio", list(opciones.keys()), horizontal=True)
                        p_final = opciones[sel_p]
                    
                    with c2:
                        cant = st.number_input("Cantidad", min_value=1, max_value=int(it['stock']), value=1)
                    
                    with c3:
                        st.write(" ")
                        if st.button("➕ Añadir"):
                            st.session_state.carrito.append({
                                "id": int(it['id']), "nombre": it['nombre'],
                                "cantidad": int(cant), "precio": p_final,
                                "subtotal": float(cant * p_final)
                            })
                            st.rerun()

        # 3. TOTALES Y GUARDADO
        if st.session_state.carrito:
            df_cart = pd.DataFrame(st.session_state.carrito)
            st.table(df_cart[['nombre', 'cantidad', 'precio', 'subtotal']])
            
            sub_total = df_cart['subtotal'].sum()
            col1, col2 = st.columns(2)
            desc = col1.number_input("Descuento ($)", value=0.0)
            flete = col2.number_input("Flete ($)", value=0.0)
            
            itbms = (sub_total - desc) * 0.07
            total = (sub_total - desc) + itbms + flete
            
            st.metric("TOTAL A PAGAR", f"${total:.2f}")

            if st.button("🚀 CONFIRMAR Y GENERAR PDF", type="primary", use_container_width=True):
                if not st.session_state.cliente_sel:
                    st.error("Seleccione un cliente")
                else:
                    try:
                        # Obtener número factura
                        ventas_db = self.db.fetch("ventas")
                        n_fact = len(ventas_db) + 1 if ventas_db else 1
                        
                        datos = {
                            "cliente": st.session_state.cliente_sel['nombre'],
                            "subtotal": sub_total, "itbms": itbms, "descuento": desc,
                            "flete": flete, "total": total, "num_fact": n_fact,
                            "detalle": st.session_state.carrito, "fecha": datetime.now().isoformat()
                        }
                        
                        # INSERTAR VENTA
                        self.db.insert("ventas", datos)
                        
                        # ACTUALIZAR STOCK (Usando el nuevo fetch con filtros)
                        for item in st.session_state.carrito:
                            p_actual = self.db.fetch("productos", filters={"id": item['id']})[0]
                            nuevo_stock = int(p_actual['stock']) - int(item['cantidad'])
                            self.db.update("productos", {"stock": nuevo_stock}, item['id'])
                        
                        # GENERAR PDF
                        pdf_bytes = self.generar_pdf(datos, st.session_state.cliente_sel, n_fact)
                        st.download_button("📥 Descargar Factura", pdf_bytes, f"Factura_{n_fact}.pdf", "application/pdf")
                        st.success("Venta completada")
                        st.session_state.carrito = []
                        
                    except Exception as e:
                        st.error(f"Error: {e}")