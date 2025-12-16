import sqlite3
import random
import bcrypt
from datetime import datetime, timedelta

# Configuración
DB_NAME = "taller3d.db"
USUARIO_OBJETIVO = "asd" # <--- Tu usuario

def sembrar_inteligente():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print(f"🔍 Buscando usuario '{USUARIO_OBJETIVO}'...")

    # 1. Obtener ID del usuario
    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (USUARIO_OBJETIVO,))
    user_data = cursor.fetchone()

    if not user_data:
        print(f"❌ El usuario '{USUARIO_OBJETIVO}' no existe. Creándolo...")
        # Crear usuario si no existe
        hashed = bcrypt.hashpw("asd".encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO usuarios (username, password, nombre_emprendimiento) VALUES (?, ?, ?)", 
                       (USUARIO_OBJETIVO, hashed, "Taller ASD"))
        conn.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user_data[0]
        print(f"✅ Usuario encontrado (ID: {user_id})")

    # 2. Obtener una Impresora válida
    cursor.execute("SELECT id FROM impresoras WHERE user_id = ?", (user_id,))
    imp_data = cursor.fetchone()
    
    if not imp_data:
        print("⚠️ No tienes impresoras. Creando una 'Ender 3 Pro' de prueba...")
        cursor.execute("INSERT INTO impresoras (nombre, marca, modelo, horas_uso, user_id) VALUES (?, ?, ?, ?, ?)",
                       ("Ender de Prueba", "Creality", "Ender 3", 0, user_id))
        imp_id = cursor.lastrowid
    else:
        imp_id = imp_data[0]

    # 3. Obtener una Bobina válida
    cursor.execute("SELECT id FROM bobinas WHERE user_id = ?", (user_id,))
    bob_data = cursor.fetchone()
    
    if not bob_data:
        print("⚠️ No tienes bobinas. Creando 'PLA Generico' de prueba...")
        cursor.execute("INSERT INTO bobinas (marca, material, color, peso_actual, costo, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                       ("Generico", "PLA", "Gris", 1000, 20000, user_id))
        bob_id = cursor.lastrowid
    else:
        bob_id = bob_data[0]

    # 4. Insertar Historial (La parte divertida)
    print(f"🌱 Sembrando 15 trabajos para el usuario {USUARIO_OBJETIVO}...")
    
    piezas = ["Soporte Celular", "Llavero Team", "Caja Raspberry", "Maceta Groot", "Engranaje"]
    
    for i in range(10): # Últimos 10 días
        fecha_simulada = datetime.now() - timedelta(days=i)
        fecha_str = fecha_simulada.strftime("%Y-%m-%d %H:%M:%S")
        
        # Insertar entre 1 y 3 trabajos por día
        for _ in range(random.randint(1, 3)):
            nombre = random.choice(piezas)
            peso = random.uniform(30, 150)
            tiempo = random.uniform(1, 5)
            
            # Costos
            costo_final = peso * 25 # $25 por gramo aprox
            
            # Ganancia (Simulamos que cobraste el triple del costo)
            precio_venta = costo_final * 3 
            ganancia = precio_venta - costo_final

            query = '''
            INSERT INTO impresiones 
            (nombre_pieza, costo_final, peso_usado, tiempo_usado, cantidad, delivery_date, precio_unit, ganancia, id_impresora, id_bobina, user_id, fecha) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            cursor.execute(query, (
                nombre, 
                costo_final, 
                peso, 
                tiempo, 
                1, # Cantidad
                fecha_str, # Delivery date (mismo día)
                precio_venta, 
                ganancia, 
                imp_id, 
                bob_id, 
                user_id, 
                fecha_str # FECHA REAL DEL REGISTRO
            ))

    conn.commit()
    conn.close()
    print("\n✅ ¡LISTO! Datos inyectados correctamente.")
    print("👉 CIERRA el programa si lo tenías abierto y ábrelo de nuevo.")

if __name__ == "__main__":
    sembrar_inteligente()