import React, { useState } from 'react';

import axios from 'axios';

function UploadFolders() {
  const [referenceFiles, setReferenceFiles] = useState([]);
  const [postcleanFiles, setPostcleanFiles] = useState([]);

  const handleReferenceChange = (e) => {
    const files = Array.from(e.target.files);
    console.log("Reference folder files:", files);
    setReferenceFiles(files);
  };

  const handlePostcleanChange = (e) => {
    const files = Array.from(e.target.files);
    console.log("Postclean folder files:", files);
    setPostcleanFiles(files);
  };

  const handleSubmit = async () => {
    if (referenceFiles.length !== postcleanFiles.length) {
      alert("Mismatch in number of reference and postclean images");
      return;
    }

    for (let i = 0; i < referenceFiles.length; i++) {
      const formData = new FormData();
      formData.append("reference", referenceFiles[i]);
      formData.append("postclean", postcleanFiles[i]);

      try {
        const res = await axios.post("http://localhost:5000/inspect", formData);
        console.log("Annotated image:", res.data.annotated_image_url);
      } catch (err) {
        console.error("Failed to inspect pair:", err);
      }
    }
  };

  return (
    <div>
      <h2>Upload Reference Folder</h2>
      <input
        type="file"
        multiple
        webkitdirectory="true"
        directory=""
        onChange={handleReferenceChange}
      />

      <h2>Upload Post-Clean Folder</h2>
      <input
        type="file"
        multiple
        webkitdirectory="true"
        directory=""
        onChange={handlePostcleanChange}
      />

      <button onClick={handleSubmit}>Submit for Inspection</button>
    </div>
  );
}

export default UploadFolders;
