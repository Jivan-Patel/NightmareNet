"""NightmareNet CLI — command-line interface for the OSS core.

Usage:
    nightmarenet train --config configs/default.yaml
    nightmarenet evaluate --checkpoint ./output/model --config configs/default.yaml
    nightmarenet benchmark --suite standard --model distilbert-base-uncased
    nightmarenet distort --type dream --strength 0.3 --text "Hello world"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def cmd_train(args: argparse.Namespace) -> int:
    """Run the full 4-phase training pipeline."""
    from nightmarenet.pipeline import Pipeline

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        return 1

    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    def on_event(event: dict) -> None:
        phase = event.get("status", "unknown")
        print(f"  [{phase}] {event.get('message', '')}")

    print("NightmareNet Training Pipeline")
    print(f"  Config: {config_path}")
    print(f"  Model: {config.get('model', {}).get('name', 'gpt2')}")
    print()

    pipeline = Pipeline(config=config, on_event=on_event)

    try:
        pipeline.run()
    except KeyboardInterrupt:
        print("\nTraining interrupted. Saving checkpoint...")
        return 130

    metrics = pipeline.metrics
    print("\nTraining complete!")
    print(f"  Final loss: {metrics.final_loss:.4f}")
    print(f"  Robustness score: {metrics.robustness_score:.4f}")

    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Output: {output_dir}")

    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    """Evaluate text robustness via distortion API logic."""
    from nightmarenet.distortions.registry import get_registry

    print("NightmareNet Evaluation")
    print(f"  Strengths: {args.strengths}")
    print()

    registry = get_registry()
    text = args.text or "The quick brown fox jumps over the lazy dog."
    strengths = [float(s) for s in args.strengths.split(",")]
    results = []
    for strength in strengths:
        dream_out = registry.apply("dream", text, strength=strength, seed=42)
        nightmare_out = registry.apply("nightmare", text, strength=strength, seed=42)
        results.append(
            {
                "strength": strength,
                "dream_sample": dream_out[:200],
                "nightmare_sample": nightmare_out[:200],
            }
        )

    print(json.dumps(results, indent=2))
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Run standard robustness benchmarks."""
    print(f"NightmareNet Benchmark Suite: {args.suite}")
    print(f"  Model: {args.model}")
    print("  This feature is under development.")
    return 0


def cmd_distort(args: argparse.Namespace) -> int:
    """Apply a distortion to input text."""
    from nightmarenet.distortions import dream, nightmare

    text = args.text
    strength = args.strength

    if args.type == "dream":
        result = dream.distort(text, strength=strength, seed=args.seed)
    elif args.type == "nightmare":
        result = nightmare.distort(text, strength=strength, seed=args.seed)
    else:
        print(f"Error: unknown distortion type: {args.type}", file=sys.stderr)
        return 1

    print(f"Original:  {text}")
    print(f"Distorted: {result}")
    print(f"  Type: {args.type}, Strength: {strength}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nightmarenet",
        description="NightmareNet — Autonomous AI Self-Improvement Platform",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # train
    train_parser = subparsers.add_parser("train", help="Run 4-phase training pipeline")
    train_parser.add_argument("--config", required=True, help="YAML config path")
    train_parser.add_argument("--output", help="Output directory for artifacts")
    train_parser.add_argument("--device", default="cpu", help="Device (cpu/cuda)")

    # evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate model robustness")
    eval_parser.add_argument("--model", required=True, help="Model name or path")
    eval_parser.add_argument("--text", help="Text to evaluate")
    eval_parser.add_argument(
        "--strengths", default="0.1,0.3,0.5,0.7,0.9", help="Comma-separated strengths"
    )

    # benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run robustness benchmarks")
    bench_parser.add_argument(
        "--suite", default="standard", choices=["standard", "adversarial", "full"]
    )
    bench_parser.add_argument("--model", default="distilbert-base-uncased")

    # distort
    distort_parser = subparsers.add_parser("distort", help="Apply distortion to text")
    distort_parser.add_argument("--type", required=True, choices=["dream", "nightmare"])
    distort_parser.add_argument("--strength", type=float, default=0.3)
    distort_parser.add_argument("--text", required=True)
    distort_parser.add_argument("--seed", type=int, default=None)

    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "train": cmd_train,
        "evaluate": cmd_evaluate,
        "benchmark": cmd_benchmark,
        "distort": cmd_distort,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
