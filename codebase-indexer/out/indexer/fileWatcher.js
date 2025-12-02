// // src/indexer/watcher.ts
// import * as vscode from "vscode";
// import { generateEmbedding } from "./embedder";
// import { saveEmbedding } from "./vectorStore";
// export function watchFiles() {
//   const watcher = vscode.workspace.createFileSystemWatcher("**/*.py");
//   watcher.onDidCreate(async (uri) => {
//     const embedding = await generateEmbedding(uri.fsPath);
//     saveEmbedding(uri.fsPath, embedding);
//     vscode.window.showInformationMessage(`Indexed new file: ${uri.fsPath}`);
//   });
//   watcher.onDidChange(async (uri) => {
//     const embedding = await generateEmbedding(uri.fsPath);
//     saveEmbedding(uri.fsPath, embedding);
//     vscode.window.showInformationMessage(`Re-indexed modified file: ${uri.fsPath}`);
//   });
//   watcher.onDidDelete((uri) => {
//     vscode.window.showInformationMessage(`Deleted file: ${uri.fsPath}`);
//   });
// }
import * as vscode from "vscode";
import * as fs from "fs";
import { addToVectorStore } from "./vectorStore.js";
export function watchFiles() {
    const watcher = vscode.workspace.createFileSystemWatcher("**/*.{py,js}");
    watcher.onDidCreate(async (uri) => {
        const content = fs.readFileSync(uri.fsPath, "utf-8");
        await addToVectorStore(uri.fsPath, content);
        vscode.window.showInformationMessage(`Indexed new file: ${uri.fsPath}`);
    });
    watcher.onDidChange(async (uri) => {
        const content = fs.readFileSync(uri.fsPath, "utf-8");
        await addToVectorStore(uri.fsPath, content);
        vscode.window.showInformationMessage(`Re-indexed modified file: ${uri.fsPath}`);
    });
    watcher.onDidDelete(async (uri) => {
        vscode.window.showInformationMessage(`Deleted file: ${uri.fsPath}`);
    });
}
//# sourceMappingURL=fileWatcher.js.map