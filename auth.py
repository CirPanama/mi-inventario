import streamlit as st
import pandas as pd

class ModuloAuth:
    def __init__(self, db):
        self.db = db

    def login(self):
        st.title("🛡️ CIR PANAMÁ OS")
        with st.container(border=True):
            # Cambiamos la etiqueta para que sea clara
            u = st.text_input("Nombre de Usuario") 
            p = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar", use_container_width=True):
                perfiles = self.db.fetch("perfiles")
                df = pd.DataFrame(perfiles)
                
                # CORRECCIÓN: Usamos 'usuario' en lugar de 'email'
                if not df.empty and 'usuario' in df.columns:
                    if u in df['usuario'].values:
                        st.session_state.auth = True
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("El usuario no existe en la tabla perfiles")
                # Acceso de emergencia
                elif u == "demo" and p == "123":
                    st.session_state.auth = True
                    st.session_state.user = "Admin Local"
                    st.rerun()
                else:
                    st.error("No se pudo conectar con la tabla perfiles o datos incorrectos")