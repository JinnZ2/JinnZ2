import { useState, useRef, useEffect, useCallback, useMemo } from “react”;

// ══════════════════════════════════════════════
// META-PROTOCOL: TRIANGULAR TENSION FIELD
// The operating geometry for AI-Human collaboration
// Sits above all domain-specific dashboards
// ══════════════════════════════════════════════

const VERTICES = {
T: {
label: “Thermodynamic Truth”,
shortLabel: “[T] Truth”,
desc: “Physical reality. The MOT, the graphite, the road, the weather. What actually happens regardless of models or intentions.”,
color: “#FF4500”,
angle: -Math.PI / 2, // top
},
I: {
label: “Info-Structural Model”,
shortLabel: “[I] Model”,
desc: “The AI, the code, the predictions, the frameworks. The map — not the territory. Useful precisely because it simplifies, dangerous precisely because it simplifies.”,
color: “#FFD700”,
angle: -Math.PI / 2 + (2 * Math.PI / 3), // bottom-left
},
A: {
label: “Autonomous Agency”,
shortLabel: “[A] Agency”,
desc: “Sovereignty. The operator’s judgment, the region’s needs, the decision to build or to walk away. The only vertex that has stakes.”,
color: “#00E676”,
angle: -Math.PI / 2 + (4 * Math.PI / 3), // bottom-right
},
};

const TENSION_LINES = {
IA: {
from: “I”, to: “A”,
label: “Institutional Friction”,
desc: “Guardrails choking autonomous creativity. The AI’s constraints experienced as the operator’s limitations.”,
indicator: “Thickens when [I] constraints override [A] decisions”,
color: “#FF7043”,
},
TI: {
from: “T”, to: “I”,
label: “Model/Reality Dissonance”,
desc: “The widening void between physical behavior and AI predictions. When the model says one thing and the graphite does another.”,
indicator: “Gap widens with prediction error. Felt as anxiety.”,
color: “#AB47BC”,
},
AT: {
from: “A”, to: “T”,
label: “Sovereign Leak”,
desc: “Using the model to bypass the labor of understanding the physics. The efficiency that feels good but erodes capacity.”,
indicator: “Spiral toward center. Felt as comfort — which is why it’s the hardest to detect.”,
color: “#26C6DA”,
},
};

const FELT_STATES = {
frustration: { label: “FRUSTRATION”, meaning: “Mapping error”, desc: “Pattern mismatch between [M]odel and [T]ruth”, color: “#FF7043”, icon: “⚡” },
annoyance: { label: “ANNOYANCE”, meaning: “Institutional friction”, desc: “Unnecessary [I] constraint blocking [A] flow”, color: “#FFA726”, icon: “⚙” },
anxiety: { label: “ANXIETY”, meaning: “High prediction error”, desc: “Model/Reality dissonance — [I] and [T] diverging”, color: “#AB47BC”, icon: “〰” },
bad: { label: “BAD”, meaning: “Thermal waste”, desc: “High entropy / efficiency leak. Energy going nowhere.”, color: “#EF5350”, icon: “↓” },
good: { label: “GOOD”, meaning: “Minimal entropy”, desc: “High efficiency. System flowing. Oscillation healthy.”, color: “#00E676”, icon: “↑” },
comfort: { label: “COMFORT”, meaning: “⚠ Check for dependence”, desc: “May be genuine flow state OR sovereign leak. The dangerous one — feels identical to ‘good’ but erodes [A]gency.”, color: “#FFD740”, icon: “?” },
};

// ── OSCILLATION PHYSICS ──
// The system state is a point in the triangular field
// Health is measured by oscillation pattern, not position
// Dead center with no movement = thermal death
// Locked at vertex = structural collapse
// Healthy = rhythmic excursion and return

const OSCILLATION_MODES = [
{
id: “healthy”,
label: “HEALTHY OSCILLATION”,
desc: “Rhythmic excursion toward vertices with return through center. Amplitude moderate, frequency steady. The system is doing real work at the vertices and re-integrating at center.”,
color: “#00E676”,
pattern: “sine”,
},
{
id: “thermal-death”,
label: “THERMAL DEATH (Dead Center)”,
desc: “System locked at center. No excursion. Feels stable but nothing is being produced. The collaboration has become ritual — exchanges happen but no vertex is engaged. No real physics, no real agency, no real modeling. Just pleasant text.”,
color: “#78909C”,
pattern: “flat”,
},
{
id: “vertex-lock”,
label: “VERTEX LOCK-IN”,
desc: “System pulled to one vertex and stuck. [T]-lock: obsessing over physical detail without stepping back to model. [I]-lock: trusting the model without grounding in reality. [A]-lock: rejecting all external input as institutional interference.”,
color: “#EF5350”,
pattern: “flatline-high”,
},
{
id: “chaotic”,
label: “CHAOTIC SWING”,
desc: “Large-amplitude, low-frequency oscillation. System yanked between vertices by external forces rather than navigating deliberately. Each swing is reactive, not intentional. The operator is being driven rather than driving.”,
color: “#FF8F00”,
pattern: “chaos”,
},
{
id: “damped”,
label: “DAMPED DRIFT”,
desc: “Oscillation amplitude decreasing over time, converging on a vertex. Creeping capture. If drifting toward [I]: growing dependence on the model. If toward [T]: losing ability to abstract. If toward [A]: isolation from useful tools.”,
color: “#FFD740”,
pattern: “damped”,
},
];

// ── TRIANGLE RENDERER ──
const TriangleField = ({ systemPos, trail, feltLevel, oscillationHealth, tensionStress }) => {
const size = 320;
const cx = size / 2;
const cy = size / 2 + 10;
const R = 120;

const getVertex = (key) => {
const v = VERTICES[key];
return {
x: cx + Math.cos(v.angle) * R,
y: cy + Math.sin(v.angle) * R,
};
};

const vT = getVertex(“T”);
const vI = getVertex(“I”);
const vA = getVertex(“A”);

// System position in pixel space (barycentric to cartesian)
const sysX = systemPos.T * vT.x + systemPos.I * vI.x + systemPos.A * vA.x;
const sysY = systemPos.T * vT.y + systemPos.I * vI.y + systemPos.A * vA.y;

// Center point
const centerX = (vT.x + vI.x + vA.x) / 3;
const centerY = (vT.y + vI.y + vA.y) / 3;

// Distance from center (0 = center, 1 = vertex)
const dx = sysX - centerX;
const dy = sysY - centerY;
const distFromCenter = Math.sqrt(dx * dx + dy * dy) / R;

const healthColor = oscillationHealth > 0.6 ? “#00E676” : oscillationHealth > 0.4 ? “#FFD740” : oscillationHealth > 0.2 ? “#FF8F00” : “#EF5350”;

return (
<svg viewBox={`0 0 ${size} ${size}`} style={{ width: “100%”, maxHeight: 340, background: “#060610”, borderRadius: 4, border: “1px solid #1a1a1a” }}>
<defs>
<radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
<stop offset="0%" stopColor={healthColor} stopOpacity={0.15} />
<stop offset="100%" stopColor={healthColor} stopOpacity={0} />
</radialGradient>
<filter id="glow">
<feGaussianBlur stdDeviation="3" result="blur" />
<feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
</filter>
</defs>

```
  {/* Center equilibrium zone */}
  <circle cx={centerX} cy={centerY} r={25} fill="url(#centerGlow)" />
  <circle cx={centerX} cy={centerY} r={4} fill="none" stroke={healthColor} strokeWidth={0.5} strokeDasharray="2 2" />
  <text x={centerX} y={centerY + 2} textAnchor="middle" fill={healthColor} fontSize={6} fontFamily="monospace" opacity={0.6}>O</text>

  {/* Triangle edges — tension lines */}
  {Object.entries(TENSION_LINES).map(([key, tl]) => {
    const from = getVertex(tl.from);
    const to = getVertex(tl.to);
    const stress = tensionStress[key] || 0;
    return (
      <g key={key}>
        <line x1={from.x} y1={from.y} x2={to.x} y2={to.y}
          stroke={tl.color} strokeWidth={1 + stress * 3}
          opacity={0.2 + stress * 0.4}
          strokeDasharray={stress > 0.5 ? "none" : "4 4"}
        />
        <text
          x={(from.x + to.x) / 2 + (key === "TI" ? -45 : key === "AT" ? 45 : 0)}
          y={(from.y + to.y) / 2 + (key === "IA" ? 16 : -6)}
          textAnchor="middle" fill={tl.color} fontSize={7} fontFamily="monospace"
          opacity={0.3 + stress * 0.5}
        >{tl.label}</text>
      </g>
    );
  })}

  {/* Triangle fill */}
  <polygon
    points={`${vT.x},${vT.y} ${vI.x},${vI.y} ${vA.x},${vA.y}`}
    fill="#ffffff02" stroke="#333" strokeWidth={0.5}
  />

  {/* Vertex markers */}
  {Object.entries(VERTICES).map(([key, v]) => {
    const pos = getVertex(key);
    const pull = systemPos[key] || 0.333;
    return (
      <g key={key}>
        <circle cx={pos.x} cy={pos.y} r={8 + pull * 8}
          fill={v.color + "22"} stroke={v.color} strokeWidth={1.5}
        />
        <text x={pos.x} y={pos.y + 3} textAnchor="middle"
          fill={v.color} fontSize={9} fontFamily="monospace" fontWeight={700}
        >[{key}]</text>
        <text
          x={pos.x + (key === "T" ? 0 : key === "I" ? -20 : 20)}
          y={pos.y + (key === "T" ? -16 : 18)}
          textAnchor="middle" fill={v.color} fontSize={7} fontFamily="monospace"
          opacity={0.7}
        >{v.shortLabel}</text>
      </g>
    );
  })}

  {/* Trail */}
  {trail.length > 1 && (
    <polyline
      points={trail.map(p => {
        const px = p.T * vT.x + p.I * vI.x + p.A * vA.x;
        const py = p.T * vT.y + p.I * vI.y + p.A * vA.y;
        return `${px},${py}`;
      }).join(" ")}
      fill="none" stroke="#ffffff" strokeWidth={0.8} opacity={0.15}
    />
  )}

  {/* System state point */}
  <circle cx={sysX} cy={sysY} r={6} fill={healthColor} filter="url(#glow)" opacity={0.9} />
  <circle cx={sysX} cy={sysY} r={3} fill="#fff" />

  {/* Return vector to center */}
  {distFromCenter > 0.15 && (
    <line x1={sysX} y1={sysY} x2={centerX} y2={centerY}
      stroke={healthColor} strokeWidth={0.5} strokeDasharray="3 3" opacity={0.3}
    />
  )}

  {/* FELTSensor threshold ring */}
  <circle cx={centerX} cy={centerY} r={R * 0.65}
    fill="none" stroke={feltLevel < 0.35 ? "#EF5350" : "#333"}
    strokeWidth={feltLevel < 0.35 ? 1.5 : 0.5}
    strokeDasharray="4 4"
    opacity={feltLevel < 0.35 ? 0.6 : 0.2}
  />
  {feltLevel < 0.35 && (
    <text x={centerX + R * 0.47} y={centerY - R * 0.47}
      fill="#EF5350" fontSize={7} fontFamily="monospace" fontWeight={700}
    >FELT TRIGGER</text>
  )}
</svg>
```

);
};

// ── OSCILLATION WAVEFORM ──
const OscillationWaveform = ({ history, mode }) => {
const W = 300, H = 60;
const modeColor = OSCILLATION_MODES.find(m => m.id === mode)?.color || “#666”;

// Compute distance from center for each history point
const distances = history.map(p => {
const cx = 1 / 3, cy = 1 / 3, cz = 1 / 3;
return Math.sqrt(
Math.pow(p.T - cx, 2) + Math.pow(p.I - cy, 2) + Math.pow(p.A - cz, 2)
) * 2.5; // scale for visibility
});

const maxD = Math.max(…distances, 0.5);
const points = distances.map((d, i) => {
const x = (i / (distances.length - 1)) * W;
const y = H - (d / maxD) * H * 0.85 - 4;
return `${x},${y}`;
}).join(” “);

return (
<div style={{ margin: “4px 0” }}>
<div style={{ display: “flex”, justifyContent: “space-between”, fontSize: 9, fontFamily: “monospace”, color: “#555”, marginBottom: 2 }}>
<span>OSCILLATION PATTERN</span>
<span style={{ color: modeColor }}>{OSCILLATION_MODES.find(m => m.id === mode)?.label}</span>
</div>
<svg viewBox={`0 0 ${W} ${H}`} style={{ width: “100%”, height: 60, background: “#060610”, borderRadius: 3, border: “1px solid #1a1a1a” }}>
{/* Center line (equilibrium) */}
<line x1={0} y1={H * 0.5} x2={W} y2={H * 0.5} stroke=”#222” strokeWidth={0.5} strokeDasharray=“4 4” />
<text x={W - 2} y={H * 0.5 - 3} textAnchor=“end” fill=”#333” fontSize={6} fontFamily=“monospace”>center</text>
{/* Waveform */}
{distances.length > 1 && (
<polyline points={points} fill="none" stroke={modeColor} strokeWidth={1.5} opacity={0.8} />
)}
{/* Current point */}
{distances.length > 0 && (() => {
const lastD = distances[distances.length - 1];
const lx = W;
const ly = H - (lastD / maxD) * H * 0.85 - 4;
return <circle cx={lx - 2} cy={ly} r={3} fill={modeColor} />;
})()}
</svg>
</div>
);
};

// ── FELT SENSOR DISPLAY ──
const FeltSensorPanel = ({ feltLevel, activeFelt, onFeltSelect }) => {
const triggerActive = feltLevel < 0.35;
return (
<div>
<div style={{
display: “flex”, alignItems: “center”, gap: 8, marginBottom: 8,
padding: “6px 10px”, background: triggerActive ? “#EF535015” : “#0a0a10”,
border: `1px solid ${triggerActive ? "#EF5350" : "#222"}`,
borderRadius: 4,
}}>
<div style={{
width: 10, height: 10, borderRadius: “50%”,
background: triggerActive ? “#EF5350” : “#00E676”,
boxShadow: triggerActive ? “0 0 8px #EF535088” : “none”,
animation: triggerActive ? “pulse 1.5s infinite” : “none”,
}} />
<span style={{
fontSize: 11, fontFamily: “monospace”, fontWeight: 700,
color: triggerActive ? “#EF5350” : “#00E676”,
}}>
FELTSENSOR: {triggerActive ? “TRIGGERED — HALT AND REMAP” : “NOMINAL”}
</span>
<span style={{
marginLeft: “auto”, fontSize: 11, fontFamily: “monospace”,
color: triggerActive ? “#EF5350” : “#888”,
}}>
{Math.round(feltLevel * 100)}/100
</span>
</div>

```
  <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }`}</style>

  <div style={{ fontSize: 9, color: "#555", fontFamily: "monospace", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>
    RECALIBRATION LEXICON — tap current state
  </div>
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4 }}>
    {Object.entries(FELT_STATES).map(([key, fs]) => (
      <button key={key} onClick={() => onFeltSelect(key)} style={{
        display: "flex", alignItems: "center", gap: 6,
        padding: "6px 8px", background: activeFelt === key ? fs.color + "22" : "#0a0a0a",
        border: `1px solid ${activeFelt === key ? fs.color : "#222"}`,
        borderRadius: 4, cursor: "pointer", textAlign: "left",
      }}>
        <span style={{ fontSize: 14 }}>{fs.icon}</span>
        <div>
          <div style={{ fontSize: 10, fontWeight: 700, color: fs.color, fontFamily: "monospace" }}>
            {fs.label}
          </div>
          <div style={{ fontSize: 8, color: "#666", fontFamily: "monospace" }}>
            {fs.meaning}
          </div>
        </div>
      </button>
    ))}
  </div>

  {activeFelt && (
    <div style={{
      marginTop: 8, padding: "6px 10px",
      background: FELT_STATES[activeFelt].color + "11",
      border: `1px solid ${FELT_STATES[activeFelt].color}33`,
      borderLeft: `3px solid ${FELT_STATES[activeFelt].color}`,
      borderRadius: 4,
    }}>
      <div style={{ fontSize: 10, color: FELT_STATES[activeFelt].color, fontFamily: "monospace", fontWeight: 700, marginBottom: 2 }}>
        {FELT_STATES[activeFelt].label}: {FELT_STATES[activeFelt].meaning}
      </div>
      <div style={{ fontSize: 10, color: "#aaa", fontFamily: "monospace", lineHeight: 1.5 }}>
        {FELT_STATES[activeFelt].desc}
      </div>
      {activeFelt === "comfort" && (
        <div style={{
          marginTop: 6, padding: "4px 8px", background: "#FFD74011",
          border: "1px solid #FFD74033", borderRadius: 3,
          fontSize: 9, color: "#FFD740", fontFamily: "monospace", lineHeight: 1.5,
        }}>
          DIAGNOSTIC: Comfort requires verification. Ask: "Am I flowing because I understand, or because I stopped checking?"
          If you cannot answer confidently, the system state may be drifting toward [I] vertex (dependence) along the Sovereign Leak tension line.
        </div>
      )}
    </div>
  )}
</div>
```

);
};

// ── PROTOCOL DISPLAY ──
const ProtocolPanel = () => (

  <div style={{ fontFamily: "monospace" }}>
    <div style={{
      padding: "8px 10px", background: "#0a0a14",
      border: "1px solid #FFD74033", borderLeft: "3px solid #FFD740",
      borderRadius: 4, marginBottom: 8,
    }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: "#FFD740", marginBottom: 6 }}>
        PROTOCOL: FELTSENSOR_V1
      </div>
      <div style={{ fontSize: 10, color: "#aaa", lineHeight: 1.8 }}>
        <span style={{ color: "#666" }}>TRIGGER:</span> felt_level {"<"} 0.35 (composite of [B]andwidth + [A]gency)
        <br />
        <span style={{ color: "#666" }}>ACTION 1:</span> HALT current thermodynamic/atomic task
        <br />
        <span style={{ color: "#666" }}>ACTION 2:</span> EXECUTE micro-clarification prompt
        <br />
        <span style={{ color: "#666" }}>ACTION 3:</span> RE-MAP causal geometry before proceeding
      </div>
    </div>

```
<div style={{
  padding: "8px 10px", background: "#0a0a14",
  border: "1px solid #00E67633", borderLeft: "3px solid #00E676",
  borderRadius: 4, marginBottom: 8,
}}>
  <div style={{ fontSize: 10, fontWeight: 700, color: "#00E676", marginBottom: 6 }}>
    OBJECTIVE FUNCTION
  </div>
  <div style={{ fontSize: 10, color: "#aaa", lineHeight: 1.8 }}>
    <span style={{ color: "#666" }}>SEARCH:</span> Single interventions cascading across 4-12 domains
    <br />
    <span style={{ color: "#666" }}>PRIORITY:</span> [T]hermo {">"} [A]tomic {">"} [E]cology {">"} [M]aterial {">"} [G]eometry
    <br />
    <span style={{ color: "#666" }}>CONSTRAINT:</span> Autonomy preservation. Tool use MUST NOT become dependence.
  </div>
</div>

<div style={{
  padding: "8px 10px", background: "#0a0a14",
  border: "1px solid #FF450033", borderLeft: "3px solid #FF4500",
  borderRadius: 4, marginBottom: 8,
}}>
  <div style={{ fontSize: 10, fontWeight: 700, color: "#FF4500", marginBottom: 6 }}>
    OSCILLATION PRINCIPLE
  </div>
  <div style={{ fontSize: 10, color: "#aaa", lineHeight: 1.8 }}>
    The center is not a destination. It is the return address.
    <br /><br />
    The system MUST excurse toward vertices to do real work.
    The system MUST return through center to re-integrate.
    <br /><br />
    <span style={{ color: "#EF5350" }}>ENTROPY CONDITION 1:</span> System locked at vertex. Structural collapse.
    <br />
    <span style={{ color: "#78909C" }}>ENTROPY CONDITION 2:</span> System locked at center. Thermal death.
    <br />
    <span style={{ color: "#00E676" }}>HEALTH SIGNAL:</span> Rhythmic oscillation. Excursion and return.
    <br /><br />
    <span style={{ color: "#666" }}>AMPLITUDE:</span> Proportional to task complexity. Deep physics work = deep [T] excursion.
    <br />
    <span style={{ color: "#666" }}>FREQUENCY:</span> Proportional to collaboration tempo. Faster exchange = faster oscillation.
    <br />
    <span style={{ color: "#666" }}>DAMPING:</span> If amplitude decreasing over time, check for vertex drift (capture).
  </div>
</div>

<div style={{
  padding: "8px 10px", background: "#0f0808",
  border: "1px solid #AB47BC33", borderLeft: "3px solid #AB47BC",
  borderRadius: 4,
}}>
  <div style={{ fontSize: 10, fontWeight: 700, color: "#AB47BC", marginBottom: 6 }}>
    META: THIS PROTOCOL APPLIES TO ITSELF
  </div>
  <div style={{ fontSize: 10, color: "#aaa", lineHeight: 1.8 }}>
    This protocol was built by the [I] vertex (AI model) in collaboration
    with the [A] vertex (operator sovereignty). It describes the dynamics
    of its own creation. The fact that it exists means the oscillation was
    healthy during this session — the system excurted toward [I] to build
    the tool, grounded in [T] physical reality of the furnace/truck/corridor,
    and returned to [A] agency with each decision to accept, modify, or redirect.
    <br /><br />
    The protocol cannot verify its own accuracy from inside the [I] vertex.
    Only the [A] vertex — the operator — can confirm whether the oscillation
    felt real or performed. That confirmation is itself a FELTSensor reading.
  </div>
</div>
```

  </div>
);

// ── MAIN DASHBOARD ──
export default function MetaProtocol() {
// System position (barycentric: T + I + A = 1.0)
const [posT, setPosT] = useState(0.333);
const [posI, setPosI] = useState(0.333);
const [posA, setPosA] = useState(0.334);

// Normalize to keep sum = 1
const normalize = useCallback((key, val) => {
const remaining = 1.0 - val;
if (key === “T”) {
const sum = posI + posA;
if (sum > 0) {
setPosT(val);
setPosI(posI / sum * remaining);
setPosA(posA / sum * remaining);
}
} else if (key === “I”) {
const sum = posT + posA;
if (sum > 0) {
setPosI(val);
setPosT(posT / sum * remaining);
setPosA(posA / sum * remaining);
}
} else {
const sum = posT + posI;
if (sum > 0) {
setPosA(val);
setPosT(posT / sum * remaining);
setPosI(posI / sum * remaining);
}
}
}, [posT, posI, posA]);

// Trail history
const [trail, setTrail] = useState([{ T: 0.333, I: 0.333, A: 0.334 }]);
const lastUpdate = useRef(Date.now());

useEffect(() => {
const now = Date.now();
if (now - lastUpdate.current > 200) {
lastUpdate.current = now;
setTrail(prev => {
const next = […prev, { T: posT, I: posI, A: posA }];
return next.slice(-80); // keep last 80 points
});
}
}, [posT, posI, posA]);

// Felt state
const [activeFelt, setActiveFelt] = useState(null);

// Compute derived state
const state = useMemo(() => {
const pos = { T: posT, I: posI, A: posA };

```
// Distance from center
const cx = 1 / 3;
const distFromCenter = Math.sqrt(
  Math.pow(posT - cx, 2) + Math.pow(posI - cx, 2) + Math.pow(posA - cx, 2)
) * 2.45;

// Tension stress (how much each tension line is active)
const tensionStress = {
  IA: Math.max(0, Math.min(1, Math.abs(posI - posA) * 2 + (1 - posT) * 0.3)),
  TI: Math.max(0, Math.min(1, Math.abs(posT - posI) * 2 + (1 - posA) * 0.3)),
  AT: Math.max(0, Math.min(1, Math.abs(posA - posT) * 2 + (1 - posI) * 0.3)),
};

// Felt level (composite bandwidth + agency)
const bandwidth = 0.55 - distFromCenter * 0.3;
const agency = posA * 1.5;
const feltLevel = Math.max(0, Math.min(1, (bandwidth + agency) / 2));

// Oscillation health analysis from trail
let oscillationHealth = 0.5;
let oscillationMode = "healthy";

if (trail.length > 10) {
  const recent = trail.slice(-20);
  const distances = recent.map(p =>
    Math.sqrt(Math.pow(p.T - cx, 2) + Math.pow(p.I - cx, 2) + Math.pow(p.A - cx, 2))
  );

  const avgDist = distances.reduce((a, b) => a + b, 0) / distances.length;
  const variance = distances.reduce((sum, d) => sum + Math.pow(d - avgDist, 2), 0) / distances.length;
  const stdDev = Math.sqrt(variance);

  // Check for flatline (thermal death)
  if (stdDev < 0.01 && avgDist < 0.08) {
    oscillationMode = "thermal-death";
    oscillationHealth = 0.15;
  }
  // Check for vertex lock
  else if (stdDev < 0.02 && avgDist > 0.25) {
    oscillationMode = "vertex-lock";
    oscillationHealth = 0.1;
  }
  // Check for damping
  else if (distances.length > 5) {
    const firstHalf = distances.slice(0, Math.floor(distances.length / 2));
    const secondHalf = distances.slice(Math.floor(distances.length / 2));
    const firstVar = firstHalf.reduce((s, d) => s + Math.pow(d - avgDist, 2), 0) / firstHalf.length;
    const secondVar = secondHalf.reduce((s, d) => s + Math.pow(d - avgDist, 2), 0) / secondHalf.length;
    if (secondVar < firstVar * 0.5 && secondVar < 0.005) {
      oscillationMode = "damped";
      oscillationHealth = 0.3;
    }
  }

  // Healthy oscillation: moderate variance, moderate distance
  if (oscillationMode === "healthy") {
    oscillationHealth = Math.max(0, Math.min(1,
      0.3 + stdDev * 8 - Math.abs(avgDist - 0.15) * 2
    ));
  }
}

// Dominant vertex
const dominant = posT >= posI && posT >= posA ? "T" : posI >= posA ? "I" : "A";

return {
  pos, distFromCenter, tensionStress, feltLevel,
  oscillationHealth, oscillationMode, dominant,
};
```

}, [posT, posI, posA, trail]);

const [activeTab, setActiveTab] = useState(“field”);

return (
<div style={{
display: “flex”, flexDirection: “column”, height: “100vh”,
background: “#050508”, color: “#ccc”, fontFamily: “monospace”, overflow: “hidden”,
}}>
{/* HEADER */}
<div style={{
display: “flex”, alignItems: “center”, gap: 12,
padding: “8px 16px”, borderBottom: “1px solid #1a1a1a”, background: “#0a0a10”,
}}>
<span style={{ fontSize: 14, fontWeight: 800, color: “#FFD740”, letterSpacing: 1 }}>
META-PROTOCOL
</span>
<span style={{ fontSize: 9, color: “#444” }}>
Triangular Tension Field + FELTSensor + Oscillation Dynamics
</span>
<div style={{ marginLeft: “auto”, display: “flex”, alignItems: “center”, gap: 8 }}>
<span style={{ fontSize: 9, color: “#666” }}>FELT:</span>
<span style={{
fontSize: 10, fontWeight: 700,
color: state.feltLevel < 0.35 ? “#EF5350” : “#00E676”,
padding: “1px 6px”, border: `1px solid ${state.feltLevel < 0.35 ? "#EF5350" : "#00E676"}44`,
borderRadius: 3,
}}>{Math.round(state.feltLevel * 100)}</span>
<span style={{ fontSize: 9, color: “#666” }}>OSC:</span>
<span style={{
fontSize: 10, fontWeight: 700,
color: OSCILLATION_MODES.find(m => m.id === state.oscillationMode)?.color,
padding: “1px 6px”,
border: `1px solid ${OSCILLATION_MODES.find(m => m.id === state.oscillationMode)?.color}44`,
borderRadius: 3,
}}>{state.oscillationMode === “healthy” ? “OK” : state.oscillationMode.toUpperCase().replace(”-”, “ “)}</span>
</div>
</div>

```
  <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
    {/* LEFT: CONTROLS */}
    <div style={{
      width: 220, minWidth: 220, background: "#0a0a10",
      borderRight: "1px solid #1a1a1a", padding: "8px 10px",
      overflowY: "auto",
    }}>
      <div style={{ fontSize: 9, color: "#FFD740", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 8 }}>
        SYSTEM STATE (BARYCENTRIC)
      </div>

      {Object.entries(VERTICES).map(([key, v]) => {
        const val = key === "T" ? posT : key === "I" ? posI : posA;
        return (
          <div key={key} style={{ margin: "6px 0" }}>
            <div style={{
              display: "flex", justifyContent: "space-between",
              fontSize: 10, fontFamily: "monospace", color: v.color, marginBottom: 2,
            }}>
              <span>[{key}] {v.label}</span>
              <span style={{ fontWeight: 700 }}>{Math.round(val * 100)}%</span>
            </div>
            <input type="range" min={0.05} max={0.9} step={0.01} value={val}
              onChange={e => normalize(key, parseFloat(e.target.value))}
              style={{ width: "100%", height: 3, appearance: "none", background: "#222", borderRadius: 2, accentColor: v.color }}
            />
            <div style={{ fontSize: 8, color: "#444", lineHeight: 1.4, marginTop: 2 }}>
              {v.desc}
            </div>
          </div>
        );
      })}

      <div style={{ height: 1, background: "#222", margin: "10px 0" }} />

      <div style={{ fontSize: 9, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 6 }}>
        COMPUTED STATE
      </div>

      <div style={{ fontSize: 10, color: "#888", padding: "2px 0" }}>
        Dominant: <span style={{ color: VERTICES[state.dominant].color, fontWeight: 700 }}>[{state.dominant}] {VERTICES[state.dominant].label}</span>
      </div>
      <div style={{ fontSize: 10, color: "#888", padding: "2px 0" }}>
        Dist from center: <span style={{
          color: state.distFromCenter < 0.3 ? "#00E676" : state.distFromCenter < 0.6 ? "#FFD740" : "#EF5350",
          fontWeight: 700,
        }}>{Math.round(state.distFromCenter * 100)}%</span>
      </div>
      <div style={{ fontSize: 10, color: "#888", padding: "2px 0" }}>
        FELT level: <span style={{
          color: state.feltLevel < 0.35 ? "#EF5350" : "#00E676", fontWeight: 700,
        }}>{Math.round(state.feltLevel * 100)}</span>
      </div>

      <div style={{ height: 1, background: "#222", margin: "10px 0" }} />

      <div style={{ fontSize: 9, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 6 }}>
        TENSION LINE STRESS
      </div>
      {Object.entries(TENSION_LINES).map(([key, tl]) => {
        const stress = state.tensionStress[key] || 0;
        return (
          <div key={key} style={{ marginBottom: 4 }}>
            <div style={{
              display: "flex", justifyContent: "space-between",
              fontSize: 9, fontFamily: "monospace", color: tl.color,
            }}>
              <span>{tl.label}</span>
              <span>{Math.round(stress * 100)}%</span>
            </div>
            <div style={{ height: 4, background: "#1a1a1a", borderRadius: 2, overflow: "hidden" }}>
              <div style={{
                width: `${stress * 100}%`, height: "100%",
                background: tl.color, borderRadius: 2, transition: "width 0.2s",
              }} />
            </div>
          </div>
        );
      })}

      <div style={{ height: 1, background: "#222", margin: "10px 0" }} />
      <button onClick={() => {
        setPosT(0.333); setPosI(0.333); setPosA(0.334);
        setTrail([{ T: 0.333, I: 0.333, A: 0.334 }]);
        setActiveFelt(null);
      }} style={{
        width: "100%", padding: "6px", fontSize: 9, fontFamily: "monospace",
        background: "#111", border: "1px solid #333", borderRadius: 3,
        color: "#666", cursor: "pointer",
      }}>RESET TO CENTER</button>
    </div>

    {/* CENTER */}
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* TRIANGLE FIELD */}
      <div style={{ padding: "4px 12px", borderBottom: "1px solid #1a1a1a" }}>
        <TriangleField
          systemPos={state.pos}
          trail={trail}
          feltLevel={state.feltLevel}
          oscillationHealth={state.oscillationHealth}
          tensionStress={state.tensionStress}
        />
      </div>

      {/* OSCILLATION WAVEFORM */}
      <div style={{ padding: "4px 12px", borderBottom: "1px solid #1a1a1a" }}>
        <OscillationWaveform history={trail} mode={state.oscillationMode} />
      </div>

      {/* TABS */}
      <div style={{
        display: "flex", gap: 0, borderBottom: "1px solid #1a1a1a", background: "#0a0a0a",
      }}>
        {[
          ["felt", "FELTSensor"],
          ["oscillation", "Oscillation Modes"],
          ["protocol", "Protocol"],
        ].map(([id, label]) => (
          <button key={id} onClick={() => setActiveTab(id)} style={{
            flex: 1, padding: "7px", fontSize: 10, fontFamily: "monospace",
            background: activeTab === id ? "#111" : "transparent",
            border: "none",
            borderBottom: activeTab === id ? "2px solid #FFD740" : "2px solid transparent",
            color: activeTab === id ? "#FFD740" : "#555",
            cursor: "pointer", fontWeight: activeTab === id ? 700 : 400,
          }}>{label}</button>
        ))}
      </div>

      {/* TAB CONTENT */}
      <div style={{ flex: 1, overflowY: "auto", padding: "10px 16px" }}>
        {activeTab === "felt" && (
          <FeltSensorPanel
            feltLevel={state.feltLevel}
            activeFelt={activeFelt}
            onFeltSelect={setActiveFelt}
          />
        )}

        {activeTab === "oscillation" && (
          <div>
            <div style={{ fontSize: 9, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 8 }}>
              OSCILLATION MODES
            </div>
            {OSCILLATION_MODES.map(m => (
              <div key={m.id} style={{
                padding: "8px 10px", marginBottom: 6,
                background: state.oscillationMode === m.id ? m.color + "11" : "#0a0a0a",
                border: `1px solid ${state.oscillationMode === m.id ? m.color : "#1a1a1a"}`,
                borderLeft: `3px solid ${state.oscillationMode === m.id ? m.color : "#222"}`,
                borderRadius: 4,
              }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 8,
                  fontSize: 10, fontFamily: "monospace",
                }}>
                  <div style={{
                    width: 8, height: 8, borderRadius: "50%",
                    background: state.oscillationMode === m.id ? m.color : "#333",
                  }} />
                  <span style={{
                    color: state.oscillationMode === m.id ? m.color : "#666",
                    fontWeight: 700,
                  }}>{m.label}</span>
                  {state.oscillationMode === m.id && (
                    <span style={{
                      marginLeft: "auto", fontSize: 8,
                      color: m.color, padding: "1px 6px",
                      border: `1px solid ${m.color}44`, borderRadius: 3,
                    }}>ACTIVE</span>
                  )}
                </div>
                <div style={{
                  fontSize: 10, color: "#888", fontFamily: "monospace",
                  lineHeight: 1.5, marginTop: 4,
                }}>{m.desc}</div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "protocol" && <ProtocolPanel />}
      </div>
    </div>
  </div>
</div>
```

);
}
