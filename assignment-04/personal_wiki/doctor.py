"""Setup checks, network probes, and device information for the run manifest."""
from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

from . import __version__
from .chunking import collect_vault_files
from .config import PACKAGE_ROOT, Settings, utc_now_iso
from .evidence import read_json, write_json
from .index import load_index, vault_fingerprint


def _run(cmd: list, timeout: float = 10) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def internet_reachable(timeout: float = 3.0) -> tuple:
    """True when any TCP or HTTP probe reaches the internet. DNS is recorded but not counted (caches lie)."""
    probes: dict = {}
    for host, port in (("1.1.1.1", 443), ("8.8.8.8", 53)):
        try:
            socket.create_connection((host, port), timeout=timeout).close()
            probes[f"tcp {host}:{port}"] = "connected"
        except OSError as e:
            probes[f"tcp {host}:{port}"] = f"failed ({e.__class__.__name__}: {e})"
    try:
        socket.getaddrinfo("pypi.org", 443)
        probes["dns pypi.org"] = "resolved (not counted; caches can answer offline)"
    except OSError as e:
        probes["dns pypi.org"] = f"failed ({e})"
    try:
        req = urllib.request.Request("https://example.com", method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            probes["https example.com"] = f"HTTP {resp.status}"
    except Exception as e:  # any failure means this probe did not reach the internet
        probes["https example.com"] = f"failed ({e.__class__.__name__})"
    reachable = any(v == "connected" or v.startswith("HTTP") for v in probes.values())
    return reachable, probes


def device_info(vault: Path | None = None) -> dict:
    info: dict = {"system": platform.system(), "release": platform.release(), "machine": platform.machine(),
                  "python": sys.version.split()[0], "hostname": platform.node()}
    if sys.platform == "darwin":
        info["macos"] = _run(["sw_vers", "-productVersion"])
        info["cpu"] = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
        mem = _run(["sysctl", "-n", "hw.memsize"])
        info["memory_bytes"] = int(mem) if mem.isdigit() else None
        cores = _run(["sysctl", "-n", "hw.ncpu"])
        info["cores"] = int(cores) if cores.isdigit() else os.cpu_count()
        vm = _run(["vm_stat"])
        try:
            page = int(vm.split("page size of")[1].split("bytes")[0].strip())
            pages = {}
            for line in vm.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    v = v.strip().rstrip(".")
                    if v.isdigit():
                        pages[k.strip()] = int(v)
            info["memory_available_bytes"] = page * (pages.get("Pages free", 0) + pages.get("Pages inactive", 0) + pages.get("Pages speculative", 0))
        except (IndexError, ValueError):
            info["memory_available_bytes"] = None
        info["gpu"] = "Apple Silicon unified memory (shared with the CPU)" if "Apple" in info.get("cpu", "") else "unknown"
    else:
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text()
            info["cpu"] = next((l.split(":", 1)[1].strip() for l in cpuinfo.splitlines() if l.startswith("model name")), platform.processor())
            meminfo = Path("/proc/meminfo").read_text()
            def kb(key):
                return next((int(l.split()[1]) * 1024 for l in meminfo.splitlines() if l.startswith(key)), None)
            info["memory_bytes"] = kb("MemTotal")
            info["memory_available_bytes"] = kb("MemAvailable")
        except OSError:
            info["cpu"] = platform.processor()
        info["cores"] = os.cpu_count()
        info["gpu"] = "none detected (CPU only)"
    try:
        usage = shutil.disk_usage(str(vault or PACKAGE_ROOT))
        info["disk_free_bytes"] = usage.free
    except OSError:
        info["disk_free_bytes"] = None
    return info


def run_doctor(settings: Settings, require_offline: bool = False) -> dict:
    checks: list = []

    def add(name, ok, detail, critical=True):
        checks.append({"name": name, "ok": bool(ok), "detail": detail, "critical": critical})

    add("wiki", True, f"personal_wiki {__version__} at {PACKAGE_ROOT}")
    add("python", sys.version_info >= (3, 11), f"{sys.version.split()[0]} ({sys.executable})")
    raw_files = [f for f in collect_vault_files(settings.vault) if f.startswith("raw/")] if settings.vault.exists() else []
    wiki_files = [f for f in collect_vault_files(settings.vault) if f.startswith("wiki/")] if settings.vault.exists() else []
    add("vault", settings.raw_dir.is_dir() and bool(raw_files),
        f"{settings.vault}: {len(raw_files)} raw source(s), {len(wiki_files)} wiki note(s), index.md {'present' if settings.index_md.exists() else 'missing (run wiki ingest)'}")
    catalog_path = PACKAGE_ROOT / "sources.json"
    if catalog_path.exists() and raw_files:
        import hashlib
        catalog = {s["file"]: s["sha256"] for s in read_json(catalog_path).get("sources", [])}
        mismatched, unknown = [], []
        for f in raw_files:
            digest = hashlib.sha256((settings.vault / f).read_bytes()).hexdigest()
            if f not in catalog:
                unknown.append(f)
            elif catalog[f] != digest:
                mismatched.append(f)
        add("sources", not mismatched, f"{len(raw_files) - len(mismatched) - len(unknown)} raw file(s) match sources.json"
            + (f"; CHANGED since the catalog: {mismatched}" if mismatched else "") + (f"; not in the catalog: {unknown}" if unknown else ""), critical=False)
    for label, path in (("research rules", settings.instructions_file), ("persona", settings.persona_file)):
        add(label, path.exists(), str(path))
    index = load_index(settings.index_dir)
    if index is None:
        add("index", True, f"not built yet at {settings.index_dir} (built on first search/ask)", critical=False)
    else:
        fresh = settings.vault.exists() and index.fingerprint == vault_fingerprint(settings.vault)
        add("index", True, f"{index.n_docs} passages built {index.built_at}, {'fresh' if fresh else 'stale (rebuilt automatically on next use)'}", critical=False)
    ollama: dict = {"backend": settings.backend, "host": settings.host, "model": settings.model}
    if settings.backend == "ollama":
        from .backends.ollama import OllamaBackend
        backend = OllamaBackend(settings.host, settings.model)
        ok, message = backend.check()
        ollama["ok"] = ok
        ollama["message"] = message
        if ok:
            info = backend.model_info()
            ollama["version"] = info.ollama_version
            ollama["model_info"] = info.to_dict()
            ollama["installed"] = backend.installed_models()
        add("ollama", ok, message)
    else:
        add("ollama", True, f"backend {settings.backend}: no Ollama needed", critical=False)
    reachable, probes = internet_reachable()
    internet = {"internet_reachable": reachable, "probes": probes, "checked_at": utc_now_iso(), "require_offline": require_offline}
    if require_offline:
        add("offline", not reachable, "no probe reached the internet" if not reachable else f"ONLINE: {probes}")
    else:
        add("network", True, "offline (no probe reached the internet)" if not reachable else "online", critical=False)
    device = device_info(settings.vault)
    add("device", True, f"{device.get('cpu')}, {device.get('cores')} cores, {(device.get('memory_bytes') or 0) / 2**30:.0f} GiB memory, "
        f"{device.get('system')} {device.get('macos') or device.get('release')}", critical=False)
    critical_failed = [c for c in checks if c["critical"] and not c["ok"]]
    exit_code = 0
    if require_offline and reachable:
        exit_code = 11
    elif any(c["name"] in ("ollama",) for c in critical_failed) or any(c["name"] in ("vault", "python", "research rules", "persona") for c in critical_failed):
        exit_code = 10
    return {"schema": "doctor/1", "run_id": settings.run_id, "created_at": utc_now_iso(), "ok": not critical_failed, "exit_code": exit_code,
            "checks": checks, "internet": internet, "device": device, "ollama": ollama,
            "settings": {"vault": str(settings.vault), "index_dir": str(settings.index_dir), "results_dir": str(settings.results_dir),
                         "model": settings.model, "backend": settings.backend, "host": settings.host, "k": settings.k, "num_ctx": settings.num_ctx}}


def render_report(report: dict) -> str:
    lines = [f"wiki doctor · run {report['run_id']} · {report['created_at']}"]
    for c in report["checks"]:
        mark = "ok " if c["ok"] else ("!! " if c["critical"] else "-- ")
        lines.append(f"[{mark}] {c['name']:<15} {c['detail']}")
    lines.append("all critical checks passed" if report["ok"] else "some critical checks FAILED (see !! above)")
    return "\n".join(lines)


def save_report(settings: Settings, report: dict) -> Path:
    settings.run_dir.mkdir(parents=True, exist_ok=True)
    n = 1
    path = settings.run_dir / "doctor.json"
    while path.exists():
        n += 1
        path = settings.run_dir / f"doctor-{n}.json"
    return write_json(path, report)
