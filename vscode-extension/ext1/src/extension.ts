// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { spawn } from "child_process";
import * as path from "path";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
// export function activate(context: vscode.ExtensionContext) {

// 	// Use the console to output diagnostic information (console.log) and errors (console.error)
// 	// This line of code will only be executed once when your extension is activated
// 	console.log('Congratulations, your extension "ext1" is now active!');

// 	// The command has been defined in the package.json file
// 	// Now provide the implementation of the command with registerCommand
// 	// The commandId parameter must match the command field in package.json
// 	const disposable = vscode.commands.registerCommand('ext1.helloWorld', () => {
// 		// The code you place here will be executed every time your command is executed
// 		// Display a message box to the user
// 		vscode.window.showInformationMessage('Hello World from ext1!');
// 	});

// 	context.subscriptions.push(disposable);
// }

// This method is called when your extension is deactivated

import { ChatViewProvider } from "./view/chatViewProvider"
let mcpProcess: any = null;

export async function activate(context: vscode.ExtensionContext) {
  console.log("🚀 VSCode extension activated");
  console.log("🔍 Extension path:", context.extensionPath);

	const serverPath = path.join(context.extensionPath, "out", "mcp", "server.js");
  console.log("🔗 MCP server path:", serverPath);

  // Spawn MCP server as a detached, independent process
  mcpProcess = spawn("node", [serverPath], {
    stdio: "inherit",
    detached: true, //  keeps process alive independently
  });

  mcpProcess.on("spawn", () => console.log("✅ MCP server process started"));
  mcpProcess.on("exit", (code: any) =>
    console.log(`🛑 MCP server exited with code ${code}`)
  );
  mcpProcess.on("error", (err: Error) => console.error("MCP server error:", err));

   const provider = new ChatViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider("ragChatView", provider)
  );
}

export function deactivate() {
  if (mcpProcess) {
    console.log("🔻 Killing MCP server...");
    try {
      process.kill(-mcpProcess.pid); // kill detached group
    } catch (err) {
      console.warn("⚠️ Could not kill MCP process:", err);
    }
  }
}
