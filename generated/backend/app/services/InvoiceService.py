from .PDFGeneratorService import PDFGeneratorService

class InvoiceService:
    def __init__(self):
        self.pdf_generator = PDFGeneratorService()

    def download_invoice_pdf(self, invoice_id, user):
        # Assuming we have a method to fetch invoice data based on invoice_id
        invoice_data = self.fetch_invoice_data(invoice_id)
        if invoice_data and self.is_user_authorized(user, invoice_data):
            pdf_content = self.pdf_generator.generate_pdf(invoice_data)
            return pdf_content
        else:
            raise Exception('Unauthorized access')

    def fetch_invoice_data(self, invoice_id):
        # Placeholder for fetching invoice data
        return [{'item': 'Item 1', 'quantity': 1, 'price': 100}, {'item': 'Item 2', 'quantity': 2, 'price': 200}]

    def is_user_authorized(self, user, invoice_data):
        # Placeholder for authorization logic
        return user.vendor_id == invoice_data[0]['vendor_id']

# Example usage:
# invoice_service = InvoiceService()
# pdf_content = invoice_service.download_invoice_pdf(invoice_id, user)
# with open('invoice.pdf', 'wb') as f:
#     f.write(pdf_content)