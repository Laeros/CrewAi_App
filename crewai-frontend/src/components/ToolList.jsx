import React, { useEffect, useState } from 'react';
import { fetchTools, deleteTool } from '../services/api';

export default function ToolList({ onSelect, refresh }) {
  const [tools, setTools] = useState([]);

  useEffect(() => {
    const loadTools = async () => {
      const data = await fetchTools();
      setTools(data);
    };

    loadTools(); // ✅ Llama a la función solo cuando refresh cambia
  }, [refresh]);

  const handleDelete = async (id) => {
    await deleteTool(id);
    const updated = await fetchTools(); // ✅ recarga tras eliminación
    setTools(updated);
  };

  return (
    <div className="tool-list-container">
      <h2 className="tool-list-title">Herramientas</h2>
      <ul className="tool-list">
        {tools.map(tool => (
          <li key={tool.id} className="tool-item">
            <span className="tool-name">{tool.name}</span>
            <div className="tool-actions">
              <button className="btn select-btn" onClick={() => onSelect(tool)}>
                Ver / Editar
              </button>
              <button className="btn delete-btn" onClick={() => handleDelete(tool.id)}>
                Eliminar
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
