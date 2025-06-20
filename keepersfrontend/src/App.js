import React, { useState } from 'react';
import BatchUploadForm from './BatchUploadForm';
import ResultGallery from './ResultGallery';
import './App.css';

function App() {
  const [results, setResults] = useState([]);

  const handleBatchUpload = async (refFiles, postFiles) => {
    const formData = new FormData();
    refFiles.forEach(file => formData.append('reference[]', file));
    postFiles.forEach(file => formData.append('postclean[]', file));

    try {
      const response = await fetch('http://localhost:5000/upload-folders', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      const combinedResults = data.results.map((result, i) => ({
        ...result,
        reference: refFiles[i],
        postclean: postFiles[i]
      }));

      setResults(combinedResults);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="logo-section">
          <img src="/logo.png" alt="Keepers Logo" className="App-logo" />
          <h1 className="App-title">Cleaning Inspection</h1>
        </div>
      </header>
      <BatchUploadForm onUpload={handleBatchUpload} />
      {results.length > 0 && <ResultGallery results={results} />}
    </div>
  );
}

export default App;
