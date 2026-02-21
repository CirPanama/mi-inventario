import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

class ModuloInventario:
    def __init__(self, db):
        self.db = db

    def generar_pdf_inventario(self, datos):
        """Genera HTML para impresión"""
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
        productos = self.db.fetch("productos")
        
        col_bus, col_print = st.columns([3, 1])
        
        with col_print:
            if st.button("🖨️ Reporte", use_container_width=True, type="primary"):
                if productos:
                    st.session_state.print_inv = self.generar_pdf_inventario(productos)

        query = col_bus.text_input("🔍 Buscar por nombre o barcode...").lower()

        if productos:
            # Sección de Alertas Rápidas
            bajos = [p for p in productos if int(p.get('stock') or 0) <= int(p.get('stock_minimo') or 0)]
            if bajos:
                st.error(f"⚠️ {len(bajos)} productos necesitan reposición.")

            st.divider()

            # --- LISTADO DE PRODUCTOS ---
            for p in productos:
                # Búsqueda segura y normalizada
                nombre_p = str(p.get('nombre', '')).lower()
                barcode_p = str(p.get('barcode', '')).lower()
                
                if query in nombre_p or query in barcode_p:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        
                        stock = int(p.get('stock') or 0)
                        s_min = int(p.get('stock_minimo') or 0)
                        icono = "🔴" if stock <= s_min else "🟢"
                        
                        c1.write(f"{icono} **{p.get('nombre', 'S/N')}**")
                        c1.caption(f"Barcode: {p.get('barcode', 'N/A')} | Mín: {s_min}")
                        
                        c2.write(f"Stock: `{stock}`")
                        c2.write(f"Precio: `${float(p.get('precio_venta') or 0):.2f}`")
                        
                        with c3:
                            # Botón con key única para evitar colisiones
                            st.button("📝 Editar", key=f"btn_inv_{p.get('id')}")

        # Ejecutor de impresión
        if "print_inv" in st.session_state:
            components.html(st.session_state.print_inv, height=0, width=0)
            del st.session_state.print_inv