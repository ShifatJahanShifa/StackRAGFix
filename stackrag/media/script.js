const vscode = acquireVsCodeApi();

document.getElementById('copyBtn').addEventListener('click', () => {
  const text = document.getElementById('explanation').innerText;
  vscode.postMessage({ command: 'copy', text });
});