"""
Aplicación principal del Mini CRM
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from datetime import datetime
import database
import google_contacts
import config
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala'

# Inicializar base de datos al iniciar la aplicación
def init_app():
    """Inicializa la base de datos si no existe"""
    if not os.path.exists(config.DATABASE_PATH):
        database.init_database()
        database.insert_servicios_iniciales()
        database.insert_centros_ejemplo()

# Ejecutar inicialización al importar
init_app()

# RUTAS PRINCIPALES
@app.route('/')
def index():
    """Página principal del CRM"""
    return render_template('index.html')

# RUTAS DE CLIENTES
@app.route('/clientes')
def clientes():
    """Lista de clientes"""
    lista_clientes = database.get_clientes()
    return render_template('clientes.html', clientes=lista_clientes)

@app.route('/api/clientes', methods=['GET'])
def api_get_clientes():
    """API para obtener clientes"""
    clientes = database.get_clientes()
    return jsonify([dict(c) for c in clientes])

@app.route('/api/clientes/<int:id>', methods=['GET'])
def api_get_cliente(id):
    """API para obtener un cliente específico"""
    cliente = database.get_cliente_by_id(id)
    if cliente:
        return jsonify(dict(cliente))
    return jsonify({'error': 'Cliente no encontrado'}), 404

@app.route('/api/clientes/sync', methods=['POST'])
def api_sync_clientes():
    """API para sincronizar contactos de Google"""
    try:
        nuevos, actualizados = google_contacts.sync_now()
        return jsonify({
            'success': True,
            'nuevos': nuevos,
            'actualizados': actualizados
        })
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al sincronizar: {str(e)}'
        }), 500

# RUTAS DE SERVICIOS
@app.route('/servicios')
def servicios():
    """Lista de servicios"""
    lista_servicios = database.get_servicios()
    return render_template('servicios.html', servicios=lista_servicios)

@app.route('/servicios/nuevo', methods=['GET', 'POST'])
def nuevo_servicio():
    """Formulario para crear nuevo servicio"""
    if request.method == 'POST':
        servicio = request.form['servicio']
        precio_sin_iva = float(request.form['precio_sin_iva'])
        
        database.insert_servicio(servicio, precio_sin_iva)
        return redirect(url_for('servicios'))
    
    return render_template('form_servicio.html')

@app.route('/api/servicios', methods=['GET'])
def api_get_servicios():
    """API para obtener servicios"""
    servicios = database.get_servicios()
    return jsonify([dict(s) for s in servicios])

# RUTAS DE CENTROS
@app.route('/centros')
def centros():
    """Lista de centros"""
    lista_centros = database.get_centros()
    return render_template('centros.html', centros=lista_centros)

@app.route('/centros/nuevo', methods=['GET', 'POST'])
def nuevo_centro():
    """Formulario para crear nuevo centro"""
    if request.method == 'POST':
        nombre_centro = request.form['nombre_centro']
        localidad = request.form['localidad']
        
        database.insert_centro(nombre_centro, localidad)
        return redirect(url_for('centros'))
    
    return render_template('form_centro.html')

@app.route('/api/centros', methods=['GET'])
def api_get_centros():
    """API para obtener centros"""
    centros = database.get_centros()
    return jsonify([dict(c) for c in centros])

# RUTAS DE VENTAS
@app.route('/ventas')
def ventas():
    """Lista de ventas"""
    lista_ventas = database.get_ventas()
    return render_template('ventas.html', ventas=lista_ventas)

@app.route('/ventas/nueva', methods=['GET', 'POST'])
def nueva_venta():
    """Formulario para crear nueva venta"""
    if request.method == 'POST':
        id_centro = int(request.form['id_centro'])
        id_cliente = int(request.form['id_cliente'])
        servicios_ids = [int(sid) for sid in request.form.getlist('servicios')]
        total_con_iva = request.form.get('total_con_iva', 'true') == 'true'
        
        id_venta = database.insert_venta(id_centro, id_cliente, servicios_ids, total_con_iva)
        
        # Redirigir a la factura
        return redirect(url_for('factura', id=id_venta))
    
    # GET: mostrar formulario
    centros = database.get_centros()
    clientes = database.get_clientes()
    servicios = database.get_servicios()
    
    return render_template('form_venta.html', 
                         centros=centros, 
                         clientes=clientes, 
                         servicios=servicios,
                         iva_rate=config.IVA_RATE * 100)

@app.route('/ventas/<int:id>')
def venta_detalle(id):
    """Detalle de una venta"""
    venta_data = database.get_venta_by_id(id)
    if not venta_data:
        return "Venta no encontrada", 404
    
    return render_template('venta_detalle.html', data=venta_data)

# RUTA DE FACTURA
@app.route('/factura/<int:id>')
def factura(id):
    """Muestra la factura de una venta para impresión"""
    venta_data = database.get_venta_by_id(id)
    if not venta_data:
        return "Venta no encontrada", 404
    
    return render_template('factura.html', data=venta_data, iva_rate=config.IVA_RATE * 100)

@app.route('/factura/<int:id>/pdf')
def factura_pdf(id):
    """Genera y descarga la factura en PDF"""
    venta_data = database.get_venta_by_id(id)
    if not venta_data:
        return "Venta no encontrada", 404
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#d99a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    # Título
    elements.append(Paragraph("FACTURA", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información de la venta
    venta = venta_data['venta']
    info_data = [
        ['Factura Nº:', f"#{venta['id']:06d}"],
        ['Fecha:', datetime.fromisoformat(venta['fecha']).strftime('%d/%m/%Y %H:%M')],
        ['Centro:', venta['nombre_centro']],
        ['Localidad:', venta['localidad']],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Datos del cliente
    elements.append(Paragraph("Datos del Cliente", heading_style))
    cliente_data = [
        ['Nombre:', venta['nombre_cliente']],
        ['Teléfono:', venta['telefono_cliente'] or 'N/A'],
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Servicios
    elements.append(Paragraph("Servicios Contratados", heading_style))
    
    servicios_data = [['Servicio', 'Precio (sin IVA)']]
    for servicio in venta_data['servicios']:
        servicios_data.append([
            servicio['servicio'],
            f"{servicio['precio_sin_iva']:.2f} €"
        ])
    
    servicios_table = Table(servicios_data, colWidths=[4*inch, 2*inch])
    servicios_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d99a1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(servicios_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totales
    totales_data = [
        ['Subtotal (sin IVA):', f"{venta['total_sin_iva']:.2f} €"],
        [f'IVA ({config.IVA_RATE * 100:.0f}%):', f"{venta['total_con_iva'] - venta['total_sin_iva']:.2f} €"],
        ['TOTAL:', f"{venta['total_con_iva']:.2f} €"],
        ['TOTAL PAGADO:', f"{venta['total_pagado']:.2f} €"],
    ]
    
    totales_table = Table(totales_data, colWidths=[4*inch, 2*inch])
    totales_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -2), 'Helvetica'),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTSIZE', (0, -2), (-1, -1), 12),
        ('TEXTCOLOR', (0, -2), (-1, -1), colors.HexColor('#d99a1a')),
        ('LINEABOVE', (0, -2), (-1, -2), 2, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(totales_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Puntos de fidelidad
    elements.append(Paragraph("Programa de Fidelidad", heading_style))
    fidelidad_data = [
        ['Puntos ganados en esta compra:', f"{venta['puntos_fidelidad']:.1f}"],
        ['Puntos totales acumulados:', f"{venta_data['puntos_totales']:.1f}"],
    ]
    
    fidelidad_table = Table(fidelidad_data, colWidths=[4*inch, 2*inch])
    fidelidad_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffacd')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#d99a1a')),
    ]))
    elements.append(fidelidad_table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Enviar archivo
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'factura_{id:06d}.pdf',
        mimetype='application/pdf'
    )

# RUTAS DE TARJETA DE FIDELIDAD
@app.route('/fidelidad')
def fidelidad():
    """Lista de tarjetas de fidelidad"""
    tarjetas = database.get_tarjeta_fidelidad()
    return render_template('fidelidad.html', tarjetas=tarjetas)

# RUTAS DE REPORTES
@app.route('/reportes')
def reportes():
    """Página de reportes"""
    return render_template('reportes.html')

@app.route('/reportes/ventas-por-centro')
def reporte_ventas_centro():
    """Reporte de ventas por centro"""
    reporte = database.get_reporte_ventas_por_centro()
    return render_template('reporte_centros.html', reporte=reporte)

@app.route('/reportes/ventas-por-cliente')
def reporte_ventas_cliente():
    """Reporte de ventas por cliente"""
    reporte = database.get_reporte_ventas_por_cliente()
    return render_template('reporte_clientes.html', reporte=reporte)

@app.route('/reportes/servicios-mas-vendidos')
def reporte_servicios():
    """Reporte de servicios más vendidos"""
    reporte = database.get_reporte_servicios_mas_vendidos()
    return render_template('reporte_servicios.html', reporte=reporte)

@app.route('/reportes/top-fidelidad')
def reporte_top_fidelidad():
    """Reporte de clientes con más puntos de fidelidad"""
    reporte = database.get_reporte_top_clientes_fidelidad()
    return render_template('reporte_fidelidad.html', reporte=reporte)

@app.route('/privacidad')
def privacidad():
    """Página de política de privacidad"""
    return render_template('privacidad.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
