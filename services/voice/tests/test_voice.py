"""Voice service tests — no faster-whisper or piper required."""

from __future__ import annotations

import io

from fastapi.testclient import TestClient
from voice.main import _synthesize_text, _transcribe_audio, app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "voice"


def test_transcribe_audio(monkeypatch):
    class Segment:
        text = " What is my portfolio AUM?"

    class Model:
        def transcribe(self, *_args, **_kwargs):
            return [Segment()], {}

    monkeypatch.setattr("voice.main._get_whisper_model", lambda: Model())
    result = _transcribe_audio(b"fake audio bytes")
    assert result == "What is my portfolio AUM?"


def test_synthesize_mock():
    # Without piper, falls back to a valid silent WAV.
    audio = _synthesize_text("Hello world")
    assert isinstance(audio, bytes)
    assert audio.startswith(b"RIFF")
    assert b"WAVE" in audio[:16]


def test_transcribe_endpoint(monkeypatch):
    monkeypatch.setattr("voice.main._transcribe_audio", lambda _audio: "Transcribed locally")
    fake_audio = io.BytesIO(b"RIFF" + b"\x00" * 40)
    r = client.post("/voice/transcribe", files={"audio": ("test.wav", fake_audio, "audio/wav")})
    assert r.status_code == 200
    data = r.json()
    assert data["transcript"] == "Transcribed locally"


def test_synthesize_endpoint():
    r = client.post("/voice/synthesize", data={"text": "Your AUM is 20 million dollars."})
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/wav"


def test_status_endpoint():
    r = client.get("/voice/status")
    assert r.status_code == 200
    assert r.json()["voice_to_voice"] is True
