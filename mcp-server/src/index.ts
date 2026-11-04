import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { isMainModule } from "./entry-guard.js";
import { type McpSurfaceOptions, registerMcpSurface } from "./toolsets/registry.js";

export const SERVER_INSTRUCTIONS = [
  "av-kit is a local YouTube read/consume toolkit. Never upload or write to YouTube.",
  "Downloads: avkit_download add → start → list until processor Idle. Pause is queue-level; items have no Paused status.",
  "Transcripts: add channel → start → get. Output is files (output_dir); tools return paths and counts, not transcript text.",
  "TTS: load a model first; prepare is preview only; generate returns the job at once; poll get; cancel stops a running job.",
  "Destructive actions require confirm: true. Download, transcript and convert remove/clear keep files on disk. Capture remove deletes the shot's files; capture flatten overwrites the image file (after a backup when capture.flatten_backup is on; a JPEG/WebP shot gets a new PNG copy instead); capture revert overwrites it from its newest backup. These three capture actions also ask the user in the IDE and are refused unless the user accepts; call them only when the user explicitly asked.",
  "Convert is local files only; never upload YouTube.",
  "Capture is local screen plus local inbox files; never upload YouTube. capture_interactive needs the desktop app overlay.",
  "Settings use leaf keys (quality, not downloader.quality) and namespace.",
  "Setup: the desktop app's Settings → MCP card shows a per-client setup prompt.",
].join("\n");

export function createServer(options: McpSurfaceOptions = {}): McpServer {
  const server = new McpServer(
    { name: "av-kit", version: "0.1.0-rc.1" },
    { instructions: SERVER_INSTRUCTIONS },
  );
  registerMcpSurface(server, options);
  return server;
}

export async function main(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

if (isMainModule(process.argv[1], import.meta.url)) {
  void main();
}
