// src/index.ts
// function greet(name: string): string {
//     return `Hello, ${name}!`;
// }
// console.log(greet("TypeScript"));
import * as esprima from 'esprima';
import * as fs from 'fs';
// Load JS file
const filePath = 'example.js';
const code = fs.readFileSync(filePath, 'utf-8');
// Parse to AST
const ast = esprima.parseScript(code, { range: true });
// Arrays to store results
const functions = [];
const statements = [];
// Helper to extract code from range
const getCode = (range) => code.slice(range[0], range[1]);
// Iterate top-level nodes
ast.body.forEach(node => {
    switch (node.type) {
        case 'FunctionDeclaration':
            functions.push(getCode(node.range));
            break;
        case 'VariableDeclaration':
            // Check if variable is a function expression or arrow function
            node.declarations.forEach(decl => {
                if (decl.init &&
                    (decl.init.type === 'FunctionExpression' || decl.init.type === 'ArrowFunctionExpression')) {
                    functions.push(getCode(decl.range));
                }
                else {
                    statements.push(getCode(decl.range));
                }
            });
            break;
        default:
            statements.push(getCode(node.range));
    }
});
console.log('--- Functions ---');
functions.forEach(f => console.log(f, '\n'));
console.log('--- Statements ---');
statements.forEach(s => console.log(s, '\n'));
