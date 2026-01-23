#!/bin/bash
# Script de inicio del Mini CRM

echo "🚗 Mini CRM - VIP Car Wash"
echo "=========================="
echo ""

# Verificar que estamos en el directorio correcto
cd "$(dirname "$0")"

# Verificar si la base de datos existe
if [ ! -f "data/crm.db" ]; then
    echo "⚠️  Base de datos no encontrada. Inicializando..."
    python3 database.py
    echo "✅ Base de datos inicializada"
    echo ""
fi

# Verificar dependencias
echo "📦 Verificando dependencias..."
python3 -c "import flask, google.auth, reportlab" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Faltan dependencias. Instalando..."
    pip install -r requirements.txt
    echo "✅ Dependencias instaladas"
    echo ""
fi

# Iniciar servidor
echo "🚀 Iniciando servidor..."
echo "📍 URL: http://localhost:5000"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python3 app.py
