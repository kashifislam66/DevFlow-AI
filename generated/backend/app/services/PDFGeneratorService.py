from fpdf import FPDF

class PDFGeneratorService:
    def generate_pdf(self, invoice_data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 12)
        for item in invoice_data:
            pdf.cell(200, 10, txt = item, ln = True)
        return pdf.output(dest='S')

# Example usage:
# pdf_content = PDFGeneratorService().generate_pdf(invoice_data)
# with open('invoice.pdf', 'wb') as f:
#     f.write(pdf_content)