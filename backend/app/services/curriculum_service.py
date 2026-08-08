import json
from pathlib import Path


class CurriculumService:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[3]
        self.data_path = project_root / "data" / "curriculum.json"

        with open(self.data_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def get_all_days(self) -> list[dict]:
        return self.data["days"]

    def get_day(self, day_number: int) -> dict | None:
        for day in self.data["days"]:
            if day["day"] == day_number:
                return day

        return None

    def get_modules(self) -> list[dict]:
        return self.data["modules"]