import os
import json
import subprocess
from typing import Any, Dict, List, Optional
from .exceptions import LoggedError


class TerraformError(LoggedError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Terraform:
    def __init__(self, directory: str) -> None:
        if directory and not os.path.exists(directory):
            raise TerraformError(
                f"Can't find directory '{directory}'. Are you at the root of the project?"
            )
        env = os.environ.copy()
        env["TF_IN_AUTOMATION"] = "true"
        self.env = env
        self.dir = directory
        self.exe = "terraform"
        self._run("init")

    def select_workspace(self, workspace: str) -> None:
        self._run("workspace", "select", workspace)
        self.workspace = workspace

    def plan(
        self,
        out: str,
        vars: Optional[Dict[str, Any]] = None,
        refresh_only: bool = False,
    ) -> None:
        subcmd = [
            "plan",
            f"-out={out}",
        ]
        var_file = f"config.{self.workspace}.tfvars"
        if os.path.exists(os.path.join(self.dir, var_file)):
            subcmd.append(f"-var-file={var_file}")
        if vars:
            subcmd.extend([f"-var={k}={v}" for k, v in vars.items()])
        if refresh_only:
            subcmd.append("-refresh-only")
        self._run(*subcmd)

    def apply(self, planfile: str) -> None:
        self._run("apply", planfile)

    def outputs(self) -> Any:
        cmd = [self.exe, "output", "-json"]
        result = subprocess.run(cmd, cwd=self.dir, env=self.env, stdout=subprocess.PIPE)
        return json.loads(result.stdout)

    def _run(self, *subcmd: str) -> None:
        try:
            cmd = [self.exe] + list(subcmd)
            subprocess.run(cmd, cwd=self.dir, env=self.env, check=True)
        except subprocess.CalledProcessError:
            raise TerraformError(
                "An error occured in terraform. Please see above error message."
            )
