from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from datetime import datetime
from utils import ruta_recurso
import os

def generar_vale(data, filename="vale.pdf", generar_pdf=True):
    if not generar_pdf:
        return  # No generar PDF si está deshabilitado

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'titulo',
        parent=styles['Title'],
        fontSize=18,
        alignment=1,  # Centrado
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )

    subtitulo_style = ParagraphStyle(
        'subtitulo',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=1,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'normal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8
    )

    firma_style = ParagraphStyle(
        'firma',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=5
    )

    contenido = []

    # ENCABEZADO PROFESIONAL
    contenido.append(Spacer(1, 20))

    # Logo si existe
    logo_path = ruta_recurso("img/logo.png")  # Cambia esto por tu logo


    self.setStyleSheet(f"""
        QWidget {{
            background-image: url({logo_path});
            background-repeat: no-repeat;
            background-position: center;
        }}
    """)
    
    if os.path.exists(logo_path):
        img = Image(logo_path, 2*inch, 1*inch)
        img.hAlign = 'CENTER'
        contenido.append(img)
        contenido.append(Spacer(1, 10))

    contenido.append(Paragraph("SCCO - SISTEMA DE CONTROL DE CILINDROS", titulo_style))
    contenido.append(Paragraph("VALE DE MOVIMIENTO", subtitulo_style))
    contenido.append(Spacer(1, 20))

    # FECHA Y NÚMERO
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    contenido.append(Paragraph(f"Fecha de emisión: {fecha_actual}", normal_style))

    if "Guía" in data:
        contenido.append(Paragraph(f"Número de guía: {data['Guía']}", normal_style))
    if "N° Documento" in data:
        contenido.append(Paragraph(f"N° Documento: {data['N° Documento']}", normal_style))
    contenido.append(Spacer(1, 15))

    # TABLA CON INFORMACIÓN PRINCIPAL
    table_data = [
        ["Tipo de Movimiento:", data.get("Tipo", "N/A")],
        ["Fecha del Movimiento:", data.get("Fecha", "N/A")],
        ["Transportista:", data.get("Transportista", "N/A")],
        ["Registrado por:", data.get("Registrado por", "N/A")],
    ]

    # Agregar campos específicos según el tipo
    if "Cilindro" in data:
        table_data.append(["Código de Cilindro:", data["Cilindro"]])

    if "Material" in data:
        table_data.append(["Material:", data["Material"]])

    if "Área" in data:
        table_data.append(["Área:", data["Área"]])

    if "Encargado" in data:
        table_data.append(["Encargado Almacén:", data["Encargado"]])

    if "Responsable" in data:
        table_data.append(["Responsable Área:", data["Responsable"]])

    table = Table(table_data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    contenido.append(table)
    contenido.append(Spacer(1, 30))

    # OBSERVACIONES
    contenido.append(Paragraph("Observaciones:", styles['Heading4']))
    contenido.append(Paragraph("________________________________________________________________________________", normal_style))
    contenido.append(Paragraph("________________________________________________________________________________", normal_style))
    contenido.append(Spacer(1, 20))

    # FIRMAS
    firmas_data = [
        ["______________________________", "______________________________"],
        ["Encargado de Almacén", "Responsable del Área"],
        ["Fecha: ____/____/________", "Fecha: ____/____/________"],
        ["Nombre: ____________________", "Nombre: ____________________"],
        ["Firma: _____________________", "Firma: _____________________"]
    ]

    firmas_table = Table(firmas_data, colWidths=[3*inch, 3*inch])
    firmas_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    contenido.append(firmas_table)
    contenido.append(Spacer(1, 20))

    # PIE DE PÁGINA
    contenido.append(Paragraph("Documento generado automáticamente por el Sistema SCCO", firma_style))
    contenido.append(Paragraph("Este vale es válido únicamente con las firmas correspondientes", firma_style))

    doc.build(contenido)