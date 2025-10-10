my-rag-extension/
│── package.json             # Extension manifest (commands, activation, etc.)
│── tsconfig.json            # TypeScript config for extension backend
│── webpack.config.js        # Bundler for frontend (React)
│── src/
│   ├── extension.ts         # Entry point (register commands, open webview)
│   ├── panel/
│   │   ├── ChatPanel.ts     # Manages webview lifecycle (open, dispose, postMessage)
│   │   └── messageTypes.ts  # Shared types for frontend <-> backend messaging
│   └── backend/
│       └── ragClient.ts     # Calls your RAG backend (Python/Node API)
│
│── webview-ui/              # React frontend for Webview
│   ├── package.json         # Frontend dependencies (React, Tailwind, etc.)
│   ├── tsconfig.json
│   ├── vite.config.ts       # Or webpack config for frontend build
│   └── src/
│       ├── index.tsx        # Entry point
│       ├── App.tsx          # Root chat component
│       ├── components/
│       │   ├── ChatWindow.tsx
│       │   ├── MessageBubble.tsx
│       │   └── InputBox.tsx
│       └── styles/
│           └── index.css    # Tailwind styles
│
│── dist/                    # Compiled frontend bundle (React → JS for Webview)
│   └── bundle.js
│
└── README.md



## current documentation 

vscode-extension/
│
├── src/
│   ├── backend/                # Future RAG logic, model calls, etc.
│   ├── panel/
│   │   └── chat_panel.ts       # Handles webview creation + message passing
│   ├── test/                   # Test files (optional)
│   ├── type/                   # Type definitions (optional)
│   └── extension.ts            # Entry point (registers command, opens chat)
│
├── out/                        # Compiled JS output (from TypeScript)
│   ├── extension.js
│   └── panel/chat_panel.js
│
├── webview-ui/                 # React frontend (your chat UI)
│   ├── src/                    # All React components
│   ├── index.html
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── package.json                # Extension build + dependencies
├── tsconfig.json               # TypeScript config for extension
└── README.md
