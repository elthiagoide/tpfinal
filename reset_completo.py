import sqlite3
import bcrypt
import random
import os
from datetime import datetime, timedelta

DB_FILE = "taller3d.db"

def resetear_todo():
    # 1. Borrar DB vieja si existe para evitar conflictos
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print("🗑️ Base de datos vieja eliminada.")
        except:
            print("⚠️ No se pudo borrar el archivo (quizás está en uso). Ciérralo e intenta de nuevo.")
            return

    # 2. Conexión nueva (crea el archivo)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print("✨ Creando estructura de base de datos nueva...")

    # --- TABLAS (Estructura Final) ---
    cursor.execute('''CREATE TABLE usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, nombre_emprendimiento TEXT)''')
    
    cursor.execute('''CREATE TABLE impresoras (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, marca TEXT, modelo TEXT, estado TEXT DEFAULT 'Disponible', horas_uso REAL DEFAULT 0, power_kw REAL DEFAULT 0.3, user_id INTEGER)''')
    
    cursor.execute('''CREATE TABLE bobinas (id INTEGER PRIMARY KEY AUTOINCREMENT, marca TEXT, material TEXT, color TEXT, peso_actual REAL DEFAULT 1000, costo REAL, user_id INTEGER)''')

    cursor.execute('''CREATE TABLE impresiones (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_pieza TEXT, fecha TIMESTAMP, costo_final REAL, peso_usado REAL, tiempo_usado REAL, cantidad INTEGER, delivery_date TEXT, precio_unit REAL, ganancia REAL, id_impresora INTEGER, id_bobina INTEGER, user_id INTEGER)''')
    
    cursor.execute('''CREATE TABLE pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, descripcion TEXT, fecha_entrega TEXT, estado TEXT DEFAULT 'Pendiente', precio_estimado REAL, id_impresora INTEGER, user_id INTEGER)''') # Antes se llamaba 'proyectos_agenda'

    # --- DATOS DE PRUEBA ---
    print("🌱 Sembrando datos para usuario 'asd'...")
    
    # Usuario
    hashed = bcrypt.hashpw("asd".encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO usuarios (username, password, nombre_emprendimiento) VALUES (?, ?, ?)", 
                   ("asd", hashed, "Taller ASD"))
    uid = cursor.lastrowid

    # Impresoras
    impresoras = [("Bambu X1", "Bambu Lab", "X1C", 0.35), ("Ender 3", "Creality", "V2", 0.3)]
    imp_ids = []
    for n, m, mod, kw in impresoras:
        cursor.execute("INSERT INTO impresoras (nombre, marca, modelo, power_kw, user_id) VALUES (?, ?, ?, ?, ?)", (n, m, mod, kw, uid))
        imp_ids.append(cursor.lastrowid)

    # Bobinas
    bobinas = [("Grilon", "PLA", "Rojo", 20000), ("Printalot", "PETG", "Negro", 22000)]
    bob_ids = []
    for mar, mat, col, cos in bobinas:
        cursor.execute("INSERT INTO bobinas (marca, material, color, costo, user_id) VALUES (?, ?, ?, ?, ?)", (mar, mat, col, cos, uid))
        bob_ids.append(cursor.lastrowid)

    # Historial (Últimos 10 días para el gráfico)
    for i in range(15):
        fecha = (datetime.now() - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d %H:%M:%S")
        imp = random.choice(imp_ids)
        bob = random.choice(bob_ids)
        costo = random.randint(500, 3000)
        ganancia = costo * 1.5
        
        cursor.execute('''INSERT INTO impresiones (nombre_pieza, fecha, costo_final, ganancia, id_impresora, id_bobina, user_id) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (f"Pieza_{i}", fecha, costo, ganancia, imp, bob, uid))

    # Agenda (Pendientes)
    fechas_futuras = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)]
    cursor.execute("INSERT INTO pedidos (cliente, descripcion, fecha_entrega, estado, user_id) VALUES (?, ?, ?, ?, ?)", 
                   ("Juan Perez", "Soporte Auricular", fechas_futuras[0], "Pendiente", uid))
    cursor.execute("INSERT INTO pedidos (cliente, descripcion, fecha_entrega, estado, user_id) VALUES (?, ?, ?, ?, ?)", 
                   ("Empresa X", "50 Llaveros", fechas_futuras[1], "Pendiente", uid))

    conn.commit()
    conn.close()
    print("✅ ¡LISTO! Base de datos regenerada correctamente.")
    print("👉 Ejecuta ahora main.py e inicia sesión con: asd / asd")

if __name__ == "__main__":
    resetear_todo()