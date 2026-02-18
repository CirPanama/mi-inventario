import streamlit as st
import pandas as pd

class ModuloAdmin:
    def __init__(self, db):
        self.db = db

    def render(self):
        st.header("🛡️ Administración")
        st.subheader("Logs del Sistema")
        logs = self.db.fetch("logs_sistema")
        if logs: st.dataframe(pd.DataFrame(logs))
        
        st.subheader("Perfiles")
        perf = self.db.fetch("perfiles")
        if perf: st.data_editor(pd.DataFrame(perf))