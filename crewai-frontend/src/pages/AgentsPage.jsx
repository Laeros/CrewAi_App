import React, { useState } from 'react';
import AgentList from '../components/AgentList';
import AgentForm from '../components/AgentForm';

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [editing, setEditing] = useState(false);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Gestión de Agentes</h1>
        <button
          className="primary-btn"
          onClick={() => {
            setSelectedAgent(null);
            setEditing(true);
          }}
        >
          Crear Agente
        </button>
      </div>

      <div className="page-content">
        {editing ? (
          <AgentForm
            agent={selectedAgent}
            onSave={() => setEditing(false)}
            onCancel={() => setEditing(false)}
          />
        ) : (
          <AgentList
            onSelect={(agent) => {
              setSelectedAgent(agent);
              setEditing(true);
            }}
          />
        )}
      </div>
    </div>
  );
}
