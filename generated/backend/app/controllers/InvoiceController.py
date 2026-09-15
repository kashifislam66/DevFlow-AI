from fastapi import APIRouter, Depends, HTTPException
from backend.app.models import Vendor
from backend.app.services import InvoiceService
from backend.app.utils.auth import get_current_user

router = APIRouter()

@router.post('/api/v1/invoices/download', response_class=FileResponse)
async def download_invoice(invoice_id: int, user: Vendor = Depends(get_current_user)):
    pdf_content = await InvoiceService.download_invoice_pdf(invoice_id, user)
    return FileResponse(content=pdf_content, filename='invoice.pdf')