import sqlite3
import bcrypt

DB_NAME = "taller3d.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Usuarios (Con Avatar)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_emprendimiento TEXT,
            avatar_path TEXT
        )
    ''')

    # 2. Impresoras (Con consumo energético)
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

    # 4. Impresiones (Historial)
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
    
    # 5. Proyectos Agenda (Planificador)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos_agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nombre TEXT,
            meta INTEGER,
            materiales TEXT, -- JSON
            flota TEXT,      -- JSON
            tiempo_hs REAL,
            costo_energia REAL,
            precio_unit REAL DEFAULT 0,
            delivery_date TEXT,
            ganancia REAL DEFAULT 0,
            estado TEXT DEFAULT 'Pendiente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    
    # --- MIGRACIONES AUTOMÁTICAS (Para no romper bases de datos viejas) ---
    try: cursor.execute("ALTER TABLE usuarios ADD COLUMN avatar_path TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE impresoras ADD COLUMN power_kw REAL DEFAULT 0")
    except: pass
    try: cursor.execute("ALTER TABLE impresiones ADD COLUMN ganancia REAL DEFAULT 0")
    except: pass
    try: cursor.execute("ALTER TABLE proyectos_agenda ADD COLUMN estado TEXT DEFAULT 'Pendiente'")
    except: pass
    try: cursor.execute("ALTER TABLE proyectos_agenda ADD COLUMN delivery_date TEXT")
    except: pass
    
    conn.commit()
    conn.close()

# --- USUARIOS ---

def registrar_usuario(username, password, nombre_emprendimiento, avatar_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO usuarios (username, password, nombre_emprendimiento, avatar_path) VALUES (?, ?, ?, ?)', 
                       (username, hashed, nombre_emprendimiento, avatar_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password, username, nombre_emprendimiento, avatar_path FROM usuarios WHERE username = ?', (username,))
    record = cursor.fetchone()
    conn.close()

    if record:
        user_id, hashed_password, db_user, db_empresa, db_avatar = record
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return (user_id, db_user, db_empresa, db_avatar)
    return None

def obtener_todos_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, nombre_emprendimiento, avatar_path FROM usuarios")
    datos = cursor.fetchall()
    conn.close()
    return datos

# --- IMPRESORAS ---

def agregar_impresora(nombre, marca, modelo, horas, user_id, power_kw=0):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO impresoras (nombre, marca, modelo, horas_uso, power_kw, user_id) VALUES (?, ?, ?, ?, ?, ?)", 
                       (nombre, marca, modelo, horas, power_kw, user_id))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def obtener_impresoras(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM impresoras WHERE user_id = ?", (user_id,))
    d = cursor.fetchall()
    conn.close()
    return d

def eliminar_impresora(id_impresora):
    conn = get_connection()
    conn.execute("DELETE FROM impresoras WHERE id = ?", (id_impresora,))
    conn.commit()
    conn.close()

# --- BOBINAS ---

def agregar_bobina(marca, material, color, peso, costo, user_id):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO bobinas (marca, material, color, peso_actual, costo, user_id) VALUES (?, ?, ?, ?, ?, ?)", 
                       (marca, material, color, peso, costo, user_id))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def obtener_bobinas(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bobinas WHERE user_id = ?", (user_id,))
    d = cursor.fetchall()
    conn.close()
    return d

def eliminar_bobina(id_bobina):
    conn = get_connection()
    conn.execute("DELETE FROM bobinas WHERE id = ?", (id_bobina,))
    conn.commit()
    conn.close()

# --- IMPRESIONES & HISTORIAL (Lógica Multi-Material y Energía) ---

def registrar_impresion(nombre_pieza, tiempo, lista_materiales, id_impresora, user_id):
    """
    lista_materiales: [(id_bobina, gramos), (id_bobina, gramos)...]
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        costo_total_material = 0
        peso_total = 0
        
        # 1. Descontar materiales y calcular costo
        for id_bob, peso in lista_materiales:
            cursor.execute("SELECT peso_actual, costo FROM bobinas WHERE id=?", (id_bob,))
            res = cursor.fetchone()
            if res:
                peso_act, costo_rollo = res
                precio_g = costo_rollo / 1000
                costo_total_material += (precio_g * peso)
                peso_total += peso
                
                # Descontar stock
                cursor.execute("UPDATE bobinas SET peso_actual = peso_actual - ? WHERE id=?", (peso, id_bob))

        # 2. Calcular Luz
        cursor.execute("SELECT power_kw FROM impresoras WHERE id=?", (id_impresora,))
        res_imp = cursor.fetchone()
        kw = res_imp[0] if res_imp else 0
        
        # Costo Zona (hardcodeado o importado)
        costo_zona = 100.0 # Precio promedio
        try:
            import config
            costo_zona = getattr(config, 'COSTO_KW_ZONA', 100.0)
        except: pass
        
        costo_luz = kw * tiempo * costo_zona
        costo_final = costo_total_material + costo_luz
        
        # 3. Registrar
        # Usamos la primera bobina como referencia principal
        id_bob_ref = lista_materiales[0][0] if lista_materiales else None
        
        cursor.execute("INSERT INTO impresiones (nombre_pieza, costo_final, peso_usado, tiempo_usado, id_impresora, id_bobina, user_id, fecha, ganancia) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), 0)",
                       (nombre_pieza, costo_final, peso_total, tiempo, id_impresora, id_bob_ref, user_id))
        
        # 4. Sumar horas a impresora
        cursor.execute("UPDATE impresoras SET horas_uso = horas_uso + ? WHERE id=?", (tiempo, id_impresora))
        
        conn.commit()
        return True, f"Registrado!\nCosto Mat: ${costo_total_material:.0f} | Luz: ${costo_luz:.0f}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def obtener_historial(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Join para traer nombres
    q = """
    SELECT i.id, i.nombre_pieza, i.fecha, i.costo_final, i.peso_usado, i.ganancia, 
           imp.nombre, b.marca, b.color
    FROM impresiones i
    LEFT JOIN impresoras imp ON i.id_impresora = imp.id
    LEFT JOIN bobinas b ON i.id_bobina = b.id
    WHERE i.user_id = ? ORDER BY i.fecha DESC
    """
    cursor.execute(q, (user_id,))
    d = cursor.fetchall()
    conn.close()
    return d

def eliminar_impresion(id_impresion):
    conn = get_connection()
    conn.execute("DELETE FROM impresiones WHERE id=?", (id_impresion,))
    conn.commit()
    conn.close()

# --- AGENDA / PLANIFICADOR ---

def guardar_proyecto_agenda(user_id, nombre, meta, mat_json, flota_json, tiempo, costo_e, precio_u, delivery, ganancia):
    conn = get_connection()
    try:
        conn.execute('''
            INSERT INTO proyectos_agenda (
                user_id, nombre, meta, materiales, flota, tiempo_hs, 
                costo_energia, precio_unit, delivery_date, ganancia, estado
            ) VALUES (?,?,?,?,?,?,?,?,?,?, 'Pendiente')
        ''', (user_id, nombre, meta, mat_json, flota_json, tiempo, costo_e, precio_u, delivery, ganancia))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def obtener_proyectos_agenda(user_id, order_by="ORDER BY created_at DESC"):
    conn = get_connection()
    cursor = conn.cursor()
    # Importante: el order_by debe venir sanitizado o controlado desde el código
    q = f"SELECT * FROM proyectos_agenda WHERE user_id=? {order_by}"
    cursor.execute(q, (user_id,))
    d = cursor.fetchall()
    conn.close()
    return d

def obtener_ultimas_agendas(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    # Trae los pendientes más próximos a vencer o recientes
    q = "SELECT * FROM proyectos_agenda WHERE user_id=? AND estado='Pendiente' ORDER BY delivery_date ASC LIMIT ?"
    cursor.execute(q, (user_id, limit))
    d = cursor.fetchall()
    conn.close()
    return d

def eliminar_pedido(id_ped):
    conn = get_connection()
    conn.execute("DELETE FROM proyectos_agenda WHERE id=?", (id_ped,))
    conn.commit()
    conn.close()

# --- ESTADÍSTICAS DASHBOARD ---

def calcular_ingresos_total(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Ganancia + Costo = Ingreso Bruto aproximado (o usar precio venta si existiera columna)
    # Aquí sumamos costo_final + ganancia registrada en impresiones
    cursor.execute("SELECT SUM(costo_final + ganancia) FROM impresiones WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    conn.close()
    return r[0] if r and r[0] else 0

def calcular_gasto_total(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(costo_final) FROM impresiones WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    conn.close()
    return r[0] if r and r[0] else 0

def contar_proyectos_agenda(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM proyectos_agenda WHERE user_id=? AND estado='Pendiente'", (user_id,))
    r = cursor.fetchone()
    conn.close()
    return r[0] if r else 0

def contar_trabajos(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM impresiones WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    conn.close()
    return r[0] if r else 0

def obtener_balance_ultimos_dias(user_id, dias=7):
    conn = get_connection()
    cursor = conn.cursor()
    q = '''
        SELECT strftime('%Y-%m-%d', fecha) as dia, SUM(costo_final), SUM(costo_final+ganancia) 
        FROM impresiones WHERE user_id=? GROUP BY dia ORDER BY dia DESC LIMIT ?
    '''
    cursor.execute(q, (user_id, dias))
    raw = cursor.fetchall()
    conn.close()
    # Invertir para que el gráfico vaya de antiguo a nuevo
    return raw[::-1]

# Inicializar al importar
setup_database()