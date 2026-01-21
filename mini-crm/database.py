"""
Módulo de gestión de base de datos para el Mini CRM
"""
import sqlite3
from datetime import datetime
import config

def get_connection():
    """Obtiene una conexión a la base de datos"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inicializa la base de datos con todas las tablas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla CLIENTES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            cumple TEXT,
            direccion TEXT,
            google_resource_name TEXT UNIQUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla SERVICIOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servicio TEXT NOT NULL UNIQUE,
            precio_sin_iva REAL NOT NULL,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla CENTROS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS centros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_centro TEXT NOT NULL UNIQUE,
            localidad TEXT NOT NULL
        )
    ''')
    
    # Tabla VENTAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_centro INTEGER NOT NULL,
            id_cliente INTEGER NOT NULL,
            nombre_cliente TEXT NOT NULL,
            telefono_cliente TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_sin_iva REAL NOT NULL,
            total_con_iva REAL NOT NULL,
            total_pagado REAL NOT NULL,
            puntos_fidelidad REAL NOT NULL,
            FOREIGN KEY (id_centro) REFERENCES centros(id),
            FOREIGN KEY (id_cliente) REFERENCES clientes(id)
        )
    ''')
    
    # Tabla intermedia para servicios de cada venta (relación muchos a muchos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas_servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            id_servicio INTEGER NOT NULL,
            precio_sin_iva REAL NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (id_servicio) REFERENCES servicios(id)
        )
    ''')
    
    # Tabla TARJETA DE FIDELIDAD (vista materializada)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarjeta_fidelidad (
            id INTEGER PRIMARY KEY,
            id_cliente INTEGER UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            puntuacion REAL DEFAULT 0,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')
    
    # Índices para mejorar rendimiento
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(id_cliente)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_centro ON ventas(id_centro)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clientes_google ON clientes(google_resource_name)')
    
    conn.commit()
    conn.close()

def insert_servicios_iniciales():
    """Inserta los servicios iniciales desde VIP Car Wash"""
    servicios = [
        # COMBOS
        ("BÁSICO", 150.00),
        ("FULL DETAIL", 250.00),
        ("PREMIUM", 750.00),
        
        # EXTERIOR
        ("Limpieza exterior básica", 50.00),
        ("LIMPIEZA BAJOS", 12.00),
        ("CAPOTA Y MECANISMO", 69.00),
        ("TRATAMIENTO CERÁMICO", 490.00),
        ("CORRECCIÓN PINTURA", 1750.00),
        ("CRISTALES EXTERIOR", 12.00),
        ("CROMADOS", 18.00),
        ("DESCONT. PINTURA", 89.00),
        ("ENCERADO", 85.00),
        ("PULIDO DE FAROS", 99.00),
        ("DETALLADO LLANTAS", 39.00),
        ("MARCOS DE PUERTA", 11.00),
        ("DETALLADO MOTOR", 89.00),
        ("RENOVACIÓN PLÁSTICOS", 39.00),
        ("PULIDO", 799.00),
        ("TECHO PANORÁMICO", 12.00),
        
        # INTERIOR
        ("Limpieza interior básica", 50.00),
        ("ALFOMBRAS", 29.00),
        ("OLOR A COCHE NUEVO", 49.00),
        ("CINTURONES", 19.00),
        ("CRISTALES INTERIOR", 12.00),
        ("CUERO", 160.00),
        ("SILLA INFANTIL", 18.00),
        ("MALETERO", 19.00),
        ("MOQUETAS", 59.00),
        ("OZONO", 59.00),
        ("PELOS MASCOTA", 49.00),
        ("SALPICADERO", 20.00),
        ("TAPICERÍA", 120.00),
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for servicio, precio in servicios:
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO servicios (servicio, precio_sin_iva) VALUES (?, ?)',
                (servicio, precio)
            )
        except sqlite3.IntegrityError:
            pass  # El servicio ya existe
    
    conn.commit()
    conn.close()

def insert_centros_ejemplo():
    """Inserta centros de ejemplo"""
    centros = [
        ("VIP Car Wash Madrid Centro", "Madrid"),
        ("VIP Car Wash Barcelona Norte", "Barcelona"),
        ("VIP Car Wash Valencia Este", "Valencia"),
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for nombre, localidad in centros:
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO centros (nombre_centro, localidad) VALUES (?, ?)',
                (nombre, localidad)
            )
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# Funciones CRUD para CLIENTES
def get_clientes():
    """Obtiene todos los clientes"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def get_cliente_by_id(id_cliente):
    """Obtiene un cliente por su ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()
    return cliente

def insert_cliente(nombre, telefono='', email='', cumple='', direccion='', google_resource_name=None):
    """Inserta un nuevo cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO clientes (nombre, telefono, email, cumple, direccion, google_resource_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, telefono, email, cumple, direccion, google_resource_name))
    
    id_cliente = cursor.lastrowid
    
    # Crear entrada en tarjeta de fidelidad
    cursor.execute('''
        INSERT INTO tarjeta_fidelidad (id_cliente, nombre, puntuacion)
        VALUES (?, ?, 0)
    ''', (id_cliente, nombre))
    
    conn.commit()
    conn.close()
    
    return id_cliente

def update_cliente(id_cliente, nombre, telefono, email, cumple, direccion):
    """Actualiza un cliente existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE clientes 
        SET nombre = ?, telefono = ?, email = ?, cumple = ?, direccion = ?,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (nombre, telefono, email, cumple, direccion, id_cliente))
    
    # Actualizar nombre en tarjeta de fidelidad
    cursor.execute('''
        UPDATE tarjeta_fidelidad 
        SET nombre = ?
        WHERE id_cliente = ?
    ''', (nombre, id_cliente))
    
    conn.commit()
    conn.close()

# Funciones CRUD para SERVICIOS
def get_servicios():
    """Obtiene todos los servicios activos"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servicios WHERE activo = 1 ORDER BY servicio')
    servicios = cursor.fetchall()
    conn.close()
    return servicios

def get_servicio_by_id(id_servicio):
    """Obtiene un servicio por su ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servicios WHERE id = ?', (id_servicio,))
    servicio = cursor.fetchone()
    conn.close()
    return servicio

def insert_servicio(servicio, precio_sin_iva):
    """Inserta un nuevo servicio"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO servicios (servicio, precio_sin_iva)
        VALUES (?, ?)
    ''', (servicio, precio_sin_iva))
    
    id_servicio = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return id_servicio

def update_servicio(id_servicio, servicio, precio_sin_iva):
    """Actualiza un servicio existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE servicios 
        SET servicio = ?, precio_sin_iva = ?
        WHERE id = ?
    ''', (servicio, precio_sin_iva, id_servicio))
    
    conn.commit()
    conn.close()

# Funciones CRUD para CENTROS
def get_centros():
    """Obtiene todos los centros"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM centros ORDER BY nombre_centro')
    centros = cursor.fetchall()
    conn.close()
    return centros

def get_centro_by_id(id_centro):
    """Obtiene un centro por su ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM centros WHERE id = ?', (id_centro,))
    centro = cursor.fetchone()
    conn.close()
    return centro

def insert_centro(nombre_centro, localidad):
    """Inserta un nuevo centro"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO centros (nombre_centro, localidad)
        VALUES (?, ?)
    ''', (nombre_centro, localidad))
    
    id_centro = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return id_centro

# Funciones para VENTAS
def insert_venta(id_centro, id_cliente, servicios_ids, total_con_iva=True):
    """
    Inserta una nueva venta
    
    Args:
        id_centro: ID del centro
        id_cliente: ID del cliente
        servicios_ids: Lista de IDs de servicios
        total_con_iva: Si True, el total pagado incluye IVA
    
    Returns:
        ID de la venta creada
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener datos del cliente
    cursor.execute('SELECT nombre, telefono FROM clientes WHERE id = ?', (id_cliente,))
    cliente = cursor.fetchone()
    nombre_cliente = cliente['nombre']
    telefono_cliente = cliente['telefono']
    
    # Calcular totales
    total_sin_iva = 0
    servicios_data = []
    
    for id_servicio in servicios_ids:
        cursor.execute('SELECT precio_sin_iva FROM servicios WHERE id = ?', (id_servicio,))
        servicio = cursor.fetchone()
        if servicio:
            precio = servicio['precio_sin_iva']
            total_sin_iva += precio
            servicios_data.append((id_servicio, precio))
    
    total_con_iva_calc = total_sin_iva * (1 + config.IVA_RATE)
    total_pagado = total_con_iva_calc if total_con_iva else total_sin_iva
    puntos_fidelidad = total_pagado * config.POINTS_PER_EURO
    
    # Insertar venta
    cursor.execute('''
        INSERT INTO ventas (
            id_centro, id_cliente, nombre_cliente, telefono_cliente,
            total_sin_iva, total_con_iva, total_pagado, puntos_fidelidad
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_centro, id_cliente, nombre_cliente, telefono_cliente,
          total_sin_iva, total_con_iva_calc, total_pagado, puntos_fidelidad))
    
    id_venta = cursor.lastrowid
    
    # Insertar servicios de la venta
    for id_servicio, precio in servicios_data:
        cursor.execute('''
            INSERT INTO ventas_servicios (id_venta, id_servicio, precio_sin_iva)
            VALUES (?, ?, ?)
        ''', (id_venta, id_servicio, precio))
    
    # Actualizar puntos de fidelidad del cliente
    cursor.execute('''
        UPDATE tarjeta_fidelidad
        SET puntuacion = puntuacion + ?,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id_cliente = ?
    ''', (puntos_fidelidad, id_cliente))
    
    conn.commit()
    conn.close()
    
    return id_venta

def get_venta_by_id(id_venta):
    """Obtiene una venta con todos sus detalles"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener datos de la venta
    cursor.execute('''
        SELECT v.*, c.nombre_centro, c.localidad
        FROM ventas v
        JOIN centros c ON v.id_centro = c.id
        WHERE v.id = ?
    ''', (id_venta,))
    venta = cursor.fetchone()
    
    if not venta:
        conn.close()
        return None
    
    # Obtener servicios de la venta
    cursor.execute('''
        SELECT s.servicio, vs.precio_sin_iva
        FROM ventas_servicios vs
        JOIN servicios s ON vs.id_servicio = s.id
        WHERE vs.id_venta = ?
    ''', (id_venta,))
    servicios = cursor.fetchall()
    
    # Obtener puntos de fidelidad del cliente
    cursor.execute('''
        SELECT puntuacion
        FROM tarjeta_fidelidad
        WHERE id_cliente = ?
    ''', (venta['id_cliente'],))
    fidelidad = cursor.fetchone()
    
    conn.close()
    
    return {
        'venta': dict(venta),
        'servicios': [dict(s) for s in servicios],
        'puntos_totales': fidelidad['puntuacion'] if fidelidad else 0
    }

def get_ventas():
    """Obtiene todas las ventas"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, c.nombre_centro
        FROM ventas v
        JOIN centros c ON v.id_centro = c.id
        ORDER BY v.fecha DESC
    ''')
    ventas = cursor.fetchall()
    conn.close()
    return ventas

# Funciones para TARJETA DE FIDELIDAD
def get_tarjeta_fidelidad():
    """Obtiene todas las tarjetas de fidelidad"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tarjeta_fidelidad
        ORDER BY puntuacion DESC
    ''')
    tarjetas = cursor.fetchall()
    conn.close()
    return tarjetas

def get_tarjeta_by_cliente(id_cliente):
    """Obtiene la tarjeta de fidelidad de un cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tarjeta_fidelidad
        WHERE id_cliente = ?
    ''', (id_cliente,))
    tarjeta = cursor.fetchone()
    conn.close()
    return tarjeta

# Funciones de reportes
def get_reporte_ventas_por_centro():
    """Reporte de ventas agrupadas por centro"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            c.nombre_centro,
            c.localidad,
            COUNT(v.id) as total_ventas,
            SUM(v.total_sin_iva) as total_sin_iva,
            SUM(v.total_con_iva) as total_con_iva,
            SUM(v.total_pagado) as total_pagado
        FROM centros c
        LEFT JOIN ventas v ON c.id = v.id_centro
        GROUP BY c.id
        ORDER BY total_pagado DESC
    ''')
    reporte = cursor.fetchall()
    conn.close()
    return reporte

def get_reporte_ventas_por_cliente():
    """Reporte de ventas agrupadas por cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            cl.nombre,
            cl.telefono,
            cl.email,
            COUNT(v.id) as total_ventas,
            SUM(v.total_pagado) as total_pagado,
            tf.puntuacion as puntos_fidelidad
        FROM clientes cl
        LEFT JOIN ventas v ON cl.id = v.id_cliente
        LEFT JOIN tarjeta_fidelidad tf ON cl.id = tf.id_cliente
        GROUP BY cl.id
        ORDER BY total_pagado DESC
    ''')
    reporte = cursor.fetchall()
    conn.close()
    return reporte

def get_reporte_servicios_mas_vendidos():
    """Reporte de servicios más vendidos"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            s.servicio,
            s.precio_sin_iva,
            COUNT(vs.id) as veces_vendido,
            SUM(vs.precio_sin_iva) as total_vendido
        FROM servicios s
        LEFT JOIN ventas_servicios vs ON s.id = vs.id_servicio
        GROUP BY s.id
        ORDER BY veces_vendido DESC, total_vendido DESC
    ''')
    reporte = cursor.fetchall()
    conn.close()
    return reporte

def get_reporte_top_clientes_fidelidad():
    """Reporte de clientes con más puntos de fidelidad"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            tf.nombre,
            cl.telefono,
            cl.email,
            tf.puntuacion,
            COUNT(v.id) as total_compras,
            SUM(v.total_pagado) as total_gastado
        FROM tarjeta_fidelidad tf
        JOIN clientes cl ON tf.id_cliente = cl.id
        LEFT JOIN ventas v ON cl.id = v.id_cliente
        GROUP BY tf.id_cliente
        ORDER BY tf.puntuacion DESC
        LIMIT 50
    ''')
    reporte = cursor.fetchall()
    conn.close()
    return reporte

if __name__ == '__main__':
    # Inicializar base de datos
    init_database()
    insert_servicios_iniciales()
    insert_centros_ejemplo()
    print("Base de datos inicializada correctamente")
