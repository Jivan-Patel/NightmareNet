"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Panel } from "./Panel";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Progress } from "@/components/ui/Progress";
import {
  IconActivity,
  IconCheck,
  IconClock,
  IconDownload,
  IconRunning,
  IconSparkle,
} from "./icons";

type PhaseTab = "wake" | "dream" | "nightmare" | "compress";

const TABS: { key: PhaseTab; label: string; tone: "neural" | "dream" | "nightmare" | "warning" }[] = [
  { key: "wake", label: "Wake", tone: "neural" },
  { key: "dream", label: "Dream", tone: "dream" },
  { key: "nightmare", label: "Nightmare", tone: "nightmare" },
  { key: "compress", label: "Compress", tone: "warning" },
];

const PHASE_DATA: Record<
  PhaseTab,
  { lossStart: number; lossEnd: number; epochs: number; samples: number; description: string; metrics: { label: string; value: string }[] }
> = {
  wake: {
    lossStart: 2.41,
    lossEnd: 1.18,
    epochs: 1,
    samples: 200,
    description: "Standard supervised learning over the clean corpus to anchor representations.",
    metrics: [
      { label: "Avg Loss", value: "1.42" },
      { label: "Steps", value: "256" },
      { label: "Tokens/s", value: "1.2k" },
      { label: "LR", value: "5e-5" },
    ],
  },
  dream: {
    lossStart: 1.18,
    lossEnd: 0.82,
    epochs: 1,
    samples: 200,
    description: "Mild distortion cycle exposing the model to plausible variations and paraphrases.",
    metrics: [
      { label: "Strength", value: "0.25" },
      { label: "Avg Loss", value: "0.97" },
      { label: "Sim", value: "0.86" },
      { label: "Length Δ", value: "+3%" },
    ],
  },
  nightmare: {
    lossStart: 0.82,
    lossEnd: 1.34,
    epochs: 1,
    samples: 200,
    description: "Adversarial stress: typos, swaps, deletions and learned attacks at high strength.",
    metrics: [
      { label: "Strength", value: "0.80" },
      { label: "Attack", value: "PGD" },
      { label: "Avg Loss", value: "1.12" },
      { label: "Δ Robust", value: "+4.1" },
    ],
  },
  compress: {
    lossStart: 1.34,
    lossEnd: 1.21,
    epochs: 1,
    samples: 200,
    description: "Knowledge distillation + pruning into a leaner, deployment-ready student model.",
    metrics: [
      { label: "Pruning", value: "0.40" },
      { label: "KL Wt", value: "0.5" },
      { label: "Size", value: "−42%" },
      { label: "Δ Quality", value: "−0.8" },
    ],
  },
};

function PhaseTimeline({ active }: { active: PhaseTab }) {
  return (
    <div className="relative flex items-center justify-between">
      <div className="absolute left-0 right-0 top-1/2 h-px -translate-y-1/2 bg-white/[0.06]" />
      {TABS.map((tab) => {
        const isActive = tab.key === active;
        return (
          <div key={tab.key} className="relative flex flex-col items-center gap-1">
            <motion.div
              animate={{ scale: isActive ? 1.05 : 1 }}
              className={[
                "flex h-8 w-8 items-center justify-center rounded-full border-2 bg-abyss",
                isActive
                  ? `border-${tab.tone} text-${tab.tone} shadow-[0_0_14px_currentColor]`
                  : "border-white/10 text-slate-500",
              ].join(" ")}
            >
              <span className="font-mono text-[11px]">{tab.label[0]}</span>
            </motion.div>
            <span className={isActive ? `text-[11px] text-${tab.tone}` : "text-[11px] text-slate-500"}>
              {tab.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export function RunDetail() {
  const [active, setActive] = useState<PhaseTab>("dream");
  const tab = TABS.find((t) => t.key === active)!;
  const data = PHASE_DATA[active];

  return (
    <Panel
      title="Run · wikitext-resilient-v3"
      subtitle="exp_4f0a · DistilBERT · cycle 4 of 5"
      icon={<IconRunning size={14} />}
      glow="neural"
      toolbar={
        <>
          <Badge variant="neural" size="xs" dot>running</Badge>
          <Button variant="ghost" size="sm" aria-label="Download report">
            <IconDownload size={12} />
          </Button>
          <Button variant="danger" size="sm">Cancel</Button>
        </>
      }
    >
      <PhaseTimeline active={active} />

      <div className="mt-4 flex flex-wrap gap-1.5 border-b border-white/[0.06] pb-2">
        {TABS.map((t) => {
          const a = t.key === active;
          return (
            <button
              key={t.key}
              type="button"
              onClick={() => setActive(t.key)}
              className={[
                "rounded-md px-2.5 py-1 text-[11px] font-medium tracking-wide cursor-pointer transition-colors",
                a
                  ? `bg-${t.tone}/10 text-${t.tone}`
                  : "text-slate-500 hover:bg-white/[0.04] hover:text-slate-200",
              ].join(" ")}
              aria-pressed={a}
            >
              {t.label}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={active}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.18 }}
          className="mt-4 space-y-4"
        >
          <p className="text-xs leading-relaxed text-slate-400">{data.description}</p>

          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {data.metrics.map((m) => (
              <div key={m.label} className="rounded-md border border-white/[0.06] bg-white/[0.02] p-2.5">
                <p className="text-[10px] uppercase tracking-widest text-slate-500">{m.label}</p>
                <p className="mt-0.5 font-mono text-sm text-slate-100">{m.value}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="mb-1.5 flex items-center gap-1.5">
                <IconActivity size={11} />
                <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                  Loss
                </span>
              </div>
              <p className="font-mono text-base text-slate-100">
                {data.lossStart.toFixed(2)} → {data.lossEnd.toFixed(2)}
              </p>
              <p className="text-[10px] text-slate-500">
                Δ {(data.lossEnd - data.lossStart).toFixed(2)}
              </p>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="mb-1.5 flex items-center gap-1.5">
                <IconClock size={11} />
                <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                  Epochs · Samples
                </span>
              </div>
              <p className="font-mono text-base text-slate-100">
                {data.epochs} · {data.samples}
              </p>
              <p className="text-[10px] text-slate-500">batch_size = 8</p>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="mb-1.5 flex items-center gap-1.5">
                <IconSparkle size={11} />
                <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                  Phase progress
                </span>
              </div>
              <Progress value={68} tone={tab.tone} size="sm" showValue />
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </Panel>
  );
}
