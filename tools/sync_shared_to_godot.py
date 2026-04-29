from __future__ import annotations

import shutil
from pathlib import Path


def sync_shared_to_godot() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    shared_dir = repo_root / "shared_data"
    godot_data_dir = repo_root / "game3d" / "data"

    shared_dir.mkdir(parents=True, exist_ok=True)
    godot_data_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[Path] = []
    for source_path in sorted(shared_dir.glob("*.json")):
        target_path = godot_data_dir / source_path.name
        shutil.copy2(source_path, target_path)
        copied_files.append(target_path)

    return copied_files


def main() -> None:
    copied_files = sync_shared_to_godot()
    if not copied_files:
        print("No JSON files found in shared_data/. Nothing to sync.")
        return

    print("Synced JSON files to game3d/data:")
    for path in copied_files:
        print(f"- {path}")


if __name__ == "__main__":
    main()
