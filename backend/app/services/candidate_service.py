import json
from pathlib import Path

from app.models.candidate import Candidate


class CandidateService:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[3]
        self.data_path = project_root / "data" / "candidates.json"

        with open(self.data_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.candidates = {
            candidate["member"]["id"]: Candidate(**candidate)
            for candidate in data["candidates"]
        }

    def get_candidate(self, candidate_id: str) -> Candidate | None:
        return self.candidates.get(candidate_id)

    def get_all_candidates(self) -> list[Candidate]:
        return list(self.candidates.values())