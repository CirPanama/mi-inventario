import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

class ModuloCotizaciones:
    def __init__(self, db):
        self.db = db

    def generar_pdf(self, datos, cliente_info, tipo="COTIZACIÓN"):
        """Genera el PDF con el formato oficial de CIR PANAMÁ"""
        pdf = FPDF()
        pdf.add_page()
        
        # --- ENCABEZADO ---
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 8, "CIR PANAMÁ", ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, "RUC: 3-716-1500 DV. 97", ln=True, align="C")
        pdf.cell(0, 5, "Ciudad de Colón, Calle 1, Paseo Washington, Edificio 13, Ap. 19 b", ln=True, align="C")
        pdf.cell(0, 5, "TEL: (507) 6865-7082 | Email: hola.cirpanama@gmail.com", ln=True, align="C")
        pdf.ln(10)

        # --- INFO CLIENTE Y DOCUMENTO ---
        pdf.set_font("Arial", "B", 10)
        nombre_cli = str(cliente_info.get('nombre', 'CLIENTE GENERAL')).upper()
        pdf.cell(100, 6, f"CLIENTE: {nombre_cli}", 0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, tipo, 0, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        ident = cliente_info.get('identificacion', 'N/A')
        pdf.cell(100, 6, f"ID/RUC: {ident}", 0)
        num_cot = f"{datetime.now().year}-{datos.get('id', 0):03d}"
        pdf.cell(0, 6, f"NÚMERO: {num_cot}", 0, 1, "R")
        pdf.ln(8)

        # --- TABLA DE ITEMS ---
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(90, 8, " Descripcion", 1, 0, "L", True)
        pdf.cell(20, 8, " Cant.", 1, 0, "C", True)
        pdf.cell(35, 8, " Precio", 1, 0, "C", True)
        pdf.cell(35, 8, " Total", 1, 1, "C", True)

        pdf.set_font("Arial", "", 10)
        detalles = datos.get('detalles', [])
        for item in detalles:
            pdf.cell(90, 7, f" {item.get('nombre', 'S/D')}", 1)
            pdf.cell(20, 7, f" {item.get('cantidad', 1)}", 1, 0, "C")
            p_unit = float(item.get('precio', 0))
            pdf.cell(35, 7, f" ${p_unit:.2f}", 1, 0, "C")
            p_sub = float(item.get('subtotal', 0))
            pdf.cell(35, 7, f" ${p_sub:.2f}", 1, 1, "C")
        
        # --- TOTALES ---
        pdf.ln(5)
        pdf.set_x(130)
        total = float(datos.get('total', 0))
        pdf.set_font("Arial", "B", 11)
        pdf.cell(30, 7, "TOTAL:", 0)
        pdf.cell(35, 7, f"${total:.2f}", 0, 1, "R")
        
        return pdf.output(dest='S').encode('latin-1')

    def render(self):
        st.header("📄 Módulo de Cotizaciones")
        tab1, tab2 = st.tabs(["🆕 Crear Cotización", "📂 Historial"])

        with tab1:
            self.vista_crear()
        
        with tab2:
            self.vista_historial()

    def vista_crear(self):
        if 'cart_cot' not in st.session_state:
            st.session_state.cart_cot = []

        # Selector de Cliente
        clientes = self.db.fetch("clientes")
        if not clientes:
            st.warning("⚠️ Debe registrar clientes primero.")
            return

        df_c = pd.DataFrame(clientes)
        cli_sel = st.selectbox("👤 Seleccionar Cliente", df_c['nombre'].tolist())
        cliente_full = df_c[df_c['nombre'] == cli_sel].iloc[0].to_dict()

        # Selector de Ítems
        with st.container(border=True):
            tipo_item = st.radio("Tipo de Ítem:", ["Producto Inventario", "Manual / Mano de Obra"], horizontal=True)
            
            if tipo_item == "Producto Inventario":
                prods = self.db.fetch("productos")
                if prods:
                    df_p = pd.DataFrame(prods)
                    p_sel = st.selectbox("Producto", df_p['nombre'].tolist())
                    item_p = df_p[df_p['nombre'] == p_sel].iloc[0]
                    
                    c1, c2, c3 = st.columns([2, 1, 1])
                    precio_op = c1.radio("Precio", [f"P5: {item_p['p5']}", f"P7: {item_p['p7']}", f"P10: {item_p['p10']}"], horizontal=True)
                    valor_p = float(precio_op.split(": ")[1])
                    cant = c2.number_input("Cantidad", min_value=1, value=1)
                    if c3.button("➕ Añadir"):
                        st.session_state.cart_cot.append({
                            "id": item_p['id'], "nombre": item_p['nombre'], 
                            "cantidad": cant, "precio": valor_p, "subtotal": cant * valor_p, "tipo": "producto"
                        })
                        st.rerun()
            else:
                c1, c2, c3 = st.columns([2, 1, 1])
                desc = c1.text_input("Descripción del servicio")
                monto = c2.number_input("Monto $", min_value=0.0)
                if c3.button("🔧 Añadir Servicio"):
                    st.session_state.cart_cot.append({
                        "id": None, "nombre": desc, "cantidad": 1, 
                        "precio": monto, "subtotal": monto, "tipo": "manual"
                    })
                    st.rerun()

        # Mostrar Carrito y Guardar
        if st.session_state.cart_cot:
            st.table(pd.DataFrame(st.session_state.cart_cot)[['nombre', 'cantidad', 'precio', 'subtotal']])
            total_cot = sum(i['subtotal'] for i in st.session_state.cart_cot)
            
            if st.button("💾 Guardar y Generar PDF"):
                payload = {
                    "cliente": cli_sel,
                    "total": total_cot,
                    "detalles": st.session_state.cart_cot,
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "estado": "Pendiente"
                }
                res = self.db.insert("cotizaciones", payload)
                st.success("Cotización Guardada")
                
                pdf_bytes = self.generar_pdf(payload, cliente_full)
                st.download_button("📥 Descargar PDF", pdf_bytes, f"Cotizacion_{cli_sel}.pdf", "application/pdf")
                st.session_state.cart_cot = []

    def vista_historial(self):
        cots = self.db.fetch("cotizaciones")
        if not cots:
            st.info("No hay cotizaciones registradas.")
            return

        for c in cots:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                # Manejo seguro de nulos para evitar el error de formato
                v_total = float(c.get('total', 0) if c.get('total') is not None else 0)
                v_cliente = c.get('cliente', 'Desconocido')
                
                col1.write(f"**Cliente:** {v_cliente}")
                col1.caption(f"📅 Fecha: {c.get('fecha', 'S/F')}")
                
                col2.write(f"Total: **${v_total:.2f}**")
                col2.write(f"Estado: `{c.get('estado', 'Pendiente')}`")
                
                # Botón de PDF en historial
                try:
                    pdf_h = self.generar_pdf(c, {"nombre": v_cliente})
                    col3.download_button("📥 PDF", pdf_h, f"Cot_{c.get('id')}.pdf", key=f"btn_{c.get('id')}")
                except Exception as e:
                    col3.error("Error PDF")

                if c.get('estado') == "Pendiente":
                    if col3.button("🚀 Facturar", key=f"fact_{c.get('id')}"):
                        self.convertir_a_factura(c)

    def convertir_a_factura(self, cot):
        # Lógica para mover a ventas y descontar stock
        try:
            nueva_venta = {
                "cliente": cot['cliente'],
                "total": cot['total'],
                "detalles": cot['detalles'],
                "fecha": datetime.now().isoformat()
            }
            self.db.insert("ventas", nueva_venta)
            
            # Descontar stock solo de productos de inventario
            for item in cot['detalles']:
                if item['id'] is not None:
                    p = self.db.fetch("productos", filters={"id": item['id']})[0]
                    self.db.update("productos", {"stock": p['stock'] - item['cantidad']}, item['id'])
            
            self.db.update("cotizaciones", {"estado": "Facturado"}, cot['id'])
            st.success("✅ ¡Cotización convertida en factura con éxito!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al facturar: {e}")