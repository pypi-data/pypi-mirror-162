from subprocess import run, PIPE
from typing import Dict, Optional


def build(
    config: str, project: str, substitutions: Optional[Dict[str, str]] = None
) -> None:
    cmd = [
        "gcloud",
        "builds",
        "submit",
        ".",
        f"--config={config}",
        f"--project={project}",
    ]
    if substitutions:
        substitutions_value = ",".join([f"{k}={v}" for k, v in substitutions.items()])
        cmd.append(f"--substitutions={substitutions_value}")
    print(
        "Running build (https://console.cloud.google.com/cloud-build/builds?project=aaa-private-assets)..."
    )
    run(cmd, stdout=PIPE, stderr=PIPE)
