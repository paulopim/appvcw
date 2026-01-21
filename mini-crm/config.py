"""
Configuración del Mini CRM
"""
import os

# Configuración de la base de datos
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'crm.db')

# Configuración de Google API
# Para obtener las credenciales:
# 1. Ve a https://console.cloud.google.com/
# 2. Crea un proyecto nuevo
# 3. Habilita Google People API
# 4. Crea credenciales OAuth 2.0
# 5. Descarga el archivo JSON y guárdalo como 'credentials.json'
GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
GOOGLE_TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'data', 'token.json')

# Scopes necesarios para Google People API
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

# Configuración de impuestos
IVA_RATE = 0.21  # 21%

# Configuración de puntos de fidelidad
POINTS_PER_EURO = 0.1  # 1 punto por cada 10€
