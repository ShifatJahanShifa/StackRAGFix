// // The module 'vscode' contains the VS Code extensibility API
// // Import the module and reference it with the alias vscode in your code below
import * as path from "path";
import * as dotenv from "dotenv";
dotenv.config();
dotenv.config({
  path: path.join(__dirname, "../.env")
});
import * as vscode from 'vscode';
import { ChatViewProvider } from "./view/chatWebView"

export function activate(context: vscode.ExtensionContext) {
	console.log("Extension activated!");
  // Get API keys from settings
  const config = vscode.workspace.getConfiguration('myExtension');
  const mistralKey = config.get('mistralApiKey');
  const qdrantKey1 = config.get('qdrantApiKey');
  const qdrantKey2 = config.get('qdrantClusterEndpoint');

  console.log("Loaded API keys:", !!mistralKey, !!qdrantKey1, !!qdrantKey2);

  const provider = new ChatViewProvider(context.extensionUri, context);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider("ragChatView", provider)
  );
}

export function deactivate() {}