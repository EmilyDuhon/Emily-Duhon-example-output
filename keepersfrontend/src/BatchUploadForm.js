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

  const handleFileSelect = (e, setFiles) => {
    setFiles(Array.from(e.target.files));
  };

  return (
    <div className="batch-form-container">
      <h2>Upload Images</h2>
      <form onSubmit={handleSubmit}>
        <div className="upload-section">
          <label>Reference Images</label>
          <div className="button-group">
            <label className="upload-button">
              Folder
              <input
                type="file"
                webkitdirectory="true"
                mozdirectory="true"
                multiple
                onChange={(e) => handleFileSelect(e, setReferenceFiles)}
              />
            </label>
            <label className="upload-button">
              File
              <input
                type="file"
                multiple
                onChange={(e) => handleFileSelect(e, setReferenceFiles)}
              />
            </label>
          </div>
        </div>

        <div className="upload-section">
          <label>Post-clean Images</label>
          <div className="button-group">
            <label className="upload-button">
              Folder
              <input
                type="file"
                webkitdirectory="true"
                mozdirectory="true"
                multiple
                onChange={(e) => handleFileSelect(e, setPostCleanFiles)}
              />
            </label>
            <label className="upload-button">
              File
              <input
                type="file"
                multiple
                onChange={(e) => handleFileSelect(e, setPostCleanFiles)}
              />
            </label>
          </div>
        </div>

        <submit-button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </submit-button>
      </form>
    </div>
  );
};

export default BatchUploadForm;
