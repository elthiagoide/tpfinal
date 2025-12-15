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
            power_kw REAL DEFAULT 0,
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
            cantidad INTEGER DEFAULT 1,
            delivery_date TEXT,
            precio_unit REAL DEFAULT 0,
            ganancia REAL DEFAULT 0,
            id_impresora INTEGER,
            id_bobina INTEGER,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(id_impresora) REFERENCES impresoras(id),
            FOREIGN KEY(id_bobina) REFERENCES bobinas(id),
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    # Migración: si la columna power_kw no existía en versiones previas, agregarla
    try:
        cursor.execute("PRAGMA table_info(impresoras)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'power_kw' not in cols:
            cursor.execute("ALTER TABLE impresoras ADD COLUMN power_kw REAL DEFAULT 0")
            conn.commit()
    except Exception:
        pass
    # Migración: agregar columnas nuevas en impresiones si faltan
    try:
        cursor.execute("PRAGMA table_info(impresiones)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'cantidad' not in cols:
            cursor.execute("ALTER TABLE impresiones ADD COLUMN cantidad INTEGER DEFAULT 1")
        if 'delivery_date' not in cols:
            cursor.execute("ALTER TABLE impresiones ADD COLUMN delivery_date TEXT")
        if 'precio_unit' not in cols:
            cursor.execute("ALTER TABLE impresiones ADD COLUMN precio_unit REAL DEFAULT 0")
        if 'ganancia' not in cols:
            cursor.execute("ALTER TABLE impresiones ADD COLUMN ganancia REAL DEFAULT 0")
        conn.commit()
    except Exception:
        pass
    conn.close()

    # 5. Tabla Proyectos / Agenda
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos_agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nombre TEXT,
            meta INTEGER,
            materiales TEXT,
            flota TEXT,
            tiempo_hs REAL,
            costo_energia REAL,
            precio_unit REAL DEFAULT 0,
            delivery_date TEXT,
            ganancia REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    # Migración: si la tabla existía sin las columnas nuevas, agregarlas
    try:
        cursor.execute("PRAGMA table_info(proyectos_agenda)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'precio_unit' not in cols:
            cursor.execute("ALTER TABLE proyectos_agenda ADD COLUMN precio_unit REAL DEFAULT 0")
        if 'delivery_date' not in cols:
            cursor.execute("ALTER TABLE proyectos_agenda ADD COLUMN delivery_date TEXT")
        conn.commit()
    except Exception:
        pass
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

def agregar_impresora(nombre, marca, modelo, horas, user_id, power_kw=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO impresoras (nombre, marca, modelo, horas_uso, power_kw, user_id) VALUES (?, ?, ?, ?, ?, ?)", 
                       (nombre, marca, modelo, horas, power_kw, user_id))
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

def actualizar_power_impresora(id_impresora, power_kw):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE impresoras SET power_kw = ? WHERE id = ?", (power_kw, id_impresora))
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

def registrar_impresion(nombre_pieza, peso_usado, tiempo_usado, id_impresora, id_bobina, user_id, cantidad=1, delivery_date=None, precio_unit=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT peso_actual, costo FROM bobinas WHERE id = ?", (id_bobina,))
        bobina = cursor.fetchone()
        if not bobina: return False, "Bobina no encontrada"
        
        peso_actual_bobina, costo_bobina_total = bobina
        if peso_actual_bobina < peso_usado: return False, "No hay suficiente filamento"

        precio_por_gramo = costo_bobina_total / 1000 
        costo_unit = precio_por_gramo * peso_usado
        costo_final = costo_unit * max(1, int(cantidad))

        # Calcular ganancia si el usuario pasó precio_unit
        ingresos = float(precio_unit) * max(1, int(cantidad))
        ganancia = ingresos - costo_final

        cursor.execute("INSERT INTO impresiones (nombre_pieza, costo_final, peso_usado, tiempo_usado, cantidad, delivery_date, precio_unit, ganancia, id_impresora, id_bobina, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (nombre_pieza, costo_final, peso_usado, tiempo_usado, int(cantidad), delivery_date, float(precio_unit), ganancia, id_impresora, id_bobina, user_id))

        cursor.execute("UPDATE bobinas SET peso_actual = peso_actual - ? WHERE id = ?", (peso_usado * max(1, int(cantidad)), id_bobina))
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
               i.cantidad, i.delivery_date, i.precio_unit, i.ganancia,
               imp.nombre, b.marca, b.color
        FROM impresiones i
        LEFT JOIN impresoras imp ON i.id_impresora = imp.id
        LEFT JOIN bobinas b ON i.id_bobina = b.id
        WHERE i.user_id = ?
        ORDER BY i.fecha DESC
    """
    cursor.execute(query, (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos


def guardar_proyecto_agenda(user_id, nombre, meta, materiales_json, flota_json, tiempo_hs, costo_energia, precio_unit=0.0, delivery_date=None, ganancia=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO proyectos_agenda (user_id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, nombre, meta, materiales_json, flota_json, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def obtener_proyectos_agenda(user_id, order_by='fecha_desc'):
    conn = get_connection()
    cursor = conn.cursor()
    # order_by options: fecha_desc, fecha_asc, ganancia_desc, ganancia_asc
    order_clause = 'created_at DESC'
    if order_by == 'fecha_asc':
        order_clause = 'created_at ASC'
    elif order_by == 'ganancia_desc':
        order_clause = 'ganancia DESC'
    elif order_by == 'ganancia_asc':
        order_clause = 'ganancia ASC'
    cursor.execute(f"SELECT id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at FROM proyectos_agenda WHERE user_id = ? ORDER BY {order_clause}", (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos


def contar_proyectos_agenda(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM proyectos_agenda WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def obtener_ultimas_agendas(user_id, limit=3):
    """Devuelve hasta `limit` proyectos ordenados por cercanía a la fecha actual (si tienen delivery_date),
    o por fecha de creación si no hay delivery_date. Incluye proyectos con fechas pasadas si son los más cercanos."""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at
        FROM proyectos_agenda
        WHERE user_id = ?
        ORDER BY CASE WHEN delivery_date IS NULL THEN 1 ELSE 0 END,
                 ABS(julianday(COALESCE(delivery_date, date('now'))) - julianday('now')) ASC
        LIMIT ?
    '''
    cursor.execute(query, (user_id, limit))
    datos = cursor.fetchall()
    conn.close()
    return datos


def obtener_proyecto_agenda(id_proyecto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at FROM proyectos_agenda WHERE id = ?", (id_proyecto,))
    dato = cursor.fetchone()
    conn.close()
    return dato


def eliminar_proyecto_agenda(id_proyecto):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM proyectos_agenda WHERE id = ?", (id_proyecto,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

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


def calcular_ingresos_total(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    # precio_unit * cantidad (si precio_unit o cantidad son NULL, tratarlos como 0/1)
    cursor.execute("SELECT SUM(COALESCE(precio_unit,0) * COALESCE(cantidad,1)) FROM impresiones WHERE user_id = ?", (user_id,))
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado if resultado else 0.0


def calcular_ganancia_total(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(ganancia) FROM impresiones WHERE user_id = ?", (user_id,))
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

def decrementar_peso_bobina(bobina_id, gramos):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE bobinas SET peso_actual = peso_actual - ? WHERE id = ?", (float(gramos), bobina_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def crear_impresion_agregada(nombre_pieza, costo_final, peso_usado, tiempo_usado, cantidad, delivery_date, precio_unit, ganancia, id_impresora, id_bobina, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO impresiones (nombre_pieza, costo_final, peso_usado, tiempo_usado, cantidad, delivery_date, precio_unit, ganancia, id_impresora, id_bobina, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (nombre_pieza, costo_final, peso_usado, tiempo_usado, int(cantidad), delivery_date, float(precio_unit), float(ganancia), id_impresora, id_bobina, user_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

setup_database()