import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import fetch from "node-fetch";
import { indexWorkspace, deleteExistingCollection } from "../indexing/indexService";
import { retrieveRelevantCode } from "../indexing/indexService";
// hosted url: https://shifa1301-stackrag-backend.hf.space

export class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "ragChatView";
  private _view?: vscode.WebviewView;

  constructor(private readonly extensionUri: vscode.Uri,
    private readonly context: vscode.ExtensionContext
  ) {}

  public resolveWebviewView(
  webviewView: vscode.WebviewView,
  _context: vscode.WebviewViewResolveContext,
  _token: vscode.CancellationToken
) {
  this._view = webviewView;

  webviewView.webview.options = {
    enableScripts: true,
    localResourceRoots: [
      vscode.Uri.joinPath(this.extensionUri, "src", "view"),
      vscode.Uri.joinPath(this.extensionUri, "media"),
    ],
  };

  const databaseIconUri = webviewView.webview.asWebviewUri(
    vscode.Uri.joinPath(this.extensionUri, "media", "database.svg")
  );

  const currentFileIconUri = webviewView.webview.asWebviewUri(
    vscode.Uri.joinPath(this.extensionUri, "media", "current-file.svg")
  );

   const addContextIconUri = webviewView.webview.asWebviewUri(
    vscode.Uri.joinPath(this.extensionUri, "media", "add-context.svg")
  );

  const codebaseSummaryIconUri = webviewView.webview.asWebviewUri(
    vscode.Uri.joinPath(this.extensionUri, "media", "codebase.svg")
  );

  const lastTime = this.context.workspaceState.get("lastIndexedTime");

  webviewView.webview.postMessage({
      type: "initial_index_state",
      payload: { lastIndexedTime: lastTime }
  });

  const htmlPath = vscode.Uri.joinPath(
    this.extensionUri,
    "src",
    "view",
    "webview.html"
  );

  let htmlContent = fs.readFileSync(htmlPath.fsPath, "utf8");

  htmlContent = htmlContent.replace(
    "{{DATABASE_ICON}}",
    databaseIconUri.toString()
  );
  htmlContent = htmlContent.replace(
    "{{CURRENT_FILE_ICON}}",
    currentFileIconUri.toString()
  );
  htmlContent = htmlContent.replace(
    "{{ADD_CONTEXT_ICON}}",
    addContextIconUri.toString()
  );
  htmlContent = htmlContent.replace(
    "{{CODEBASE_ICON}}",
    codebaseSummaryIconUri.toString()
  );
  
  htmlContent = htmlContent.replace(
    "{{cspSource}}",
    webviewView.webview.cspSource
  );

  webviewView.webview.html = htmlContent;

  // Listen to messages from Webview
  webviewView.webview.onDidReceiveMessage(async (message) => {
    console.log("Received from webview:", message);

    if (message.type === "chat_request") {

      const { prompt, language, mode, history, selectedFiles, compare, specialMode } = message.payload;
      
      if (specialMode === "codebase") {
        await this.handleCodebaseSummary(mode, webviewView, prompt);
        return;
      }
      // Trim history here
      const MAX_MESSAGES = 1;
      const trimmedHistory = history.slice(-MAX_MESSAGES); 
      console.log("DEBUG: trimmedHistory", trimmedHistory);
      const editor = vscode.window.activeTextEditor;

      let currentFileContent = "";
      let fileName = "";

      // ================= FINAL LANGUAGE RESOLUTION =================
      let finalLanguage = language;

      const editorLanguage = editor?.document.languageId;

      if (language !== "default") {
        finalLanguage = language;
      }
      else if (editorLanguage) {
        finalLanguage = editorLanguage;
      }
      else {
        finalLanguage = "python";
      }

      console.log("DEBUG: finalLanguage =", finalLanguage);
      

      if (editor) {
        currentFileContent = editor.document.getText();
        fileName = editor.document.fileName;
      }
      if (!editor) {
        currentFileContent = "";
        fileName = "";
      }


      console.log("DEBUG: currentFileContent", currentFileContent);

      const MAX_FILE_CHARS = 8000;
      currentFileContent = currentFileContent.slice(0, MAX_FILE_CHARS);

      // added file contexts
      let selectedFilesContent = "";

      if (selectedFiles && selectedFiles.length > 0) {
        for (const relativePath of selectedFiles) {
          const fullPath = vscode.Uri.joinPath(
            vscode.workspace.workspaceFolders![0].uri,
            relativePath
          );

          try {
            const fileBytes = await vscode.workspace.fs.readFile(fullPath);
            const fileContent = Buffer.from(fileBytes).toString("utf8");

            selectedFilesContent += `\n\n--- File: ${relativePath} ---\n`;
            selectedFilesContent += fileContent.slice(0, 8000);
          } catch (err) {
            console.error("Error reading file:", relativePath);
          }
        }
      }

      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) return;

      const rootPath = workspaceFolder.uri.fsPath;
      console.log("DEBUG: rootPath", rootPath)

      let retrievedCode = "";
      retrievedCode = await retrieveRelevantCode(rootPath, prompt);
      console.log("DEBUG: Retrieved code:", retrievedCode);

      // construct the prompt or copilot:
      const structuredPrompt = `
        Generate a response to the user's question based on the following information:
     
        Code Language: ${finalLanguage}

        Conversation History:
        ${JSON.stringify(trimmedHistory, null, 2)}

        Current File:
        ${currentFileContent}

        Additional Selected Files:
        ${selectedFilesContent}

        Retrieved Code: ${retrievedCode}

        User Question:
        ${prompt}

        Provide a helpful response.
        `;

      let endpoint = "/chat";

      if (mode === "Debug") {
        endpoint = "/bugfix";
      } else if (mode === "Refactor") {
        endpoint = "/refactoring";
      }


      // support for copilot
      try {
        // ================= STACKRAG CALL =================
        const stackPromise = fetch(`http://127.0.0.1:8000/api/v1${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: prompt,
            language: finalLanguage,
            history: trimmedHistory,
            currentFileName: fileName,
            currentFileContent: currentFileContent,
            selectedFilesContent: selectedFilesContent,
            code: retrievedCode
          }),
        });

        // ================= COPILOT CALL =================
        let copilotPromise: Promise<string | null> | null = null;

        if (compare) {
          copilotPromise = (async () => {
            try {
              const models = await vscode.lm.selectChatModels();

              if (!models || models.length === 0) {
                return "Copilot model not available.";
              }

              const model = models[0];
              console.log("DEBUG: model",model);

              const messages: vscode.LanguageModelChatMessage[] = [
                vscode.LanguageModelChatMessage.User(structuredPrompt)
              ];

              const response = await model.sendRequest(messages, {});

              let fullText = "";
              for await (const chunk of response.text) {
                fullText += chunk;
              }

              return fullText.trim() || "Empty Copilot response.";

            } catch (err: any) {
              return `Copilot error: ${err.message || err}`;
            }
          })();
        }

        // ================= WAIT FOR RESULTS =================
        const stackRes = await stackPromise;
        const stackData = await stackRes.json();

        let copilotResult: string | null = null;

        if (compare && copilotPromise) {
          copilotResult = await copilotPromise;
        }

        // ================= SEND BACK TO WEBVIEW =================
        if (compare) {
          webviewView.webview.postMessage({
            type: "chat_compare_response",
            payload: {
              stackrag: stackData.response,
              copilot: copilotResult
            }
          });
        } else {
          await this.saveHistory(mode, prompt, stackData.response);

          webviewView.webview.postMessage({
            type: "chat_response",
            payload: {
              content: stackData.response
            }
          });
        }

      } catch (err) {
        webviewView.webview.postMessage({
          type: "chat_response",
          payload: {
            content: "Error: Unable to process request"
          }
        });
      }
    }


    if (message.type === "get_history") {
      const history = this.context.workspaceState.get("chatHistory", {});
      console.log("DEBUGlll: history",history);
      webviewView.webview.postMessage({
          type: "history_data",
          payload: history
      });
    }


    if (message.type === "get_workspace_files") {
      const files = await vscode.workspace.findFiles(
        "**/*.{py,js}",
        "**/node_modules/**"
      );

      const fileNames = files.map(file =>
        vscode.workspace.asRelativePath(file)
      );

      webviewView.webview.postMessage({
        type: "workspace_files_response",
        payload: fileNames
      });
    }


    if (message.type === "save_selected_response") {
      const { mode, prompt, selectedContent } = message.payload;
      await this.saveHistory(mode, prompt, selectedContent);
    }


    if (message.type === "start_indexing") {

      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) return;

      const rootPath = workspaceFolder.uri.fsPath;
      console.log("DEBUG: rootPath", rootPath)

      try {
          const totalIndexed = await indexWorkspace(rootPath, (current, total) => {
              webviewView.webview.postMessage({
                  type: "index_progress",
                  payload: { current, total }
              });
          });

          const now = new Date().toISOString();

          await this.context.workspaceState.update(
              "lastIndexedTime",
              now
          );

          webviewView.webview.postMessage({
              type: "index_complete",
              payload: { timestamp: now,
                totalIndexed
              }
          });

      } catch (err) {
          webviewView.webview.postMessage({
              type: "index_error"
          });
      }
    }
    

    if (message.type === "reindex") {
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) return;

      const rootPath = workspaceFolder.uri.fsPath;

      try {
        // step 1: delete
        await deleteExistingCollection(rootPath);

        // step 2: reindex immediately
        let totalIndexed = await indexWorkspace(rootPath, (current, total) => {
          webviewView.webview.postMessage({
            type: "index_progress",
            payload: { current, total }
          });
        });

        const now = new Date().toISOString();

        await this.context.workspaceState.update("lastIndexedTime", now);

        webviewView.webview.postMessage({
          type: "index_complete",
          payload: { timestamp: now, totalIndexed }
        });

      } catch (err) {
        console.error("Reindex error:", err);
        webviewView.webview.postMessage({
          type: "index_error"
        });
      }
    }


    if (message.type === "codebase_summary_request") {
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) return;

      const rootPath = workspaceFolder.uri.fsPath;

      try {
        const files = await vscode.workspace.findFiles(
          "**/*.{py,js}",
          "**/node_modules/**"
        );

        let combinedCode = "";
        const MAX_TOTAL_CHARS = 120000; // safety limit

        for (const file of files) {
          try {
            const fileBytes = await vscode.workspace.fs.readFile(file);
            const content = Buffer.from(fileBytes).toString("utf8");

            combinedCode += `\n\n===== FILE: ${vscode.workspace.asRelativePath(file)} =====\n`;
            combinedCode += content;

            if (combinedCode.length > MAX_TOTAL_CHARS) {
              combinedCode = combinedCode.slice(0, MAX_TOTAL_CHARS);
              break;
            }
          } catch (err) {
            console.error("Error reading file:", file.fsPath);
          }
        }

        const res = await fetch("http://127.0.0.1:8000/api/v1/codebase-summary", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            prompt: message.payload.prompt,
            codebase: combinedCode
          })
        });

        const data = await res.json();
        webviewView.webview.postMessage({
          type: "chat_response",
          payload: {
            content: data.response
          }
        });
      } catch (err) {
        console.error("Codebase summary error:", err);

        webviewView.webview.postMessage({
          type: "chat_response",
          payload: {
            content: "Error generating codebase summary."
          }
        });
      }
    }


    if (message.type === "delete_mode_history") {
      const { date, mode } = message.payload;

      const history = this.context.workspaceState.get<any>("chatHistory", {});

      if (history[date] && history[date][mode]) {
        delete history[date][mode];

        if (Object.keys(history[date]).length === 0) {
          delete history[date];
        }

        await this.context.workspaceState.update("chatHistory", history);
      }

      webviewView.webview.postMessage({
        type: "history_data",
        payload: history
      });
    }
    
  });
}

  
private async normalizeLanguage(lang?: string) {
  if (!lang) return "python";

  if (lang === "javascriptreact") return "javascript";
  if (lang === "typescriptreact") return "typescript";

  return lang;
}

private async handleCodebaseSummary(
  mode: string,
  webviewView: vscode.WebviewView,
  prompt: string
) {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  if (!workspaceFolder) return;

  try {
    const files = await vscode.workspace.findFiles(
      "**/*.{py,js}",
      "**/node_modules/**"
    );

    let combinedCode = "";
    const MAX_TOTAL_CHARS = 120000;

    for (const file of files) {
      try {
        const fileBytes = await vscode.workspace.fs.readFile(file);
        const content = Buffer.from(fileBytes).toString("utf8");

        combinedCode += `\n\n===== FILE: ${vscode.workspace.asRelativePath(file)} =====\n`;
        combinedCode += content;

        if (combinedCode.length > MAX_TOTAL_CHARS) {
          combinedCode = combinedCode.slice(0, MAX_TOTAL_CHARS);
          break;
        }
      } catch {}
    }

    const res = await fetch(
      "http://127.0.0.1:8000/api/v1/codebase-summary",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt,
          codebase: combinedCode
        })
      }
    );

    const data = await res.json();
    await this.saveHistory(mode, prompt, data.response);

          webviewView.webview.postMessage({
            type: "chat_response",
            payload: {
              content: data.response
            }
          });

    webviewView.webview.postMessage({
      type: "chat_response",
      payload: { content: data.response }
    });

  } catch (err) {
    webviewView.webview.postMessage({
      type: "chat_response",
      payload: { content: "Error generating codebase summary." }
    });
  }
}

private async saveHistory(mode: string, userPrompt: string, assistantReply: string) {

  // const today = new Date().toISOString().split("T")[0]; 
  const now = new Date();
  const today = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  console.log("Saving history for", today);// "2026-02-17"
  console.log("Saving history for", today);

  const history = this.context.workspaceState.get<any>("chatHistory", {});

  if (!history[today]) {
    history[today] = {
      Ask: [],
      Debug: [],
      Refactor: []
    };
  }

  history[today][mode].push({
    user: userPrompt,
    assistant: assistantReply,
    timestamp: Date.now()
  });

  await this.context.workspaceState.update("chatHistory", history);
}
}