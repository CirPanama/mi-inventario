import streamlit as st
import pandas as pd

class ModuloAuth:
    def __init__(self, db):
        self.db = db

    def login(self):
        st.title("🛡️ CIR PANAMÁ OS")
        with st.container(border=True):
            u = st.text_input("Usuario (Email)")
            p = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", use_container_width=True):
                perfiles = self.db.fetch("perfiles")
                df = pd.DataFrame(perfiles)
                if not df.empty and u in df['email'].values:
                    st.session_state.auth = True
                    st.session_state.user = u
                    st.rerun()
                elif u == "admin" and p == "123":
                    st.session_state.auth = True
                    st.session_state.user = "Admin"
                    st.rerun()
                else:
                    st.error("Acceso denegado")