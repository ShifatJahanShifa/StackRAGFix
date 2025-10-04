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

