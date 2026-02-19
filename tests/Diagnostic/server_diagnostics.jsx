import { useState, useEffect, useCallback } from "react";

// ── Generates a synthetic sky JPEG via canvas ─────────────────────────────────
async function generateTestImage() {
  return new Promise((resolve) => {
    const canvas = document.createElement("canvas");
    canvas.width = 320;
    canvas.height = 240;
    const ctx = canvas.getContext("2d");

    const gradient = ctx.createLinearGradient(0, 0, 0, 240);
    gradient.addColorStop(0, "#4a90d9");
    gradient.addColorStop(0.65, "#87CEEB");
    gradient.addColorStop(1, "#c8e8f8");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 320, 240);

    // clouds
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    [[70, 90, 35], [110, 75, 50], [150, 90, 35],
     [200, 110, 28], [235, 98, 42], [265, 110, 28]].forEach(([x, y, r]) => {
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    });

    // label
    ctx.fillStyle = "rgba(0,0,0,0.3)";
    ctx.font = "11px monospace";
    ctx.fillText("SYNTHETIC TEST IMAGE", 8, 230);

    canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.85);
  });
}

// ── Color helpers ─────────────────────────────────────────────────────────────
const statusColor = (r) => {
  if (!r) return "#2a3a4a";
  if (r.ok) return "#00e87a";
  if (r.status) return "#ffb347";
  return "#ff4d6d";
};

const latencyColor = (ms) => {
  if (ms < 100) return "#00e87a";
  if (ms < 400) return "#ffb347";
  return "#ff4d6d";
};

// ── Endpoint definitions ──────────────────────────────────────────────────────
const ENDPOINTS = [
  { path: "/api/test",        method: "GET",  label: "Server Health",  critical: true  },
  { path: "/api/latest",      method: "GET",  label: "Latest Data",    critical: false },
  { path: "/api/statistics",  method: "GET",  label: "Statistics",     critical: false },
  { path: "/api/config",      method: "GET",  label: "Configuration",  critical: false },
  { path: "/api/history?limit=1", method: "GET", label: "History",    critical: false },
  { path: "/image/latest",    method: "GET",  label: "Latest Image",   critical: false },
];

export default function ServerDiagnostics() {
  const [serverUrl, setServerUrl]         = useState("http://localhost:5000");
  const [isChecking, setIsChecking]       = useState(false);
  const [autoRefresh, setAutoRefresh]     = useState(false);
  const [results, setResults]             = useState({});
  const [lastCheck, setLastCheck]         = useState(null);
  const [uploadResult, setUploadResult]   = useState(null);
  const [isUploading, setIsUploading]     = useState(false);
  const [customFile, setCustomFile]       = useState(null);
  const [activeTab, setActiveTab]         = useState("health");

  // ── Check a single endpoint ───────────────────────────────────────────────
  const checkEndpoint = async (ep) => {
    const t0 = performance.now();
    try {
      const resp = await fetch(serverUrl + ep.path, {
        method: ep.method,
        signal: AbortSignal.timeout(6000),
      });
      const ms = Math.round(performance.now() - t0);
      const ct = resp.headers.get("content-type") || "";
      let body = null;
      if (ct.includes("json")) {
        try { body = await resp.json(); } catch {}
      } else if (!ct.includes("image")) {
        try { body = (await resp.text()).slice(0, 400); } catch {}
      } else {
        body = "[image/jpeg data]";
      }
      return { status: resp.status, ms, ok: resp.ok, body };
    } catch (err) {
      return { status: null, ms: Math.round(performance.now() - t0), ok: false, error: err.message };
    }
  };

  // ── Run full health check ─────────────────────────────────────────────────
  const runCheck = useCallback(async () => {
    setIsChecking(true);
    const fresh = {};
    await Promise.all(ENDPOINTS.map(async (ep) => {
      fresh[ep.path] = await checkEndpoint(ep);
    }));
    setResults(fresh);
    setLastCheck(new Date().toLocaleTimeString());
    setIsChecking(false);
  }, [serverUrl]);

  // ── Auto-refresh ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(runCheck, 5000);
    return () => clearInterval(id);
  }, [autoRefresh, runCheck]);

  // ── Upload test ───────────────────────────────────────────────────────────
  const runUpload = async () => {
    setIsUploading(true);
    setUploadResult(null);
    const t0 = performance.now();
    try {
      const blob = customFile ?? await generateTestImage();
      const resp = await fetch(serverUrl + "/upload", {
        method: "POST",
        headers: { "Content-Type": "image/jpeg" },
        body: blob,
        signal: AbortSignal.timeout(15000),
      });
      const ms   = Math.round(performance.now() - t0);
      const body = await resp.text();
      setUploadResult({ status: resp.status, ok: resp.ok, ms, body, size: blob.size });
    } catch (err) {
      setUploadResult({ status: null, ok: false, ms: Math.round(performance.now() - t0), error: err.message });
    }
    setIsUploading(false);
  };

  // ── Derived stats ─────────────────────────────────────────────────────────
  const total = ENDPOINTS.length;
  const okCount = Object.values(results).filter(r => r.ok).length;
  const overall = Object.keys(results).length === 0 ? null
    : okCount === total ? "NOMINAL"
    : okCount > 0       ? "DEGRADED"
    : "OFFLINE";

  const overallColor = overall === "NOMINAL" ? "#00e87a"
    : overall === "DEGRADED" ? "#ffb347" : "#ff4d6d";

  // ── Styles ────────────────────────────────────────────────────────────────
  const s = {
    root: {
      fontFamily: "'Courier New', Courier, monospace",
      background: "#06080c",
      color: "#8ab0c0",
      minHeight: "100vh",
      padding: "0",
    },
    topBar: {
      background: "#090e14",
      borderBottom: "1px solid #0f2030",
      padding: "14px 28px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      flexWrap: "wrap",
      gap: "10px",
    },
    title: {
      color: "#00e87a",
      fontSize: "14px",
      letterSpacing: "3px",
      textTransform: "uppercase",
      margin: 0,
      fontWeight: "normal",
    },
    subtitle: {
      color: "#2a4a5a",
      fontSize: "10px",
      letterSpacing: "2px",
      marginTop: "3px",
    },
    body: { padding: "24px 28px" },
    urlRow: {
      display: "flex",
      gap: "8px",
      marginBottom: "20px",
      flexWrap: "wrap",
      alignItems: "center",
    },
    input: {
      flex: "1 1 240px",
      background: "#040608",
      border: "1px solid #0f2535",
      color: "#60d0ff",
      padding: "9px 14px",
      fontFamily: "monospace",
      fontSize: "13px",
      borderRadius: "3px",
      outline: "none",
    },
    btn: (active, accent = "#00e87a") => ({
      background: active ? accent : "transparent",
      border: `1px solid ${accent}`,
      color: active ? "#000" : accent,
      padding: "9px 18px",
      fontFamily: "monospace",
      fontSize: "11px",
      letterSpacing: "1.5px",
      cursor: "pointer",
      borderRadius: "3px",
      textTransform: "uppercase",
      transition: "all 0.15s",
    }),
    tabs: {
      display: "flex",
      gap: "0",
      marginBottom: "20px",
      borderBottom: "1px solid #0f2030",
    },
    tab: (active) => ({
      padding: "10px 24px",
      fontSize: "11px",
      letterSpacing: "2px",
      textTransform: "uppercase",
      cursor: "pointer",
      color: active ? "#00e87a" : "#3a5a6a",
      borderBottom: active ? "2px solid #00e87a" : "2px solid transparent",
      marginBottom: "-1px",
      background: "transparent",
      border: "none",
      fontFamily: "monospace",
    }),
    banner: (color) => ({
      padding: "12px 18px",
      background: `${color}11`,
      border: `1px solid ${color}44`,
      borderLeft: `3px solid ${color}`,
      borderRadius: "3px",
      marginBottom: "20px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      flexWrap: "wrap",
      gap: "8px",
    }),
    grid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
      gap: "12px",
    },
    card: (r) => ({
      background: "#090e14",
      border: `1px solid ${statusColor(r)}22`,
      borderLeft: `3px solid ${statusColor(r)}`,
      borderRadius: "3px",
      padding: "16px",
    }),
    badge: (r) => ({
      display: "inline-block",
      padding: "2px 9px",
      background: `${statusColor(r)}18`,
      border: `1px solid ${statusColor(r)}55`,
      color: statusColor(r),
      fontSize: "10px",
      letterSpacing: "1px",
      borderRadius: "2px",
      marginRight: "8px",
    }),
    pre: {
      background: "#030507",
      border: "1px solid #0a1a28",
      padding: "10px",
      fontSize: "10px",
      color: "#4a7a8a",
      maxHeight: "110px",
      overflowY: "auto",
      marginTop: "10px",
      borderRadius: "2px",
      whiteSpace: "pre-wrap",
      wordBreak: "break-all",
      lineHeight: "1.5",
    },
  };

  return (
    <div style={s.root}>
      {/* Top Bar */}
      <div style={s.topBar}>
        <div>
          <h1 style={s.title}>◈ Sky Predictor — Server Diagnostics</h1>
          <div style={s.subtitle}>CONNECTION HEALTH  ·  UPLOAD ENDPOINT TESTER</div>
        </div>
        {lastCheck && (
          <div style={{ textAlign: "right", fontSize: "10px", color: "#2a4a5a" }}>
            LAST SCAN<br />
            <span style={{ color: "#8ab0c0" }}>{lastCheck}</span>
          </div>
        )}
      </div>

      <div style={s.body}>
        {/* Server URL row */}
        <div style={s.urlRow}>
          <input
            style={s.input}
            value={serverUrl}
            onChange={(e) => setServerUrl(e.target.value)}
            placeholder="http://localhost:5000"
          />
          <button style={s.btn(isChecking)} onClick={runCheck} disabled={isChecking}>
            {isChecking ? "⟳ Scanning..." : "Run Health Check"}
          </button>
          <button
            style={s.btn(autoRefresh, "#00aaff")}
            onClick={() => setAutoRefresh(v => !v)}
          >
            {autoRefresh ? "◉ Live ON" : "◎ Live OFF"}
          </button>
        </div>

        {/* Overall banner */}
        {overall && (
          <div style={s.banner(overallColor)}>
            <span style={{ color: overallColor, letterSpacing: "2px", fontSize: "13px" }}>
              {overall === "NOMINAL" ? "✓" : overall === "DEGRADED" ? "⚠" : "✗"} {overall}
            </span>
            <span style={{ color: "#2a4a5a", fontSize: "10px" }}>
              {okCount}/{total} ENDPOINTS RESPONDING
            </span>
          </div>
        )}

        {/* Tabs */}
        <div style={s.tabs}>
          <button style={s.tab(activeTab === "health")} onClick={() => setActiveTab("health")}>
            Endpoint Health
          </button>
          <button style={s.tab(activeTab === "upload")} onClick={() => setActiveTab("upload")}>
            Upload Tester
          </button>
        </div>

        {/* ── TAB: Health ─────────────────────────────────────────────────── */}
        {activeTab === "health" && (
          <>
            {Object.keys(results).length === 0 && !isChecking && (
              <div style={{ color: "#2a4a5a", fontSize: "12px", textAlign: "center", padding: "40px 0", letterSpacing: "2px" }}>
                PRESS "RUN HEALTH CHECK" TO BEGIN DIAGNOSTICS
              </div>
            )}
            {isChecking && (
              <div style={{ color: "#00e87a", fontSize: "11px", textAlign: "center", padding: "40px 0", letterSpacing: "3px" }}>
                ⟳ SCANNING {total} ENDPOINTS...
              </div>
            )}
            <div style={s.grid}>
              {ENDPOINTS.map((ep) => {
                const r = results[ep.path];
                return (
                  <div key={ep.path} style={s.card(r)}>
                    <div style={{ fontSize: "11px", color: "#4a7a8a", letterSpacing: "1.5px", textTransform: "uppercase", marginBottom: "3px" }}>
                      {ep.critical && <span style={{ color: "#ffb347" }}>★ </span>}
                      {ep.label}
                    </div>
                    <div style={{ fontSize: "10px", color: "#2a4a5a", marginBottom: "10px" }}>
                      {ep.method} {ep.path}
                    </div>
                    {r ? (
                      <>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                          <span style={s.badge(r)}>
                            {r.ok ? "OK" : r.status ? `${r.status}` : "CONN ERR"}
                          </span>
                          <span style={{ color: latencyColor(r.ms), fontSize: "11px" }}>
                            {r.ms}ms
                          </span>
                          {/* Latency bar */}
                          <div style={{ flex: 1, minWidth: "60px", height: "4px", background: "#0a1a28", borderRadius: "2px", overflow: "hidden" }}>
                            <div style={{
                              width: `${Math.min(r.ms / 5, 100)}%`,
                              height: "100%",
                              background: latencyColor(r.ms),
                              borderRadius: "2px",
                              transition: "width 0.4s",
                            }} />
                          </div>
                        </div>
                        {r.error && (
                          <div style={{ color: "#ff4d6d", fontSize: "10px", marginTop: "8px" }}>
                            ✗ {r.error}
                          </div>
                        )}
                        {r.body && typeof r.body === "object" && (
                          <div style={s.pre}>{JSON.stringify(r.body, null, 2)}</div>
                        )}
                        {r.body && typeof r.body === "string" && r.body !== "[image/jpeg data]" && (
                          <div style={s.pre}>{r.body}</div>
                        )}
                        {r.body === "[image/jpeg data]" && (
                          <div style={{ fontSize: "10px", color: "#4a8aaa", marginTop: "8px" }}>
                            ◈ Image binary received
                          </div>
                        )}
                      </>
                    ) : (
                      <div style={{ color: "#1a3040", fontSize: "10px", letterSpacing: "1px" }}>NOT CHECKED</div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}

        {/* ── TAB: Upload ──────────────────────────────────────────────────── */}
        {activeTab === "upload" && (
          <div>
            <div style={{ color: "#2a4a5a", fontSize: "11px", marginBottom: "16px", lineHeight: "1.7" }}>
              Simulates an ESP32-CAM POST to <span style={{ color: "#60d0ff" }}>/upload</span>.
              Sends a JPEG image and displays the full server response, status code, and latency.
              If no image is chosen, a synthetic 320×240 sky JPEG is generated automatically.
            </div>

            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "12px" }}>
              {/* File picker */}
              <label style={{ ...s.btn(false, "#ffb347"), cursor: "pointer", display: "inline-flex", alignItems: "center" }}>
                <input
                  type="file"
                  accept="image/*"
                  style={{ display: "none" }}
                  onChange={(e) => setCustomFile(e.target.files[0] || null)}
                />
                {customFile ? `◈ ${customFile.name}` : "Choose Image"}
              </label>

              {customFile && (
                <button style={s.btn(false, "#ff4d6d")} onClick={() => setCustomFile(null)}>
                  ✗ Clear
                </button>
              )}

              <button style={s.btn(isUploading)} onClick={runUpload} disabled={isUploading}>
                {isUploading ? "⟳ Sending..." : customFile ? "Upload Image" : "Send Synthetic Image"}
              </button>
            </div>

            {!customFile && (
              <div style={{ fontSize: "10px", color: "#2a4a5a", marginBottom: "20px", letterSpacing: "1px" }}>
                AUTO MODE — will synthesise a 320×240 sky-blue gradient JPEG
              </div>
            )}

            {isUploading && (
              <div style={{ color: "#00e87a", fontSize: "11px", letterSpacing: "3px", padding: "24px 0" }}>
                ⟳ POSTING TO {serverUrl}/upload ...
              </div>
            )}

            {uploadResult && (() => {
              const accent = uploadResult.ok ? "#00e87a" : "#ff4d6d";
              return (
                <div style={{
                  background: "#090e14",
                  border: `1px solid ${accent}33`,
                  borderLeft: `3px solid ${accent}`,
                  borderRadius: "3px",
                  padding: "20px",
                }}>
                  {/* Metrics row */}
                  <div style={{ display: "flex", gap: "28px", marginBottom: "16px", flexWrap: "wrap", alignItems: "center" }}>
                    <div>
                      <div style={{ fontSize: "9px", color: "#2a4a5a", letterSpacing: "2px", marginBottom: "2px" }}>HTTP STATUS</div>
                      <div style={{ color: accent, fontSize: "28px", lineHeight: 1 }}>
                        {uploadResult.status ?? "—"}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: "9px", color: "#2a4a5a", letterSpacing: "2px", marginBottom: "2px" }}>LATENCY</div>
                      <div style={{ color: latencyColor(uploadResult.ms), fontSize: "28px", lineHeight: 1 }}>
                        {uploadResult.ms}ms
                      </div>
                    </div>
                    {uploadResult.size && (
                      <div>
                        <div style={{ fontSize: "9px", color: "#2a4a5a", letterSpacing: "2px", marginBottom: "2px" }}>PAYLOAD SIZE</div>
                        <div style={{ color: "#8ab0c0", fontSize: "28px", lineHeight: 1 }}>
                          {(uploadResult.size / 1024).toFixed(1)}KB
                        </div>
                      </div>
                    )}
                    <div style={{ flex: 1 }}>
                      <span style={{
                        padding: "6px 16px",
                        background: `${accent}18`,
                        border: `1px solid ${accent}55`,
                        color: accent,
                        fontSize: "12px",
                        letterSpacing: "2px",
                        borderRadius: "2px",
                      }}>
                        {uploadResult.ok ? "✓ UPLOAD ACCEPTED" : "✗ UPLOAD REJECTED"}
                      </span>
                    </div>
                  </div>

                  <div style={{ fontSize: "9px", color: "#2a4a5a", letterSpacing: "2px", marginBottom: "6px" }}>
                    SERVER RESPONSE BODY
                  </div>
                  <div style={{ ...s.pre, maxHeight: "220px", fontSize: "11px", color: uploadResult.ok ? "#4a9a6a" : "#9a4a4a" }}>
                    {uploadResult.error || uploadResult.body || "(empty response)"}
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* Footer */}
        <div style={{ marginTop: "32px", fontSize: "9px", color: "#0f2030", letterSpacing: "2px", textAlign: "center" }}>
          SKY PREDICTOR DIAGNOSTICS · BROWSER-BASED · TARGET: {serverUrl}
        </div>
      </div>
    </div>
  );
}
