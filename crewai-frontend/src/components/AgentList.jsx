import React, { useEffect, useState } from 'react';
import { fetchAgents, deleteAgent } from '../services/api';

export default function AgentList({ onSelect, refresh }) {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    const loadAgents = async () => {
      const data = await fetchAgents();
      setAgents(data);
    };

    loadAgents(); // ✅ correcto
  }, [refresh]); // ✅ recarga al cambiar

  const handleDelete = async (id) => {
    await deleteAgent(id);
    const updated = await fetchAgents(); // actualiza tras eliminar
    setAgents(updated);
  };

  return (
    <div className="list">
      <h2 className="list-title">Agentes disponibles</h2>
      <ul className="list-items">
        {agents.map(agent => (
          <li key={agent.id} className="list-entry">
            <span className="agent-name" onClick={() => onSelect(agent)}>
              {agent.name}
            </span>
            <button className="delete-btn" onClick={() => handleDelete(agent.id)}>
              Eliminar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
