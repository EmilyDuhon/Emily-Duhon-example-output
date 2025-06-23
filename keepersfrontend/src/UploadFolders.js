import React, { useState } from 'react';
import './BatchUploadForm.css';

const BatchUploadForm = ({ onUpload }) => {
  const [referenceFiles, setReferenceFiles] = useState([]);
  const [postCleanFiles, setPostCleanFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (referenceFiles.length !== postCleanFiles.length) {
      alert("Mismatched number of reference and post-clean files.");
      return;
    }

    setLoading(true);
    await onUpload(referenceFiles, postCleanFiles);
    setLoading(false);
  };

  return (
    <div className="batch-form-container">
      <h2>Upload Folders</h2>
      <form onSubmit={handleSubmit}>
        <div className="upload-section">
          <label>Reference Images</label>
          <input
            type="file"
            webkitdirectory="true"
            multiple
            onChange={e => setReferenceFiles([...e.target.files])}
          />
        </div>

        <div className="upload-section">
          <label>Post-clean Images</label>
          <input
            type="file"
            webkitdirectory="true"
            multiple
            onChange={e => setPostCleanFiles([...e.target.files])}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>
    </div>
  );
};

export default BatchUploadForm;
