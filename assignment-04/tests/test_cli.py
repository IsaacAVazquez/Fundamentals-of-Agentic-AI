import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(args, tmp_path, tmp_vault, extra_env=None):
    env = {**os.environ, "WIKI_VAULT": str(tmp_vault), "WIKI_RESULTS_DIR": str(tmp_path / "results"),
           "WIKI_INDEX_DIR": str(tmp_path / "index"), "WIKI_RUN_ID": "cli-run", "WIKI_BACKEND": "fake"}
    env.update(extra_env or {})
    return subprocess.run([sys.executable, "-m", "personal_wiki", *args], capture_output=True, text=True, env=env, cwd=ROOT)


def test_help(tmp_path, tmp_vault):
    r = run(["--help"], tmp_path, tmp_vault)
    assert r.returncode == 0
    for cmd in ("chat", "ask", "search", "ingest", "help", "doctor"):
        assert cmd in r.stdout
    r2 = run(["help", "ask"], tmp_path, tmp_vault)
    assert r2.returncode == 0 and "--mode" in r2.stdout
    r3 = run([], tmp_path, tmp_vault)
    assert r3.returncode == 0 and "modes" in r3.stdout


def test_search_without_model(tmp_path, tmp_vault):
    r = run(["search", "capacitive probe"], tmp_path, tmp_vault, {"WIKI_BACKEND": "ollama", "WIKI_HOST": "http://127.0.0.1:9"})
    assert r.returncode == 0, r.stderr
    assert "[1] raw/Garden Sensor Log.md # Setup" in r.stdout and "no model call" in r.stdout
    assert (tmp_path / "results/cli-run/search/capacitive-probe.md").exists()


def test_ask_fake_end_to_end(tmp_path, tmp_vault):
    r = run(["ask", "--id", "Q1", "When was the sensor installed in the raised bed?"], tmp_path, tmp_vault)
    assert r.returncode == 0, r.stderr
    assert "model fake-gemma (fake, local)" in r.stdout and "status: supported" in r.stdout and "[1] raw/Garden Sensor Log.md" in r.stdout
    assert (tmp_path / "results/cli-run/ask/Q1.md").exists()
    r2 = run(["ask", "--json", "What grade did the sensor project receive?"], tmp_path, tmp_vault)
    assert r2.returncode == 0 and json.loads(r2.stdout)["status"] == "insufficient"


def test_chat_script_fake(tmp_path, tmp_vault):
    script = tmp_path / "s.txt"
    script.write_text("# expect: retrieval=no\nwhat can you help me with?\n/notes When was the sensor installed?\n")
    r = run(["chat", "--script", str(script)], tmp_path, tmp_vault)
    assert r.returncode == 0, r.stderr
    data = json.loads((tmp_path / "results/cli-run/chat/s.json").read_text())
    assert len(data["turns"]) == 2 and data["turns"][1]["retrieved"]


def test_doctor_json_and_manifest(tmp_path, tmp_vault):
    r = run(["doctor", "--json", "--save"], tmp_path, tmp_vault)
    assert r.returncode in (0, 10), r.stderr
    report = json.loads(r.stdout)
    assert report["schema"] == "doctor/1" and "device" in report
    r2 = run(["manifest"], tmp_path, tmp_vault)
    assert r2.returncode == 0
    manifest = json.loads((tmp_path / "results/cli-run/manifest.json").read_text())
    assert manifest["run_id"] == "cli-run" and "doctor.json" in manifest["files"]


def test_missing_vault_exit_5(tmp_path, tmp_vault):
    r = run(["search", "x"], tmp_path, tmp_vault, {"WIKI_VAULT": str(tmp_path / "nonexistent")})
    assert r.returncode == 5 and "no vault at" in r.stderr


def test_ingest_dry_run_and_index_check(tmp_path, tmp_vault):
    r = run(["ingest", "--dry-run"], tmp_path, tmp_vault)
    assert r.returncode == 0, r.stderr
    assert "plan (" in r.stdout
    r2 = run(["index", "--check"], tmp_path, tmp_vault)
    assert r2.returncode in (0, 1)
