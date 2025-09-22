import React from "react";

const LiveFeed = ({ feedUrl }) => {
  return (
    <div className="p-3 bg-white rounded shadow-sm text-center">
      <h5>ESP32 Live Feed</h5>
      <img
        src={feedUrl}
        alt="ESP32 Live Feed"
        className="img-fluid rounded"
        style={{ maxHeight: "400px" }}
      />
    </div>
  );
};

export default LiveFeed;
