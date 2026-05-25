"use client";

import { motion } from "framer-motion";
import { Panel } from "./Panel";
import { Badge } from "@/components/ui/Badge";
import { CircularProgress, Progress } from "@/components/ui/Progress";
import {
  IconActivity,
  IconBenchmark,
  IconCpu,
  IconHome,
  IconQueue,
  IconRunning,
  IconSparkle,
  IconTrend,
} from "./icons";

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  tone?: "neural" | "dream" | "nightmare" | "success" | "warning";
  icon: React.ReactNode;
}

function MetricCard({ label, value, delta, tone = "neural", icon }: MetricCardProps) {
  const toneClasses = {
    neural: "from-neural/[0.05] to-transparent border-neural/15 text-neural",
    dream: "from-dream/[0.05] to-transparent border-dream/15 text-dream",
    nightmare: "from-nightmare/[0.05] to-transparent border-nightmare/15 text-nightmare",
    success: "from-emerald-500/[0.05] to-transparent border-emerald-500/15 text-emerald-300",
    warning: "from-amber-500/[0.05] to-transparent border-amber-500/15 text-amber-300",
  }[tone];
  return (
    <div
      className={[
        "flex items-start gap-3 rounded-lg border bg-gradient-to-br p-3",
        toneClasses,
      ].join(" ")}
    >
      <span className="flex h-8 w-8 items-center justify-center rounded-md bg-white/[0.04]">
        {icon}
      </span>
      <div className="min-w-0">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
          {label}
        </p>
        <p className="mt-0.5 font-mono text-lg leading-none text-slate-100">{value}</p>
        {delta && <p className="mt-1 text-[10px] text-slate-500">{delta}</p>}
      </div>
    </div>
  );
}

const SPARK_DATA = [76.2, 77.1, 76.8, 78.4, 79.0, 80.3, 81.2, 80.9, 81.7, 82.4];

function MiniSparkline({ values }: { values: number[] }) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const w = 220;
  const h = 60;
  const pad = 4;
  const range = Math.max(0.0001, max - min);
  const pts = values.map((v, i) => {
    const x = pad + (i / (values.length - 1)) * (w - pad * 2);
    const y = h - pad - ((v - min) / range) * (h - pad * 2);
    return [x, y] as const;
  });
  const path = pts.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  const area = `${path} L${pts[pts.length - 1][0]} ${h - pad} L${pts[0][0]} ${h - pad} Z`;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
      <defs>
        <linearGradient id="cc-spark" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="var(--color-neural)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="var(--color-neural)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#cc-spark)" />
      <motion.path
        d={path}
        fill="none"
        stroke="var(--color-neural)"
        strokeWidth="1.6"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.2, ease: "easeOut" }}
      />
      {pts.map(([x, y], i) => (
        <circle
          key={i}
          cx={x}
          cy={y}
          r={i === pts.length - 1 ? 2.5 : 1}
          fill={i === pts.length - 1 ? "var(--color-neural)" : "rgba(255,255,255,0.4)"}
        />
      ))}
    </svg>
  );
}

export function CommandCenter() {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <Panel
        title="Command Center"
        subtitle="Operational overview · last 24h"
        icon={<IconHome size={14} />}
        glow="neural"
        className="lg:col-span-2"
      >
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <MetricCard
            label="Active Runs"
            value="3"
            delta="2 training · 1 evaluating"
            tone="neural"
            icon={<IconRunning size={14} />}
          />
          <MetricCard
            label="Total Experiments"
            value="148"
            delta="+12 this week"
            tone="dream"
            icon={<IconBenchmark size={14} />}
          />
          <MetricCard
            label="Robustness"
            value="82.4"
            delta="+4.1 vs baseline"
            tone="success"
            icon={<IconSparkle size={14} />}
          />
          <MetricCard
            label="Queue"
            value="5"
            delta="ETA · 12m"
            tone="warning"
            icon={<IconQueue size={14} />}
          />
        </div>

        <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <IconTrend size={12} />
                <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                  Robustness Trend · 10 cycles
                </span>
              </div>
              <Badge variant="success" size="xs">
                +6.2 net
              </Badge>
            </div>
            <MiniSparkline values={SPARK_DATA} />
          </div>

          <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
            <div className="mb-2 flex items-center gap-1.5">
              <IconCpu size={12} />
              <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                Cluster Utilization
              </span>
            </div>
            <div className="space-y-2.5">
              <div>
                <div className="mb-1 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">GPU · RTX 3050 Ti</span>
                  <span className="font-mono text-slate-300">72%</span>
                </div>
                <Progress value={72} tone="neural" size="xs" />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">VRAM · 4GB</span>
                  <span className="font-mono text-slate-300">3.1GB / 4.0GB</span>
                </div>
                <Progress value={77} tone="warning" size="xs" />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">CPU</span>
                  <span className="font-mono text-slate-300">34%</span>
                </div>
                <Progress value={34} tone="success" size="xs" />
              </div>
            </div>
          </div>
        </div>
      </Panel>

      <Panel
        title="System Pulse"
        subtitle="Live runtime telemetry"
        icon={<IconActivity size={14} />}
        glow="dream"
      >
        <div className="flex flex-col items-center gap-3 py-2">
          <CircularProgress value={82.4} size={120} thickness={8} tone="neural" showValue={false} />
          <div className="-mt-[88px] flex flex-col items-center pointer-events-none">
            <span className="font-mono text-2xl text-slate-100">82.4</span>
            <span className="text-[10px] uppercase tracking-widest text-slate-500">Robustness</span>
          </div>
          <div className="mt-12 grid w-full grid-cols-3 gap-2 text-center">
            {[
              { label: "Wake", value: "0.42", tone: "neural" as const },
              { label: "Dream", value: "0.71", tone: "dream" as const },
              { label: "Nightmare", value: "1.84", tone: "nightmare" as const },
            ].map((m) => (
              <div key={m.label} className="rounded-md border border-white/[0.06] bg-white/[0.02] py-1.5">
                <p className="text-[10px] uppercase tracking-widest text-slate-500">{m.label}</p>
                <p className={`font-mono text-sm text-${m.tone}`}>{m.value}</p>
              </div>
            ))}
          </div>
        </div>
      </Panel>
    </div>
  );
}
