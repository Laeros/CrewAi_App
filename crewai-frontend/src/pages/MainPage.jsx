import React, { useState, useEffect } from 'react';
import AgentList from '../components/AgentList';
import AgentForm from '../components/AgentForm';
import Chat from '../components/Chat';
import ToolList from '../components/ToolList';
import ToolForm from '../components/ToolForm';
import { fetchTools } from '../services/api';

export default function MainPage() {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedChat, setSelectedChat] = useState(null);
  const [showAgentForm, setShowAgentForm] = useState(false);
  const [showToolForm, setShowToolForm] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);
  const [editingTool, setEditingTool] = useState(null);
  const [currentChatActive, setCurrentChatActive] = useState(false);

  const [tools, setTools] = useState([]);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    const data = await fetchTools();
    setTools(data);
  };

  const handleNewChat = () => {
    setSelectedChat(null);
    setSelectedAgent(null);
    setCurrentChatActive(false);
    setShowAgentForm(false);
    setShowToolForm(false);
  };

  const handleChatSelect = (chat) => {
    setSelectedChat(chat);
    setCurrentChatActive(true);
    setShowAgentForm(false);
    setShowToolForm(false);
  };

  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    setShowAgentForm(false);
    setShowToolForm(false);
  };

  const handleShowAgentForm = () => {
    setShowAgentForm(true);
    setShowToolForm(false);
    setEditingAgent(null);
  };

  const handleShowToolForm = () => {
    setShowToolForm(true);
    setShowAgentForm(false);
    setEditingTool(null);
  };

  const handleCloseForm = () => {
    setShowAgentForm(false);
    setShowToolForm(false);
    setEditingAgent(null);
    setEditingTool(null);
    loadTools();
  };

  const isFormExpanded = showAgentForm || showToolForm;

  return (
    <div className="app-container">
      <div className={`left-panel ${isFormExpanded ? 'expanded' : ''}`}>
        <div className="left-panel-header">
          <h1 className="app-title">Chat App</h1>
          <button className="new-chat-btn" onClick={handleNewChat}>
            📝 Nuevo Chat
          </button>
        </div>

        <div className="left-panel-content">
          <div className="section">
            <div className="section-header">
              <h3 className="section-title">Agentes</h3>
              <button className="section-add-btn" onClick={handleShowAgentForm}>
                + Agregar
              </button>
            </div>
            <AgentList 
              onSelect={handleAgentSelect}
              selectedAgent={selectedAgent}
            />
          </div>

          <div className="section">
            <div className="section-header">
              <h3 className="section-title">Herramientas</h3>
              <button className="section-add-btn" onClick={handleShowToolForm}>
                + Agregar
              </button>
            </div>
            <div className="tool-list">
              <ToolList 
                tools={tools}
                onSelect={(tool) => {
                  setEditingTool(tool);
                  handleShowToolForm();
                }}
              />
            </div>
          </div>
        </div>

        {showAgentForm && (
          <div className="form-overlay visible">
            <div className="form-header">
              <h2 className="form-title">
                {editingAgent ? 'Editar Agente' : 'Nuevo Agente'}
              </h2>
              <button className="form-close" onClick={handleCloseForm}>&times;</button>
            </div>
            <div className="form-content">
              <AgentForm
                agent={editingAgent}
                onSave={handleCloseForm}
                onCancel={handleCloseForm}
              />
            </div>
          </div>
        )}

        {showToolForm && (
          <div className="form-overlay visible">
            <div className="form-header">
              <h2 className="form-title">
                {editingTool ? 'Editar Herramienta' : 'Nueva Herramienta'}
              </h2>
              <button className="form-close" onClick={handleCloseForm}>&times;</button>
            </div>
            <div className="form-content">
              <ToolForm
                tool={editingTool}
                onSave={handleCloseForm}
                onCancel={handleCloseForm}
              />
            </div>
          </div>
        )}
      </div>

      <div className="right-panel">
        <div className="chat-header">
          <h1 className="chat-header-title">
            Hola, Rodrigo. ¿Todo listo para empezar?
          </h1>
        </div>

        <div className="chat-main">
          {selectedAgent ? (
            <Chat 
              agent={selectedAgent} 
              chat={selectedChat}
              onChatStart={() => setCurrentChatActive(true)}
            />
          ) : (
            <div className="chat-welcome">
              <h2 className="welcome-title">¡Bienvenido!</h2>
              <p className="welcome-subtitle">
                Selecciona un agente para empezar a chatear
              </p>
            </div>
          )}

          <div className="chat-input-container">
            <div className="chat-input-wrapper">
              <button className="tools-button">
                ⚙️ Herramientas
              </button>
              <textarea 
                className="chat-input"
                placeholder="Pregunta lo que quieras..."
                rows="1"
              />
              <button className="send-button">
                ↑
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
