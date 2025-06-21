// src/services/api.js
import axios from 'axios';

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: 'https://crewaiapp-production.up.railway.app',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Variable para almacenar el token en memoria
let jwtToken = null;

// Función para establecer el token JWT (memoria + localStorage)
export function setAuthToken(token) {
  jwtToken = token;
  localStorage.setItem('jwtToken', token);
}

// Función para cargar token desde localStorage al iniciar app
export function loadAuthToken() {
  const storedToken = localStorage.getItem('jwtToken');
  if (storedToken) {
    jwtToken = storedToken;
  }
}

// Función para cerrar sesión
export function clearAuthToken() {
  jwtToken = null;
  localStorage.removeItem('jwtToken');
}

// Interceptor para incluir el token JWT en cada request
api.interceptors.request.use(
  (config) => {
    if (jwtToken) {
      config.headers.Authorization = `Bearer ${jwtToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores globales (ej. 401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('Token expirado o sesión no válida');
      // Aquí puedes redirigir o mostrar un mensaje
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// -------------------- AGENTES --------------------

export async function fetchAgents() {
  const res = await api.get('/agents');
  return res.data;
}

export async function createAgent(agent) {
  const res = await api.post('/agents', agent);
  return res.data;
}

export async function updateAgent(agentId, agent) {
  const res = await api.put(`/agents/${agentId}`, agent);
  return res.data;
}

export async function deleteAgent(agentId) {
  const res = await api.delete(`/agents/${agentId}`);
  return res.data;
}

// -------------------- HERRAMIENTAS --------------------

export async function fetchTools() {
  const res = await api.get('/tools');
  return res.data;
}

export async function createTool(tool) {
  const res = await api.post('/tools', tool);
  return res.data;
}

export async function updateTool(toolId, tool) {
  const res = await api.put(`/tools/${toolId}`, tool);
  return res.data;
}

export async function deleteTool(toolId) {
  const res = await api.delete(`/tools/${toolId}`);
  return res.data;
}

// -------------------- CHAT --------------------

export async function fetchChats(agentId) {
  const res = await api.get(`/agents/${agentId}/chats`);
  return res.data;
}

export async function deleteChats(agentId) {
  const res = await api.delete(`/agents/${agentId}/chats`);
  return res.data;
}

export async function sendMessage(agentId, message) {
  const res = await api.post(`/chat/${agentId}`, { message });
  return res.data;
}

// -------------------- AUTENTICACIÓN --------------------

export async function loginUser(credentials) {
  const res = await api.post('/login', credentials);
  const data = res.data;

  if (data.token) {
    setAuthToken(data.token);
  }

  return data;
}
