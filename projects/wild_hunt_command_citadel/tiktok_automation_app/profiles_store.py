from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class StoredProfile:
    name: str
    payload: Dict[str, Any]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "payload": self.payload,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "StoredProfile":
        now = datetime.utcnow().isoformat() + "Z"
        return cls(
            name=str(raw.get("name", "")).strip(),
            payload=dict(raw.get("payload", {})),
            created_at=str(raw.get("created_at", now)),
            updated_at=str(raw.get("updated_at", now)),
        )


class ProfileStore:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = Path(storage_path)
        self._profiles: Dict[str, StoredProfile] = {}
        self.load()

    def load(self) -> None:
        self._profiles = {}
        if not self.storage_path.exists():
            return

        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except Exception:
            return

        items: List[Dict[str, Any]] = []
        if isinstance(raw, dict):
            if isinstance(raw.get("profiles"), list):
                items = [item for item in raw["profiles"] if isinstance(item, dict)]
            elif isinstance(raw.get("profiles"), dict):
                for name, payload in raw["profiles"].items():
                    items.append({"name": name, "payload": payload})
        elif isinstance(raw, list):
            items = [item for item in raw if isinstance(item, dict)]

        for item in items:
            profile = StoredProfile.from_dict(item)
            if profile.name:
                self._profiles[profile.name] = profile

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "profiles": [profile.to_dict() for profile in self._sorted_profiles()],
        }
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def names(self) -> List[str]:
        return [profile.name for profile in self._sorted_profiles()]

    def all(self) -> List[StoredProfile]:
        return self._sorted_profiles()

    def get(self, name: str) -> Optional[StoredProfile]:
        return self._profiles.get(name)

    def upsert(self, name: str, payload: Dict[str, Any]) -> StoredProfile:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Имя профиля не может быть пустым.")

        now = datetime.utcnow().isoformat() + "Z"
        existing = self._profiles.get(clean_name)
        if existing:
            existing.payload = dict(payload)
            existing.updated_at = now
            profile = existing
        else:
            profile = StoredProfile(
                name=clean_name,
                payload=dict(payload),
                created_at=now,
                updated_at=now,
            )
            self._profiles[clean_name] = profile

        self.save()
        return profile

    def delete(self, name: str) -> bool:
        if name not in self._profiles:
            return False
        del self._profiles[name]
        self.save()
        return True

    def _sorted_profiles(self) -> List[StoredProfile]:
        return sorted(
            self._profiles.values(),
            key=lambda profile: (profile.updated_at, profile.name.lower()),
            reverse=True,
        )
