import React, { useEffect, useState } from 'react';
import { fetchChats, sendMessage, deleteChats } from '../services/api';

export default function Chat({ agent }) {
  const [chats, setChats] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (agent) {
      loadChats();
    }
  }, [agent]);

  const loadChats = async () => {
    const data = await fetchChats(agent.id);
    setChats(data);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    setLoading(true);
    const res = await sendMessage(agent.id, input);
    setChats([...chats, { message: input, sender: 'user' }, { message: res.respuesta, sender: 'agent' }]);
    setInput('');
    setLoading(false);
  };

  const handleClear = async () => {
    await deleteChats(agent.id);
    setChats([]);
  };

  if (!agent) return <p className="chat-placeholder">Seleccione un agente para chatear.</p>;

  return (
    <div className="chat-container">
      <h2 className="chat-title">Chat con {agent.name}</h2>
      <div className="chat-box">
        {chats.map((chat, i) => (
          <div
            key={i}
            className={`chat-bubble ${i % 2 === 0 ? 'user' : 'agent'}`}
          >
            <span className="sender">{i % 2 === 0 ? 'Usuario' : 'Agente'}:</span> {chat.message}
          </div>
        ))}
      </div>
      <textarea
        className="chat-input"
        rows={3}
        placeholder="Escribe tu mensaje..."
        value={input}
        onChange={e => setInput(e.target.value)}
        disabled={loading}
      />
      <div className="chat-buttons">
        <button className="btn send-btn" onClick={handleSend} disabled={loading}>
          Enviar
        </button>
        <button className="btn clear-btn" onClick={handleClear} disabled={loading}>
          Limpiar chat
        </button>
      </div>
    </div>
  );
}
