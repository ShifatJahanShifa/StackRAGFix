import * as esprima from "esprima";
import { promises as fsPromises } from "fs";
import * as path from "path";


export async function findJsFiles(rootDir: string): Promise<string[]> {
    const jsFiles: string[] = [];

    async function traverseDirectory(dir: string) {
        const entries = await fsPromises.readdir(dir, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);

            if (entry.isDirectory()) {
                await traverseDirectory(fullPath);
            } else if (entry.isFile() && fullPath.endsWith(".js")) {
                jsFiles.push(fullPath);
            }
        }
    }

    await traverseDirectory(rootDir);
    return jsFiles;
}

async function splitJsCode(filePath: string, code: string) {
    const ast = esprima.parseScript(code, { range: true, loc: true });

    const chunks: {
        content: string;
        metadata: {
            filePath: string;
            type: "function" | "statements";
            ext: 'js' ;
        };
    }[] = [];

    const getCode = (range: [number, number]) => code.slice(range[0], range[1]);

    ast.body.forEach(node => {
        switch (node.type) {
            case "FunctionDeclaration":
                chunks.push({
                    content: getCode(node.range as [number, number]),
                    metadata: {
                        filePath,
                        type: "function",
                        ext: 'js',
                    }
                });
                break;

            case "VariableDeclaration":
                node.declarations.forEach(decl => {
                    if (
                        decl.init &&
                        (decl.init.type === "FunctionExpression" ||
                            decl.init.type === "ArrowFunctionExpression")
                    ) {
                        chunks.push({
                            content: getCode(decl.range as [number, number]),
                            metadata: {
                                filePath,
                                type: "function",
                                ext: 'js',
                            }
                        });
                    } else {
                        chunks.push({
                            content: getCode(decl.range as [number, number]),
                            metadata: {
                                filePath,
                                type: "statements",
                                ext: 'js',
                            }
                        });
                    }
                });
                break;

            default:
                chunks.push({
                    content: getCode(node.range as [number, number]),
                    metadata: {
                        filePath,
                        type: "statements",
                        ext: 'js',
                    }
                });
                break;
        }
    });

    return chunks;
}

async function readJsFilesConcurrently(jsFiles: string[]) {
    let totalCharacters = 0;
    let maxChars = 0;

    let chunks: Array<{
        content: string;
        metadata: {
            filePath: string;
            type: "function" | "statements";
            ext: 'js';
        };
    }> = [];

    const concurrencyLimit = 100;
    const batches = Array.from(
        { length: Math.ceil(jsFiles.length / concurrencyLimit) },
        (_, i) => jsFiles.slice(i * concurrencyLimit, (i + 1) * concurrencyLimit)
    );

    for (const batch of batches) {
        const readOperations = batch.map(async (filePath) => {
            try {
                const code = await fsPromises.readFile(filePath, "utf-8");
                const fileChunks = await splitJsCode(filePath, code);
                chunks.push(...fileChunks);

                totalCharacters += code.length;
                maxChars = Math.max(maxChars, code.length);
            } catch (error) {
                console.log(`Failed to read file: ${filePath} - ${error}`);
                return null;
            }
        });

        await Promise.all(readOperations);
    }

    return { totalCharacters, maxChars, chunks };
}


export async function processJsFiles(rootDir: string) {
    const jsFiles = await findJsFiles(rootDir);
    console.log(`Found ${jsFiles.length} JS files.`);

    const result = await readJsFilesConcurrently(jsFiles);
    console.log('DEBUG: code chunk', result);
    return result.chunks;
    // const outputPath = "jsCodeChunks.json";
    // await fsPromises.writeFile(outputPath, JSON.stringify(result.chunks, null, 2));

    // console.log(`JS Chunking completed. Output saved to ${outputPath}`);
}
