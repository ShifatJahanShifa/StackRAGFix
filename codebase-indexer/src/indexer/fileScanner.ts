// import * as vscode from "vscode";
// import * as fs from "fs";
// import * as path from "path";

// export async function scanWorkspace(): Promise<string[]> {
//   const workspaceFolders = vscode.workspace.workspaceFolders;
//   if (!workspaceFolders) return [];

//   const files: string[] = [];
//   for (const folder of workspaceFolders) {
//     await readDirRecursive(folder.uri.fsPath, files);
//   }
//   return files.filter(f => f.endsWith(".py")); // only python for now
// }

// async function readDirRecursive(dir: string, fileList: string[]) {
//   const entries = fs.readdirSync(dir, { withFileTypes: true });
//   for (const entry of entries) {
//     const fullPath = path.join(dir, entry.name);
//     if (entry.isDirectory()) {
//       await readDirRecursive(fullPath, fileList);
//     } else {
//       fileList.push(fullPath);
//     }
//   }
// }



import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";

export async function scanWorkspace(): Promise<string[]> {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders) return [];

  const files: string[] = [];
  for (const folder of workspaceFolders) {
    await readDirRecursive(folder.uri.fsPath, files);
  }
  return files.filter(f => f.endsWith(".py") || f.endsWith(".js"));
}

async function readDirRecursive(dir: string, fileList: string[]) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await readDirRecursive(fullPath, fileList);
    } else {
      fileList.push(fullPath);
    }
  }
}
