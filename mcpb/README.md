# avatar-pipeline-mcp (MCPB Bundle)

VRM avatar creative pipeline — VRoid brute-force, Blender validate, VTube staging.

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "avatar-pipeline-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "avatar_pipeline_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **avatar_pipeline**: avatar_pipeline

## Requirements

- Python 3.12+
- uv
