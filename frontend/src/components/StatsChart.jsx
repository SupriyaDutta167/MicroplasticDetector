import React, { useEffect, useRef } from "react";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const StatsChart = ({ stats }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!stats) return;

    const data = {
      labels: ["Water", "Microplastics"],
      datasets: [
        {
          label: "Composition (%)",
          data: [100 - stats.percent_plastic, stats.percent_plastic],
          backgroundColor: ["#36A2EB", "#FF6384"],
        },
      ],
    };

    const config = { type: "pie", data, options: { responsive: true } };

    const chartInstance = new Chart(chartRef.current, config);
    return () => chartInstance.destroy();
  }, [stats]);

  return (
    <div className="p-3 bg-white rounded shadow-sm mt-3">
      <h5>Solution Composition</h5>
      <canvas ref={chartRef}></canvas>
      <p className="mt-2">
        Microplastics: <strong>{stats?.percent_plastic}%</strong> | Water:{" "}
        <strong>{100 - (stats?.percent_plastic || 0)}%</strong>
      </p>
    </div>
  );
};

export default StatsChart;
