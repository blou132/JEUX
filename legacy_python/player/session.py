from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerRunConfig:
    # Minimal controls for the text-based MVP run.
    steps: int = 400
    dt: float = 1.0
    log_interval: int = 20
