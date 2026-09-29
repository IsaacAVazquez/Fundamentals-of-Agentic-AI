import socket
import urllib.request

from personal_wiki import doctor


def test_internet_probe_handles_failures(monkeypatch):
    def refuse(*a, **k):
        raise OSError("Network is unreachable")
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.setattr(urllib.request, "urlopen", refuse)
    reachable, probes = doctor.internet_reachable(timeout=0.1)
    assert reachable is False and len(probes) == 4 and all("failed" in v for v in probes.values())


def test_run_doctor_report_and_offline_requirement(fake_settings, monkeypatch):
    monkeypatch.setattr(doctor, "internet_reachable", lambda timeout=3.0: (True, {"tcp 1.1.1.1:443": "connected"}))
    report = doctor.run_doctor(fake_settings, require_offline=True)
    assert report["exit_code"] == 11 and any(c["name"] == "offline" and not c["ok"] for c in report["checks"])
    monkeypatch.setattr(doctor, "internet_reachable", lambda timeout=3.0: (False, {}))
    report = doctor.run_doctor(fake_settings, require_offline=True)
    assert report["exit_code"] == 0 and report["ok"] and report["device"]["cores"]
    names = {c["name"] for c in report["checks"]}
    assert {"python", "vault", "research rules", "persona", "ollama", "offline", "device"} <= names
    path = doctor.save_report(fake_settings, report)
    path2 = doctor.save_report(fake_settings, report)
    assert path.name == "doctor.json" and path2.name == "doctor-2.json"
