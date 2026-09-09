from fastapi import HTTPException
from backend.app.models import Invoice

class InvoiceService:
    def get_approved_invoice(self, invoice_id: int, user_id: int):
        invoice = Invoice.get_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail='Invoice not found')
        if invoice.approved and invoice.vendor_id == user_id:
            return invoice
        raise HTTPException(status_code=403, detail='Unauthorized access')