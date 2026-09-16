import React from 'react';
import { Button } from 'antd';

const InvoiceDownload = ({ invoiceId }) => {
  const handleDownload = () => {
    window.open(`/api/invoices/${invoiceId}/pdf`, '_blank');
  };

  return (
    <Button type='primary' onClick={handleDownload}>Download PDF</Button>
  );
};

export default InvoiceDownload;