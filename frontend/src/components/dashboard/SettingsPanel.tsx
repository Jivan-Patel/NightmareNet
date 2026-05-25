"use client";

import { useState } from "react";
import { Panel } from "./Panel";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { useToast } from "@/components/ui/Toast";
import { IconKey, IconSettings, IconShield, IconWand } from "./icons";

type Tab = "keys" | "model" | "distortion";

const TABS: { key: Tab; label: string; icon: React.ReactNode }[] = [
  { key: "keys", label: "API Keys", icon: <IconKey size={12} /> },
  { key: "model", label: "Model", icon: <IconShield size={12} /> },
  { key: "distortion", label: "Distortion", icon: <IconWand size={12} /> },
];

interface ApiKey {
  id: string;
  name: string;
  scope: string;
  created: string;
  lastUsed: string;
  preview: string;
}

const KEYS: ApiKey[] = [
  { id: "rk_2bF…1Jq", name: "Production · CI", scope: "eval-only", created: "2026-04-12", lastUsed: "12m ago", preview: "rk_2bF***1Jq" },
  { id: "rk_84a…M0p", name: "Local dev", scope: "full", created: "2026-04-02", lastUsed: "3h ago", preview: "rk_84a***M0p" },
  { id: "rk_19e…Tx2", name: "Notebook · GPU", scope: "training", created: "2026-03-28", lastUsed: "1d ago", preview: "rk_19e***Tx2" },
];

export function SettingsPanel() {
  const [tab, setTab] = useState<Tab>("keys");
  const [model, setModel] = useState("distilbert-base-uncased");
  const [batch, setBatch] = useState("8");
  const [lr, setLr] = useState("5e-5");
  const [dreamStrength, setDreamStrength] = useState("0.25");
  const [nightmareStrength, setNightmareStrength] = useState("0.80");
  const [seed, setSeed] = useState("42");
  const toast = useToast();

  return (
    <Panel
      title="Settings"
      subtitle="Workspace · API · Defaults"
      icon={<IconSettings size={14} />}
      glow="dream"
      toolbar={<Badge variant="outline" size="xs">workspace · adit</Badge>}
    >
      <div className="mb-4 flex flex-wrap gap-1 border-b border-white/[0.06] pb-2">
        {TABS.map((t) => {
          const active = t.key === tab;
          return (
            <button
              key={t.key}
              type="button"
              onClick={() => setTab(t.key)}
              className={[
                "inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[11px] cursor-pointer transition-colors",
                active ? "bg-neural/[0.08] text-neural" : "text-slate-500 hover:bg-white/[0.04] hover:text-slate-300",
              ].join(" ")}
              aria-pressed={active}
            >
              {t.icon}
              {t.label}
            </button>
          );
        })}
      </div>

      {tab === "keys" && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-[11px] text-slate-400">Manage workspace API keys. Rotate often. Scope down to eval-only for CI.</p>
            <Button variant="primary" size="sm" onClick={() => toast.push({ title: "Generated new key", description: "Visible once — copy now.", variant: "success" })}>
              Generate key
            </Button>
          </div>
          <ul className="space-y-2">
            {KEYS.map((k) => (
              <li key={k.id} className="flex items-center gap-3 rounded-lg border border-white/[0.05] bg-white/[0.02] p-2.5">
                <span className="flex h-7 w-7 items-center justify-center rounded-md bg-white/[0.04] text-slate-400">
                  <IconKey size={12} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm text-slate-100">{k.name}</p>
                  <p className="font-mono text-[10px] text-slate-500">
                    {k.preview} · scope {k.scope} · created {k.created} · last used {k.lastUsed}
                  </p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => toast.push({ title: "Key copied", variant: "info" })}>
                  Copy
                </Button>
                <Button variant="danger" size="sm" onClick={() => toast.push({ title: "Key revoked", description: k.name, variant: "warning" })}>
                  Revoke
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === "model" && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Select
            label="Default model"
            value={model}
            onChange={setModel}
            options={[
              { value: "distilbert-base-uncased", label: "DistilBERT", hint: "67M" },
              { value: "bert-base-uncased", label: "BERT", hint: "110M" },
              { value: "roberta-base", label: "RoBERTa", hint: "125M" },
              { value: "gpt2", label: "GPT-2", hint: "124M" },
              { value: "distilgpt2", label: "DistilGPT-2", hint: "82M" },
            ]}
          />
          <Input label="Batch size" value={batch} onChange={(e) => setBatch(e.target.value)} type="number" />
          <Input label="Learning rate" value={lr} onChange={(e) => setLr(e.target.value)} hint="Wake/Dream phases" />
          <Input label="Random seed" value={seed} onChange={(e) => setSeed(e.target.value)} type="number" />
          <div className="sm:col-span-2 flex justify-end gap-2">
            <Button variant="ghost" size="sm">Reset</Button>
            <Button variant="primary" size="sm" onClick={() => toast.push({ title: "Settings saved", variant: "success" })}>
              Save defaults
            </Button>
          </div>
        </div>
      )}

      {tab === "distortion" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input label="Dream strength" value={dreamStrength} onChange={(e) => setDreamStrength(e.target.value)} hint="0.10 — 0.50" />
            <Input label="Nightmare strength" value={nightmareStrength} onChange={(e) => setNightmareStrength(e.target.value)} hint="0.50 — 1.00" />
          </div>
          <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
            <p className="mb-1.5 text-[10px] uppercase tracking-widest text-slate-500">Distortion mix</p>
            <ul className="space-y-1.5 text-[11px]">
              {[
                { label: "Character (typos · swaps · deletes)", weight: 35 },
                { label: "Word (synonyms · drops)", weight: 30 },
                { label: "Semantic (paraphrase)", weight: 20 },
                { label: "Adversarial (PGD · TextFooler)", weight: 15 },
              ].map((m) => (
                <li key={m.label} className="grid grid-cols-[1fr_120px_40px] items-center gap-3">
                  <span className="truncate text-slate-300">{m.label}</span>
                  <span className="h-1 w-full overflow-hidden rounded-full bg-white/[0.04]">
                    <span className="block h-full rounded-full bg-gradient-to-r from-dream to-neural" style={{ width: `${m.weight}%` }} />
                  </span>
                  <span className="text-right font-mono text-slate-300">{m.weight}%</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="flex justify-end">
            <Button variant="primary" size="sm" onClick={() => toast.push({ title: "Distortion mix saved", variant: "success" })}>
              Save mix
            </Button>
          </div>
        </div>
      )}
    </Panel>
  );
}
