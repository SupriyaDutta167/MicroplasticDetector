import React, { useState } from "react";

const UploadForm = ({ onUpload }) => {
  const [file, setFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (file && onUpload) {
      onUpload(file);
      setFile(null);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-3 bg-white rounded shadow-sm d-flex gap-2 align-items-center">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
        className="form-control"
      />
      <button type="submit" className="btn btn-primary">
        Upload Image
      </button>
    </form>
  );
};

export default UploadForm;
