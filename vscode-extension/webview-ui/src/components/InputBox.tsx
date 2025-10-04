import React, { useState } from "react";

interface Props {
  onSend: (msg: string) => void;
}

const InputBox: React.FC<Props> = ({ onSend }) => {
  const [value, setValue] = useState("");

  return (
    <div className="flex mt-4">
      <input
        className="flex-1 border rounded p-2"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type your message..."
      />
      <button
        className="ml-2 px-4 py-2 bg-blue-500 text-white rounded"
        onClick={() => {
          onSend(value);
          setValue("");
        }}
      >
        Send
      </button>
    </div>
  );
};

export default InputBox;
