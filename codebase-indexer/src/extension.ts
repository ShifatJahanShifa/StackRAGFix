// // The module 'vscode' contains the VS Code extensibility API
// // Import the module and reference it with the alias vscode in your code below
// import * as vscode from 'vscode';

// // This method is called when your extension is activated
// // Your extension is activated the very first time the command is executed
// export function activate(context: vscode.ExtensionContext) {

// 	// Use the console to output diagnostic information (console.log) and errors (console.error)
// 	// This line of code will only be executed once when your extension is activated
// 	console.log('Congratulations, your extension "codebase-indexer" is now active!');

// 	// The command has been defined in the package.json file
// 	// Now provide the implementation of the command with registerCommand
// 	// The commandId parameter must match the command field in package.json
// 	const disposable = vscode.commands.registerCommand('codebase-indexer.helloWorld', () => {
// 		// The code you place here will be executed every time your command is executed
// 		// Display a message box to the user
// 		vscode.window.showInformationMessage('Hello World from codebase-indexer!');
// 	});

// 	context.subscriptions.push(disposable);
// }

// // This method is called when your extension is deactivated
// export function deactivate() {}




import * as vscode from "vscode";
import fs from "fs";
import { scanWorkspace } from "./indexer/fileScanner.js";
import { addToVectorStore } from "./indexer/vectorStore.js";
import { watchFiles } from "./indexer/fileWatcher.js";
import { searchCodebase } from "./indexer/search.js";

export async function activate(context: vscode.ExtensionContext) {
  vscode.window.showInformationMessage("StackRAG Indexer Active!");

  const buildIndexCmd = vscode.commands.registerCommand("stackrag.buildIndex", async () => {
    const files = await scanWorkspace();
    vscode.window.showInformationMessage(`Indexing ${files.length} files...`);
    for (const file of files) {
      const content = fs.readFileSync(file, "utf-8");
      await addToVectorStore(file, content);
    }
    vscode.window.showInformationMessage("Indexing complete!");
  });

  const searchCmd = vscode.commands.registerCommand("stackrag.searchIndex", async () => {
    const query = await vscode.window.showInputBox({ prompt: "Enter your search query" });
    if (!query) return;

    const results = await searchCodebase(query);
    results.forEach(r => {
      vscode.window.showInformationMessage(`Result: ${r.source}\n${r.snippet}`);
    });
  });

  watchFiles();
  context.subscriptions.push(buildIndexCmd, searchCmd);
}

export function deactivate() {}
