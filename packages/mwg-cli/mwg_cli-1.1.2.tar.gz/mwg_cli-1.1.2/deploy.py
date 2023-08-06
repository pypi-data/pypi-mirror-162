from sys import argv
from subprocess import CalledProcessError, run

version = argv[1]

try:
    run(["python", "-m", "build"], check=True)
    run(["twine", "upload", f"dist/mwg_cli-{version}*"], check=True)
    run(
        [
            "gcloud",
            "builds",
            "submit",
            ".",
            f"--substitutions=_VERSION={version}",
            "--project=aaa-private-assets",
        ],
        check=True,
    )
except CalledProcessError as e:
    print(e)
