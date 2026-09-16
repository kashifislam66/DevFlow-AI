from reportlab.pdfgen import canvas
import os

def generate_invoice_pdf(invoice_id):
    pdf_path = f'/tmp/invoice_{invoice_id}.pdf'
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, f'Invoice ID: {invoice_id}')
    c.save()
    return pdf_path