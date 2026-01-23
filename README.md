# 🚗 Mini CRM - VIP Car Wash

Sistema completo de gestión de relaciones con clientes (CRM) con integración a Google Contacts, programa de fidelidad y generación automática de facturas.

## 📋 Características Principales

### 1. **Gestión de Clientes** 👥
- ✅ Importación automática desde Google Contacts
- ✅ Sincronización bidireccional con Google People API
- ✅ Actualización automática al agregar nuevos contactos en Google
- ✅ Campos: ID, Nombre, Teléfono, Email, Cumpleaños, Dirección

### 2. **Gestión de Ventas** 💰
- ✅ Registro de ventas con múltiples servicios
- ✅ Selección de centro y cliente mediante desplegables
- ✅ Cálculo automático de totales (con/sin IVA 21%)
- ✅ Generación automática de puntos de fidelidad (1 punto / 10€)
- ✅ Factura imprimible y descargable en PDF
- ✅ Campos: ID Venta, Centro, Cliente, Servicios, Fecha, Totales, Puntos

### 3. **Catálogo de Servicios** 🔧
- ✅ 32 servicios predefinidos de VIP Car Wash
- ✅ Gestión completa de servicios (añadir, editar)
- ✅ Precios sin IVA con cálculo automático
- ✅ Categorías: Combos, Exterior, Interior

### 4. **Gestión de Centros** 🏢
- ✅ Múltiples centros de trabajo
- ✅ Registro de localidad para cada centro
- ✅ 3 centros de ejemplo preconfigurados

### 5. **Tarjeta de Fidelidad** ⭐
- ✅ Puntuación automática: 1 punto por cada 10€
- ✅ Acumulación en cada venta
- ✅ Ranking de clientes por puntos
- ✅ Visualización en factura

### 6. **Reportes y Análisis** 📊
- ✅ **Ventas por Centro**: Análisis de rendimiento por ubicación
- ✅ **Ventas por Cliente**: Ranking de mejores clientes
- ✅ **Servicios Más Vendidos**: Popularidad de servicios
- ✅ **Top Fidelidad**: Clientes con más puntos

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.8+ con Flask
- **Base de Datos**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Integración**: Google People API (OAuth 2.0)
- **PDF**: ReportLab
- **Estilos**: CSS personalizado con diseño responsive

## 📦 Instalación

### 1. Requisitos Previos
```bash
python3 --version  # Python 3.8 o superior
pip --version      # pip instalado
```

### 2. Instalación de Dependencias
```bash
cd /home/user/webapp/mini-crm
pip install -r requirements.txt
```

### 3. Configuración de Google API

#### a) Crear Proyecto en Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo o selecciona uno existente
3. Habilita **Google People API**:
   - Menú → APIs & Services → Library
   - Busca "Google People API"
   - Haz clic en "Enable"

#### b) Crear Credenciales OAuth 2.0
1. Menú → APIs & Services → Credentials
2. Click en "Create Credentials" → "OAuth client ID"
3. Tipo de aplicación: "Desktop app"
4. Nombre: "Mini CRM"
5. Descarga el archivo JSON
6. Renómbralo como `credentials.json`
7. Colócalo en: `/home/user/webapp/mini-crm/credentials.json`

#### c) Primera Autenticación
```bash
python3 google_contacts.py
```
Esto abrirá tu navegador para autorizar el acceso. El token se guardará automáticamente.

### 4. Inicializar Base de Datos
```bash
python3 database.py
```
Esto creará:
- Base de datos SQLite
- Todas las tablas
- 32 servicios predefinidos
- 3 centros de ejemplo

## 🚀 Ejecución

### Iniciar el Servidor
```bash
python3 app.py
```

El servidor estará disponible en: **http://localhost:5000**

### Acceso desde Otra Máquina
```bash
python3 app.py
# Accede desde: http://<IP-DEL-SERVIDOR>:5000
```

## 📖 Uso del Sistema

### 1. Sincronizar Contactos de Google
1. Ve a **Clientes** o **Inicio**
2. Click en "Sincronizar con Google"
3. Los contactos se importarán automáticamente
4. La sincronización se puede repetir para actualizar

### 2. Registrar una Venta
1. Ve a **Ventas** → **Nueva Venta**
2. Selecciona el **Centro**
3. Selecciona el **Cliente** (se autocompletan nombre y teléfono)
4. Marca los **Servicios** contratados
5. Elige si cobrar **con IVA o sin IVA**
6. El sistema calcula automáticamente:
   - Total sin IVA
   - IVA (21%)
   - Total con IVA
   - Total a pagar
   - Puntos de fidelidad
7. Click en **Registrar Venta y Generar Factura**

### 3. Generar Factura
Después de registrar la venta:
- Se muestra automáticamente la factura
- Incluye todos los detalles de la venta
- Muestra puntos ganados y totales acumulados
- Opciones:
  - 🖨️ **Imprimir**: Para impresora
  - 📄 **Descargar PDF**: Archivo profesional

### 4. Añadir Servicios
1. Ve a **Servicios** → **Nuevo Servicio**
2. Completa:
   - Nombre del servicio
   - Precio sin IVA
3. El servicio estará disponible inmediatamente

### 5. Añadir Centros
1. Ve a **Centros** → **Nuevo Centro**
2. Completa:
   - Nombre del centro
   - Localidad
3. El centro estará disponible para ventas

### 6. Consultar Reportes
Ve a **Reportes** y selecciona:

- **Ventas por Centro**: Total de ventas e ingresos por ubicación
- **Ventas por Cliente**: Ranking de clientes por volumen de compras
- **Servicios Más Vendidos**: Popularidad de cada servicio
- **Top Fidelidad**: Clientes con más puntos acumulados

## 🗂️ Estructura de la Base de Datos

### Tabla: CLIENTES
```sql
- id (INTEGER PRIMARY KEY)
- nombre (TEXT)
- telefono (TEXT)
- email (TEXT)
- cumple (TEXT)
- direccion (TEXT)
- google_resource_name (TEXT UNIQUE)
- fecha_creacion (TIMESTAMP)
- fecha_actualizacion (TIMESTAMP)
```

### Tabla: SERVICIOS
```sql
- id (INTEGER PRIMARY KEY)
- servicio (TEXT UNIQUE)
- precio_sin_iva (REAL)
- activo (INTEGER)
```

### Tabla: CENTROS
```sql
- id (INTEGER PRIMARY KEY)
- nombre_centro (TEXT UNIQUE)
- localidad (TEXT)
```

### Tabla: VENTAS
```sql
- id (INTEGER PRIMARY KEY)
- id_centro (INTEGER FK)
- id_cliente (INTEGER FK)
- nombre_cliente (TEXT)
- telefono_cliente (TEXT)
- fecha (TIMESTAMP)
- total_sin_iva (REAL)
- total_con_iva (REAL)
- total_pagado (REAL)
- puntos_fidelidad (REAL)
```

### Tabla: VENTAS_SERVICIOS
```sql
- id (INTEGER PRIMARY KEY)
- id_venta (INTEGER FK)
- id_servicio (INTEGER FK)
- precio_sin_iva (REAL)
```

### Tabla: TARJETA_FIDELIDAD
```sql
- id (INTEGER PRIMARY KEY)
- id_cliente (INTEGER UNIQUE FK)
- nombre (TEXT)
- puntuacion (REAL)
- fecha_actualizacion (TIMESTAMP)
```

## ⚙️ Configuración

### Archivo: `config.py`

```python
# IVA
IVA_RATE = 0.21  # 21%

# Puntos de Fidelidad
POINTS_PER_EURO = 0.1  # 1 punto por cada 10€

# Google API Scopes
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
```

## 🎨 Servicios Predefinidos

### COMBOS
- BÁSICO: 150€
- FULL DETAIL: 250€
- PREMIUM: 750€

### EXTERIOR (19 servicios)
- Limpieza exterior básica: 50€
- Limpieza bajos: 12€
- Capota y mecanismo: 69€
- Tratamiento cerámico: 490€
- Corrección pintura: 1750€
- Y más...

### INTERIOR (10 servicios)
- Limpieza interior básica: 50€
- Alfombras: 29€
- Olor a coche nuevo: 49€
- Cuero: 160€
- Ozono: 59€
- Y más...

## 🔒 Seguridad

- ✅ Credenciales OAuth 2.0 para Google API
- ✅ Tokens almacenados localmente
- ✅ Base de datos SQLite con integridad referencial
- ✅ Validación de formularios en cliente y servidor

## 🐛 Solución de Problemas

### Error: "No se encontró credentials.json"
**Solución**: Descarga las credenciales OAuth 2.0 desde Google Cloud Console y colócalas en la raíz del proyecto.

### Error al sincronizar contactos
**Solución**: 
1. Elimina `data/token.json`
2. Ejecuta `python3 google_contacts.py`
3. Vuelve a autorizar en el navegador

### Base de datos bloqueada
**Solución**: 
```bash
rm data/crm.db
python3 database.py
```

### Puerto 5000 en uso
**Solución**: Cambia el puerto en `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 📱 Características Responsive

El sistema es completamente responsive y funciona en:
- 💻 Desktop
- 📱 Tablet
- 📱 Móvil

## 🖨️ Impresión

Las facturas están optimizadas para impresión:
- Oculta navegación y botones
- Formato A4
- Márgenes apropiados
- Colores print-friendly

## 📊 API Endpoints

### Clientes
- `GET /api/clientes` - Lista de clientes
- `GET /api/clientes/<id>` - Cliente específico
- `POST /api/clientes/sync` - Sincronizar con Google

### Servicios
- `GET /api/servicios` - Lista de servicios

### Centros
- `GET /api/centros` - Lista de centros

## 🎯 Funcionalidades Avanzadas

### Cálculo Automático de Puntos
```python
puntos = total_pagado * 0.1  # 1 punto cada 10€
```

### Actualización Automática de Fidelidad
Cada venta actualiza automáticamente:
1. Puntos de la venta
2. Puntos totales del cliente
3. Fecha de última actualización

### Factura PDF Profesional
- Logo y encabezado personalizado
- Tabla de servicios
- Desglose de totales
- Información de fidelidad
- Diseño profesional con colores corporativos

## 👨‍💻 Desarrollo

### Estructura del Proyecto
```
mini-crm/
├── app.py                 # Aplicación Flask principal
├── database.py            # Gestión de base de datos
├── google_contacts.py     # Integración Google API
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── data/
│   ├── crm.db            # Base de datos SQLite
│   └── token.json        # Token Google (generado)
├── static/
│   ├── css/
│   │   └── style.css     # Estilos
│   └── js/
│       └── main.js       # JavaScript
└── templates/
    ├── base.html         # Template base
    ├── index.html        # Página principal
    ├── form_venta.html   # Formulario de ventas
    ├── factura.html      # Factura
    └── ...               # Otros templates
```

## 📝 Licencia

Este proyecto es un sistema personalizado para VIP Car Wash.

## 🤝 Soporte

Para problemas o consultas, contacta con el desarrollador.

---

**Desarrollado con ❤️ para VIP Car Wash**
