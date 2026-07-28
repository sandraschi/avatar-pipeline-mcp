# avatar-pipeline-mcp User Guide

Avatar Pipeline MCP orchestrates the VRM avatar creative pipeline from VRoid Studio export through Blender validation and re-export to VTube Studio staging. It chains multiple fleet MCP servers into a single streamlined workflow.

## Installation

### Prerequisites

- Python 3.10+
- Blender with VRM addon installed (for validation/reexport)
- VRoid Studio (for avatar export)
- VTube Studio (for final avatar hosting)

### Quick Install

```bash
git clone https://github.com/sandraschi/avatar-pipeline-mcp.git
cd avatar-pipeline-mcp
uv sync
```

### MCP Client Configuration

**Claude Desktop:**
```json
{
  "mcpServers": {
    "avatar-pipeline-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/avatar-pipeline-mcp", "python", "-m", "avatar_pipeline_mcp"],
      "env": {
        "AVATAR_PIPELINE_WORK_DIR": "C:/pipeline_work"
      }
    }
  }
}
```

**Cursor:**
```json
{
  "mcpServers": {
    "avatar-pipeline-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/avatar-pipeline-mcp", "python", "-m", "avatar_pipeline_mcp"]
    }
  }
}
```

## Tutorials

### Tutorial 1: Check Pipeline Status

Start by checking the current state of the pipeline:

```python
result = await avatar_pipeline(operation="status")
print(f"Work directory: {result['work_dir']}")
print(f"Staged files: {result['staging']}")
print(f"Output files: {result['outputs']}")
print(f"VRoid URL: {result['vroid_url']}")
```

Expected output:
```
Work directory: C:\Users\user\AppData\Local\Temp\avatar_pipeline
Staged files: ['anime_gal.vrm']
Output files: ['anime_gal_fixed.vrm']
VRoid URL: http://127.0.0.1:10881
```

### Tutorial 2: Export Avatar from VRoid Studio

Quick-export an avatar from VRoid Studio:

```python
result = await avatar_pipeline(
    operation="vroid_quick_avatar",
    vrm_filename="my_design.vrm",
    pick_sample=True
)
if result["success"]:
    print(f"Exported to: {result['export_path']}")
    print(f"Staged as: {result['staged_path']}")
    print(f"Size: {result.get('size_kb', 'unknown')} KB")
```

For production work (no sample selection):
```python
result = await avatar_pipeline(
    operation="vroid_quick_avatar",
    vrm_filename="production_design.vrm",
    pick_sample=False
)
```

### Tutorial 3: Stage a Local VRM File

Bring an existing VRM file into the pipeline:

```python
result = await avatar_pipeline(
    operation="hub_stage_file",
    source_path="C:/MyProjects/custom_avatar.vrm",
    vrm_filename="custom_avatar.vrm"
)
if result["success"]:
    print(f"Staged path: {result['staged_path']}")
    print(f"Size: {result['size_kb']} KB")
```

### Tutorial 4: Validate VRM with Blender

Check that a VRM imports correctly into Blender:

```python
result = await avatar_pipeline(
    operation="blender_validate",
    vrm_filename="anime_gal.vrm"
)
if result["success"]:
    print(f"Meshes: {result['meshes']}")
    print(f"Armatures: {result['armatures']}")
    print(f"Objects: {result['objects']}")
```

### Tutorial 5: Re-export VRM Through Blender

Fix VRM export issues by re-exporting through Blender:

```python
result = await avatar_pipeline(
    operation="blender_reexport",
    vrm_filename="anime_gal.vrm",
    output_name="anime_gal_fixed.vrm"
)
if result["success"]:
    print(f"Fixed VRM: {result['export_path']}")
    print(f"Size: {result['size_kb']} KB")
```

### Tutorial 6: Stage for VTube Studio

Prepare a VRM for VTube Studio:

```python
result = await avatar_pipeline(
    operation="stage_for_vts",
    vrm_filename="anime_gal.vrm",
    label="production_v1"
)
if result["success"]:
    print(f"VTS path: {result['staged_path']}")
    print(f"Manifest: {result['manifest']}")
```

The manifest file contains:
```json
{
  "label": "production_v1",
  "vrm_file": "anime_gal.vrm",
  "vts_hint": "Load via VTube Studio UI or pyvts LoadModelV2Request",
  "vts_api": "ws://localhost:8001"
}
```

### Tutorial 7: Run the Full Pipeline

Execute the complete pipeline end-to-end:

```python
result = await avatar_pipeline(
    operation="full_pipeline",
    vrm_filename="complete_avatar.vrm",
    pick_sample=True,
    label="final_v1"
)

for step in result["steps"]:
    name = step["step"]
    status = "OK" if step.get("success") else ("SKIPPED" if step.get("skipped") else "FAILED")
    print(f"  {name}: {status}")

if result["success"]:
    print(f"\nFinal VRM: {result['staged_path']}")
```

### Tutorial 8: Full Pipeline with Existing VRM

If the VRM already exists, skip the VRoid export step:

```python
# First stage the file
await avatar_pipeline(
    operation="hub_stage_file",
    source_path="C:/existing.vrm"
)

# Then run full pipeline skipping VRoid
result = await avatar_pipeline(
    operation="full_pipeline",
    vrm_filename="existing.vrm",
    skip_vroid=True
)
```

### Tutorial 9: List All Pipeline Files

View all files currently in the pipeline:

```python
result = await avatar_pipeline(operation="list_staging")
for f in result["files"]:
    print(f"  {f['path']} ({f['size_kb']} KB)")
```

### Tutorial 10: Multi-Export Pipeline Run

Export multiple VRM files through the pipeline:

```python
avatars = ["character_a.vrm", "character_b.vrm", "character_c.vrm"]

for name in avatars:
    print(f"\nProcessing {name}...")
    result = await avatar_pipeline(
        operation="vroid_quick_avatar",
        vrm_filename=name
    )
    if result["success"]:
        result = await avatar_pipeline(
            operation="blender_validate",
            vrm_filename=name
        )
        if result["success"]:
            await avatar_pipeline(
                operation="stage_for_vts",
                vrm_filename=name,
                label=name.replace(".vrm", "")
            )
```

### Tutorial 11: Pipeline with Custom Directory

Set up the pipeline with a non-default work directory:

```python
# Set environment variable
import os
os.environ["AVATAR_PIPELINE_WORK_DIR"] = "D:/pipeline_projects"

# Check it's working
result = await avatar_pipeline(operation="status")
print(f"Work dir: {result['work_dir']}")
```

### Tutorial 12: Validate and Fix Pipeline

Run validation then re-export if issues found:

```python
validate = await avatar_pipeline(
    operation="blender_validate",
    vrm_filename="needs_fix.vrm"
)

if not validate["success"]:
    print(f"Validation failed: {validate.get('error')}")
else:
    print(f"Meshes: {validate['meshes']}, Armatures: {validate['armatures']}")

    if validate["meshes"] > 0:
        reexport = await avatar_pipeline(
            operation="blender_reexport",
            vrm_filename="needs_fix.vrm"
        )
        if reexport["success"]:
            print(f"Re-exported: {reexport['export_path']}")
```

### Tutorial 13: Production Pipeline

Production workflow for creating VTube-ready avatars:

```python
# Step 1: Export from VRoid
export = await avatar_pipeline(
    operation="vroid_quick_avatar",
    vrm_filename="vtuber_avatar.vrm",
    pick_sample=False
)
if not export["success"]:
    print(f"VRoid export failed: {export.get('error')}")
    exit(1)

# Step 2: Validate
validate = await avatar_pipeline(
    operation="blender_validate",
    vrm_filename="vtuber_avatar.vrm"
)
if not validate["success"]:
    print(f"Validation failed, re-exporting...")
    # Re-export to fix issues
    await avatar_pipeline(
        operation="blender_reexport",
        vrm_filename="vtuber_avatar.vrm",
        output_name="vtuber_avatar_fixed.vrm"
    )

# Step 3: Stage for VTube
vts = await avatar_pipeline(
    operation="stage_for_vts",
    vrm_filename="vtuber_avatar.vrm",
    label="vtuber_production"
)
print(f"Ready at: {vts['staged_path']}")
```

### Tutorial 14: Check Fleet Server Availability

Verify that required fleet servers are reachable:

```python
# Check VRoid Studio
vroid = await avatar_pipeline(operation="status")
vroid_url = vroid.get("vroid_url", "http://127.0.0.1:10881")
print(f"VRoid expected at: {vroid_url}")

# Check work directory is writable
import os
work_dir = vroid.get("work_dir", "")
if work_dir:
    can_write = os.access(work_dir, os.W_OK)
    print(f"Work dir writable: {can_write}")
```

### Tutorial 15: Batch Process from Hub

Process multiple avatars staged from the fleet exchange hub:

```python
import json

# Get current staging list
staging = await avatar_pipeline(operation="list_staging")
vrm_files = [f["path"] for f in staging["files"] if f["path"].endswith(".vrm")]

for vrm_path in vrm_files:
    filename = vrm_path.split("/")[-1]
    print(f"Processing: {filename}")
    
    result = await avatar_pipeline(
        operation="blender_validate",
        vrm_filename=filename
    )
    
    if result["success"]:
        await avatar_pipeline(
            operation="stage_for_vts",
            vrm_filename=filename
        )
        print(f"  Validated and staged OK")
    else:
        # Try re-export
        fix = await avatar_pipeline(
            operation="blender_reexport",
            vrm_filename=filename
        )
        if fix["success"]:
            print(f"  Fixed and re-exported")
        else:
            print(f"  FAILED: {result.get('error')}")
```

## REST API Reference

### GET /health

```json
{"status": "ok", "uptime_s": 3600.0}
```

### POST /api/v1/control/tool

**Request:**
```json
{
  "tool": "avatar_pipeline",
  "arguments": {
    "operation": "status"
  }
}
```

**Response:**
```json
{
  "success": true,
  "staging": ["test.vrm"],
  "outputs": [],
  "vroid_url": "http://127.0.0.1:10881",
  "mode": "orchestrator"
}
```

**Full pipeline execution:**
```json
{
  "tool": "avatar_pipeline",
  "arguments": {
    "operation": "full_pipeline",
    "vrm_filename": "new_model.vrm",
    "label": "production"
  }
}
```

### GET /api/v1/download/{filename}

Downloads a file from the pipeline directories. Searches output, staging, and VTube directories in order.

**Response:** Binary file data with Content-Type derived from extension.

## Troubleshooting

### Issue 1: VRoid Studio not reachable
Ensure VRoid Studio is running and the vroidstudio-mcp server is active at VROIDSTUDIO_MCP_URL (default http://127.0.0.1:10881). Check that VRoid Studio is not blocked by a firewall.

### Issue 2: Blender import fails
Verify Blender is installed with the VRM addon enabled. The pipeline uses blender-mcp for headless operations. Check that BLENDER_MCP_URL is correct and Blender is running.

### Issue 3: VRM file not in staging
When performing blender_validate or stage_for_vts, the VRM must already exist in the staging or output directory. Use hub_stage_file first to copy a file in, or vroid_quick_avatar to generate one.

### Issue 4: hub_stage_file path errors
Provide an absolute path to an existing file. Relative paths are resolved from the server's working directory. The source_path must be a valid, readable file.

### Issue 5: Re-export produces no output
Blender's VRM addon may need specific settings. Check that the VRM can be imported (use blender_validate first). The export may fail silently if the output directory is not writable.

### Issue 6: Pipeline step failures
The full_pipeline stops at the first failure. Check each step's error message. Previous successful steps are preserved in the results for audit purposes.

### Issue 7: Manifest file generation fails
Manifest files are written to the VTube staging subdirectory. Ensure there is disk space available and the directory is writable. The manifest contains metadata for pyvts integration.

### Issue 8: Fleet HTTP timeouts
Large VRM files may exceed the 300s timeout. Operations like blender_reexport can take several minutes for complex models. Adjust timeout in fleet_http.py if needed.

### Issue 9: Work directory permissions
The server creates directories under AVATAR_PIPELINE_WORK_DIR. If this is on a restricted path, the server may fail to create staging/output/hub directories. Use a user-writable path.

### Issue 10: Cross-server version mismatches
Ensure vroidstudio-mcp and blender-mcp fleet servers are compatible versions. API changes in downstream servers may cause pipeline failures. Check logs for HTTP 400/500 responses.

### Issue 11: File name collisions
When multiple avatars use the same vrm_filename, files may be overwritten. Use unique filenames per run, or process avatars sequentially with distinct names.

### Issue 12: Empty staging after vroid_quick_avatar
The export_path from VRoid may be empty if the export was cancelled or failed. Check VRoid Studio's UI to ensure export completed. The pipeline expects a valid VRM file on disk.

## FAQ

### What is the avatar pipeline?
A multi-stage workflow that takes avatar designs from VRoid Studio, validates and fixes them in Blender, and stages them for VTube Studio consumption.

### Which fleet servers are required?
vroidstudio-mcp for VRoid export, blender-mcp for validation/reexport, and optionally pywinauto-mcp for fleet UI automation.

### What is the staging directory used for?
The staging directory holds VRM files at various pipeline stages. Staging -> validation -> re-export -> VTube staging. Each stage has its own subdirectory.

### How does Blender validation work?
The pipeline imports the VRM headlessly into Blender via the VRM addon, then reports mesh count, armature count, and object names. This validates the file is importable.

### Can I use my own VRM files?
Yes. Use hub_stage_file to import existing VRM files into the pipeline from any local path.

### What is the manifest file for VTube?
A JSON file containing metadata (label, VRM filename, VTube WebSocket API URL) that helps VTube Studio or pyvts load the avatar.

### Does this delete original files?
No. Original files are copied. The staging/output directories contain copies. Source files specified in hub_stage_file are not modified or deleted.

### Can I run multiple pipelines?
Yes, but only one server instance runs at a time. You can run multiple sequential pipelines with different filenames. Each pipeline execution is independent.

### How do I monitor progress?
Use list_staging to see current files. Use blender_validate results to check file integrity. Use status to see the pipeline overview at any time.

### What happens if a fleet server is down?
The pipeline returns an error immediately with details about which server was unreachable. Previous successful steps are preserved in the response.

### Is VRoid Studio required?
No, but it simplifies avatar creation. You can import any VRM file via hub_stage_file. The vroid_quick_avatar operation is optional.

### What file formats are supported?
VRM 1.0 format (.vrm) is the standard. The pipeline handles VRM import, export, and validation exclusively.

### Can I validate VRM files without Blender?
No, Blender with the VRM addon is required for validation. This ensures consistent, reliable VRM import checking.

### What is the fleet exchange hub?
A cross-repo staging area for sharing files between pipeline components and other MCP servers in the fleet.

### How do I specify the work directory?
Set the AVATAR_PIPELINE_WORK_DIR environment variable. Default is `%TEMP%/avatar_pipeline`. The directory must be writable and have sufficient disk space for VRM files (typically 10-100 MB per avatar).

### Can I run this on Linux?
Yes. The pipeline uses Python and HTTP to communicate with fleet servers. Blender and VRoid Studio run as separate services. The orchestrator itself is cross-platform.

### What happens if Blender doesn't have the VRM addon?
The blender_validate and blender_reexport operations will fail. Install the VRM addon for Blender from the official repository. The server does not validate addon availability.

### Can I skip validation?
Yes. Call stage_for_vts directly without prior validation. This is not recommended for production use but may be useful for testing.

### How do I clean up old files?
The pipeline does not automatically clean up. Manually delete files from staging, output, and vts directories. Use list_staging to identify files for cleanup.

### What is the manifest.json format?
A JSON file containing:
- label: Human-readable label for VTube Studio
- vrm_file: Relative path to the VRM file
- vts_hint: Loading instructions for VTube Studio
- vts_api: WebSocket API endpoint (default ws://localhost:8001)

### Can I use custom Blender scripts?
Yes. The fleet blender-mcp server supports arbitrary Python script execution via the script_execute tool, which the pipeline uses internally for VRM operations.

### What are typical failure modes?
Common failures: VRoid export cancelled by user, Blender VRM addon missing, fleet server unreachable, disk space full, file path contains special characters, network timeout during large file transfers.

### How long does a full pipeline take?
Typical completion times: VRoid export 5-30 seconds, Blender validation 30-120 seconds, Blender re-export 60-240 seconds, VTube staging < 1 second. Total: 2-5 minutes.

### Can I pause and resume the pipeline?
Not directly. Each operation is independent. You can check progress with list_staging between operations. Failed operations can be retried individually.

### What is the vroidstudio-mcp server doing?
It automates VRoid Studio's UI to click through the export process for a quick avatar generation. The `pick_sample` parameter controls whether to use VRoid's sample model or create a new one.

### How are temporary files managed?
The pipeline copies files between directories. Temporary files from fleet servers (like VRoid exports) are cleaned up by those servers. Pipeline staging files persist until manually deleted.

## Additional REST Endpoints

### GET /api/v1/pipeline/status
Returns the current pipeline configuration and environment.
**Response:**
```json
{
  "work_dir": "C:/pipeline",
  "staging_dir": "C:/pipeline/staging",
  "output_dir": "C:/pipeline/output",
  "vroid_url": "http://127.0.0.1:10881",
  "blender_url": "http://127.0.0.1:10849",
  "disk_free_gb": 100.5
}
```

### GET /api/v1/pipeline/stats
Returns pipeline usage statistics.
**Response:**
```json
{
  "total_avatars_processed": 25,
  "total_vroid_exports": 20,
  "total_blender_validates": 22,
  "total_blender_reexports": 5,
  "total_vts_stages": 15,
  "uptime_days": 7.5
}
```

## Advanced Configuration

### Custom Fleet URLs
```bash
export VROIDSTUDIO_MCP_URL=http://192.168.1.100:10881
export BLENDER_MCP_URL=http://192.168.1.100:10849
export PYWINAUTO_MCP_URL=http://192.168.1.100:10789
```

### Pipeline Tuning
- For slow Blender operations: increase timeout in fleet_http.py call_blender_tool timeout parameter
- For large files: ensure work directory has 10x the VRM file size in free space
- For batch processing: run operations sequentially to avoid fleet server overload
- For production: use unique labels per avatar to avoid manifest collisions

## Environment Configuration Summary
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| AVATAR_PIPELINE_HOST | No | 127.0.0.1 | Bind address for the REST server |
| AVATAR_PIPELINE_PORT | No | 10952 | Port for the REST server |
| AVATAR_PIPELINE_WORK_DIR | No | %TEMP%/avatar_pipeline | Working directory for all pipeline files |
| BLENDER_MCP_URL | No | http://127.0.0.1:10849 | URL for the blender-mcp fleet server |
| VROIDSTUDIO_MCP_URL | No | http://127.0.0.1:10881 | URL for the vroidstudio-mcp fleet server |
| PYWINAUTO_MCP_URL | No | http://127.0.0.1:10789 | URL for the pywinauto-mcp fleet server |

## Quick Reference Card

### Pipeline Operations
| Operation | Parameters | Use Case |
|-----------|-----------|----------|
| status | none | Check pipeline state before starting |
| vroid_quick_avatar | vrm_filename, pick_sample | Export avatar from VRoid Studio |
| hub_stage_file | source_path, vrm_filename | Import existing VRM file |
| blender_validate | vrm_filename | Check VRM imports correctly |
| blender_reexport | vrm_filename, output_name | Fix invalid VRM files |
| stage_for_vts | vrm_filename, label | Prepare for VTube Studio |
| full_pipeline | all parameters | Complete automated workflow |
| list_staging | none | View all pipeline files |

### Pipeline Directory Layout
```
AVATAR_PIPELINE_WORK_DIR/
  staging/          # Imported VRM files awaiting processing
  staging/vts/      # VTube-ready copies with manifests
  output/           # Re-exported/fixed VRM files
  hub/              # Cross-fleet file exchange area
```

### Directories Served by Download Endpoint
| Order | Directory | Contents |
|-------|-----------|----------|
| 1 | output/ | Re-exported VRM files |
| 2 | staging/ | Original staged VRM files |
| 3 | staging/vts/ | VTube-ready copies |

### Fleet Dependency Summary
| Server | Default URL | Used By Operations | Timeout |
|--------|------------|-------------------|---------|
| vroidstudio-mcp | http://127.0.0.1:10881 | vroid_quick_avatar, full_pipeline | 300s |
| blender-mcp | http://127.0.0.1:10849 | blender_validate, blender_reexport, full_pipeline | 300s |

## Error Code Reference
| Code | Meaning | Recovery Action |
|------|---------|----------------|
| source_path required | hub_stage_file missing path | Provide absolute source path |
| File not found | Source file does not exist | Check path and permissions |
| VRM not in staging | Operation target missing | Import file first via hub_stage_file or vroid_quick_avatar |
| Blender import failed | VRM file corrupt or incompatible | Re-export from modeling tool |
| VRoid Studio unreachable | vroidstudio-mcp not running | Start vroidstudio-mcp server |
| Blender unreachable | blender-mcp not running | Start blender-mcp server |
| Export cancelled | VRoid export interrupted | Retry vroid_quick_avatar |
| Unknown operation | Invalid operation parameter | Use discover to list valid ops |

## Common Workflows Summary

### Quick Test
1. avatar_pipeline(operation="vroid_quick_avatar", vrm_filename="test.vrm")
2. avatar_pipeline(operation="blender_validate", vrm_filename="test.vrm")
3. avatar_pipeline(operation="stage_for_vts", vrm_filename="test.vrm", label="test")

### Full Production
1. avatar_pipeline(operation="full_pipeline", vrm_filename="prod.vrm", pick_sample=false, label="release_v1")

### Operation Usage Patterns
| Pattern | Operation Sequence | Best For |
|---------|-------------------|----------|
| Quick test | vroid_quick_avatar -> blender_validate -> stage_for_vts | Validating VRoid output |
| Import and verify | hub_stage_file -> blender_validate -> stage_for_vts | Processing external VRM files |
| Fix and stage | hub_stage_file -> blender_validate -> blender_reexport -> stage_for_vts | Repairing broken VRM files |
| Automated pipeline | full_pipeline | One-step production workflow |
| Batch processing | vroid_quick_avatar (multiple) -> list_staging -> blender_validate (each) | Processing multiple avatars |

### REST API Usage Summary
All pipeline operations are accessible via REST as well as MCP. Use POST requests to /api/v1/control/tool with JSON body containing "tool" and "arguments" fields. The /health endpoint provides server status. The /api/v1/download/{filename} endpoint retrieves staged files. GET endpoints need no authentication. POST endpoints accept JSON content-type only. The REST response is identical to the MCP tool response format.

### Fleet Server Startup Checklist
Before running any pipeline operation, verify these servers are accessible:
1. vroidstudio-mcp: Run `curl http://127.0.0.1:10881/health`. Should return status ok.
2. blender-mcp: Run `curl http://127.0.0.1:10849/health`. Should return status ok.
3. avatar-pipeline-mcp: Run `curl http://127.0.0.1:10952/health`. Should return status ok.
4. If any server is unreachable, start it and retry. Pipeline operations fail immediately when fleet servers are down.

### Pipeline Decision Flow
1. Do you have a VRM file? Yes -> Go to step 3. No -> Go to step 2.
2. Use vroid_quick_avatar to generate one from VRoid Studio. If you need a specific design, set pick_sample=false and interact with VRoid manually.
3. Import or stage the VRM. Use hub_stage_file for existing local files, or the VRM is already staged from step 2.
4. Validate with blender_validate. If it succeeds, the VRM is compatible. If it fails, the VRM needs fixing.
5. Fix with blender_reexport. This re-exports through Blender's VRM addon which fixes many common issues.
6. Re-validate the fixed file. If it passes, proceed. If it still fails, the VRM may need manual editing.
7. Stage for VTube with stage_for_vts. This creates the VTube-ready copy with a manifest file.
8. Verify with list_staging. Confirm all expected files exist with reasonable sizes.
9. Load in VTube Studio using the manifest for quick setup.

### Step-by-Step Validation
1. Hub stage file: avatar_pipeline(operation="hub_stage_file", source_path="C:/model.vrm")
2. Validate: avatar_pipeline(operation="blender_validate", vrm_filename="model.vrm")
3. If passes: stage for VTube: avatar_pipeline(operation="stage_for_vts", vrm_filename="model.vrm", label="validated")
4. If fails: re-export: avatar_pipeline(operation="blender_reexport", vrm_filename="model.vrm", output_name="model_fixed.vrm")
5. Validate the fix: avatar_pipeline(operation="blender_validate", vrm_filename="model_fixed.vrm")
6. Stage for VTube: avatar_pipeline(operation="stage_for_vts", vrm_filename="model_fixed.vrm", label="fixed_v1")

### Import and Fix
1. avatar_pipeline(operation="hub_stage_file", source_path="C:/model.vrm")
2. avatar_pipeline(operation="blender_validate", vrm_filename="model.vrm")
3. avatar_pipeline(operation="blender_reexport", vrm_filename="model.vrm")
4. avatar_pipeline(operation="stage_for_vts", vrm_filename="model_fixed.vrm")

## Additional Tutorial Content

### Tutorial 16: Checking Fleet Server Logs
When operations fail, check the corresponding fleet server's logs. vroidstudio-mcp logs to stderr (visible in MCP client logs). blender-mcp logs to its own log file. Pipeline logs appear in the avatar-pipeline-mcp stderr output. Set LOG_LEVEL=DEBUG on all servers for maximum diagnostic detail.

### Tutorial 17: Validating Pipeline Output
After running the full pipeline, verify all output files:
```python
result = await avatar_pipeline(operation="list_staging")
for f in result["files"]:
    if f["path"].endswith(".vrm"):
        # Validate the output exists and has reasonable size
        if f["size_kb"] < 100:
            print(f"WARNING: {f['path']} is very small ({f['size_kb']} KB)")
        else:
            print(f"OK: {f['path']} ({f['size_kb']} KB)")
```

### Tutorial 18: Cross-Fleet Hub Operations
The hub directory stores files shared between fleet components. To stage a file from another fleet server's output:
```python
# Download from blender-mcp output
import httpx
resp = httpx.get("http://127.0.0.1:10849/api/v1/download/exported.vrm")
if resp.status_code == 200:
    local_path = "C:/temp/downloaded.vrm"
    with open(local_path, "wb") as f:
        f.write(resp.content)
    # Stage into pipeline
    await avatar_pipeline(operation="hub_stage_file", source_path=local_path)
```

### Tutorial 19: Scheduling Pipeline Runs
For automated avatar exports, use Windows Task Scheduler or cron:
```python
# Save as scheduled_pipeline.py and run via task scheduler
import asyncio, subprocess
async def main():
    result = await avatar_pipeline(operation="full_pipeline", vrm_filename="daily_avatar.vrm")
    if result["success"]:
        # Notify success
        print(f"Pipeline completed: {result['staged_path']}")
    else:
        # Log failure
        print(f"Pipeline failed: {result.get('error', 'unknown')}")
asyncio.run(main())
```

### Additional Pipeline Checklist
- Before starting: verify fleet servers are running with curl http://127.0.0.1:10881/health and curl http://127.0.0.1:10849/health
- After VRoid export: verify the VRM file exists with list_staging
- Before Blender ops: ensure enough disk space (minimum 1 GB free)
- After re-export: compare file sizes to detect corruption
- Before VTube staging: verify manifest.json content is correct
- After full pipeline: manually load VRM in VTube Studio to verify
- Clean up: regularly clean staging/output to prevent disk full

### Tutorial 20: Memory-Constrained Environments
When running on systems with limited memory:
- Use smaller VRM files (aim for < 10 MB per file)
- Process one avatar at a time, not batches
- Monitor disk usage with list_staging
- Clean up staging frequently to free space
- Avoid storing multiple copies in staging and output simultaneously

## Environment Quick Reference
| Variable | Default | Used By |
|----------|---------|---------|
| AVATAR_PIPELINE_HOST | 127.0.0.1 | Server binding |
| AVATAR_PIPELINE_PORT | 10952 | Server port |
| AVATAR_PIPELINE_WORK_DIR | %TEMP%/avatar_pipeline | File storage |
| BLENDER_MCP_URL | http://127.0.0.1:10849 | Blender fleet |
| VROIDSTUDIO_MCP_URL | http://127.0.0.1:10881 | VRoid fleet |

## Troubleshooting Quick Guide
| Symptom | Most Likely Cause | Check First |
|---------|------------------|-------------|
| All operations fail | Server not running | Check port 10952 is up |
| VRoid export fails | vroidstudio-mcp down | curl :10881/health |
| Blender fails | blender-mcp down | curl :10849/health |
| File not in staging | Wrong filename | Use list_staging to verify |
| Pipeline download fails | File in wrong dir | Check output/ not staging/ |

## REST API Quick Commands
```bash
# Quick health check
curl http://localhost:10952/health

# Run full pipeline in one command
curl -X POST http://localhost:10952/api/v1/control/tool -H "Content-Type: application/json" -d '{"tool":"avatar_pipeline","arguments":{"operation":"full_pipeline","vrm_filename":"test.vrm"}}'

# List all staging files
curl -X POST http://localhost:10952/api/v1/control/tool -H "Content-Type: application/json" -d '{"tool":"avatar_pipeline","arguments":{"operation":"list_staging"}}'

# Download output file
curl -O http://localhost:10952/api/v1/download/test_fixed.vrm

# Check status
curl -X POST http://localhost:10952/api/v1/control/tool -H "Content-Type: application/json" -d '{"tool":"avatar_pipeline","arguments":{"operation":"status"}}'
```
| Full pipeline fails mid-way | Check step results | Response has steps[] with errors |
| Can't download file | Wrong filename | File may be in output/ not staging/ |
| Blender validation fails | VRM corrupt or incompatible | Run blender_reexport to fix |
| VRoid export stuck | VRoid Studio UI open | Close modal dialogs in VRoid |

## Pipeline Error Code Quick Guide
| Error String | Meaning | Action |
|-------------|---------|--------|
| "source_path required" | hub_stage_file missing path | Provide absolute file path |
| "File not found: ..." | Source file doesn't exist | Verify path exists |
| "VRM not in staging" | File not in expected directory | Import with hub_stage_file first |
| "Blender import failed" | VRM cannot be loaded | File may be corrupt |
| "Re-export file missing" | Blender didn't produce output | Check blender-mcp logs |
| "validation failed" | full_pipeline sub-step error | Check steps array for details |

## Typical REST Workflow Examples
### One-step full pipeline
```bash
curl -X POST http://localhost:10952/api/v1/control/tool -H "Content-Type: application/json" \
  -d '{"tool":"avatar_pipeline","arguments":{"operation":"full_pipeline","vrm_filename":"demo.vrm","label":"demo_v1"}}'
```

### Import and validate
```bash
curl -X POST http://localhost:10952/api/v1/control/tool -H "Content-Type: application/json" \
  -d '{"tool":"avatar_pipeline","arguments":{"operation":"hub_stage_file","source_path":"C:/model.vrm"}}'

curl -X POST http://localhost:10952/api/v1/control/tool -H "Content-Type: application/json" \
  -d '{"tool":"avatar_pipeline","arguments":{"operation":"blender_validate","vrm_filename":"model.vrm"}}'
```

### Operation Parameter Summary
All operations use the avatar_pipeline tool with an "operation" parameter. Additional parameters depend on the operation. Use the status operation to check current pipeline state. The full_pipeline operation accepts all parameters from individual sub-operations.

### Command Line REST Examples
Check health: curl http://localhost:10952/health. Check VRoid: curl http://localhost:10881/health. Check Blender: curl http://localhost:10849/health. Run pipeline: curl POST with tool="avatar_pipeline" and arguments as JSON.

### Rest API Tool Call Format
All pipeline operations use POST to /api/v1/control/tool with JSON body: {"tool": "avatar_pipeline", "arguments": {"operation": "...", ...}}. The response matches the MCP tool response exactly. Files are downloaded from /api/v1/download/{filename}.

### Quick Troubleshooting Steps
1. Check server: curl http://localhost:10952/health
2. Check VRoid: curl http://localhost:10881/health
3. Check Blender: curl http://localhost:10849/health
4. List staging: use avatar_pipeline(operation="list_staging")
5. Validate VRM: use avatar_pipeline(operation="blender_validate", vrm_filename="file.vrm")

### Output File Naming
When files are staged or exported, the filename is determined by the vrm_filename parameter. The default is "anime_gal.vrm". Re-exported files get "_fixed" suffix by default, configurable via output_name. VTube manifest files use the VRM filename stem plus ".manifest.json".

### Pipeline Glossary
* **VRM**: Virtual Reality Model format for 3D avatars with bone and blend shape data
* **Blend shapes**: Facial expression morph targets for lip sync and emotions
* **Armature**: Skeletal bone structure for animation
* **Manifest**: JSON file with avatar metadata for VTube Studio integration
* **Staging**: Intermediate directory where VRM files wait for processing
* **Validation**: Headless import test in Blender to verify VRM file integrity
* **Re-export**: Clean export through Blender's VRM addon to fix common issues

### Pipeline Workflow Summary
The pipeline follows this order: VRoid export (or file import) -> Blender validation -> Blender re-export (if needed) -> VTube staging. Each operation builds on the outputs of the previous one. Use list_staging between operations to track progress. The full_pipeline operation automates the entire sequence.

### Pipeline Environment Configuration
| Variable | Purpose | Default | Required |
|----------|---------|---------|----------|
| AVATAR_PIPELINE_HOST | Server bind address | 127.0.0.1 | No |
| AVATAR_PIPELINE_PORT | Server port | 10952 | No |
| AVATAR_PIPELINE_WORK_DIR | File storage directory | %TEMP%/avatar_pipeline | No |
| BLENDER_MCP_URL | Blender fleet server | http://127.0.0.1:10849 | No |
| VROIDSTUDIO_MCP_URL | VRoid fleet server | http://127.0.0.1:10881 | No |
All variables have sensible defaults for local development. Change them for production deployments or remote fleet servers.

### Operation Output Field Reference
| Operation | Field | Type | Description |
|-----------|-------|------|-------------|
| status | work_dir | str | Current pipeline working directory |
| status | staging | list | VRM filenames in staging directory |
| status | outputs | list | VRM filenames in output directory |
| vroid_quick_avatar | export_path | str | Original export path from VRoid |
| vroid_quick_avatar | staged_path | str | Path in pipeline staging directory |
| hub_stage_file | staged_path | str | Destination path in staging |
| hub_stage_file | size_kb | float | File size in kilobytes |
| blender_validate | meshes | int | Number of mesh objects |
| blender_validate | armatures | int | Number of armature objects |
| blender_validate | objects | list | Names of all imported objects |
| blender_reexport | source | str | Source VRM file path |
| blender_reexport | export_path | str | Destination re-exported file path |
| stage_for_vts | staged_path | str | Path in VTube staging directory |
| stage_for_vts | manifest | str | Path to JSON manifest file |
| full_pipeline | steps | list | Array of step results with status |
| full_pipeline | vrm_filename | str | Final VRM filename |
| full_pipeline | staged_path | str | Final staged VRM path |
| list_staging | files | list | Array of file info objects with path and size_kb |
