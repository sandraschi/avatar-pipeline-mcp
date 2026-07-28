"""FastMCP server — avatar creative pipeline."""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Annotated, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from avatar_pipeline_mcp.fleet_http import (
    DEFAULT_VROID_URL,
    blender_reexport_vrm,
    blender_validate_vrm,
    call_vroid_tool,
    download_fleet_file,
    stage_vrm_for_vts,
)

logger = logging.getLogger("avatar-pipeline-mcp")

WORK_DIR = Path(os.environ.get("AVATAR_PIPELINE_WORK_DIR", Path(os.environ.get("TEMP", ".")) / "avatar_pipeline"))
STAGING_DIR = WORK_DIR / "staging"
HUB_DIR = WORK_DIR / "hub"
OUTPUT_DIR = WORK_DIR / "output"
for d in (STAGING_DIR, HUB_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

_START = time.time()

mcp = FastMCP(
    "avatar-pipeline-mcp",
    instructions=(
        "VRM avatar creative pipeline orchestrator. Chains vroidstudio-mcp brute-force export, "
        "Blender VRM validation/reexport, and VTube Studio staging. "
        "Operations: status, vroid_quick_avatar, hub_stage_file, blender_validate, "
        "blender_reexport, stage_for_vts, full_pipeline."
    ),
)


@mcp.tool()
async def avatar_pipeline(
    operation: Annotated[
        str,
        Field(
            description=(
                "status | vroid_quick_avatar | hub_stage_file | blender_validate | "
                "blender_reexport | stage_for_vts | full_pipeline | list_staging"
            ),
        ),
    ] = "status",
    vrm_filename: Annotated[str, Field(description="VRM filename in staging/output.")] = "anime_gal.vrm",
    source_path: Annotated[str, Field(description="Local path for hub_stage_file.")] = "",
    output_name: Annotated[str, Field(description="Output VRM name for reexport.")] = "",
    pick_sample: Annotated[bool, Field(description="VRoid sample model click.")] = True,
    skip_vroid: Annotated[bool, Field(description="full_pipeline: skip VRoid step if VRM exists.")] = False,
    label: Annotated[str, Field(description="Staging label for VTube.")] = "pipeline_avatar",
) -> dict[str, Any]:
    """Avatar pipeline portmanteau — VRoid, Blender, VTube staging."""
    op = operation.strip().lower()

    if op == "status":
        staged = [p.name for p in STAGING_DIR.glob("*.vrm")]
        outputs = [p.name for p in OUTPUT_DIR.glob("*.vrm")]
        return {
            "success": True,
            "work_dir": str(WORK_DIR),
            "staging": staged,
            "outputs": outputs,
            "vroid_url": DEFAULT_VROID_URL,
            "mode": "orchestrator",
        }

    if op == "vroid_quick_avatar":
        result = await call_vroid_tool(
            "vroid_studio",
            {"operation": "quick_gal_export", "output_name": vrm_filename, "pick_sample": pick_sample},
        )
        if not result.get("success"):
            return result
        export_path = result.get("export_path", "")
        if export_path and Path(export_path).is_file():
            dest = STAGING_DIR / vrm_filename
            shutil.copy2(export_path, dest)
            result["staged_path"] = str(dest)
        return result

    if op == "hub_stage_file":
        if not source_path:
            return {"success": False, "error": "source_path required"}
        src = Path(source_path)
        if not src.is_file():
            return {"success": False, "error": f"File not found: {source_path}"}
        dest = STAGING_DIR / (vrm_filename or src.name)
        shutil.copy2(src, dest)
        return {"success": True, "staged_path": str(dest), "size_kb": round(dest.stat().st_size / 1024, 1)}

    staged_vrm = STAGING_DIR / vrm_filename
    if op in ("blender_validate", "blender_reexport", "stage_for_vts") and not staged_vrm.is_file():
        alt = OUTPUT_DIR / vrm_filename
        if alt.is_file():
            staged_vrm = alt
        else:
            return {"success": False, "error": f"VRM not in staging: {vrm_filename}"}

    if op == "blender_validate":
        return await blender_validate_vrm(str(staged_vrm))

    if op == "blender_reexport":
        out_name = output_name or vrm_filename.replace(".vrm", "_fixed.vrm")
        out_path = str((OUTPUT_DIR / out_name).resolve())
        import_result = await blender_validate_vrm(str(staged_vrm))
        if not import_result.get("success"):
            return import_result
        return await blender_reexport_vrm(str(staged_vrm), out_path)

    if op == "stage_for_vts":
        return stage_vrm_for_vts(str(staged_vrm), STAGING_DIR / "vts", label=label)

    if op == "full_pipeline":
        steps: list[dict[str, Any]] = []
        target = STAGING_DIR / vrm_filename
        if not skip_vroid or not target.is_file():
            vroid = await call_vroid_tool(
                "vroid_studio",
                {"operation": "quick_gal_export", "output_name": vrm_filename, "pick_sample": pick_sample},
            )
            steps.append({"step": "vroid_quick_avatar", **vroid})
            if not vroid.get("success"):
                return {"success": False, "steps": steps, "error": vroid.get("error")}
            export_path = vroid.get("export_path", "")
            if export_path:
                shutil.copy2(export_path, target)
        else:
            steps.append({"step": "vroid_quick_avatar", "success": True, "skipped": True})

        validate = await blender_validate_vrm(str(target))
        steps.append({"step": "blender_validate", **validate})
        if not validate.get("success"):
            return {"success": False, "steps": steps, "error": validate.get("error", "validation failed")}

        vts = stage_vrm_for_vts(str(target), STAGING_DIR / "vts", label=label)
        steps.append({"step": "stage_for_vts", **vts})
        return {
            "success": vts.get("success", False),
            "vrm_filename": vrm_filename,
            "staged_path": str(target),
            "steps": steps,
        }

    if op == "list_staging":
        files = []
        for folder in (STAGING_DIR, OUTPUT_DIR, STAGING_DIR / "vts"):
            if not folder.is_dir():
                continue
            for p in folder.iterdir():
                if p.is_file():
                    files.append({"path": str(p), "size_kb": round(p.stat().st_size / 1024, 1)})
        return {"success": True, "files": files}

    return {"success": False, "error": f"Unknown operation: {operation}"}


class ToolCallBody(BaseModel):
    tool: str
    arguments: dict[str, Any] | None = None


app = FastAPI(title="avatar-pipeline-mcp", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "ok", "uptime_s": round(time.time() - _START, 1)}


@app.get("/api/v1/download/{filename}")
async def download_file(filename: str):
    for base in (OUTPUT_DIR, STAGING_DIR, STAGING_DIR / "vts"):
        path = base / filename
        if path.is_file():
            return FileResponse(path)
    raise HTTPException(404, "File not found")


@app.post("/api/v1/control/tool")
async def control_tool(body: ToolCallBody):
    try:
        if body.tool == "avatar_pipeline":
            return await avatar_pipeline(**(body.arguments or {}))
        return {"success": False, "error": f"Unknown tool: {body.tool}"}
    except Exception as exc:
        logger.exception("tool call failed")
        return {"success": False, "error": str(exc)}


app.mount("/mcp", mcp.http_app(path="/"))


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    host = os.environ.get("AVATAR_PIPELINE_HOST", "127.0.0.1")
    port = int(os.environ.get("AVATAR_PIPELINE_PORT", "10952"))
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
