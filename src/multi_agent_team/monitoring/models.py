from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Agent:
    id: str
    role: str | None = None
    team: str | None = None
    mission: str | None = None
    status: str = "idle"
    last_seen: str | None = None

    def dict(self):
        return asdict(self)


