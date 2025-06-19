import React, { useState } from 'react';
import ToolList from '../components/ToolList';
import ToolForm from '../components/ToolForm';

export default function ToolsPage() {
  const [selectedTool, setSelectedTool] = useState(null);
  const [editing, setEditing] = useState(false);

  return (
    <div className="tools-page">
      <h1 className="tools-title">Gestión de Herramientas</h1>
      <div className="tools-actions">
        <button className="create-btn" onClick={() => {
          setSelectedTool(null);
          setEditing(true);
        }}>
          Crear Herramienta
        </button>
      </div>
      <div className="tools-content">
        {editing ? (
          <ToolForm
            tool={selectedTool}
            onSave={() => setEditing(false)}
            onCancel={() => setEditing(false)}
          />
        ) : (
          <ToolList onSelect={(tool) => {
            setSelectedTool(tool);
            setEditing(true);
          }} />
        )}
      </div>
    </div>
  );
}
