import streamlit as st
from supabase import create_client

class DBManager:
    def __init__(self):
        # Mantenemos tus credenciales actuales
        self.url = "https://jegxtslswopyixvtuexu.supabase.co"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImplZ3h0c2xzd29weWl4dnR1ZXh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0OTA3MTksImV4cCI6MjA4NjA2NjcxOX0.UXQ3WhR356jObinxJFGdELjuj10BaNnPrD8BrXKdLY0"
        self.supabase = create_client(self.url, self.key)

    def fetch(self, tabla, filters=None):
        """
        Trae datos de una tabla. 
        Soporta filtros opcionales para buscar registros específicos.
        """
        try:
            query = self.supabase.table(tabla).select("*")
            
            # Si se pasan filtros (como el ID del producto en ventas), se aplican aquí
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            res = query.execute()
            return res.data if res.data else []
        except Exception as e:
            st.error(f"Error al obtener datos de {tabla}: {e}")
            return []

    def insert(self, tabla, datos):
        """Inserta datos y maneja errores básicos."""
        try:
            return self.supabase.table(tabla).insert(datos).execute()
        except Exception as e:
            st.error(f"Error al insertar en {tabla}: {e}")
            raise e

    def update(self, tabla, datos, id_fila):
        """Actualiza un registro filtrando por su ID."""
        try:
            return self.supabase.table(tabla).update(datos).eq("id", id_fila).execute()
        except Exception as e:
            st.error(f"Error al actualizar en {tabla}: {e}")
            raise e

    def delete(self, tabla, id_fila):
        """Elimina un registro filtrando por su ID."""
        try:
            return self.supabase.table(tabla).delete().eq("id", id_fila).execute()
        except Exception as e:
            st.error(f"Error al eliminar en {tabla}: {e}")
            raise e

    def get_user(self, username):
        """Método optimizado para el login."""
        try:
            res = self.supabase.table("usuarios").select("*").eq("username", username).execute()
            return res.data[0] if res.data else None
        except Exception:
            return None