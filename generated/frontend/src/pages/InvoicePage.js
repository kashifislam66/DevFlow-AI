import React, { useState, useEffect } from 'react';
import InvoiceDownloadButton from '../components/InvoiceDownloadButton';

const InvoicePage = ({ invoiceId, user }) => {
  const [invoiceData, setInvoiceData] = useState(null);

  useEffect(() => {
    // Placeholder for fetching invoice data
    const fetchInvoiceData = async () => {
      const response = await fetch(`/api/v1/invoices/${invoiceId}`);
      if (response.ok) {
        const data = await response.json();
        setInvoiceData(data);
      }
    };

    fetchInvoiceData();
  }, [invoiceId]);

  return (
    <div>
      <h1>Invoice Details</h1>
      <pre>{JSON.stringify(invoiceData, null, 2)}</pre>
      <InvoiceDownloadButton invoiceId={invoiceId} user={user} />
    </div>
  );
};

export default InvoicePage;

// Example usage:
// <InvoicePage invoiceId={invoiceId} user={user} />