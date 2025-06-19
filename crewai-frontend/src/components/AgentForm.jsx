import React, { useState, useEffect } from 'react';
import { createAgent, updateAgent, fetchTools } from '../services/api';

// Puedes expandir estos modelos si tu backend los soporta
const AVAILABLE_MODELS = [
  { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
  { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' }
];

export default function AgentForm({ agent, onSave, onCancel }) {
  const [name, setName] = useState(agent?.name || '');
  const [prompt, setPrompt] = useState(agent?.prompt || '');
  const [model, setModel] = useState(agent?.model || 'gpt-4-turbo');
  const [tools, setTools] = useState(agent?.tools || []);
  const [availableTools, setAvailableTools] = useState([]);

  useEffect(() => {
    fetchTools().then(setAvailableTools);
  }, []);

  const toggleTool = (toolName) => {
    setTools(prev =>
      prev.includes(toolName)
        ? prev.filter(t => t !== toolName)
        : [...prev, toolName]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const agentData = {
      name,
      prompt,
      llm_provider: 'openai', // Fijo para evitar confusión
      model,
      temperature: 0.7,       // Valor estándar oculto al usuario
      max_tokens: 512,        // Valor por defecto oculto al usuario
      tools
    };

    try {
      if (agent?.id) {
        await updateAgent(agent.id, agentData);
      } else {
        await createAgent(agentData);
      }
      onSave();
    } catch (error) {
      alert('Error al guardar el agente.');
      console.error(error);
    }
  };

  return (
    <form className="agent-form" onSubmit={handleSubmit}>
      <h3 className="form-title">{agent ? 'Editar Agente' : 'Crear Agente'}</h3>

      <label className="form-label">
        Nombre:
        <input
          className="form-input"
          value={name}
          onChange={e => setName(e.target.value)}
          required
        />
      </label>

      <label className="form-label">
        Instrucciones para el agente:
        <textarea
          className="form-textarea"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Ejemplo: Ayuda al usuario a traducir textos con precisión..."
          required
        />
      </label>

      <label className="form-label">
        Modelo de IA:
        <select
          className="form-select"
          value={model}
          onChange={e => setModel(e.target.value)}
        >
          {AVAILABLE_MODELS.map(({ label, value }) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </label>

      <fieldset className="form-fieldset">
        <legend>Herramientas que puede usar el agente</legend>
        <div className="tool-checkboxes">
          {availableTools.length === 0 && <p>Cargando herramientas...</p>}
          {availableTools.map(tool => (
            <label key={tool.name} className="checkbox-label">
              <input
                type="checkbox"
                checked={tools.includes(tool.name)}
                onChange={() => toggleTool(tool.name)}
              />
              {tool.name}
            </label>
          ))}
        </div>
      </fieldset>

      <div className="form-buttons">
        <button type="submit" className="btn save-btn">Guardar</button>
        <button type="button" className="btn cancel-btn" onClick={onCancel}>Cancelar</button>
      </div>
    </form>
  );
}
