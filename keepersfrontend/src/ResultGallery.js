import React from 'react';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import './ResultGallery.css';

const ResultGallery = ({ results }) => {
  return (
    <div className="gallery">
      {results.map((res, idx) => (
        <div className="image-row" key={idx}>
          <div className="image-wrapper">
            <p>Reference</p>
            <LazyLoadImage
              effect="blur"
              src={URL.createObjectURL(res.reference)}
              alt="Reference"
              className="gallery-img"
            />
          </div>

          <div className="image-wrapper">
            <p>Post-clean</p>
            <LazyLoadImage
              effect="blur"
              src={URL.createObjectURL(res.postclean)}
              alt="Post-clean"
              className="gallery-img"
            />
          </div>

          <div className="image-wrapper">
            <p>Result</p>
            <LazyLoadImage
              effect="blur"
              src={`http://localhost:5000${res.annotated_image_url}`}
              alt="Annotated"
              className="gallery-img"
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default ResultGallery;
