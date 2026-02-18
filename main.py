import streamlit as st
import pandas as pd
from database import DBManager
from auth import ModuloAuth
from inventario import ModuloInventario
from ventas import ModuloVentas
from contabilidad import ModuloContabilidad
from admin import ModuloAdmin

st.set_page_config(page_title="CIR PANAMÁ OS", layout="wide")

def main():
    if 'db' not in st.session_state: st.session_state.db = DBManager()
    if 'auth' not in st.session_state: st.session_state.auth = False

    db = st.session_state.db

    if not st.session_state.auth:
        ModuloAuth(db).login()
    else:
        st.sidebar.title(f"Usuario: {st.session_state.user}")
        menu = st.sidebar.radio("Navegación", ["Ventas", "Inventario", "Contabilidad", "Admin"])
        
        if st.sidebar.button("Salir"):
            st.session_state.auth = False
            st.rerun()

        if menu == "Ventas": ModuloVentas(db).render()
        elif menu == "Inventario": ModuloInventario(db).render()
        elif menu == "Contabilidad": ModuloContabilidad(db).render()
        elif menu == "Admin": ModuloAdmin(db).render()

if __name__ == "__main__":
    main()