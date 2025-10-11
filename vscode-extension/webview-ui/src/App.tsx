import React, { useEffect, useState, useRef } from "react";
import ChatWindow from "./components/ChatWindow";
import InputBox from "./components/InputBox";

const vscode = (window as any).acquireVsCodeApi();

const App: React.FC = () => {
  console.log("DEbugggg Webview reloaded at:", new Date().toISOString());
  const [messages, setMessages] = useState<{ role: string; text: string }[]>(
    () => vscode.getState()?.messages || []
  );

    // Keep a ref to messages so our event listener always uses latest value
  const messagesRef = useRef(messages);
  messagesRef.current = messages;

  const sendMessage = (text: string) => {
    // Add user message immediately
    const userMessage = { role: "user", text };
    const newMessages = [...messagesRef.current, userMessage];
    setMessages(newMessages);
    vscode.setState({ messages: newMessages });

    // Send the message to the extension host
    vscode.postMessage({
      type: "chat",
      text,
      history: messagesRef.current.map((msg) => ({
        role: msg.role,
        content: msg.text,
      })),
    });
  };

  useEffect(() => {
    const handler = (event: MessageEvent) => {
      const message = event.data;
      if (message.role && message.text) {
        const newMessages = [...messagesRef.current, message];
        setMessages(newMessages);
        vscode.setState({ messages: newMessages });
      }
    };

    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, []); 

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">🦜 Agentic RAG Chatbot</h1>
      <ChatWindow messages={messages} />
      <InputBox onSend={sendMessage} />
    </div>
  );
};

export default App;
