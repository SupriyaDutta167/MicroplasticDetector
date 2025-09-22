import axios from "axios";

const API_BASE = "http://localhost:8000";

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getLatest = async () => {
  return axios.get(`${API_BASE}/api/latest`);
};

export const getESP32Stats = async () => {
  return axios.get(`${API_BASE}/esp32/stats`);
};

export const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  return `${API_BASE}${imagePath}`;
};
