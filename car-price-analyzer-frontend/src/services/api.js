import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status}`);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.status);
    return Promise.reject(error);
  }
);

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const analyzePrice = async (carData) => {
  const response = await api.post('/api/analyze', carData);
  return response.data;
};

export const scrapeListings = async (carData) => {
  const response = await api.post('/api/scrape', carData);
  return response.data;
};

export const getListings = async (marca, model, limit = 50) => {
  const response = await api.get(`/api/listings/${marca}/${model}`, {
    params: { limit }
  });
  return response.data;
};

export const getBrands = async () => {
  const response = await api.get('/api/brands');
  return response.data;
};

export const getEquipment = async () => {
  const response = await api.get('/api/equipment');
  return response.data;
};

// New vehicle API endpoints
export const fetchMakes = async (forceRefresh = false) => {
  const response = await api.get('/api/vehicles/makes', {
    params: { force_refresh: forceRefresh }
  });
  return response.data;
};

export const fetchModels = async (make, year = null, forceRefresh = false) => {
  const params = { force_refresh: forceRefresh };
  if (year) {
    params.year = year;
  }

  const response = await api.get(`/api/vehicles/models/${make}`, { params });
  return response.data;
};

export const fetchVehicleSpecs = async (make, model, year) => {
  const response = await api.get(`/api/vehicles/specs/${make}/${model}`, {
    params: { year }
  });
  return response.data;
};

export const refreshVehicleCache = async () => {
  const response = await api.post('/api/vehicles/refresh-cache');
  return response.data;
};

export default api;