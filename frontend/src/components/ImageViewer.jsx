import React from "react";

const ImageViewer = ({ imageUrl, liveFeed }) => {
  if (!imageUrl) {
    return (
      <div className="image-viewer">
        <div className="no-image">
          <div className="no-image-icon">
            {liveFeed ? '📹' : '🖼️'}
          </div>
          <span>
            {liveFeed 
              ? 'Connecting to live camera feed...' 
              : 'No image uploaded yet'
            }
          </span>
          {!liveFeed && (
            <small style={{ opacity: 0.7, marginTop: '0.5rem' }}>
              Upload an image to start analysis
            </small>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="image-viewer">
      <img 
        src={imageUrl} 
        alt={liveFeed ? "Live Camera Feed" : "Detection Result"}
        onError={(e) => {
          e.target.style.display = 'none';
          e.target.nextSibling.style.display = 'flex';
        }}
      />
      <div 
        className="no-image" 
        style={{ display: 'none' }}
      >
        <div className="no-image-icon">⚠️</div>
        <span>
          {liveFeed 
            ? 'Camera feed unavailable' 
            : 'Failed to load image'
          }
        </span>
      </div>
    </div>
  );
};

export default ImageViewer;