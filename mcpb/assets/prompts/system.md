# avatar-pipeline-mcp System Guide

Avatar Pipeline MCP is a VRM avatar creative pipeline orchestrator that chains vroidstudio-mcp brute-force export, Blender VRM validation/reexport, and VTube Studio staging. It provides a single portmanteau tool (`avatar_pipeline`) with multiple operations for the complete avatar creation workflow.

## Tools Reference

### `avatar_pipeline` (Portmanteau)

The avatar_pipeline tool is the sole MCP tool for this server. It consolidates all pipeline operations into a single interface using an `operation` discriminator parameter.

**Parameters:**
- `operation` (str, required, default: "status"): The pipeline operation to execute. Must be one of:
  - "status": Check pipeline status and work directory state
  - "vroid_quick_avatar": Export a quick avatar from VRoid Studio
  - "hub_stage_file": Stage a local VRM file into the pipeline
  - "blender_validate": Validate a VRM file using Blender headless import
  - "blender_reexport": Re-export a VRM file using Blender's VRM addon
  - "stage_for_vts": Stage a VRM for VTube Studio consumption
  - "full_pipeline": Run the complete pipeline from VRoid to VTube staging
  - "list_staging": List all files in staging, output, and VTube directories
- `vrm_filename` (str, optional, default: "anime_gal.vrm"): VRM filename in staging/output directories
- `source_path` (str, optional, default: ""): Local file path for `hub_stage_file` operation only
- `output_name` (str, optional, default: ""): Output VRM name for re-export operations
- `pick_sample` (bool, optional, default: True): Whether to use VRoid sample model
- `skip_vroid` (bool, optional, default: False): For `full_pipeline`, skip VRoid step if VRM already exists
- `label` (str, optional, default: "pipeline_avatar"): Staging label for VTube Studio

**Returns:**
All operations return structured dictionaries with a `success` boolean and operation-specific data fields.

#### Operation: `status`

Returns the current pipeline state including work directory, staged files, output files, and VRoid Studio URL.

```json
{
  "success": true,
  "work_dir": "C:\\Users\\user\\AppData\\Local\\Temp\\avatar_pipeline",
  "staging": ["anime_gal.vrm"],
  "outputs": ["anime_gal_fixed.vrm"],
  "vroid_url": "http://127.0.0.1:10881",
  "mode": "orchestrator"
}
```

#### Operation: `vroid_quick_avatar`

Exports a quick avatar from VRoid Studio by calling the vroidstudio-mcp fleet tool with `operation: quick_gal_export`. The exported VRM is copied to the staging directory.

**Parameters used:** `vrm_filename`, `pick_sample`

```json
{
  "success": true,
  "export_path": "/path/to/vrm/output.vrm",
  "staged_path": "/staging/anime_gal.vrm",
  "size_kb": 5120.5
}
```

#### Operation: `hub_stage_file`

Copies a VRM file from a local filesystem path into the pipeline's staging directory.

**Parameters used:** `source_path` (required), `vrm_filename`

```json
{
  "success": true,
  "staged_path": "/staging/my_avatar.vrm",
  "size_kb": 4800.2
}
```

**Errors:**
- Returns `success: false` if `source_path` is empty
- Returns `success: false` if the source file does not exist

#### Operation: `blender_validate`

Imports a VRM file headlessly into Blender and reports mesh/armature statistics. Validates that the VRM can be correctly imported before downstream operations.

**Parameters used:** `vrm_filename`

```json
{
  "success": true,
  "meshes": 1,
  "armatures": 1,
  "objects": ["Armature", "Body", "Face", "Hair"],
  "vrm_path": "/staging/anime_gal.vrm"
}
```

**Errors:**
- Returns error if Blender is not reachable at BLENDER_MCP_URL
- Returns error if VRM import fails (corrupt file, unsupported features)
- Returns error if VRM not found in staging or output directories

#### Operation: `blender_reexport`

Imports a VRM into Blender and re-exports it via the Blender VRM addon. This can fix common VRM issues like incorrect bone roll, missing blend shapes, or invalid export settings.

**Parameters used:** `vrm_filename`, `output_name`

```json
{
  "success": true,
  "source": "/staging/anime_gal.vrm",
  "export_path": "/output/anime_gal_fixed.vrm",
  "size_kb": 4900.8
}
```

**Errors:**
- Returns error if Blender validation step fails
- Returns error if re-exported file is not produced

#### Operation: `stage_for_vts`

Copies a VRM file into a VTube Studio staging subdirectory with a JSON manifest file containing metadata for VTube API integration.

**Parameters used:** `vrm_filename`, `label`

```json
{
  "success": true,
  "staged_path": "/staging/vts/anime_gal.vrm",
  "manifest": "/staging/vts/anime_gal.manifest.json",
  "size_kb": 5100.3
}
```

The manifest file content:
```json
{
  "label": "pipeline_avatar",
  "vrm_file": "anime_gal.vrm",
  "vts_hint": "Load via VTube Studio UI or pyvts LoadModelV2Request",
  "vts_api": "ws://localhost:8001"
}
```

#### Operation: `full_pipeline`

Executes the complete pipeline in sequence:

1. **VRoid quick export** (or skip if `skip_vroid=true` and VRM exists)
2. **Blender validation** of the exported VRM
3. **VTube Studio staging** with manifest generation

Returns a detailed step-by-step report including each sub-operation's result.

```json
{
  "success": true,
  "vrm_filename": "anime_gal.vrm",
  "staged_path": "/staging/anime_gal.vrm",
  "steps": [
    {
      "step": "vroid_quick_avatar",
      "success": true,
      "export_path": "/tmp/vroid_export.vrm"
    },
    {
      "step": "blender_validate",
      "success": true,
      "meshes": 1,
      "armatures": 1
    },
    {
      "step": "stage_for_vts",
      "success": true,
      "manifest": "/staging/vts/manifest.json"
    }
  ]
}
```

**Errors:**
- Returns immediate failure with partial steps if any stage fails
- The failed step's error is included in the response
- Previous successful steps are preserved in the steps list

#### Operation: `list_staging`

Lists all files across staging, output, and VTube Studio staging directories with file sizes.

```json
{
  "success": true,
  "files": [
    {"path": "/staging/anime_gal.vrm", "size_kb": 5100.3},
    {"path": "/output/anime_gal_fixed.vrm", "size_kb": 4900.8},
    {"path": "/staging/vts/anime_gal.vrm", "size_kb": 5100.3},
    {"path": "/staging/vts/anime_gal.manifest.json", "size_kb": 0.5}
  ]
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AVATAR_PIPELINE_HOST | 127.0.0.1 | Server bind address |
| AVATAR_PIPELINE_PORT | 10952 | Server HTTP port |
| AVATAR_PIPELINE_WORK_DIR | %TEMP%/avatar_pipeline | Working directory for pipeline staging |
| BLENDER_MCP_URL | http://127.0.0.1:10849 | Blender MCP server URL for VRM validation/reexport |
| VROIDSTUDIO_MCP_URL | http://127.0.0.1:10881 | VRoid Studio MCP server URL for avatar export |
| PYWINAUTO_MCP_URL | http://127.0.0.1:10789 | pywinauto MCP server URL (fleet integration) |

### Directory Structure

The server creates and manages these directories under the work directory:

- `staging/`: Incoming VRM files ready for processing
- `staging/vts/`: VRM files staged for VTube Studio consumption
- `output/`: Processed/re-exported VRM files
- `hub/`: Cross-fleet exchange files

## REST API

### GET /health
Returns server health status with uptime.

```json
{"status": "ok", "uptime_s": 3600.0}
```

### GET /api/v1/download/{filename}
Downloads a pipeline file (from output, staging, or VTube directories).

**Response:** Binary file download with appropriate content-type.

### POST /api/v1/control/tool
Executes a pipeline tool via REST.

**Request:**
```json
{
  "tool": "avatar_pipeline",
  "arguments": {
    "operation": "status"
  }
}
```

### Mounted MCP Endpoint
The FastMCP app is mounted at `/mcp` for streamable HTTP MCP transport, enabling SSE-based client connections.

## Fleet Integration

The pipeline relies on HTTP communication with these fleet MCP servers:

| Server | Default URL | Purpose |
|--------|-------------|---------|
| vroidstudio-mcp | http://127.0.0.1:10881 | VRoid Studio avatar export |
| blender-mcp | http://127.0.0.1:10849 | VRM validation and re-export |
| pywinauto-mcp | http://127.0.0.1:10789 | Fleet UI automation |

All fleet calls use httpx with configurable timeouts (default 300s for Blender operations, 120s for downloads).

## Error Handling

All tool calls return structured error responses:

```json
{
  "success": false,
  "error": "VRM not in staging: anime_gal.vrm",
  "tool": "avatar_pipeline"
}
```

Common error scenarios:
- **Missing source file**: `hub_stage_file` with invalid path
- **VRM not found**: Operation requires a VRM that does not exist in staging or output
- **Blender unreachable**: BLENDER_MCP_URL not responding
- **VRoid unreachable**: VROIDSTUDIO_MCP_URL not responding
- **Export failure**: VRoid export command did not produce a file
- **Validation failure**: Blender could not import the VRM (corrupt or incompatible)
- **Re-export failure**: Blender re-export did not produce output file

## Operation Summary Table
| Operation | Complexity | Fleet Dependencies | Typical Duration |
|-----------|-----------|-------------------|-----------------|
| status | None | None | < 1s |
| vroid_quick_avatar | Simple | vroidstudio-mcp | 5-30s |
| hub_stage_file | Simple | None | < 1s |
| blender_validate | Moderate | blender-mcp | 30-120s |
| blender_reexport | Complex | blender-mcp | 60-240s |
| stage_for_vts | Simple | None | < 1s |
| full_pipeline | Complex | Both fleet servers | 2-5 min |
| list_staging | None | None | < 1s |

## Tool Call Examples for Quick Reference
```
avatar_pipeline(operation="status")
avatar_pipeline(operation="vroid_quick_avatar", vrm_filename="test.vrm")
avatar_pipeline(operation="hub_stage_file", source_path="C:/model.vrm")
avatar_pipeline(operation="blender_validate", vrm_filename="test.vrm")
avatar_pipeline(operation="blender_reexport", vrm_filename="test.vrm")
avatar_pipeline(operation="stage_for_vts", vrm_filename="test.vrm", label="v1")
avatar_pipeline(operation="full_pipeline", vrm_filename="test.vrm", label="v1")
avatar_pipeline(operation="list_staging")
```

## Pipeline Resource Requirements Summary
- **Python**: 3.10+ required. Tested with 3.11 and 3.12.
- **FastMCP**: 3.2+ recommended for best compatibility.
- **Disk**: 500 MB minimum, 1+ GB recommended for VRM staging.
- **Network**: Localhost HTTP to fleet servers. 300s timeout for Blender operations.
- **Memory**: ~50 MB for server process. VRM files not loaded by orchestrator.
- **Fleet Dependencies**: vroidstudio-mcp (port 10881), blender-mcp (port 10849).

## Fleet Server Protocol Summary
All fleet communication uses the same HTTP POST protocol:
```
POST /api/v1/control/tool
Content-Type: application/json
Body: {"tool": "tool_name", "arguments": {...}}
Response: {"success": bool, ...}
```
Timeout defaults to 300 seconds for Blender (complex VRM operations) and 120 seconds for downloads. Both are configurable in fleet_http.py.

## Pipeline Configuration Summary

| Setting | Config Method | Default | Notes |
|---------|--------------|---------|-------|
| Server bind | AVATAR_PIPELINE_HOST env | 127.0.0.1 | Change for remote access |
| Server port | AVATAR_PIPELINE_PORT env | 10952 | Must be in fleet range 10700-11500 |
| Work directory | AVATAR_PIPELINE_WORK_DIR env | %TEMP%/avatar_pipeline | Auto-created, must be writable |
| Blender URL | BLENDER_MCP_URL env | http://127.0.0.1:10849 | Blender fleet server endpoint |
| VRoid URL | VROIDSTUDIO_MCP_URL env | http://127.0.0.1:10881 | VRoid fleet server endpoint |
| pywinauto URL | PYWINAUTO_MCP_URL env | http://127.0.0.1:10789 | Fleet UI automation endpoint |

## Operation Usage Quick Reference
```
# Check pipeline health
avatar_pipeline(operation="status")

# Export from VRoid (sample model, fast)
avatar_pipeline(operation="vroid_quick_avatar", vrm_filename="test.vrm", pick_sample=true)

# Export from VRoid (create new model)
avatar_pipeline(operation="vroid_quick_avatar", vrm_filename="new.vrm", pick_sample=false)

# Import existing VRM
avatar_pipeline(operation="hub_stage_file", source_path="C:/model.vrm")

# Validate VRM in Blender
avatar_pipeline(operation="blender_validate", vrm_filename="model.vrm")

# Re-export through Blender (fixes common issues)
avatar_pipeline(operation="blender_reexport", vrm_filename="model.vrm", output_name="model_fixed.vrm")

# Stage for VTube Studio
avatar_pipeline(operation="stage_for_vts", vrm_filename="model.vrm", label="production_avatar")

# Full automated pipeline
avatar_pipeline(operation="full_pipeline", vrm_filename="final.vrm", pick_sample=true, label="v1")

# Full pipeline (skip VRoid if VRM exists)
avatar_pipeline(operation="full_pipeline", vrm_filename="existing.vrm", skip_vroid=true)

# List all pipeline files
avatar_pipeline(operation="list_staging")
```

## Error Response Format

All errors follow a consistent format:
```json
{
  "success": false,
  "error": "Descriptive error message explaining the failure"
}
```

For fleet integration errors, additional context from the downstream server is included:
```json
{
  "success": false,
  "error": "VRoid Studio export failed",
  "blender": {"success": false, "error": "Connection refused"}
}
```

## Server Lifecycle

### Startup Sequence
1. Server loads environment variables from AVATAR_PIPELINE_HOST, AVATAR_PIPELINE_PORT, AVATAR_PIPELINE_WORK_DIR
2. Creates directory structure: staging/, staging/vts/, output/, hub/
3. Registers the avatar_pipeline portmanteau tool with FastMCP
4. Initializes REST API with FastAPI, mounting /health, /api/v1/download/{filename}, /api/v1/control/tool
5. Mounts FastMCP app at /mcp for streamable HTTP MCP connections
6. Starts uvicorn server on the configured host and port
7. Logs startup confirmation and waits for MCP client connections

### Shutdown Sequence
1. There is no explicit shutdown tool - terminate the server process gracefully
2. In-flight operations will complete or be interrupted based on OS signal handling
3. Fleet HTTP connections are not explicitly closed (handled by httpx internal pooling)
4. Work directory files persist on disk after shutdown
5. No cleanup of staging/output directories on shutdown

### Error Recovery
If the server crashes during a pipeline operation:
- Fleet servers may have incomplete operations (orphaned VRoid exports)
- Staging directory may contain incomplete files
- Call list_staging to inspect current state
- Discard incomplete files and restart the affected operation
- The download endpoint can retrieve any successfully created files

## Workflow Sequences

### Full Production Pipeline
1. Ensure vroidstudio-mcp and blender-mcp fleet servers are running
2. Call `avatar_pipeline(operation="vroid_quick_avatar", vrm_filename="production_model.vrm", pick_sample=false)` to create from VRoid
3. Call `avatar_pipeline(operation="blender_validate", vrm_filename="production_model.vrm")` to verify import
4. If validation passes, call `avatar_pipeline(operation="blender_reexport", vrm_filename="production_model.vrm")` to ensure clean export
5. Call `avatar_pipeline(operation="stage_for_vts", vrm_filename="production_model.vrm", label="production_v1")` to prepare for VTube
6. Verify final files with `avatar_pipeline(operation="list_staging")`
7. The staged VRM with manifest is ready for VTube Studio consumption

### Quick Avatar Creation Flow
1. Call status to check pipeline readiness
2. Call vroid_quick_avatar to generate a sample avatar
3. Call blender_validate to confirm it imports correctly
4. Call stage_for_vts to prepare for immediate use
5. The full pipeline can be run in a single step using full_pipeline operation

### External File Import Flow
1. Obtain a VRM file from any source (download, 3D modeling tool, asset store)
2. Call `avatar_pipeline(operation="hub_stage_file", source_path="C:/downloads/model.vrm")` to import
3. Call `avatar_pipeline(operation="blender_validate", vrm_filename="model.vrm")` to check quality
4. If issues found, call `blender_reexport` to fix
5. Call `stage_for_vts` with appropriate label
6. Verify with list_staging

### Batch Processing Flow
1. Collect multiple VRM files in a directory
2. For each file, call hub_stage_file to import
3. Use list_staging to track imported files
4. Run blender_validate on each staged VRM
5. Run stage_for_vts with unique labels per avatar
6. Track all staged files with list_staging

### Validation and Repair Flow
1. Stage a VRM file into the pipeline
2. Run blender_validate to check structural integrity
3. If validate fails, analyze the error message
4. Try blender_reexport to fix common VRM issues (incorrect bone roll, missing blend shapes, invalid export settings)
5. Re-validate the re-exported file
6. If still failing, the VRM may need manual editing in Blender
7. Stage for VTube only after successful validation

## Architecture

The server follows an orchestrator pattern, delegating all file operations to specialized fleet MCP servers:

```
avatar-pipeline-mcp (orchestrator)
  |-- vroidstudio-mcp (VRoid Studio automation)
  |     |-- quick_gal_export: generate avatar from VRoid
  |-- blender-mcp (Blender headless operations)
  |     |-- script_execute: run Python scripts in Blender
  |     |-- validate VRM import
  |     |-- re-export VRM with fixes
  |-- VTube Studio (external target)
        |-- WebSocket API (ws://localhost:8001)
        |-- LoadModelV2Request for model loading
```

The pipeline uses three staging directories:
- **staging/**: Incoming VRM files ready for validation
- **output/**: Processed and re-exported VRM files
- **staging/vts/**: VRM files with manifests for VTube Studio

This separation allows for clear workflow tracking and rollback capabilities.

## Data Flow

### VRM Export Path
1. VRoid Studio exports VRM to temporary location
2. Pipeline copies VRM to staging directory
3. Blender imports VRM, validates mesh/armature structure
4. If re-export requested, Blender writes clean VRM to output directory
5. VTube staging copies VRM to vts subdirectory with manifest
6. VTube Studio loads from staging/vts via WebSocket API

### File Resolution Order
When an operation needs to find a VRM file:
1. Check staging directory first
2. Fall back to output directory
3. Return error if not found in either

## Performance Considerations

- VRM files average 3-10 MB for standard avatars
- Blender operations are the bottleneck (30-180s for complex models)
- VRoid export is fast (< 5s for sample models)
- Pipeline staging uses file copies, not symlinks
- Fleet HTTP calls use 300s timeout for Blender operations
- Download operations use 120s timeout
- Multiple sequential operations can be combined via full_pipeline
- Work directory should have ample disk space (1+ GB recommended)

## Deployment Architecture

The pipeline-server is designed to run alongside fleet MCP servers on the same machine or local network. Recommended deployment:

1. **vroidstudio-mcp**: Runs on the VRoid Studio automation machine (port 10881)
2. **blender-mcp**: Runs on the Blender rendering machine (port 10849) - needs GPU for headless rendering
3. **avatar-pipeline-mcp**: The orchestrator, can run on any machine that can reach both fleet servers

All communication uses HTTP with configurable timeouts. The orchestrator does not require GPU access. Fleet servers should have ample disk space for temporary files.

## Tool Parameter Reference Table

| Parameter | Type | Required | Default | Used By Operations |
|-----------|------|----------|---------|-------------------|
| operation | str | Yes | "status" | All |
| vrm_filename | str | No | "anime_gal.vrm" | vroid_quick_avatar, blender_validate, blender_reexport, stage_for_vts, full_pipeline |
| source_path | str | No | "" | hub_stage_file |
| output_name | str | No | "" | blender_reexport |
| pick_sample | bool | No | true | vroid_quick_avatar, full_pipeline |
| skip_vroid | bool | No | false | full_pipeline |
| label | str | No | "pipeline_avatar" | stage_for_vts, full_pipeline |

## Operation Response Schema Reference

| Operation | Success Fields | Error Fields |
|-----------|---------------|--------------|
| status | work_dir, staging[], outputs[], vroid_url, mode | error msg |
| vroid_quick_avatar | export_path, staged_path, size_kb | error msg |
| hub_stage_file | staged_path, size_kb | error msg |
| blender_validate | meshes, armatures, objects[], vrm_path | error msg |
| blender_reexport | source, export_path, size_kb | error msg |
| stage_for_vts | staged_path, manifest, size_kb | error msg |
| full_pipeline | vrm_filename, staged_path, steps[] | steps[], error msg |
| list_staging | files[] | error msg |

## Cross-Platform Notes

- **Windows**: All operations supported. VRoid Studio automation requires Windows. Blender headless mode works on Windows with the VRM addon.
- **Linux**: Blender operations supported via blender-mcp. VRoid Studio requires Windows or Wine. The orchestrator itself runs on any platform with Python 3.10+.
- **macOS**: Blender operations supported. VRoid Studio not available. Work directory defaults to /tmp/avatar_pipeline.

## Internal Data Model

The server maintains the following state:

- **STAGING_DIR** (Path): Directory for incoming VRM files. Created on startup. Files placed by vroid_quick_avatar and hub_stage_file.
- **OUTPUT_DIR** (Path): Directory for re-exported VRM files. Created on startup. Files placed by blender_reexport.
- **HUB_DIR** (Path): Directory for cross-fleet file exchange. Created on startup.
- **VTS_DIR** (Path): Subdirectory of staging for VTube-ready files with manifests.

Each operation creates or reads files in these directories. The server does not maintain an in-memory database of files - it scans directories on each list_staging call.

## Resource Requirements

- **Disk**: Minimum 500 MB free for staging. 1+ GB recommended for active pipeline use. VRM files average 3-10 MB each.
- **Memory**: ~50 MB for the server process. Individual VRM files are not loaded into memory by the orchestrator.
- **Network**: Fleet server URLs must be reachable. Defaults use localhost. Timeout set to 300 seconds for Blender operations.
- **CPU**: Minimal - the orchestrator is I/O bound waiting for fleet HTTP responses. Blender operations consume significant CPU/GPU on the blender-mcp host.

## Fleet Communication Protocol

### Request Format
All fleet tool calls use HTTP POST to /api/v1/control/tool with JSON body:
```json
{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1"
  }
}
```

### Response Format
Fleet servers must return JSON with at minimum a "success" boolean:
```json
{
  "success": true,
  ... operation-specific fields ...
}
```

On error:
```json
{
  "success": false,
  "error": "Human-readable error description"
}
```

### Timeout Configuration
- Default fleet call timeout: 300 seconds (Blender operations)
- Download timeout: 120 seconds
- These can be adjusted by modifying the timeout parameter in fleet_http.py

## Directory and File Management

### Work Directory
Controlled by AVATAR_PIPELINE_WORK_DIR (default: %TEMP%/avatar_pipeline). The server creates these subdirectories on startup:

- staging/: Incoming VRM files ready for processing. Files are placed here by hub_stage_file and vroid_quick_avatar.
- staging/vts/: VTube Studio ready copies. Each file here has a corresponding .manifest.json with metadata.
- output/: Processed/re-exported VRM files. Created by blender_reexport.
- hub/: Cross-fleet exchange directory for sharing files with other MCP servers.

### File Resolution Order
When an operation needs to find a VRM file (blender_validate, blender_reexport, stage_for_vts):
1. Check staging/ directory for the filename
2. Fall back to output/ directory
3. If not found in either, return error: "VRM not in staging: filename"

### File Cleanup
The pipeline does not automatically clean up files. Files accumulate in the work directory until manually deleted. For large batch operations, periodically review and clean up using list_staging to identify files.

## Version Compatibility

The server requires compatible versions of:
- vroidstudio-mcp: provides quick_gal_export operation
- blender-mcp: provides script_execute with VRM addon support
- Both servers must accept the /api/v1/control/tool REST API format
- Blender must have VRM addon installed for import/export operations

## Detailed Operation Reference

### Operation: vroid_quick_avatar
The quick avatar export initiates a VRoid Studio export workflow. When pick_sample is true, it uses VRoid's built-in sample model for rapid prototyping. When false, it waits for manual interaction in VRoid Studio. The exported VRM is automatically copied to the staging directory. The response includes the original export_path from VRoid and the new staged_path in the pipeline staging directory.

### Operation: hub_stage_file
This operation copies a VRM file from any accessible filesystem path into the pipeline's staging directory. It validates that the source file exists before copying. The vrm_filename parameter controls the destination filename. If omitted, the original filename is preserved. The response includes size information for verification.

### Operation: blender_validate
The validation operation imports the VRM into Blender headlessly, then reports mesh counts, armature counts, and object names. This is critical for catching VRM compatibility issues early. Common validation failures include: missing mesh data, invalid armature hierarchy, corrupted binary data, and incompatible VRM format versions.

### Operation: blender_reexport
Re-exporting through Blender can fix several common VRM issues: incorrect bone orientations, improperly weighted vertices, missing blend shape export settings, and non-standard material configurations. The re-exported file is saved to the output directory. The operation first validates the VRM can be imported, then exports with optimized settings.

### Operation: stage_for_vts
VTube Studio staging creates a separate copy of the VRM in the staging/vts subdirectory along with a JSON manifest file. The manifest contains: the label (human-readable identifier), the vrm_file reference, a hint for VTube Studio loading methods, and the VTube Studio WebSocket API endpoint. This makes it easy for pyvts or the VTube Studio UI to discover and load the avatar.

### Operation: full_pipeline
The complete pipeline executes three stages in sequence: VRoid export (or skip if skip_vroid is true and VRM exists), Blender validation, and VTube staging. The detailed step-by-step response includes status from each stage for audit purposes. If any stage fails, the pipeline stops and returns the error along with successful steps completed so far.

### Operation: list_staging
Lists all files in the staging, output, and VTube directories. Each file includes its full path and size. This is useful for inventory management and tracking pipeline progress. Empty directories are omitted from the results.
