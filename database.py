import sqlite3
import bcrypt

DB_NAME = "taller3d.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabla Usuarios (MODIFICADA: Agregamos nombre_emprendimiento)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_emprendimiento TEXT
        )
    ''')

    # 2. Impresoras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS impresoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            estado TEXT DEFAULT 'Disponible',
            horas_uso REAL DEFAULT 0,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')
    
    # 3. Bobinas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bobinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            material TEXT NOT NULL,
            color TEXT NOT NULL,
            peso_actual REAL DEFAULT 1000,
            costo REAL DEFAULT 0,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')

    # 4. Impresiones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS impresiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_pieza TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            costo_final REAL,
            peso_usado REAL,
            tiempo_usado REAL,
            id_impresora INTEGER,
            id_bobina INTEGER,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(id_impresora) REFERENCES impresoras(id),
            FOREIGN KEY(id_bobina) REFERENCES bobinas(id),
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    conn.close()

# --- USUARIOS (ACTUALIZADO) ---

def registrar_usuario(username, password, nombre_emprendimiento):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO usuarios (username, password, nombre_emprendimiento) VALUES (?, ?, ?)', 
                       (username, hashed, nombre_emprendimiento))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_usuario(username, password):
    """Devuelve (id, username, nombre_emprendimiento) si es correcto, o None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password, username, nombre_emprendimiento FROM usuarios WHERE username = ?', (username,))
    record = cursor.fetchone()
    conn.close()

    if record:
        user_id, hashed_password, db_user, db_empresa = record
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            # Devolvemos todos los datos necesarios para el perfil
            empresa_final = db_empresa if db_empresa else "Mi Taller 3D"
            return (user_id, db_user, empresa_final)
            
    return None

# --- RESTO DE FUNCIONES (IMPRESORAS, BOBINAS, ETC. IGUAL QUE ANTES) ---

def agregar_impresora(nombre, marca, modelo, horas, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO impresoras (nombre, marca, modelo, horas_uso, user_id) VALUES (?, ?, ?, ?, ?)", 
                       (nombre, marca, modelo, horas, user_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def obtener_impresoras(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM impresoras WHERE user_id = ?", (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def contar_impresoras(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM impresoras WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def eliminar_impresora(id_impresora):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM impresoras WHERE id = ?", (id_impresora,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def agregar_bobina(marca, material, color, peso, costo, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bobinas (marca, material, color, peso_actual, costo, user_id) VALUES (?, ?, ?, ?, ?, ?)", 
                       (marca, material, color, peso, costo, user_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def obtener_bobinas(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bobinas WHERE user_id = ?", (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def contar_bobinas(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bobinas WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def eliminar_bobina(id_bobina):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM bobinas WHERE id = ?", (id_bobina,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def registrar_impresion(nombre_pieza, peso_usado, tiempo_usado, id_impresora, id_bobina, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT peso_actual, costo FROM bobinas WHERE id = ?", (id_bobina,))
        bobina = cursor.fetchone()
        if not bobina: return False, "Bobina no encontrada"
        
        peso_actual_bobina, costo_bobina_total = bobina
        if peso_actual_bobina < peso_usado: return False, "No hay suficiente filamento"

        precio_por_gramo = costo_bobina_total / 1000 
        costo_final = precio_por_gramo * peso_usado

        cursor.execute("INSERT INTO impresiones (nombre_pieza, costo_final, peso_usado, tiempo_usado, id_impresora, id_bobina, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (nombre_pieza, costo_final, peso_usado, tiempo_usado, id_impresora, id_bobina, user_id))

        cursor.execute("UPDATE bobinas SET peso_actual = peso_actual - ? WHERE id = ?", (peso_usado, id_bobina))
        cursor.execute("UPDATE impresoras SET horas_uso = horas_uso + ? WHERE id = ?", (tiempo_usado, id_impresora))

        conn.commit()
        return True, f"Impresión registrada. Costo: ${costo_final:.2f}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def obtener_historial(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT i.id, i.nombre_pieza, i.fecha, i.costo_final, i.peso_usado, 
               imp.nombre, b.marca, b.color
        FROM impresiones i
        JOIN impresoras imp ON i.id_impresora = imp.id
        JOIN bobinas b ON i.id_bobina = b.id
        WHERE i.user_id = ?
        ORDER BY i.fecha DESC
    """
    cursor.execute(query, (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def contar_trabajos(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM impresiones WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def calcular_gasto_total(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(costo_final) FROM impresiones WHERE user_id = ?", (user_id,))
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado if resultado else 0.0

def eliminar_impresion(id_impresion):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM impresiones WHERE id = ?", (id_impresion,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

setup_database()