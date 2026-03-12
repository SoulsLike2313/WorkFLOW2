from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

CDP_KEYS = (
    "cdp",
    "cdp_url",
    "debugger_address",
    "debuggerAddress",
    "remote_debugging_url",
    "remote_debugging_address",
    "webSocketDebuggerUrl",
    "wsEndpoint",
    "ws_endpoint",
)


def _normalize_candidate(value: str) -> Optional[str]:
    text = value.strip().strip('"').strip("'")
    if not text:
        return None

    if text.startswith("ws://") or text.startswith("wss://"):
        return text
    if text.startswith("http://") or text.startswith("https://"):
        return text

    localhost_match = re.match(r"^(127\.0\.0\.1|localhost):(\d{2,5})$", text)
    if localhost_match:
        return f"http://{text}"

    return None


def _deep_find_cdp(data: Any) -> Optional[str]:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in CDP_KEYS and isinstance(value, str):
                normalized = _normalize_candidate(value)
                if normalized:
                    return normalized
            nested = _deep_find_cdp(value)
            if nested:
                return nested
    elif isinstance(data, list):
        for item in data:
            nested = _deep_find_cdp(item)
            if nested:
                return nested
    elif isinstance(data, str):
        normalized = _normalize_candidate(data)
        if normalized:
            return normalized
    return None


def extract_cdp_from_text(raw: str) -> Optional[str]:
    normalized = _normalize_candidate(raw)
    if normalized:
        return normalized

    candidates = re.findall(r"(?:ws|wss|http|https)://[^\s\"'<>]+", raw)
    for candidate in candidates:
        value = _normalize_candidate(candidate)
        if value:
            return value

    localhost = re.findall(r"(?:127\.0\.0\.1|localhost):\d{2,5}", raw)
    for candidate in localhost:
        value = _normalize_candidate(candidate)
        if value:
            return value
    return None


def extract_profile_url_from_data(data: Any) -> Optional[str]:
    if isinstance(data, dict):
        for key in ("profile_url", "url", "profileUrl", "homepage"):
            candidate = data.get(key)
            if isinstance(candidate, str):
                if "tiktok.com" in candidate:
                    return candidate.strip()
        for value in data.values():
            found = extract_profile_url_from_data(value)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = extract_profile_url_from_data(item)
            if found:
                return found
    elif isinstance(data, str) and "tiktok.com" in data:
        return data.strip()
    return None


def parse_profile_file(path: Path) -> tuple[Optional[str], Optional[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cdp_url = _deep_find_cdp(payload)
    profile_url = extract_profile_url_from_data(payload)
    return cdp_url, profile_url


def parse_profile_payload(text: str, file_path: Optional[str] = None) -> tuple[Optional[str], Optional[str]]:
    cdp_url = extract_cdp_from_text(text)
    profile_url: Optional[str] = None

    if not cdp_url:
        try:
            payload = json.loads(text)
            cdp_url = _deep_find_cdp(payload)
            profile_url = extract_profile_url_from_data(payload)
        except json.JSONDecodeError:
            pass

    if file_path:
        path = Path(file_path)
        if path.exists() and path.suffix.lower() == ".json":
            try:
                cdp_from_file, profile_from_file = parse_profile_file(path)
                cdp_url = cdp_url or cdp_from_file
                profile_url = profile_url or profile_from_file
            except Exception:
                pass

    if profile_url:
        parsed = urlparse(profile_url)
        if not parsed.scheme:
            profile_url = f"https://{profile_url.lstrip('/')}"
    return cdp_url, profile_url
