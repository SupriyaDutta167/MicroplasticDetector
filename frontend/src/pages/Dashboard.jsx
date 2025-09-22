import { useEffect, useState } from "react";
import { uploadImage, getLatest, getESP32Stats, getImageUrl } from "../api/api";
import StatsPanel from "../components/StatsPanel";
import ImageViewer from "../components/ImageViewer";
import "./Dashboard.css";

const Dashboard = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [latestData, setLatestData] = useState(null);
  const [liveFeed, setLiveFeed] = useState(false);
  const [espStats, setEspStats] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState(null);
  const [liveResults, setLiveResults] = useState(null);

  // Your PC's IP address
  const PC_IP = "10.190.245.191";

  // 🔊 Load beep sound
  const beep = new Audio("/beep.mp3");

  // Poll latest detection stats every 2s (for upload mode)
  useEffect(() => {
    const interval = setInterval(() => {
      if (!liveFeed) {
        getLatest().then((res) => {
          if (res.data?.imageUrl) {
            res.data.imageUrl = getImageUrl(res.data.imageUrl);
          }
          setLatestData(res.data);

          // Update upload results when new data comes in
          if (res.data && (res.data.imageUrl || res.data.stats)) {
            setUploadResults(res.data);

            // 🚨 Check poor quality on upload
            if (res.data.stats?.percent_plastic > 10) {
              beep.play();
              setTimeout(() => beep.play(), 500);
            }
          }
        }).catch(err => {
          console.error('Error fetching latest data:', err);
        });
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [liveFeed]);

  // Poll ESP32 (or phone camera) stats if live feed
  useEffect(() => {
    const interval = setInterval(() => {
      if (liveFeed) {
        getESP32Stats().then((res) => {
          const total = res.data.water_ml + res.data.objects;
          const percent_water = total > 0 ? (res.data.water_ml / total) * 100 : 0;
          const percent_plastic = total > 0 ? (res.data.objects / total) * 100 : 0;
          const statsData = {
            ...res.data,
            percent_water,
            percent_plastic,
          };
          setEspStats(statsData);
          // Update live results
          setLiveResults({
            stats: statsData,
            imageUrl: `http://${PC_IP}:8000/esp32/video_feed`
          });

          // 🚨 Check poor quality on live feed
          if (percent_plastic > 10) {
            beep.play();
            setTimeout(() => beep.play(), 500);
          }
        }).catch(err => {
          console.error('Error fetching ESP32 stats:', err);
        });
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [liveFeed, PC_IP]);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    // Clear previous upload results when new file is selected
    setUploadResults(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setUploadResults(null); // Clear previous results
    try {
      await uploadImage(selectedFile);
      // The polling effect will pick up the new results
      setSelectedFile(null);
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
    } finally {
      setIsUploading(false);
    }
  };

  const toggleMode = () => {
    const newMode = !liveFeed;
    setLiveFeed(newMode);
    
    // Clear results when switching modes
    if (newMode) {
      setUploadResults(null);
    } else {
      setLiveResults(null);
    }
    
    // Clear selected file when switching to live mode
    if (newMode) {
      setSelectedFile(null);
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
    }
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="header">
        <h1 className="title">🔬 Microplastic Detector</h1>
        <p className="subtitle">Advanced water quality analysis and microplastic detection</p>
      </div>

      {/* Toggle Controls */}
      <div className="toggle-controls">
        <div className="toggle-container">
          <span className={`toggle-label ${!liveFeed ? 'active' : ''}`}>
            📤 Upload Mode
          </span>
          <label className="toggle-switch">
            <input 
              type="checkbox" 
              checked={liveFeed} 
              onChange={toggleMode}
            />
            <span className="toggle-slider"></span>
          </label>
          <span className={`toggle-label ${liveFeed ? 'active' : ''}`}>
            📹 Live Mode
          </span>
        </div>
      </div>

      {/* Pages Container */}
      <div className="pages-container">
        <div className={`pages-wrapper ${liveFeed ? 'live-mode' : ''}`}>
          
          {/* Upload Page */}
          <div className="page upload-page">
            <div className="upload-section">
              <div className="upload-text">
                <h2 className="page-title">📤 Upload & Analyze</h2>
                <p className="page-description">
                  Upload an image of water sample to detect microplastics
                </p>
              </div>
              
              <div className="file-input-container">
                <input
                  id="file-input"
                  type="file"
                  className="file-input"
                  onChange={handleFileChange}
                  accept="image/*"
                  disabled={isUploading}
                />
                <label 
                  htmlFor="file-input" 
                  className={`file-input-label ${selectedFile ? 'file-selected' : ''}`}
                >
                  <div className="file-icon">
                    {selectedFile ? '✅' : '📁'}
                  </div>
                  <div style={{ textAlign: 'center', fontSize: '0.75rem' }}>
                    {selectedFile ? (
                      <>
                        <strong style={{ fontSize: '0.7rem' }}>
                          {selectedFile.name.length > 12 
                            ? selectedFile.name.substring(0, 12) + '...' 
                            : selectedFile.name}
                        </strong>
                        <div style={{ fontSize: '0.6rem', opacity: 0.7, marginTop: '0.2rem' }}>
                          Click to change
                        </div>
                      </>
                    ) : (
                      <>
                        <strong>Choose Image File</strong>
                        <div style={{ fontSize: '0.6rem', opacity: 0.7, marginTop: '0.2rem' }}>
                          Drag & drop or click to browse
                        </div>
                      </>
                    )}
                  </div>
                </label>
              </div>
              
              <button
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                className={`upload-button ${isUploading ? 'loading' : ''}`}
              >
                {isUploading ? '' : '🚀 Start Analysis'}
              </button>
            </div>

            {/* Upload Results */}
            {uploadResults && (
              <div className="results-section">
                <div className="result-card">
                  <h3 className="result-title">🖼️ Analysis Result</h3>
                  <ImageViewer
                    imageUrl={uploadResults.imageUrl}
                    liveFeed={false}
                  />
                </div>
                <div className="result-card">
                  <h3 className="result-title">📊 Detection Stats</h3>
                  <StatsPanel 
                    stats={uploadResults.stats} 
                    isLive={false}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Live Feed Page */}
          <div className="page live-page">
            <div className="live-header">
              <div>
                <h2 className="page-title">📹 Live Camera Feed</h2>
                <p className="page-description">
                  Real-time microplastic detection from camera stream
                </p>
              </div>
              <div className="live-indicator">
                <div className="live-dot"></div>
                Live Feed Active
              </div>
            </div>

            {/* Live Results */}
            <div className="results-section">
              <div className="result-card">
                <h3 className="result-title">📹 Live Stream</h3>
                <ImageViewer
                  imageUrl={`http://${PC_IP}:8000/esp32/video_feed`}
                  liveFeed={true}
                />
              </div>
              <div className="result-card">
                <h3 className="result-title">📊 Real-time Stats</h3>
                <StatsPanel 
                  stats={espStats} 
                  isLive={true}
                />
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;
