"use client";

import { useState } from "react";
import { getSupabaseBrowser } from "@/lib/supabase-browser";

export default function DownloadSummariesButton() {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    try {
      const sb = getSupabaseBrowser();
      if (!sb) { alert("Supabase client unavailable."); return; }

      const { data, error } = await sb
        .from("summary_archive")
        .select("*")
        .order("generated_at", { ascending: true });

      if (error || !data?.length) {
        alert(error ? `Error: ${error.message}` : "No archived summaries found yet.");
        return;
      }

      const JSZip = (await import("jszip")).default;
      const zip = new JSZip();
      data.forEach((row: { generated_at: string; data: unknown }) => {
        const ts = row.generated_at.replace(/[:.]/g, "-").slice(0, 19);
        zip.file(`summary_${ts}.json`, JSON.stringify(row.data, null, 2));
      });

      const blob = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "executive_summaries.zip";
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      style={{
        fontSize: 13,
        fontWeight: 600,
        color: loading ? "var(--color-text-muted)" : "var(--color-text)",
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: 6,
        padding: "6px 14px",
        display: "flex",
        alignItems: "center",
        gap: 6,
        cursor: loading ? "not-allowed" : "pointer",
        whiteSpace: "nowrap",
      }}
    >
      {loading ? "Preparing…" : "⬇ Download All Summaries"}
    </button>
  );
}
