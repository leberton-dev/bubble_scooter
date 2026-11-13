import json
import os
from pathlib import Path
from typing import cast


class SaveFile:
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    @staticmethod
    def data_dir() -> Path:
        base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
        return Path(base) / "bubble_scooter"

    def load(self) -> int:
        try:
            data = cast(object, json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            return 0
        if not isinstance(data, dict):
            return 0
        score = cast(dict[str, object], data).get("best_score")
        if not isinstance(score, int) or isinstance(score, bool):
            return 0
        return score

    def save(self, score: int) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps({"best_score": score}), encoding="utf-8")
        os.replace(tmp, self.path)
