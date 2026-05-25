"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Panel } from "./Panel";
import { Badge } from "@/components/ui/Badge";
import { IconLayers } from "./icons";

const PHASES = [
  { key: "wake", label: "Wake", color: "var(--color-neural)", description: "Anchor representations on clean data" },
  { key: "dream", label: "Dream", color: "var(--color-dream)", description: "Mild distortions to learn invariance" },
  { key: "nightmare", label: "Nightmare", color: "var(--color-nightmare)", description: "Adversarial stress for robustness" },
  { key: "compress", label: "Compress", color: "var(--color-warning)", description: "Distill into a leaner student" },
] as const;

export function PhaseVisualizer({ activePhase = 1 }: { activePhase?: number }) {
  const [t, setT] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setT((x) => (x + 1) % 360), 60);
    return () => clearInterval(id);
  }, []);

  const r = 90;
  const cx = 130;
  const cy = 130;
  const arcAngle = 360 / PHASES.length;
  const phase = PHASES[activePhase];

  return (
    <Panel
      title="Phase Visualizer"
      subtitle="Sleep cycle · animated"
      icon={<IconLayers size={14} />}
      glow="dream"
      toolbar={
        <Badge variant="neural" size="xs" dot>
          cycle 4 / 5
        </Badge>
      }
    >
      <div className="flex flex-col items-center gap-4 py-2 lg:flex-row lg:items-center lg:gap-6">
        <div className="relative" style={{ width: 260, height: 260 }}>
          <svg width="260" height="260" viewBox="0 0 260 260">
            <defs>
              {PHASES.map((p, i) => (
                <linearGradient key={p.key} id={`pv-grad-${i}`} x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor={p.color} stopOpacity="0.85" />
                  <stop offset="100%" stopColor={p.color} stopOpacity="0.25" />
                </linearGradient>
              ))}
            </defs>
            <circle cx={cx} cy={cy} r={r + 14} stroke="rgba(255,255,255,0.04)" fill="none" />
            <circle cx={cx} cy={cy} r={r - 18} stroke="rgba(255,255,255,0.04)" fill="none" />

            {PHASES.map((p, i) => {
              const start = i * arcAngle - 90;
              const end = start + arcAngle - 4;
              const sx = cx + r * Math.cos((start * Math.PI) / 180);
              const sy = cy + r * Math.sin((start * Math.PI) / 180);
              const ex = cx + r * Math.cos((end * Math.PI) / 180);
              const ey = cy + r * Math.sin((end * Math.PI) / 180);
              const large = end - start > 180 ? 1 : 0;
              const isActive = i === activePhase;
              return (
                <motion.path
                  key={p.key}
                  d={`M ${sx} ${sy} A ${r} ${r} 0 ${large} 1 ${ex} ${ey}`}
                  stroke={`url(#pv-grad-${i})`}
                  strokeWidth={isActive ? 14 : 8}
                  strokeLinecap="round"
                  fill="none"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: isActive ? 1 : 0.5 }}
                  transition={{ duration: 1, delay: i * 0.12, ease: "easeOut" }}
                  style={isActive ? { filter: `drop-shadow(0 0 6px ${p.color})` } : undefined}
                />
              );
            })}

            <motion.circle
              cx={cx + r * Math.cos((t * Math.PI) / 180 - Math.PI / 2)}
              cy={cy + r * Math.sin((t * Math.PI) / 180 - Math.PI / 2)}
              r="4"
              fill={phase.color}
              style={{ filter: `drop-shadow(0 0 8px ${phase.color})` }}
            />

            {PHASES.map((p, i) => {
              const angle = i * arcAngle + arcAngle / 2 - 90;
              const tx = cx + (r + 30) * Math.cos((angle * Math.PI) / 180);
              const ty = cy + (r + 30) * Math.sin((angle * Math.PI) / 180);
              const isActive = i === activePhase;
              return (
                <text
                  key={p.key}
                  x={tx}
                  y={ty}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="font-mono"
                  fontSize="10"
                  fill={isActive ? p.color : "rgba(148,163,184,0.6)"}
                  style={isActive ? { filter: `drop-shadow(0 0 4px ${p.color})` } : undefined}
                >
                  {p.label.toUpperCase()}
                </text>
              );
            })}

            <motion.circle
              cx={cx}
              cy={cy}
              r={28}
              fill="rgba(0,0,0,0.5)"
              stroke={phase.color}
              strokeWidth="1"
              animate={{ scale: [1, 1.06, 1] }}
              transition={{ duration: 1.6, repeat: Infinity }}
            />
            <text
              x={cx}
              y={cy + 1}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="11"
              fontWeight="600"
              fill={phase.color}
              style={{ filter: `drop-shadow(0 0 6px ${phase.color})` }}
            >
              {phase.label}
            </text>
          </svg>
        </div>

        <div className="flex-1 space-y-2">
          {PHASES.map((p, i) => {
            const isActive = i === activePhase;
            return (
              <div
                key={p.key}
                className={[
                  "flex items-start gap-3 rounded-lg border p-2.5 transition-colors",
                  isActive ? "border-white/[0.10] bg-white/[0.04]" : "border-white/[0.05] bg-white/[0.01]",
                ].join(" ")}
              >
                <span
                  className="mt-1 inline-block h-2 w-2 rounded-full"
                  style={{ background: p.color, boxShadow: isActive ? `0 0 8px ${p.color}` : undefined }}
                />
                <div className="min-w-0">
                  <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: p.color }}>
                    {p.label}
                  </p>
                  <p className="text-[11px] text-slate-400">{p.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Panel>
  );
}
