// src/services/api.js
import axios from 'axios';

// Base URL dinámica por entorno
const baseURL =
  import.meta.env.MODE === 'development'
    ? 'http://localhost:5000/api'
    : 'https://crewaiapp-production.up.railway.app/api'; // tu backend en Railway

// Crear instancia de axios
const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Variable para almacenar token JWT en memoria
let jwtToken = null;

// Establecer token
export function setAuthToken(token) {
  jwtToken = token;
  localStorage.setItem('jwtToken', token);
}

// Cargar token al iniciar
export function loadAuthToken() {
  const storedToken = localStorage.getItem('jwtToken');
  if (storedToken) {
    jwtToken = storedToken;
  }
}

// Cerrar sesión
export function clearAuthToken() {
  jwtToken = null;
  localStorage.removeItem('jwtToken');
}

// Incluir token en headers
api.interceptors.request.use(
  (config) => {
    if (jwtToken) {
      config.headers.Authorization = `Bearer ${jwtToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Manejo global de errores (ej. 401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('Token expirado o sesión no válida');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// -------------------- AGENTES --------------------

export const fetchAgents = async () => {
  const res = await api.get('/agents');
  return res.data;
};

export const createAgent = async (agent) => {
  const res = await api.post('/agents', agent);
  return res.data;
};

export const updateAgent = async (agentId, agent) => {
  const res = await api.put(`/agents/${agentId}`, agent);
  return res.data;
};

export const deleteAgent = async (agentId) => {
  const res = await api.delete(`/agents/${agentId}`);
  return res.data;
};

// -------------------- HERRAMIENTAS --------------------

export const fetchTools = async () => {
  const res = await api.get('/tools');
  return res.data;
};

export const createTool = async (tool) => {
  const res = await api.post('/tools', tool);
  return res.data;
};

export const updateTool = async (toolId, tool) => {
  const res = await api.put(`/tools/${toolId}`, tool);
  return res.data;
};

export const deleteTool = async (toolId) => {
  const res = await api.delete(`/tools/${toolId}`);
  return res.data;
};

// -------------------- CHAT --------------------

export const fetchChats = async (agentId) => {
  const res = await api.get(`/agents/${agentId}/chats`);
  return res.data;
};

export const deleteChats = async (agentId) => {
  const res = await api.delete(`/agents/${agentId}/chats`);
  return res.data;
};

export const sendMessage = async (agentId, message) => {
  const res = await api.post(`/chat/${agentId}`, { message });
  return res.data;
};

// -------------------- AUTENTICACIÓN --------------------

export const loginUser = async (credentials) => {
  const res = await api.post('/login', credentials);
  const data = res.data;

  if (data.token) {
    setAuthToken(data.token);
  }

  return data;
};
