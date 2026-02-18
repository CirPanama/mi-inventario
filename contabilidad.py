import streamlit as st
import pandas as pd

class ModuloContabilidad:
    def __init__(self, db):
        self.db = db

    def render(self):
        st.header("💰 Módulo Contable CIR")
        tab1, tab2, tab3, tab4 = st.tabs(["Caja", "Gastos", "Depósitos", "Recibos"])
        
        with tab1:
            st.dataframe(pd.DataFrame(self.db.fetch("contabilidad")), use_container_width=True)
        with tab2:
            st.dataframe(pd.DataFrame(self.db.fetch("gastos")), use_container_width=True)
        with tab3:
            st.dataframe(pd.DataFrame(self.db.fetch("depositos")), use_container_width=True)
        with tab4:
            st.dataframe(pd.DataFrame(self.db.fetch("recibos")), use_container_width=True)