from fastapi import HTTPException
from backend.app.models import Invoice, Vendor
from backend.app.utils.pdf_generator import generate_invoice_pdf

async def download_invoice_pdf(invoice_id: int, user: Vendor):
    invoice = await Invoice.get_or_none(id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail='Invoice not found')
    if invoice.vendor_id != user.id:
        raise HTTPException(status_code=403, detail='Unauthorized access')
    pdf_content = generate_invoice_pdf(invoice)
    return pdf_content