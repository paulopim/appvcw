# 📋 Guía de Instalación Rápida - Mini CRM

## Paso 1: Instalación de Dependencias

```bash
cd /home/user/webapp/mini-crm
pip install -r requirements.txt
```

## Paso 2: Configurar Google People API

### A. Crear Proyecto en Google Cloud

1. **Ve a**: https://console.cloud.google.com/
2. **Crea un proyecto nuevo**:
   - Click en selector de proyectos (arriba)
   - Click "Nuevo Proyecto"
   - Nombre: "Mini CRM VIP Car Wash"
   - Click "Crear"

### B. Habilitar Google People API

1. **Menú** → **APIs y Servicios** → **Biblioteca**
2. Busca: "Google People API"
3. Click en "Google People API"
4. Click en **"Habilitar"**

### C. Crear Credenciales OAuth 2.0

1. **Menú** → **APIs y Servicios** → **Credenciales**
2. Click **"Crear credenciales"** → **"ID de cliente de OAuth"**
3. Si aparece mensaje sobre configurar pantalla:
   - Click "Configurar pantalla de consentimiento"
   - Tipo: **Externo**
   - Nombre: "Mini CRM"
   - Email de asistencia: tu-email@gmail.com
   - Click "Guardar y continuar"
   - Ámbitos: Skip (siguiente)
   - Usuarios de prueba: Añade tu email
   - Click "Guardar y continuar"
   
4. Volver a **Credenciales** → **Crear credenciales** → **ID de cliente de OAuth**
5. Tipo de aplicación: **Aplicación de escritorio**
6. Nombre: "Mini CRM Desktop"
7. Click **"Crear"**
8. Click en **"Descargar JSON"**
9. **IMPORTANTE**: Renombra el archivo descargado a: `credentials.json`
10. Colócalo en: `/home/user/webapp/mini-crm/credentials.json`

## Paso 3: Inicializar Base de Datos

```bash
cd /home/user/webapp/mini-crm
python3 database.py
```

Esto creará:
- ✅ Base de datos SQLite en `data/crm.db`
- ✅ Todas las tablas necesarias
- ✅ 32 servicios de VIP Car Wash
- ✅ 3 centros de ejemplo

## Paso 4: Primera Sincronización con Google (Opcional)

```bash
python3 google_contacts.py
```

1. Se abrirá tu navegador automáticamente
2. Inicia sesión con tu cuenta de Google
3. Acepta los permisos (solo lectura de contactos)
4. Se guardará el token en `data/token.json`
5. Los contactos se importarán automáticamente

**Nota**: Si no tienes credenciales de Google aún, puedes omitir este paso. El sistema funcionará sin sincronización de contactos, pero deberás añadir clientes manualmente.

## Paso 5: Iniciar el Servidor

```bash
python3 app.py
```

**El servidor estará en**: http://localhost:5000

## ✅ Verificación de Instalación

1. Abre tu navegador en: http://localhost:5000
2. Deberías ver la página de inicio del Mini CRM
3. Navega por las secciones:
   - 👥 Clientes
   - 🔧 Servicios (verás 32 servicios predefinidos)
   - 🏢 Centros (verás 3 centros de ejemplo)
   - 💰 Ventas → Nueva Venta

## 🎯 Primera Venta de Prueba

1. Ve a **Ventas** → **Nueva Venta**
2. Selecciona un centro
3. Si sincronizaste Google, selecciona un cliente
   - Si no, primero añade un cliente manualmente
4. Marca algunos servicios
5. Click en **"Registrar Venta y Generar Factura"**
6. ¡Verás tu primera factura con puntos de fidelidad!

## 🔧 Solución de Problemas

### Error: "No module named 'flask'"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error: "No se encontró credentials.json"
- Descarga las credenciales desde Google Cloud Console
- Renómbralas exactamente como `credentials.json`
- Colócalas en la raíz del proyecto

### Error: "Puerto 5000 en uso"
Edita `app.py` línea final:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```
Luego accede en: http://localhost:8080

### Base de datos corrupta
```bash
rm data/crm.db
python3 database.py
```

## 📞 Contacto

Si necesitas ayuda adicional, consulta el README.md completo.

---

**¡Listo! Tu Mini CRM está funcionando** 🎉
