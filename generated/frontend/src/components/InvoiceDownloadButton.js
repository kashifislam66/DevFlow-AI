import React from 'react';
import { Button } from 'antd';

const InvoiceDownloadButton = ({ invoiceId, user }) => {
  const handleDownload = async () => {
    try {
      const response = await fetch(`/api/v1/invoices/download?invoiceId=${invoiceId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'invoice.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Failed to download invoice');
      }
    } catch (error) {
      console.error('Error downloading invoice:', error);
    }
  };

  return (
    <Button type="primary" onClick={handleDownload} disabled={!invoiceId || !user.token}>
      Download Invoice
    </Button>
  );
};

export default InvoiceDownloadButton;

// Example usage:
// <InvoiceDownloadButton invoiceId={invoiceId} user={user} />