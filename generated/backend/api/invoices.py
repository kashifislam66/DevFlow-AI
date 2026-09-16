from flask import Flask, request, jsonify, send_file
from backend.services.pdf_generator import generate_invoice_pdf
from backend.services.auth import check_auth

app = Flask(__name__)

@app.route('/api/invoices/<int:invoice_id>/pdf', methods=['GET'])
def download_invoice_pdf(invoice_id):
    if not check_auth(request.headers.get('Authorization')):
        return jsonify({'error': 'Unauthorized'}), 401

    pdf_path = generate_invoice_pdf(invoice_id)
    if pdf_path:
        return send_file(pdf_path, as_attachment=True, download_name=f'invoice_{invoice_id}.pdf')
    else:
        return jsonify({'error': 'Invoice not found'}), 404