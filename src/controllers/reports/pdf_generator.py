"""
PDF Generator for Purchase Reports
Generates shopping lists for out-of-stock and low-stock products
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from controllers import list_out_of_stock_products, get_low_stock_products


def generate_purchase_report(threshold=20, output_dir='reports/purchase_reports'):
    """
    Generate PDF purchase report with out-of-stock and low-stock products.
    
    Args:
        threshold: Stock threshold for low stock section
        output_dir: Output directory for PDF
    
    Returns:
        str: Path to generated PDF file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"compras_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF document (Letter size, 1cm margins)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Header
    elements.append(Paragraph("REPORTE DE COMPRAS", title_style))
    elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Get data
    out_of_stock = list_out_of_stock_products() or []
    low_stock = get_low_stock_products(threshold) or []
    
    # Section 1: Out of Stock Products
    elements.append(Paragraph("PRODUCTOS SIN STOCK (0 unidades)", section_style))
    
    if out_of_stock:
        # Table header
        data = [['Producto', 'Código', 'Categoría', 'Stock', 'Cant.', 'Costo']]
        
        # Add products with manual fields
        for product in out_of_stock:
            data.append([
                product.get('name', 'N/A'),
                product.get('barcode', 'N/A'),
                product.get('category_name', 'Sin Categoría'),
                '0',  # Stock is 0 for out-of-stock products
                '',  # Empty cell for manual entry
                ''   # Empty cell for manual entry
            ])
        
        # Create table - full width
        page_width = letter[0] - 2*cm  # Total width minus margins
        table = Table(data, colWidths=[
            page_width * 0.30,  # 30% for product name
            page_width * 0.18,  # 18% for barcode
            page_width * 0.22,  # 22% for category
            page_width * 0.10,  # 10% for stock
            page_width * 0.10,  # 10% for quantity
            page_width * 0.10   # 10% for cost
        ])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Product name left
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),   # Barcode, category left
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'), # Manual fields center
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No hay productos sin stock", styles['Normal']))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Section 2: Low Stock Products
    elements.append(Paragraph(f"PRODUCTOS CON STOCK BAJO (Menos de {threshold})", section_style))
    
    if low_stock:
        # Table header
        data = [['Producto', 'Código', 'Categoría', 'Stock', 'Cant.', 'Costo']]
        
        # Add products with manual fields - EXCLUDE products with 0 stock
        for product in low_stock:
            quantity = product.get('quantity', 0)
            if quantity > 0:  # Only include products with stock > 0
                data.append([
                    product.get('name', 'N/A'),
                    product.get('barcode', 'N/A'),
                    product.get('category_name', 'Sin Categoría'),
                    str(quantity),
                    '',  # Empty cell for manual entry
                    ''   # Empty cell for manual entry
                ])
        
        # Create table - full width
        page_width = letter[0] - 2*cm  # Total width minus margins
        table = Table(data, colWidths=[
            page_width * 0.30,  # 30% for product name
            page_width * 0.18,  # 18% for barcode
            page_width * 0.22,  # 22% for category
            page_width * 0.10,  # 10% for stock
            page_width * 0.10,  # 10% for quantity
            page_width * 0.10   # 10% for cost
        ])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Product name left
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),   # Barcode, category left
            ('ALIGN', (3, 1), (3, -1), 'CENTER'), # Stock center
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'), # Manual fields center
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph(f"No hay productos con stock menor a {threshold}", styles['Normal']))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Summary
    elements.append(Paragraph("RESUMEN", section_style))
    summary_data = [
        ['Total productos sin stock:', str(len(out_of_stock))],
        ['Total productos con stock bajo:', str(len(low_stock))],
        ['Umbral de stock bajo:', f'Menos de {threshold}']
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(summary_table)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Notes section - full width lines
    elements.append(Paragraph("NOTAS:", section_style))
    
    # Create full-width lines for notes
    page_width = letter[0] - 2*cm
    for i in range(5):  # 5 lines for notes
        # Create a table with single cell for full-width line
        note_table = Table([['']], colWidths=[page_width])
        note_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(note_table)
    
    # Build PDF
    doc.build(elements)
    
    return filepath
