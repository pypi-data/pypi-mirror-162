import os
import json
from argparse import ArgumentParser, Namespace
from typing import Optional

from . import git, plans
from .plans import PlanNotFound
from .build import build
from .terraform import Terraform
from .exceptions import LoggedError
from .config import CONFIG

TF_DIR = "tf"


def main() -> None:
    try:
        git.ensure_repo()

        parser = ArgumentParser()

        subparsers = parser.add_subparsers(title="actions")

        deployment_parser = ArgumentParser(add_help=False)
        deployment_parser.add_argument(
            "workspace",
            help="The Terraform workspace to select before planning or applying. Usually dev, qa, or prod.",
        )

        parser_plan = subparsers.add_parser(
            "plan",
            parents=[deployment_parser],
            help="Create and upload an execution plan based on the current head commit",
        )
        parser_plan.add_argument(
            "--refresh-only",
            action="store_true",
            help="Only refresh state",
        )
        parser_plan.set_defaults(func=plan)

        parser_apply = subparsers.add_parser(
            "apply",
            parents=[deployment_parser],
            help="Apply the execution plan for the current head commit",
        )
        parser_apply.set_defaults(func=apply)

        args = parser.parse_args()

        if not hasattr(args, "func"):
            parser.print_help()
            return

        args.func(args)

    except LoggedError as e:
        print(e)


def plan(args: Namespace):
    git.ensure_clean_working_tree()

    tf = Terraform(TF_DIR)
    tf.select_workspace(args.workspace)

    commit = git.latest_commit()
    build_commit = commit

    if CONFIG.build:
        build_commit = git.latest_commit(CONFIG.build.included_files)
        if os.path.exists(CONFIG.build.config):
            build(
                config=CONFIG.build.config,
                project=CONFIG.build.project,
                substitutions={
                    "_APP_NAME": CONFIG.app.name,
                    "_BUILD_COMMIT": build_commit,
                },
            )
        else:
            raise LoggedError("Could not find build config file")

    tf.plan(
        out=commit,
        vars={"app_name": CONFIG.app.name, "build_commit": build_commit},
        refresh_only=args.refresh_only,
    )
    planfile = _planfile(commit)
    plans.upload(args.workspace, planfile)
    os.remove(planfile)


def apply(args: Namespace) -> None:
    git.unshallow()
    commit = git.latest_commit()
    planfile = _planfile(commit)
    plans.download(args.workspace, planfile)
    print("Could not find plan for head commit")
    tf = Terraform(TF_DIR)
    tf.select_workspace(args.workspace)
    tf.apply(os.path.basename(planfile))


def _planfile(sha: str) -> str:
    return os.path.join(TF_DIR, sha)
