// import * as esprima from 'esprima';
// import * as fs from 'fs';
// import * as path from 'path';
// // Load JS file
// const filePath = './inputs/example.js';
// const code = fs.readFileSync(filePath, 'utf-8');
// // Parse to AST
// const ast = esprima.parseScript(code, { range: true, loc: true });
// // Arrays to store results
// type lineBoundary = {
//     startLine: number,
//     endLine: number
// }
// const functions: string[] = [];
// const statements: string[] = [];
// const functionLines: lineBoundary[] = [];
// const statementLines: lineBoundary[] = [];
// // Helper to extract code from range
// const getCode = (range: [number, number]) => code.slice(range[0], range[1]);
// // Iterate top-level nodes
// ast.body.forEach(node => {
//     switch (node.type) {
//         case 'FunctionDeclaration':
//             functions.push(getCode(node.range as [number, number]));
//             break;
//         case 'VariableDeclaration':
//             // Check if variable is a function expression or arrow function
//             node.declarations.forEach(decl => {
//                 if (decl.init && 
//                     (decl.init.type === 'FunctionExpression' || decl.init.type === 'ArrowFunctionExpression')) {
//                     functions.push(getCode(decl.range as [number, number]));
//                     functionLines.push({startLine: decl.loc?.start.line || -1, endLine: decl.loc?.end.line || -1})
//                 } else {
//                     statements.push(getCode(decl.range as [number, number]));
//                     statementLines.push({startLine: decl.loc?.start.line || -1, endLine: decl.loc?.end.line || -1})
//                 }
//             });
//             break;
//         default:
//             statements.push(getCode(node.range as [number, number]));
//     }
// });
// console.log('--- Functions ---');
// functions.forEach((f, index) => console.log(f, '\n', functionLines[index]));
// console.log('--- Statements ---');
// statements.forEach((s, index) => console.log(s, '\n', statementLines[index]));
import * as esprima from "esprima";
import { promises as fsPromises } from "fs";
import * as path from "path";
// ---------------------------------------------
// 1. Find all JS files (same as findPythonFiles)
// ---------------------------------------------
export async function findJsFiles(rootDir) {
    const jsFiles = [];
    async function traverseDirectory(dir) {
        const entries = await fsPromises.readdir(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
                await traverseDirectory(fullPath);
            }
            else if (entry.isFile() && fullPath.endsWith(".js")) {
                jsFiles.push(fullPath);
            }
        }
    }
    await traverseDirectory(rootDir);
    return jsFiles;
}
// -------------------------------------------------------
// 2. Split JS into chunks: functions + top-level statements
// -------------------------------------------------------
async function splitJsCode(filePath, code) {
    const ast = esprima.parseScript(code, { range: true, loc: true });
    const chunks = [];
    const getCode = (range) => code.slice(range[0], range[1]);
    ast.body.forEach(node => {
        switch (node.type) {
            case "FunctionDeclaration":
                chunks.push({
                    content: getCode(node.range),
                    metadata: {
                        filePath,
                        type: "function",
                        ext: "js",
                    }
                });
                break;
            case "VariableDeclaration":
                node.declarations.forEach(decl => {
                    if (decl.init &&
                        (decl.init.type === "FunctionExpression" ||
                            decl.init.type === "ArrowFunctionExpression")) {
                        chunks.push({
                            content: getCode(decl.range),
                            metadata: {
                                filePath,
                                type: "function",
                                ext: "js",
                            }
                        });
                    }
                    else {
                        chunks.push({
                            content: getCode(decl.range),
                            metadata: {
                                filePath,
                                type: "statements",
                                ext: "js",
                            }
                        });
                    }
                });
                break;
            default:
                chunks.push({
                    content: getCode(node.range),
                    metadata: {
                        filePath,
                        type: "statements",
                        ext: "js",
                    }
                });
                break;
        }
    });
    return chunks;
}
// -----------------------------------------------------------
// 3. Read files concurrently and generate unified chunk result
// -----------------------------------------------------------
async function readJsFilesConcurrently(jsFiles) {
    let totalCharacters = 0;
    let maxChars = 0;
    let chunks = [];
    const concurrencyLimit = 100;
    const batches = Array.from({ length: Math.ceil(jsFiles.length / concurrencyLimit) }, (_, i) => jsFiles.slice(i * concurrencyLimit, (i + 1) * concurrencyLimit));
    for (const batch of batches) {
        const readOperations = batch.map(async (filePath) => {
            try {
                const code = await fsPromises.readFile(filePath, "utf-8");
                const fileChunks = await splitJsCode(filePath, code);
                chunks.push(...fileChunks);
                totalCharacters += code.length;
                maxChars = Math.max(maxChars, code.length);
            }
            catch (error) {
                console.log(`Failed to read file: ${filePath} - ${error}`);
                return null;
            }
        });
        await Promise.all(readOperations);
    }
    return { totalCharacters, maxChars, chunks };
}
// -----------------------------
// 4. Main function → JSON dump
// -----------------------------
export async function processJsFiles(rootDir) {
    const jsFiles = await findJsFiles(rootDir);
    console.log(`Found ${jsFiles.length} JS files.`);
    const result = await readJsFilesConcurrently(jsFiles);
    console.log('ss', result);
    const outputPath = "jsCodeChunks.json";
    await fsPromises.writeFile(outputPath, JSON.stringify(result.chunks, null, 2));
    console.log(`JS Chunking completed. Output saved to ${outputPath}`);
}
// Execute (for testing)
const root = "inputs";
processJsFiles(root);
