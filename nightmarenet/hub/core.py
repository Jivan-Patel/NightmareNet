import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from nightmarenet.hub.utils import require_hf_hub


def _generate_model_card(repo_id: str, metadata: Dict[str, Any]) -> str:
    """
    Auto-generates an academic/robustness HuggingFace Model Card (README.md)
    complete with standardized frontmatter metadata tags.
    """
    frontmatter = {
        "tags": ["nightmarenet", "robustness", "adversarial-defense"],
        "library_name": "transformers",
        "pipeline_tag": "text-classification",
        "metrics": ["robustness_score"],
        "model-index": [{
            "name": repo_id.split("/")[-1],
            "results": [{
                "task": {"type": "text-classification"},
                "dataset": {"name": "robustness-evaluation", "type": "evaluation"},
                "metrics": [
                    {
                        "type": "robustness_score",
                        "value": metadata.get("robustness_score", 0.0),
                        "name": "Robustness Score"
                    }
                ]
            }]
        }]
    }

    for key in ["cycle_count", "final_robustness_score", "distortion_families"]:
        if key in metadata:
            frontmatter[f"nightmarenet_{key}"] = metadata[key]

    yaml_block = yaml.safe_dump(frontmatter, sort_keys=False)

    return f"""---
{yaml_block}---

# NightmareNet Hardened Model: `{repo_id}`

This model has been robustified using the NightmareNet framework.

## Model Training & Resilience Profile
## Model Training & Resilience Profile
* **Robustness Score:** {metadata.get('robustness_score', 'N/A')}
* **Cycle Details:** Loop execution phase successfully completed.
* **Distortion Vectors Defended:** {", ".join(metadata.get('distortion_families', ['None']))}
## Reproducibility Metadata Configuration
```yaml
{yaml.safe_dump(metadata.get('config', {}), default_flow_style=False)}
``` """

@require_hf_hub
def push_model(model_dir: str, repo_id: str, metadata_path: Optional[str] = None) -> None:
    """Uploads a local model directory to the HuggingFace Hub."""
    from huggingface_hub import HfApi

    src_path = Path(model_dir)
    if not src_path.exists() or not src_path.is_dir():
        msg = f"Local model artifact directory context not found: {model_dir}"
        raise FileNotFoundError(msg)

    token = os.getenv("HF_TOKEN")
    api = HfApi(token=token)

    metadata: Dict[str, Any] = {}
    if metadata_path:
        metadata_file = Path(metadata_path)
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        with open(metadata_path, encoding='utf-8') as f:
            metadata = yaml.safe_load(f) or {}

    card_content = _generate_model_card(repo_id, metadata)
    card_path = src_path / "README.md"
    with open(card_path, 'w', encoding='utf-8') as f:
        f.write(card_content)

    print(f"Syncing directory artifacts path from '{model_dir}' to remote hub: '{repo_id}'...")
    api.create_repo(repo_id=repo_id, exist_ok=True, repo_type="model")
    api.upload_folder(
        folder_path=str(src_path),
        repo_id=repo_id,
        repo_type="model"
    )
    print("✓ Model repository package successfully synchronized with HuggingFace Hub.")

@require_hf_hub
def pull_model(repo_id: str, target_dir: str) -> None:
    """
    Downloads structural weights artifacts from public/private HuggingFace repositories natively.
    """
    from huggingface_hub import snapshot_download

    dest_path = Path(target_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    print(f"Downloading remote dataset weights snapshot from location: '{repo_id}'...")
    token = os.getenv("HF_TOKEN")
    snapshot_download(
        repo_id=repo_id,
        local_dir=str(dest_path),
        token=token
    )
    print(f"✓ Model configuration successfully localized onto target directory: {target_dir}")
