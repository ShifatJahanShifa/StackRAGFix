import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

export class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "ragChatView";
  private _view?: vscode.WebviewView;

  constructor(private readonly extensionUri: vscode.Uri) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [
        vscode.Uri.joinPath(this.extensionUri, "..", "webview-ui", "dist"),
      ],
    };

    const assetsPath = path.join(
      this.extensionUri.fsPath,
      "..",
      "webview-ui",
      "dist",
      "assets"
    );

    const jsFile = fs.readdirSync(assetsPath).find((f) => f.endsWith(".js"));
    const cssFile = fs.readdirSync(assetsPath).find((f) => f.endsWith(".css"));

    const scriptUri = webviewView.webview.asWebviewUri(
      vscode.Uri.file(path.join(assetsPath, jsFile!))
    );

    const styleUri = cssFile
      ? webviewView.webview.asWebviewUri(
          vscode.Uri.file(path.join(assetsPath, cssFile))
        )
      : undefined;

    webviewView.webview.html = this.getHtml(webviewView.webview, scriptUri, styleUri);

    // Listen for messages from the webview
    webviewView.webview.onDidReceiveMessage(async (message) => {
      if (message.type === "chat") {
        webviewView.webview.postMessage({
          role: "bot",
          text: "Hello from sidebar backend!",
        });
      }
    });
  }

  private getHtml(webview: vscode.Webview, scriptUri: vscode.Uri, styleUri?: vscode.Uri) {
    return `<!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Security-Policy"
          content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'unsafe-eval' ${webview.cspSource};">
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
