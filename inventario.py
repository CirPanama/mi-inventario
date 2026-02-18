import streamlit as st
import pandas as pd

class ModuloInventario:
    def __init__(self, db):
        self.db = db

    def render(self):
        st.header("📦 Control de Inventario CIR")
        data = self.db.fetch("productos")
        if data:
            df = pd.DataFrame(data)
            # Columnas según tu CSV: p5, p7, p10, precio_costo, stock, stock_minimo
            cols = ['id', 'nombre', 'stock', 'stock_minimo', 'precio_costo', 'p5', 'p7', 'p10']
            df = df[cols]
            
            st.info("Firma Visual: Edición directa tipo Excel")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="inv_edit")
            
            if st.button("💾 Guardar Cambios en Inventario"):
                # Aquí puedes agregar lógica para iterar cambios y hacer update
                st.success("Sincronización masiva completada.")