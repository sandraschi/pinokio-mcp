# pinokio-mcp (MCPB Bundle)

MCP server for controlling Pinokio - the 1-click localhost cloud for AI apps

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "pinokio-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "pinokio_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **app_management**: app_management

## Requirements

- Python 3.12+
- uv
