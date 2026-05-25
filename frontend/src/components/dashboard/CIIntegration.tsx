"use client";

import { useMemo, useState } from "react";
import { Panel } from "./Panel";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Progress } from "@/components/ui/Progress";
import { useToast } from "@/components/ui/Toast";
import { IconCheck, IconDownload, IconGit } from "./icons";

const STEPS = [
  { key: "repo", label: "Connect repo" },
  { key: "secret", label: "Add API key secret" },
  { key: "yaml", label: "Drop CI workflow" },
  { key: "verify", label: "Verify on push" },
] as const;

type StepKey = (typeof STEPS)[number]["key"];

export function CIIntegration() {
  const [step, setStep] = useState<StepKey>("repo");
  const [repo, setRepo] = useState("nightmarenet/example-app");
  const [branch, setBranch] = useState("main");
  const [threshold, setThreshold] = useState("0.75");
  const [provider, setProvider] = useState("github");
  const toast = useToast();

  const stepIdx = STEPS.findIndex((s) => s.key === step);
  const progress = ((stepIdx + 1) / STEPS.length) * 100;

  const yaml = useMemo(
    () => `name: NightmareNet Robustness
on:
  push:
    branches: [${branch}]
  pull_request:

jobs:
  robustness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install nightmarenet
      - name: Run benchmark
        env:
          NIGHTMARENET_API_KEY: \${{ secrets.NIGHTMARENET_API_KEY }}
        run: |
          nightmarenet eval \\
            --model ./model \\
            --threshold ${threshold} \\
            --report robustness.md
      - uses: actions/upload-artifact@v4
        with:
          name: robustness-report
          path: robustness.md`,
    [branch, threshold]
  );

  const badgeMd = `![NightmareNet](https://nightmarenet.dev/api/badge/${repo.replace("/", "-")}.svg)`;

  return (
    <Panel
      title="CI Integration"
      subtitle="GitHub Action setup wizard"
      icon={<IconGit size={14} />}
      glow="neural"
      toolbar={<Badge variant="success" size="xs" dot>connected · staging</Badge>}
    >
      <div className="mb-4">
        <Progress value={progress} tone="neural" size="sm" />
        <ol className="mt-2 grid grid-cols-4 gap-1 text-[10px]">
          {STEPS.map((s, i) => {
            const active = s.key === step;
            const done = i < stepIdx;
            return (
              <li key={s.key} className="text-center">
                <button
                  type="button"
                  onClick={() => setStep(s.key)}
                  className={[
                    "w-full rounded-md border px-1 py-1 cursor-pointer",
                    active
                      ? "border-neural/40 bg-neural/[0.08] text-neural"
                      : done
                        ? "border-emerald-500/30 bg-emerald-500/[0.05] text-emerald-300"
                        : "border-white/[0.05] bg-white/[0.02] text-slate-500",
                  ].join(" ")}
                >
                  {s.label}
                </button>
              </li>
            );
          })}
        </ol>
      </div>

      {step === "repo" && (
        <div className="space-y-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Select
              size="sm"
              label="Provider"
              value={provider}
              onChange={setProvider}
              options={[
                { value: "github", label: "GitHub Actions" },
                { value: "gitlab", label: "GitLab CI", hint: "Beta" },
                { value: "bitbucket", label: "Bitbucket Pipelines", hint: "Beta" },
              ]}
            />
            <Input label="Repository" value={repo} onChange={(e) => setRepo(e.target.value)} placeholder="owner/repo" />
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input label="Default branch" value={branch} onChange={(e) => setBranch(e.target.value)} />
            <Input label="Robustness threshold" value={threshold} onChange={(e) => setThreshold(e.target.value)} hint="0.0 — 1.0" />
          </div>
        </div>
      )}

      {step === "secret" && (
        <div className="space-y-3">
          <p className="text-[12px] text-slate-400">Add your NightmareNet API key as a repository secret named <span className="font-mono text-slate-200">NIGHTMARENET_API_KEY</span>.</p>
          <div className="rounded-lg border border-white/[0.06] bg-black/40 p-3 font-mono text-[11px] text-slate-300">
            <span className="text-slate-500"># In Settings → Secrets → Actions</span>
            <br />
            gh secret set NIGHTMARENET_API_KEY --body &quot;rk_*****&quot;
          </div>
          <Button variant="ghost" size="sm" onClick={() => { toast.push({ title: "Copied", variant: "success" }); }}>
            <IconCheck size={12} /> Copy command
          </Button>
        </div>
      )}

      {step === "yaml" && (
        <div className="space-y-3">
          <p className="text-[12px] text-slate-400">Save this workflow to <span className="font-mono">.github/workflows/nightmarenet.yml</span>.</p>
          <pre className="max-h-64 overflow-auto rounded-lg border border-white/[0.06] bg-black/40 p-3 font-mono text-[10.5px] leading-relaxed text-slate-300">
            <code>{yaml}</code>
          </pre>
          <div className="flex items-center gap-2">
            <Button variant="primary" size="sm">
              <IconDownload size={12} /> Download YAML
            </Button>
            <Button variant="ghost" size="sm" onClick={() => toast.push({ title: "YAML copied", variant: "success" })}>
              Copy
            </Button>
          </div>
        </div>
      )}

      {step === "verify" && (
        <div className="space-y-3">
          <div className="flex items-start gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/[0.04] p-3">
            <span className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-md bg-emerald-500/[0.15] text-emerald-300">
              <IconCheck size={12} />
            </span>
            <div>
              <p className="text-xs font-semibold text-emerald-300">Pipeline detected</p>
              <p className="text-[11px] text-slate-400">Latest run on <span className="font-mono">main</span> · 12m ago · robustness 0.81 ≥ {threshold} threshold</p>
            </div>
          </div>
          <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
            <p className="mb-1.5 text-[10px] uppercase tracking-widest text-slate-500">README badge</p>
            <pre className="overflow-x-auto font-mono text-[11px] text-slate-300">
              <code>{badgeMd}</code>
            </pre>
            <div className="mt-2 inline-flex items-center gap-1 rounded-md border border-white/[0.08] bg-black/40 px-2 py-1 text-[10px]">
              <span className="rounded-l bg-slate-800 px-1.5 py-0.5 text-slate-300">nightmarenet</span>
              <span className="rounded-r bg-emerald-500/20 px-1.5 py-0.5 text-emerald-300">0.81 passing</span>
            </div>
          </div>
        </div>
      )}

      <div className="mt-4 flex justify-between border-t border-white/[0.05] pt-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setStep(STEPS[Math.max(0, stepIdx - 1)].key)}
          disabled={stepIdx === 0}
        >
          Back
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={() => setStep(STEPS[Math.min(STEPS.length - 1, stepIdx + 1)].key)}
          disabled={stepIdx === STEPS.length - 1}
        >
          Next step
        </Button>
      </div>
    </Panel>
  );
}
