// import * as vscode from "vscode";
// import * as path from "path";

// export class ChatPanel {
//   public static currentPanel: ChatPanel | undefined;
//   private readonly panel: vscode.WebviewPanel;
//   private readonly extensionUri: vscode.Uri;

//   public static createOrShow(extensionUri: vscode.Uri) {
//     console.log("see", extensionUri)
//     const column = vscode.window.activeTextEditor?.viewColumn;

//     if (ChatPanel.currentPanel) {
//       ChatPanel.currentPanel.panel.reveal(column);
//       return;
//     }

//     const panel = vscode.window.createWebviewPanel(
//       "ragChat",
//       "Agentic RAG Chatbot",
//       column || vscode.ViewColumn.One,
//       { enableScripts: true, localResourceRoots: [vscode.Uri.joinPath(extensionUri,"..", "webview-ui", "dist")] }
//     );

//     ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
//   }

//   private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
//     this.panel = panel;
//     this.extensionUri = extensionUri;

//     const scriptUri = panel.webview.asWebviewUri(
//       vscode.Uri.joinPath(this.extensionUri, "..", "webview-ui", "dist", "assets", "index-BuuWLSum.js")
//     );

//     this.panel.webview.html = this.getHtml(scriptUri);

//     this.panel.webview.onDidReceiveMessage(async (message) => {
//       if (message.type === "chat") {
//         // TODO: Connect with your RAG backend
//         this.panel.webview.postMessage({ role: "bot", text: "Hello from backend!" });
//       }
//     });

//     this.panel.onDidDispose(() => ChatPanel.currentPanel = undefined);
//   }

//   private getHtml(scriptUri: vscode.Uri) {
//     return `<!DOCTYPE html>
//       <html lang="en">
//       <head><meta charset="UTF-8"><title>Agentic RAG Chatbot</title></head>
//       <body>
//         <div id="root"></div>
//         <script type="module" src="${scriptUri}"></script>
//       </body>
//       </html>`;
//   }
// }


import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

export class ChatPanel {
  public static currentPanel: ChatPanel | undefined;
  private readonly panel: vscode.WebviewPanel;
  private readonly extensionUri: vscode.Uri;

  public static createOrShow(extensionUri: vscode.Uri) {
    console.log("debug", extensionUri)
    const column = vscode.window.activeTextEditor?.viewColumn;

    if (ChatPanel.currentPanel) {
      ChatPanel.currentPanel.panel.reveal(column);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      "ragChat",
      "Agentic RAG Chatbot",
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [
          vscode.Uri.joinPath(extensionUri, "..", "webview-ui", "dist")
        ],
      }
    );

    ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
  }

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this.panel = panel;
    this.extensionUri = extensionUri;

    const assetsPath = path.join(
      this.extensionUri.fsPath,
      "..",
      "webview-ui",
      "dist",
      "assets"
    );

    // Dynamically detect JS and CSS file names
    const jsFile = fs.readdirSync(assetsPath).find(f => f.endsWith(".js"));
    const cssFile = fs.readdirSync(assetsPath).find(f => f.endsWith(".css"));

    const scriptUri = panel.webview.asWebviewUri(
      vscode.Uri.file(path.join(assetsPath, jsFile!))
    );

    const styleUri = cssFile
      ? panel.webview.asWebviewUri(
          vscode.Uri.file(path.join(assetsPath, cssFile))
        )
      : undefined;

    this.panel.webview.html = this.getHtml(scriptUri, styleUri);

    this.panel.webview.onDidReceiveMessage(async (message) => {
      if (message.type === "chat") {
        this.panel.webview.postMessage({ role: "bot", text: "Hello from backend!" });
      }
    });

    this.panel.onDidDispose(() => (ChatPanel.currentPanel = undefined));
  }

  private getHtml(scriptUri: vscode.Uri, styleUri?: vscode.Uri) {
    return `<!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${
          this.panel.webview.cspSource
        } 'unsafe-inline'; script-src 'unsafe-eval' ${
      this.panel.webview.cspSource
    };">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agentic RAG Chatbot</title>
        ${styleUri ? `<link rel="stylesheet" href="${styleUri}">` : ""}
      </head>
      <body>
        <div id="root"></div>
        <script type="module" src="${scriptUri}"></script>
      </body>
      </html>`;
  }
}
