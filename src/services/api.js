import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000', // adjust to your Django backend
});

// Attach token if available
API.interceptors.request.use((req) => {
  const token = localStorage.getItem('token');
  if (token) req.headers.Authorization = `Bearer ${token}`;
  return req;
});

export const signup = (data) => API.post('/auth/signup/', data);
export const verify = (data) => API.post('/auth/verify/', data);  // optional
export const login = (data) => API.post('/auth/login/', data);
