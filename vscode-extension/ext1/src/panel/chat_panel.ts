import * as vscode from "vscode";
import * as path from "path";

export class ChatPanel {
  public static currentPanel: ChatPanel | undefined;
  private readonly panel: vscode.WebviewPanel;
  private readonly extensionUri: vscode.Uri;

  public static createOrShow(extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor?.viewColumn;

    if (ChatPanel.currentPanel) {
      ChatPanel.currentPanel.panel.reveal(column);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      "ragChat",
      "Agentic RAG Chatbot",
      column || vscode.ViewColumn.One,
      { enableScripts: true, localResourceRoots: [vscode.Uri.joinPath(extensionUri, "dist")] }
    );

    ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
  }

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this.panel = panel;
    this.extensionUri = extensionUri;

    const scriptUri = panel.webview.asWebviewUri(
      vscode.Uri.joinPath(this.extensionUri, "dist", "assets", "index.js")
    );

    this.panel.webview.html = this.getHtml(scriptUri);

    this.panel.webview.onDidReceiveMessage(async (message) => {
      if (message.type === "chat") {
        // TODO: Connect with your RAG backend
        this.panel.webview.postMessage({ role: "bot", text: "Hello from backend!" });
      }
    });

    this.panel.onDidDispose(() => ChatPanel.currentPanel = undefined);
  }

  private getHtml(scriptUri: vscode.Uri) {
    return `<!DOCTYPE html>
      <html lang="en">
      <head><meta charset="UTF-8"><title>Agentic RAG Chatbot</title></head>
      <body>
        <div id="root"></div>
        <script type="module" src="${scriptUri}"></script>
      </body>
      </html>`;
  }
}
