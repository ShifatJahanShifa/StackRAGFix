// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import path from 'path';

let webviewPanel: vscode.WebviewPanel | undefined;
export function activate(context: vscode.ExtensionContext) {
	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "stackrag" is now active!');
	vscode.commands.getCommands(true).then(cmds =>
		console.log(cmds.filter(c => c.includes("copilot")))
		)
		
	const disposable = vscode.commands.registerCommand('stackrag.helloWorld', async () => {
		try {
			// Step 1: Select available language models (Copilot models will appear if available)
			const models = await vscode.lm.selectChatModels();
			if (!models || models.length === 0) {
				vscode.window.showErrorMessage('No Copilot language models available. Is GitHub Copilot enabled?');
				return;
			}

			const model = models[0]; // Use the first available Copilot model
			console.log('gg',model);

			// Step 2: Get the current editor content
			const editor = vscode.window.activeTextEditor;
			if (!editor) {
				vscode.window.showInformationMessage('No active editor.');
				return;
			}

			const code = editor.document.getText();

			// Step 3: Create messages for chat-style interaction
			const messages: vscode.LanguageModelChatMessage[] = [
				vscode.LanguageModelChatMessage.User(`is there any bug in this code? if so, fix this code:\n\n${code}`)
			];

			// Step 4: Invoke the model
			const response = await model.sendRequest(messages, {});
			const rr = typeof response === "string" ? response : JSON.stringify(response, null, 2);

			// Step 5: Show result
			vscode.window.showInformationMessage("debug rr",rr);
			let fullText =  '';

			for await (const chunk of response.text) {
				fullText += chunk;
			}

			if (!fullText.trim()) {
				vscode.window.showWarningMessage('Empty response.');
				return;
			}

			// 5. Show result
			const output = vscode.window.createOutputChannel('Copilot Explanation');
			output.clear();
			output.appendLine('Copilot says:\n');
			output.appendLine(fullText);
			output.show();

			showInWebview(context, fullText);
		
		} catch (error: any) {
			vscode.window.showErrorMessage(`Copilot error: ${error.message || error}`);
		}
	});
	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}


// Function to create and show Webview
function showInWebview(context: vscode.ExtensionContext, explanation: string) {
	const panel = vscode.window.createWebviewPanel(
		'copilotExplanation',
		'Copilot Explanation',
		vscode.ViewColumn.Beside,
		{
		enableScripts: true,
		retainContextWhenHidden: true,
		localResourceRoots: [vscode.Uri.file(path.join(context.extensionPath, 'media'))]
		}
	);

	webviewPanel = panel;

	panel.webview.html = getWebviewContent(explanation, context);

	// Handle messages from webview (e.g., copy button)
	panel.webview.onDidReceiveMessage(message => {
		if (message.command === 'copy') {
		vscode.env.clipboard.writeText(message.text);
		vscode.window.showInformationMessage('Copied to clipboard!');
		}
	}, undefined, context.subscriptions);
}

function getWebviewContent(explanation: string, context: vscode.ExtensionContext): string {
	const scriptUri = vscode.Uri.file(path.join(context.extensionPath, 'media', 'script.js'));
	const styleUri = vscode.Uri.file(path.join(context.extensionPath, 'media', 'style.css'));

	const scriptSrc = webviewPanel?.webview.asWebviewUri(scriptUri);
	const styleSrc = webviewPanel?.webview.asWebviewUri(styleUri);

	// Escape HTML to prevent XSS
	const safeHtml = explanation
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;');

	return `
	<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Copilot Explanation</title>
	<link href="${styleSrc}" rel="stylesheet">
	</head>
	<body>
	<div class="container">
		<h1>Copilot Explanation</h1>
		<button id="copyBtn">Copy</button>
		<pre><code id="explanation">${safeHtml}</code></pre>
	</div>

	<script src="${scriptSrc}"></script>
	</body>
	</html>`;
}
