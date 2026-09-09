from fastapi import APIRouter, Depends, HTTPException
from backend.app.services import InvoiceService
from backend.app.auth import get_current_user

router = APIRouter()

@router.post('/api/v1/invoices/download', response_model=bytes)
async def download_invoice(invoice_id: int, user: dict = Depends(get_current_user), invoice_service: InvoiceService = Depends()):
    try:
        invoice = invoice_service.get_approved_invoice(invoice_id, user['id'])
        # Generate PDF using a library like ReportLab or Dompdf
        pdf_content = generate_pdf(invoice)
        return pdf_content
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail='Internal server error')