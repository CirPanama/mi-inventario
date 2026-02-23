import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

class ModuloInventario:
    def __init__(self, db):
        self.db = db

    def generar_pdf_inventario(self, datos):
        """Genera HTML para impresión (Tu código actual)"""
        fecha_actual = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
        filas = ""
        total_valor = 0
        productos_bajos = 0
        
        for p in datos:
            actual = int(p.get('stock') or 0) 
            minimo = int(p.get('stock_minimo') or 0)
            precio = float(p.get('precio_venta') or 0)
            subtotal = actual * precio
            total_valor += subtotal
            
            estilo_stock = 'color: red; font-weight: bold;' if actual <= minimo else ''
            if actual <= minimo: productos_bajos += 1
            
            filas += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('barcode', 'S/B')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('nombre', 'N/A')}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center; {estilo_stock}">{actual}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{minimo}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${precio:,.2f}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${subtotal:,.2f}</td>
            </tr>
            """

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <h2 style="text-align: center; color: #004A99; border-bottom: 2px solid #004A99;">CIR PANAMÁ - REPORTE DE INVENTARIO</h2>
            <p>Generado: {fecha_actual} | <b>Alertas: {productos_bajos} productos</b></p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead style="background: #f2f2f2;">
                    <tr>
                        <th style="border: 1px solid #ddd; padding: 8px;">Barcode</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Producto</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Stock</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Min.</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Precio</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>{filas}</tbody>
            </table>
            <h3 style="text-align: right;">Valor Total en Bodega: ${total_valor:,.2f}</h3>
        </div>
        <script>window.print();</script>
        """
        return html

    def render(self):
        st.header("📦 Inventario CIR")
        
       # --- SECCIÓN DE REGISTRO DE PRODUCTO CON CÁLCULOS P5, P7, P10 ---
        with st.expander("➕ Registrar Nuevo Producto", expanded=False):
            with st.form("form_nuevo_producto", clear_on_submit=True):
                col1, col2 = st.columns(2)
                nombre = col1.text_input("Nombre del Producto")
                barcode = col2.text_input("Código de Barras (Barcode)")
                
                c1, c2, c3 = st.columns(3)
                costo = c1.number_input("Costo de Compra ($)", min_value=0.0, format="%.2f")
                stock = c2.number_input("Stock Inicial", min_value=0, step=1)
                s_min = c3.number_input("Stock Mínimo", min_value=0, step=1)

                st.markdown("---")
                st.write("💡 **Sugerencias de Precio (Margen CIR):**")
                
                # Cálculos automáticos
                p5 = costo * 1.05
                p7 = costo * 1.07
                p10 = costo * 1.10
                
                cp1, cp2, cp3 = st.columns(3)
                cp1.info(f"**P5 (5%):** ${p5:.2f}")
                cp2.info(f"**P7 (7%):** ${p7:.2f}")
                cp3.info(f"**P10 (10%):** ${p10:.2f}")
                
                precio_final = st.number_input("Precio de Venta Final ($)", min_value=0.0, format="%.2f", help="Puedes usar una de las sugerencias arriba")
                
                submit = st.form_submit_button("Guardar Producto", use_container_width=True)
                
                if submit:
                    if nombre and precio_final > 0:
                        nuevo_p = {
                            "nombre": nombre,
                            "barcode": barcode,
                            "costo": costo, # Guardamos el costo para reportes de utilidad
                            "stock": stock,
                            "stock_minimo": s_min,
                            "precio_venta": precio_final
                        }
                        self.db.insert("productos", nuevo_p)
                        st.success(f"✅ {nombre} registrado con éxito.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Debes ingresar nombre y precio de venta.")

        # --- SECCIÓN DE INGRESO/ACTUALIZACIÓN DE STOCK ---
        with st.expander("📥 Ingreso de Productos", expanded=False):
            productos = self.db.fetch("productos")
            if not productos:
                st.info("No hay productos registrados aún.")
            else:
                with st.form("form_ingreso_producto", clear_on_submit=True):
                    # map display strings a objetos
                    prod_map = {f"{p.get('nombre','')} ({p.get('barcode','')})": p for p in productos}
                    seleccion = st.selectbox("Seleccione Producto", list(prod_map.keys()))
                    cantidad = st.number_input("Cantidad a ingresar", min_value=1, step=1)
                    submit_ing = st.form_submit_button("Actualizar Stock", use_container_width=True)
                    if submit_ing:
                        prod = prod_map.get(seleccion)
                        if prod:
                            actual = int(prod.get('stock') or 0)
                            nuevo = actual + cantidad
                            self.db.update("productos", {"stock": nuevo}, prod.get('id'))
                            st.success(f"🔄 Stock de {prod.get('nombre')} actualizado a {nuevo}.")
                            st.rerun()

        # --- SECCIÓN DE VISTA Y BÚSQUEDA ---
        productos = self.db.fetch("productos")
        
        col_bus, col_print = st.columns([3, 1])
        
        with col_print:
            if st.button("🖨️ Reporte", use_container_width=True, type="primary"):
                if productos:
                    st.session_state.print_inv = self.generar_pdf_inventario(productos)

        query = col_bus.text_input("🔍 Buscar por nombre o barcode...").lower()

        if productos:
            bajos = [p for p in productos if int(p.get('stock') or 0) <= int(p.get('stock_minimo') or 0)]
            if bajos:
                st.error(f"⚠️ {len(bajos)} productos necesitan reposición.")

            st.divider()

            for p in productos:
                nombre_p = str(p.get('nombre', '')).lower()
                barcode_p = str(p.get('barcode', '')).lower()
                
                if query in nombre_p or query in barcode_p:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        
                        stock_actual = int(p.get('stock') or 0)
                        stock_min = int(p.get('stock_minimo') or 0)
                        icono = "🔴" if stock_actual <= stock_min else "🟢"
                        
                        c1.write(f"{icono} **{p.get('nombre', 'S/N')}**")
                        c1.caption(f"Barcode: {p.get('barcode', 'N/A')} | Mín: {stock_min}")
                        
                        c2.write(f"Stock: `{stock_actual}`")
                        c2.write(f"Precio: `${float(p.get('precio_venta') or 0):.2f}`")
                        
                        with c3:
                            st.button("📝 Editar", key=f"btn_inv_{p.get('id')}")

        # Ejecutor de impresión
        if "print_inv" in st.session_state:
            components.html(st.session_state.print_inv, height=0, width=0)
            del st.session_state.print_inv