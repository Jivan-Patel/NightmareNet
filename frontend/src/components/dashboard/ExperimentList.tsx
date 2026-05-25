"use client";

import { useMemo, useState } from "react";
import { Panel } from "./Panel";
import { Badge, type BadgeVariant } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { IconBeaker, IconDownload, IconFilter, IconPlus, IconSearch } from "./icons";

interface Experiment {
  id: string;
  name: string;
  model: string;
  status: "running" | "complete" | "failed" | "queued";
  cycles: number;
  robustness: number;
  duration: string;
  createdAt: string;
}

const SAMPLE: Experiment[] = [
  { id: "exp_4f0a", name: "wikitext-resilient-v3", model: "DistilBERT", status: "running", cycles: 4, robustness: 81.4, duration: "12m 04s", createdAt: "2m ago" },
  { id: "exp_3b91", name: "gpt2-domain-shift", model: "GPT-2", status: "running", cycles: 2, robustness: 67.2, duration: "07m 41s", createdAt: "9m ago" },
  { id: "exp_3a17", name: "roberta-attack-eval", model: "RoBERTa", status: "queued", cycles: 0, robustness: 0, duration: "—", createdAt: "12m ago" },
  { id: "exp_2e80", name: "distilgpt2-night-only", model: "DistilGPT-2", status: "complete", cycles: 5, robustness: 86.1, duration: "1h 04m", createdAt: "2h ago" },
  { id: "exp_2d3c", name: "bert-baseline", model: "BERT", status: "complete", cycles: 3, robustness: 74.6, duration: "32m 18s", createdAt: "6h ago" },
  { id: "exp_2c5b", name: "wiki-stress-typos", model: "DistilBERT", status: "failed", cycles: 1, robustness: 0, duration: "04m 12s", createdAt: "1d ago" },
  { id: "exp_2a12", name: "compress-ratio-2x", model: "GPT-2", status: "complete", cycles: 4, robustness: 79.8, duration: "48m 02s", createdAt: "2d ago" },
  { id: "exp_1f88", name: "char-pgd-eval", model: "RoBERTa", status: "complete", cycles: 2, robustness: 83.5, duration: "21m 56s", createdAt: "3d ago" },
];

const statusVariant: Record<Experiment["status"], BadgeVariant> = {
  running: "neural",
  complete: "success",
  failed: "nightmare",
  queued: "warning",
};

export function ExperimentList() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | Experiment["status"]>("all");

  const rows = useMemo(() => {
    return SAMPLE.filter((r) => {
      if (filter !== "all" && r.status !== filter) return false;
      if (!query.trim()) return true;
      const q = query.toLowerCase();
      return (
        r.name.toLowerCase().includes(q) ||
        r.id.toLowerCase().includes(q) ||
        r.model.toLowerCase().includes(q)
      );
    });
  }, [query, filter]);

  const columns: DataTableColumn<Experiment>[] = [
    {
      key: "name",
      header: "Experiment",
      accessor: (r) => r.name,
      sortable: true,
      cell: (r) => (
        <div className="min-w-0">
          <p className="truncate text-sm text-slate-100">{r.name}</p>
          <p className="font-mono text-[10px] text-slate-500">{r.id}</p>
        </div>
      ),
    },
    {
      key: "model",
      header: "Model",
      accessor: (r) => r.model,
      sortable: true,
      cell: (r) => <span className="text-xs text-slate-300">{r.model}</span>,
    },
    {
      key: "status",
      header: "Status",
      accessor: (r) => r.status,
      sortable: true,
      cell: (r) => (
        <Badge variant={statusVariant[r.status]} size="xs" dot>
          {r.status}
        </Badge>
      ),
    },
    {
      key: "cycles",
      header: "Cycles",
      accessor: (r) => r.cycles,
      sortable: true,
      align: "right",
      cell: (r) => <span className="font-mono text-xs">{r.cycles}</span>,
    },
    {
      key: "robustness",
      header: "Robustness",
      accessor: (r) => r.robustness,
      sortable: true,
      align: "right",
      cell: (r) =>
        r.robustness === 0 ? (
          <span className="text-slate-600">—</span>
        ) : (
          <span
            className={[
              "font-mono text-xs",
              r.robustness >= 80 ? "text-emerald-300" : r.robustness >= 70 ? "text-neural" : "text-amber-300",
            ].join(" ")}
          >
            {r.robustness.toFixed(1)}
          </span>
        ),
    },
    {
      key: "duration",
      header: "Duration",
      accessor: (r) => r.duration,
      sortable: true,
      align: "right",
      cell: (r) => <span className="font-mono text-[11px] text-slate-400">{r.duration}</span>,
    },
    {
      key: "createdAt",
      header: "Created",
      accessor: (r) => r.createdAt,
      align: "right",
      cell: (r) => <span className="text-[11px] text-slate-500">{r.createdAt}</span>,
    },
  ];

  return (
    <Panel
      title="Experiments"
      subtitle={`${rows.length} of ${SAMPLE.length} runs`}
      icon={<IconBeaker size={14} />}
      glow="dream"
      toolbar={
        <>
          <Input
            placeholder="Search…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            leftIcon={<IconSearch size={12} />}
            containerClassName="w-44"
            className="!py-1.5 !text-xs"
          />
          <Select
            size="sm"
            value={filter}
            onChange={(v) => setFilter(v as typeof filter)}
            className="w-32"
            options={[
              { value: "all", label: "All states" },
              { value: "running", label: "Running" },
              { value: "complete", label: "Complete" },
              { value: "failed", label: "Failed" },
              { value: "queued", label: "Queued" },
            ]}
          />
          <Button variant="ghost" size="sm" aria-label="Filter">
            <IconFilter size={12} />
          </Button>
          <Button variant="ghost" size="sm" aria-label="Export">
            <IconDownload size={12} />
          </Button>
          <Button variant="primary" size="sm">
            <IconPlus size={12} /> New Run
          </Button>
        </>
      }
      bodyClassName="px-0 py-0"
    >
      <DataTable
        columns={columns}
        rows={rows}
        rowKey={(r) => r.id}
        density="compact"
        initialSort={{ key: "createdAt", direction: "desc" }}
        empty={<span>No experiments match your filters.</span>}
      />
    </Panel>
  );
}
