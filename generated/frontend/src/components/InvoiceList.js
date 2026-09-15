import React from 'react';
import { useInvoices } from '../hooks/useInvoices';

const InvoiceList = () => {
  const { invoices } = useInvoices();

  const handleDownload = (invoiceId) => {
    fetch(`/api/v1/invoices/download?invoice_id=${invoiceId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'invoice.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      });
  };

  return (
    <div>
      {invoices.map(invoice => (
        <div key={invoice.id}>
          <h3>{invoice.title}</h3>
          <button onClick={() => handleDownload(invoice.id)}>Download PDF</button>
        </div>
      ))}
    </div>
  );
};

export default InvoiceList;