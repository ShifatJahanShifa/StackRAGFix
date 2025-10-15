import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from "zod";

const FASTAPI_URL = "http://127.0.0.1:8000/retrieve";

async function main() {
  // Start the MCP server automatically when extension is activated
  const server = new McpServer({
    name: "My Extension MCP Server",
    version: "1.0.0",
  });

  server.tool(
    "get-extension-info",
    "Get some information from the extension or backend",
    { query: z.string() },
    async ({ query }) => {
      const res = await fetch(FASTAPI_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      return {
        content: [
          { type: "text", text: JSON.stringify(data, null, 2) },
        ],
      };
    }
  );

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log("✅ MCP server running via stdio transport");
}

main().catch((err) => {
  console.error("❌ MCP server failed:", err);
});
