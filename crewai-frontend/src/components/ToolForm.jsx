import React, { useState } from 'react';
import { createTool, updateTool } from '../services/api';

const PARAM_TYPES = ['string', 'number', 'boolean']; // Puedes extender a "object", "array", etc.

export default function ToolForm({ tool, onSave, onCancel }) {
  const [name, setName] = useState(tool?.name || '');
  const [description, setDescription] = useState(tool?.description || '');
  const [params, setParams] = useState(() => {
    if (tool?.parameters?.properties) {
      return Object.entries(tool.parameters.properties).map(([key, value]) => ({
        name: key,
        type: value.type || 'string',
        description: value.description || '',
        required: tool.parameters.required?.includes(key) || false
      }));
    }
    return [];
  });

  const handleParamChange = (index, field, value) => {
    const updated = [...params];
    updated[index][field] = field === 'required' ? value.target.checked : value;
    setParams(updated);
  };

  const addParam = () => {
    setParams([...params, { name: '', type: 'string', description: '', required: true }]);
  };

  const removeParam = (index) => {
    const updated = [...params];
    updated.splice(index, 1);
    setParams(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const properties = {};
    const required = [];

    for (const param of params) {
      if (!param.name.trim() || !param.type) {
        alert('Todos los parámetros deben tener nombre y tipo.');
        return;
      }
      properties[param.name.trim()] = {
        type: param.type,
        ...(param.description && { description: param.description })
      };
      if (param.required) required.push(param.name.trim());
    }

    const toolData = {
      name,
      description,
      parameters: {
        type: 'object',
        properties,
        required
      }
    };

    try {
      if (tool?.id) {
        await updateTool(tool.id, toolData);
      } else {
        await createTool(toolData);
      }
      onSave();
    } catch (error) {
      alert('Error al guardar la herramienta.');
      console.error(error);
    }
  };

  return (
    <form className="tool-form" onSubmit={handleSubmit}>
      <h3 className="form-title">{tool ? 'Editar Herramienta' : 'Crear Herramienta'}</h3>

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
        Descripción:
        <textarea
          className="form-textarea"
          value={description}
          onChange={e => setDescription(e.target.value)}
          required
        />
      </label>

      <h4>Parámetros:</h4>
      {params.map((param, index) => (
        <div className="param-row" key={index} style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
          <input
            placeholder="Nombre"
            value={param.name}
            onChange={e => handleParamChange(index, 'name', e.target.value)}
            required
          />
          <select
            value={param.type}
            onChange={e => handleParamChange(index, 'type', e.target.value)}
          >
            {PARAM_TYPES.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
          <input
            placeholder="Descripción"
            value={param.description}
            onChange={e => handleParamChange(index, 'description', e.target.value)}
          />
          <label style={{ marginLeft: '1rem' }}>
            <input
              type="checkbox"
              checked={param.required}
              onChange={e => handleParamChange(index, 'required', e)}
            /> Requerido
          </label>
          <button
            type="button"
            onClick={() => removeParam(index)}
            style={{ marginLeft: '1rem', color: 'red' }}
          >
            Eliminar
          </button>
        </div>
      ))}

      <button type="button" onClick={addParam} className="btn secondary">+ Agregar Parámetro</button>

      <div className="form-buttons" style={{ marginTop: '1.5rem' }}>
        <button type="submit" className="btn save-btn">Guardar</button>
        <button type="button" className="btn cancel-btn" onClick={onCancel}>Cancelar</button>
      </div>
    </form>
  );
}
