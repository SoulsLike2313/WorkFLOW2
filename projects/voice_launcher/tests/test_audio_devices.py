from voice_launcher_app.asr.audio_devices import AudioDeviceService


class FakePyAudio:
    def __init__(self):
        self._hosts = [
            {"name": "MME"},
            {"name": "Windows WASAPI"},
        ]
        self._devices = [
            {
                "name": "Microphone (fifine headset)",
                "hostApi": 1,
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
            },
            {
                "name": "Microphone (fifine headset)",
                "hostApi": 0,
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
            },
            {
                "name": "Speakers (Headphones)",
                "hostApi": 1,
                "maxInputChannels": 0,
                "maxOutputChannels": 2,
            },
        ]

    def get_host_api_count(self):
        return len(self._hosts)

    def get_host_api_info_by_index(self, idx):
        return dict(self._hosts[idx])

    def get_device_count(self):
        return len(self._devices)

    def get_device_info_by_index(self, idx):
        return dict(self._devices[idx])

    def terminate(self):
        return None


class FakePyAudioModule:
    def __init__(self):
        self.instances = 0

    def PyAudio(self):  # noqa: N802
        self.instances += 1
        return FakePyAudio()


def test_get_device_options_prefers_wasapi_and_caches():
    fake_module = FakePyAudioModule()
    service = AudioDeviceService(
        settings={},
        maybe_fix_mojibake=lambda s: s,
        pyaudio_mod=fake_module,
        cache_ttl=120.0,
    )

    inputs_first, outputs_first = service.get_device_options(force_refresh=True)
    inputs_second, outputs_second = service.get_device_options(force_refresh=False)

    assert fake_module.instances == 1
    assert inputs_first == inputs_second
    assert outputs_first == outputs_second
    assert inputs_first[0]["host"] == "Windows WASAPI"
    assert "fifine" in inputs_first[0]["name"].lower()
    assert "headphones" in outputs_first[0]["name"].lower()


def test_resolve_selected_index_by_id_name_and_fallback():
    options = [
        {"id": 7, "name": "Mic A", "raw": "Mic A"},
        {"id": 8, "name": "Mic B", "raw": "Mic B"},
    ]
    service = AudioDeviceService(
        settings={"microphone_id": 8},
        maybe_fix_mojibake=lambda s: s,
        pyaudio_mod=None,
    )
    assert service.resolve_selected_index(options, "microphone_id", "microphone_name") == 8

    service.settings = {"microphone_name": "Mic A"}
    assert service.resolve_selected_index(options, "microphone_id", "microphone_name") == 7

    service.settings = {}
    assert service.resolve_selected_index(options, "microphone_id", "microphone_name") == 7
