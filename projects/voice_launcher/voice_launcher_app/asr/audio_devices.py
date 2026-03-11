from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Sequence, Tuple


def _normalize_spaces(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


@dataclass
class AudioDeviceService:
    settings: Dict[str, Any]
    maybe_fix_mojibake: Callable[[str], str]
    pyaudio_mod: Any = None
    cache_ttl: float = 2.5
    cache: Dict[str, Any] = field(default_factory=lambda: {"ts": 0.0, "inputs": [], "outputs": []})

    def clean_device_name(self, name: str) -> str:
        fixed = self.maybe_fix_mojibake(name)
        return _normalize_spaces(fixed)

    @staticmethod
    def host_priority(host_name: str) -> int:
        lower = str(host_name or "").lower()
        if "wasapi" in lower:
            return 3
        if "mme" in lower:
            return 2
        if "wdm" in lower:
            return 1
        return 0

    def dedupe_options(self, options: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chosen: Dict[str, Dict[str, Any]] = {}
        for opt in options:
            key = str(opt.get("name", "")).lower()
            current = chosen.get(key)
            if current is None or int(opt.get("host_score", 0)) > int(current.get("host_score", 0)):
                chosen[key] = dict(opt)
        return list(chosen.values())

    @staticmethod
    def filter_headset_first(options: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        keywords = ("head", "headset", "headphone", "науш", "гарнит")
        targeted = [opt for opt in options if any(k in str(opt.get("name", "")).lower() for k in keywords)]
        return targeted if targeted else list(options)

    def device_score(self, option: Dict[str, Any], kind: str = "input", preferred_output_name: str = "") -> int:
        name = str(option.get("name", "")).lower()
        score = int(option.get("host_score", 0)) * 20

        if "fifine" in name:
            score += 120

        if kind == "input":
            if "микрофон" in name or "microphone" in name:
                score += 28
        else:
            if "динам" in name or "speaker" in name or "head" in name:
                score += 18

        if preferred_output_name:
            low_pref = preferred_output_name.lower()
            if "fifine" in low_pref and "fifine" in name:
                score += 40

        bad_keywords = (
            "dualsense",
            "controller",
            "xbox",
            "sound mapper",
            "первичный",
            "primary",
        )
        for bad in bad_keywords:
            if bad in name:
                score -= 120

        if kind == "output":
            for bad_out in ("lg ips", "hdmi", "display audio"):
                if bad_out in name:
                    score -= 70
        return score

    def sort_device_options(
        self,
        options: Sequence[Dict[str, Any]],
        kind: str = "input",
        preferred_output_name: str = "",
    ) -> List[Dict[str, Any]]:
        return sorted(
            [dict(o) for o in options],
            key=lambda opt: (
                -self.device_score(opt, kind=kind, preferred_output_name=preferred_output_name),
                int(opt.get("id", 0)),
            ),
        )

    def get_device_options(self, force_refresh: bool = False) -> Tuple[List[dict], List[dict]]:
        now = time.time()
        cached_inputs = self.cache.get("inputs", [])
        cached_outputs = self.cache.get("outputs", [])
        cache_age = now - float(self.cache.get("ts", 0.0))
        if (
            not force_refresh
            and cache_age <= float(self.cache_ttl)
            and isinstance(cached_inputs, list)
            and isinstance(cached_outputs, list)
        ):
            return list(cached_inputs), list(cached_outputs)

        if self.pyaudio_mod is None:
            return [], []

        try:
            pa = self.pyaudio_mod.PyAudio()
        except Exception:
            return [], []

        inputs: List[dict] = []
        outputs: List[dict] = []

        try:
            host_names: Dict[int, str] = {}
            for host_idx in range(pa.get_host_api_count()):
                info = pa.get_host_api_info_by_index(host_idx)
                host_names[host_idx] = str(info.get("name", ""))

            for idx in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(idx)
                name = self.clean_device_name(str(info.get("name", f"Device {idx}")))
                host_name = host_names.get(int(info.get("hostApi", -1)), "")
                host_score = self.host_priority(host_name)

                if int(info.get("maxInputChannels", 0)) > 0:
                    inputs.append(
                        {
                            "id": idx,
                            "raw": str(info.get("name", "")),
                            "name": name,
                            "host": host_name,
                            "host_score": host_score,
                            "label": f"[{idx}] {name}",
                        }
                    )
                if int(info.get("maxOutputChannels", 0)) > 0:
                    outputs.append(
                        {
                            "id": idx,
                            "raw": str(info.get("name", "")),
                            "name": name,
                            "host": host_name,
                            "host_score": host_score,
                            "label": f"[{idx}] {name}",
                        }
                    )
        finally:
            pa.terminate()

        inputs = self.sort_device_options(
            self.filter_headset_first(self.dedupe_options(inputs)),
            kind="input",
        )
        outputs = self.sort_device_options(
            self.filter_headset_first(self.dedupe_options(outputs)),
            kind="output",
        )
        self.cache = {"ts": now, "inputs": list(inputs), "outputs": list(outputs)}
        return inputs, outputs

    def resolve_selected_index(self, options: Sequence[Dict[str, Any]], id_key: str, name_key: str):
        if not options:
            return None

        selected_id = int(self.settings.get(id_key, -1))
        if selected_id >= 0 and any(int(opt.get("id", -1)) == selected_id for opt in options):
            return selected_id

        selected_name = self.settings.get(name_key, "")
        if selected_name:
            for opt in options:
                if opt.get("raw") == selected_name or opt.get("name") == selected_name:
                    return int(opt.get("id", -1))

        return int(options[0].get("id", -1))

    def get_selected_mic_index(self):
        selected_id = int(self.settings.get("microphone_id", -1))
        if selected_id >= 0:
            return selected_id
        input_options, _ = self.get_device_options()
        return self.resolve_selected_index(input_options, "microphone_id", "microphone_name")

    def get_selected_output_index(self):
        selected_id = int(self.settings.get("output_id", -1))
        if selected_id >= 0:
            return selected_id
        _, output_options = self.get_device_options()
        return self.resolve_selected_index(output_options, "output_id", "output_name")
