import React, { useState } from 'react';
import AgentList from '../components/AgentList';
import Chat from '../components/Chat';

export default function ChatPage() {
  const [selectedAgent, setSelectedAgent] = useState(null);

  return (
    <div className="chat-page">
      <h1 className="chat-title">Chat con Agentes</h1>
      <div className="chat-layout">
        <div className="agent-panel">
          <AgentList onSelect={setSelectedAgent} />
        </div>
        <div className="chat-panel">
          <Chat agent={selectedAgent} />
        </div>
      </div>
    </div>
  );
}
