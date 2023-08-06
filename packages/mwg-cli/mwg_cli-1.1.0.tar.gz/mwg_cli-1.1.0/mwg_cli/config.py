from dataclasses import dataclass, field
import json
from typing import List, Optional


@dataclass
class AppSettings:
    name: str


@dataclass
class BuildSettings:
    project: str = "aaa-private-assets"
    config: str = "cloudbuild.yaml"
    included_files: List[str] = field(default_factory=lambda: ["**/*"])


@dataclass
class Config:
    app: AppSettings
    build: Optional[BuildSettings]


with open("mwg.json", "r") as f:
    raw = json.load(f)

CONFIG = Config(app=AppSettings(**raw["app"]), build=BuildSettings(**raw.get("build")))
