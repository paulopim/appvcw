"""
Módulo de integración con Google People API para sincronización de contactos
"""
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config
import database

class GoogleContactsSync:
    """Clase para sincronizar contactos con Google People API"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """Autentica con Google usando OAuth 2.0"""
        # El archivo token.json almacena los tokens de acceso y actualización del usuario
        if os.path.exists(config.GOOGLE_TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(
                config.GOOGLE_TOKEN_PATH, 
                config.GOOGLE_SCOPES
            )
        
        # Si no hay credenciales válidas, solicitar al usuario que inicie sesión
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(config.GOOGLE_CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"No se encontró el archivo de credenciales en {config.GOOGLE_CREDENTIALS_PATH}\n"
                        "Por favor, descarga las credenciales OAuth 2.0 de Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.GOOGLE_CREDENTIALS_PATH,
                    config.GOOGLE_SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Guardar las credenciales para la próxima ejecución
            with open(config.GOOGLE_TOKEN_PATH, 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('people', 'v1', credentials=self.creds)
        return True
    
    def get_all_contacts(self, page_size=1000):
        """
        Obtiene todos los contactos de Google
        
        Args:
            page_size: Número de contactos por página
            
        Returns:
            Lista de contactos
        """
        if not self.service:
            self.authenticate()
        
        contacts = []
        next_page_token = None
        
        try:
            while True:
                results = self.service.people().connections().list(
                    resourceName='people/me',
                    pageSize=page_size,
                    pageToken=next_page_token,
                    personFields='names,emailAddresses,phoneNumbers,birthdays,addresses,metadata'
                ).execute()
                
                connections = results.get('connections', [])
                contacts.extend(connections)
                
                next_page_token = results.get('nextPageToken')
                if not next_page_token:
                    break
            
            return contacts
        
        except HttpError as error:
            print(f'Error al obtener contactos: {error}')
            return []
    
    def parse_contact(self, contact):
        """
        Parsea un contacto de Google al formato de nuestra base de datos
        
        Args:
            contact: Contacto de Google People API
            
        Returns:
            Diccionario con los datos del contacto
        """
        parsed = {
            'google_resource_name': contact.get('resourceName', ''),
            'nombre': '',
            'telefono': '',
            'email': '',
            'cumple': '',
            'direccion': ''
        }
        
        # Nombre
        names = contact.get('names', [])
        if names:
            parsed['nombre'] = names[0].get('displayName', '')
        
        # Teléfono
        phones = contact.get('phoneNumbers', [])
        if phones:
            parsed['telefono'] = phones[0].get('value', '')
        
        # Email
        emails = contact.get('emailAddresses', [])
        if emails:
            parsed['email'] = emails[0].get('value', '')
        
        # Cumpleaños
        birthdays = contact.get('birthdays', [])
        if birthdays:
            date = birthdays[0].get('date', {})
            if date:
                year = date.get('year', '')
                month = str(date.get('month', '')).zfill(2)
                day = str(date.get('day', '')).zfill(2)
                if month and day:
                    if year:
                        parsed['cumple'] = f"{year}-{month}-{day}"
                    else:
                        parsed['cumple'] = f"{month}-{day}"
        
        # Dirección
        addresses = contact.get('addresses', [])
        if addresses:
            address = addresses[0]
            parsed['direccion'] = address.get('formattedValue', '')
        
        return parsed
    
    def sync_contacts_to_database(self):
        """
        Sincroniza todos los contactos de Google con la base de datos
        
        Returns:
            Tupla (nuevos, actualizados)
        """
        print("Iniciando sincronización con Google Contacts...")
        
        contacts = self.get_all_contacts()
        print(f"Se encontraron {len(contacts)} contactos en Google")
        
        nuevos = 0
        actualizados = 0
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        for contact in contacts:
            parsed = self.parse_contact(contact)
            
            # Verificar si el nombre está vacío
            if not parsed['nombre']:
                continue
            
            # Verificar si el contacto ya existe
            cursor.execute(
                'SELECT id FROM clientes WHERE google_resource_name = ?',
                (parsed['google_resource_name'],)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar contacto existente
                cursor.execute('''
                    UPDATE clientes
                    SET nombre = ?, telefono = ?, email = ?, cumple = ?, direccion = ?,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE google_resource_name = ?
                ''', (parsed['nombre'], parsed['telefono'], parsed['email'], 
                      parsed['cumple'], parsed['direccion'], parsed['google_resource_name']))
                
                # Actualizar nombre en tarjeta de fidelidad
                cursor.execute('''
                    UPDATE tarjeta_fidelidad
                    SET nombre = ?
                    WHERE id_cliente = ?
                ''', (parsed['nombre'], existing['id']))
                
                actualizados += 1
            else:
                # Insertar nuevo contacto
                cursor.execute('''
                    INSERT INTO clientes (nombre, telefono, email, cumple, direccion, google_resource_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (parsed['nombre'], parsed['telefono'], parsed['email'], 
                      parsed['cumple'], parsed['direccion'], parsed['google_resource_name']))
                
                id_cliente = cursor.lastrowid
                
                # Crear entrada en tarjeta de fidelidad
                cursor.execute('''
                    INSERT INTO tarjeta_fidelidad (id_cliente, nombre, puntuacion)
                    VALUES (?, ?, 0)
                ''', (id_cliente, parsed['nombre']))
                
                nuevos += 1
        
        conn.commit()
        conn.close()
        
        print(f"Sincronización completada: {nuevos} nuevos, {actualizados} actualizados")
        return nuevos, actualizados
    
    def watch_for_changes(self):
        """
        Configura un webhook para recibir notificaciones de cambios
        (Requiere configuración adicional en Google Cloud Console)
        """
        # Esta función requiere:
        # 1. Configurar un dominio verificado en Google Cloud Console
        # 2. Crear un endpoint HTTPS público para recibir notificaciones
        # 3. Implementar el manejo de notificaciones push
        
        # Por simplicidad, se implementa polling manual mediante sync_contacts_to_database()
        pass

def sync_now():
    """Función de utilidad para sincronizar contactos manualmente"""
    sync = GoogleContactsSync()
    sync.authenticate()
    return sync.sync_contacts_to_database()

if __name__ == '__main__':
    # Prueba de sincronización
    sync_now()
