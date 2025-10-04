import React from "react";

interface Message {
  role: string;
  text: string;
}

const ChatWindow: React.FC<{ messages: Message[] }> = ({ messages }) => {
  return (
    <div className="border rounded p-4 h-96 overflow-y-auto">
      {messages.map((m, i) => (
        <div key={i} className={`my-2 ${m.role === "user" ? "text-right" : "text-left"}`}>
          <span className="inline-block bg-gray-100 p-2 rounded">{m.text}</span>
        </div>
      ))}
    </div>
  );
};

export default ChatWindow;
