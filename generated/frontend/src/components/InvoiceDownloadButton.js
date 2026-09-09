import React from 'react';
import { useNavigate } from 'react-router-dom';

const InvoiceDownloadButton = ({ invoiceId }) => {
  const navigate = useNavigate();

  const handleDownload = () => {
    navigate(`/api/v1/invoices/download?invoiceId=${invoiceId}`, { state: { download: true } });
  };

  return (
    <button onClick={handleDownload}>Download Invoice</button>
  );
};

export default InvoiceDownloadButton;