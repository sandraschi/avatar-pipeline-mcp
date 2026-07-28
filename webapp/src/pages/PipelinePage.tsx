import { useCallback, useState } from "react";
import { Loader2, Sparkles, UserCircle } from "lucide-react";

const API = "/api/v1";

type Step = { step?: string; success?: boolean; error?: string; staged_path?: string };

export default function PipelinePage() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [vrmName, setVrmName] = useState("anime_gal.vrm");

  const runPipeline = useCallback(async (operation: string) => {
    setLoading(true);
    setMessage(null);
    setSteps([]);
    try {
      const res = await fetch(`${API}/control/tool`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "avatar_pipeline",
          arguments: { operation, vrm_filename: vrmName, pick_sample: true },
        }),
      });
      const data = await res.json();
      if (data.steps) setSteps(data.steps);
      if (!data.success) {
        setMessage(data.error ?? "Pipeline failed");
        return;
      }
      setMessage(
        operation === "full_pipeline"
          ? `Pipeline complete: ${data.staged_path ?? vrmName}`
          : JSON.stringify(data, null, 2).slice(0, 400),
      );
    } catch (err) {
      setMessage(String(err));
    } finally {
      setLoading(false);
    }
  }, [vrmName]);

  return (
    <div className="min-h-screen bg-[#0f0f12] text-white p-8 max-w-4xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <UserCircle className="text-pink-400" size={28} />
          Avatar Pipeline
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          VRoid brute-force export, Blender VRM validate, VTube staging.
        </p>
      </header>

      <label className="block text-sm text-slate-400">
        VRM filename
        <input
          value={vrmName}
          onChange={(e) => setVrmName(e.target.value)}
          className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white"
        />
      </label>

      <div className="flex flex-wrap gap-3">
        {[
          ["status", "Status"],
          ["vroid_quick_avatar", "VRoid export"],
          ["blender_validate", "Blender validate"],
          ["stage_for_vts", "Stage for VTube"],
          ["full_pipeline", "Full pipeline"],
        ].map(([op, label]) => (
          <button
            key={op}
            type="button"
            disabled={loading}
            onClick={() => runPipeline(op)}
            className="px-4 py-2 rounded-xl bg-pink-600/80 hover:bg-pink-500 disabled:opacity-50 text-sm font-medium flex items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : <Sparkles size={16} />}
            {label}
          </button>
        ))}
      </div>

      {message && <pre className="text-sm text-emerald-400 whitespace-pre-wrap">{message}</pre>}

      {steps.length > 0 && (
        <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2">
          <p className="text-xs uppercase text-slate-500">Steps</p>
          {steps.map((s, i) => (
            <div key={i} className="text-sm flex gap-2">
              <span className={s.success ? "text-emerald-400" : "text-red-400"}>{s.success ? "OK" : "FAIL"}</span>
              <span className="text-slate-300">{s.step}</span>
              {s.error && <span className="text-red-300">{s.error}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
