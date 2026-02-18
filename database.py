import streamlit as st
from supabase import create_client

class DBManager:
    def __init__(self):
        self.url = "https://jegxtslswopyixvtuexu.supabase.co"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImplZ3h0c2xzd29weWl4dnR1ZXh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0OTA3MTksImV4cCI6MjA4NjA2NjcxOX0.UXQ3WhR356jObinxJFGdELjuj10BaNnPrD8BrXKdLY0"
        self.supabase = create_client(self.url, self.key)

    def fetch(self, tabla):
        res = self.supabase.table(tabla).select("*").execute()
        return res.data if res.data else []

    def insert(self, tabla, datos):
        return self.supabase.table(tabla).insert(datos).execute()

    def update(self, tabla, datos, id_fila):
        return self.supabase.table(tabla).update(datos).eq("id", id_fila).execute()

    def registrar_log(self, usuario, accion, modulo, detalle):
        log = {
            "usuario": usuario,
            "accion": accion,
            "modulo": modulo,
            "detalle": detalle
        }
        self.insert("logs_sistema", log)