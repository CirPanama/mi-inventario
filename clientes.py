import streamlit as st
import pandas as pd

class ModuloClientes:
    def __init__(self, db):
        self.db = db

    def render(self):
        # Ahora esto NO fallará porque ya lo definimos en el login del main.py
        rol = st.session_state.rol 

        st.header("👥 Gestión de Clientes - CIR")

        # 1. Carga de datos
        clientes = self.db.fetch("clientes")
        
        if clientes:
            df = pd.DataFrame(clientes)
            st.info(f"Total de clientes registrados: {len(df)}")
            
            # 2. Buscador
            busqueda = st.text_input("🔍 Buscar cliente por nombre o RUC/Cédula...", "").lower()
            
            st.divider()

            # 3. Listado en Fichas Estilizadas (Tu formato favorito)
            for c in clientes:
                nombre_c = c['nombre'].lower()
                id_c = str(c.get('identificacion', '')).lower()
                
                if busqueda in nombre_c or busqueda in id_c:
                    with st.container(border=True):
                        col_info, col_contacto, col_acc = st.columns([2.5, 2.5, 1])
                        
                        with col_info:
                            st.subheader(c['nombre'])
                            st.write(f"🆔 **ID/RUC:** {c.get('identificacion', 'N/A')}")
                            st.write(f"📍 **Dirección:** {c.get('direccion', 'S/D')}")
                        
                        with col_contacto:
                            st.markdown("**Datos de Contacto:**")
                            st.write(f"📞 **Teléfono:** {c.get('telefono', 'S/D')}")
                            st.write(f"📧 **Email:** {c.get('email', 'S/D')}")
                        
                        with col_acc:
                            st.write("Acciones")
                            # Aquí se aplicará la lógica que quieres dejar para el final, 
                            # por ahora habilitamos los botones si el rol existe
                            c_edit, c_del = st.columns(2)
                            
                            if c_edit.button("✏️", key=f"ed_cli_{c['id']}"):
                                st.session_state[f"edit_cli_{c['id']}"] = True
                            
                            if c_del.button("🗑️", key=f"del_cli_{c['id']}"):
                                self.db.delete("clientes", c['id'])
                                st.success("Cliente eliminado")
                                st.rerun()

                            # Formulario de edición rápida
                            if st.session_state.get(f"edit_cli_{c['id']}", False):
                                with st.form(f"f_ed_cli_{c['id']}"):
                                    nuevo_tel = st.text_input("Nuevo Teléfono", value=c.get('telefono', ''))
                                    nueva_dir = st.text_input("Nueva Dirección", value=c.get('direccion', ''))
                                    if st.form_submit_button("Guardar Cambios"):
                                        self.db.update("clientes", {"telefono": nuevo_tel, "direccion": nueva_dir}, c['id'])
                                        st.session_state[f"edit_cli_{c['id']}"] = False
                                        st.rerun()

        # 4. Formulario de Registro (Expander inferior)
        st.divider()
        with st.expander("➕ REGISTRAR NUEVO CLIENTE"):
            with st.form("form_nuevo_cliente"):
                f_nom = st.text_input("Nombre Completo / Razón Social")
                f_ruc = st.text_input("RUC o Cédula")
                f_tel = st.text_input("Teléfono de contacto")
                f_dir = st.text_input("Dirección")
                f_ema = st.text_input("Correo Electrónico")
                
                if st.form_submit_button("💾 Guardar Cliente"):
                    if f_nom and f_ruc:
                        self.db.insert("clientes", {
                            "nombre": f_nom,
                            "identificacion": f_ruc,
                            "telefono": f_tel,
                            "direccion": f_dir,
                            "email": f_ema
                        })
                        st.success("¡Cliente registrado!")
                        st.rerun()
                    else:
                        st.error("Nombre e Identificación son obligatorios")