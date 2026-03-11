from __future__ import annotations

import csv
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Set


def default_normalize_phrase(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


@dataclass
class LaunchDecision:
    can_launch: bool
    reason: str
    payload: Any


@dataclass
class ProcessScanner:
    runner: Callable[..., Any]
    logger: Optional[Callable[[str], None]] = None
    platform_name: str = os.name
    now: Callable[[], float] = time.time
    cache_ttl: float = 1.2
    cache: Dict[str, Any] = field(default_factory=lambda: {"ts": 0.0, "names": set(), "ready": False})

    def get_running_process_names(self, force_refresh: bool = False) -> Set[str]:
        if self.platform_name != "nt":
            return set()

        now = self.now()
        cached_ts = float(self.cache.get("ts", 0.0))
        cached_names = self.cache.get("names", set())
        cache_ready = bool(self.cache.get("ready", False))
        if (
            not force_refresh
            and cache_ready
            and isinstance(cached_names, set)
            and now - cached_ts <= float(self.cache_ttl)
        ):
            return set(cached_names)

        names: Set[str] = set()
        try:
            result = self.runner(["tasklist", "/FO", "CSV", "/NH"])
            return_code = int(getattr(result, "returncode", 1))
            stdout = str(getattr(result, "stdout", "") or "")
            if return_code == 0 and stdout:
                for row in csv.reader(stdout.splitlines()):
                    if not row:
                        continue
                    name = os.path.basename(str(row[0]).strip().strip('"')).lower()
                    if name and name != "image name":
                        names.add(name)
        except Exception as exc:
            if self.logger:
                try:
                    self.logger(f"Process list error: {exc}")
                except Exception:
                    pass

        self.cache = {"ts": now, "names": names, "ready": True}
        return set(names)


def get_entry_process_names(
    entry: Dict[str, Any],
    normalize_phrase: Callable[[str], str] = default_normalize_phrase,
) -> List[str]:
    path = str(entry.get("path", "") or "").strip()
    if not path:
        return []

    base = os.path.basename(path).strip().lower()
    stem, ext = os.path.splitext(base)
    names: List[str] = []

    if ext == ".exe" and base:
        names.append(base)
    elif ext in (".lnk", ".url") and stem:
        names.append(f"{stem}.exe")

    if base in ("launcher.exe", "start.exe", "updater.exe"):
        folder = normalize_phrase(os.path.basename(os.path.dirname(path or ""))).replace(" ", "")
        if folder:
            names.append(f"{folder}.exe")

    uniq: List[str] = []
    for item in names:
        if item and item not in uniq:
            uniq.append(item)
    return uniq


def find_running_process_for_entry(
    entry: Dict[str, Any],
    running_names: Iterable[str],
    normalize_phrase: Callable[[str], str] = default_normalize_phrase,
) -> str:
    target_proc_names = get_entry_process_names(entry, normalize_phrase=normalize_phrase)
    if not target_proc_names:
        return ""
    running_set = set(running_names)
    for pname in target_proc_names:
        if pname in running_set:
            return pname
    return ""


def command_launch_key(entry: Dict[str, Any]) -> str:
    mode = str(entry.get("mode", "normal") or "normal").strip().lower()
    path = str(entry.get("path", "") or "").strip().lower()
    return f"{mode}|{path}"


@dataclass
class LaunchGate:
    gate: Dict[str, float] = field(default_factory=dict)
    now: Callable[[], float] = time.time

    def can_launch_entry(
        self,
        entry: Dict[str, Any],
        find_running_process: Callable[[Dict[str, Any]], str],
    ) -> LaunchDecision:
        key = command_launch_key(entry)
        now = self.now()
        cooldown_until = float(self.gate.get(key, 0.0))
        if now < cooldown_until:
            return LaunchDecision(False, "cooldown", max(0.0, cooldown_until - now))

        try:
            debounce_seconds = float(entry.get("debounce_seconds", 2.8))
        except Exception:
            debounce_seconds = 2.8
        mode = str(entry.get("mode", "normal") or "normal").strip().lower()
        if mode == "launcher_play":
            debounce_seconds = max(debounce_seconds, 12.0)
        debounce_seconds = max(0.8, min(30.0, debounce_seconds))

        single_instance_raw = entry.get("single_instance", True)
        if isinstance(single_instance_raw, str):
            single_instance = single_instance_raw.strip().lower() in ("1", "true", "yes", "on")
        else:
            single_instance = bool(single_instance_raw)

        if single_instance:
            running_proc = find_running_process(entry)
            if running_proc:
                self.gate[key] = now + 1.2
                return LaunchDecision(False, "already_running", running_proc)

        self.gate[key] = now + debounce_seconds
        return LaunchDecision(True, "ok", debounce_seconds)
