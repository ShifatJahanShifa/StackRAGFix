import React, { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import InputBox from "./components/InputBox";

const App: React.FC = () => {
  const [messages, setMessages] = useState<{ role: string, text: string }[]>([]);

  const sendMessage = (text: string) => {
    const vscode = (window as any).acquireVsCodeApi();
    vscode.postMessage({ type: "chat", text });
    setMessages([...messages, { role: "user", text }]);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">🦜 Agentic RAG Chatbot</h1>
      <ChatWindow messages={messages} />
      <InputBox onSend={sendMessage} />
    </div>
  );
};

export default App;
