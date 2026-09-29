#!/usr/bin/env bash
# Write a plain-text device report into a run folder. Usage: scripts/device_report.sh RUN_DIR
# Every macOS-only command is guarded, so the script also runs (with fewer sections) on Linux.
set -euo pipefail
cd "$(dirname "$0")/.."
RUN_DIR="${1:?usage: scripts/device_report.sh RUN_DIR}"
mkdir -p "$RUN_DIR"
section() { printf '\n== %s ==\n' "$1"; }
{
  section "date (UTC)"; date -u +%Y-%m-%dT%H:%M:%SZ
  section "uname"; uname -a
  if command -v sw_vers >/dev/null; then section "sw_vers"; sw_vers; fi
  if [ "$(uname)" = Darwin ] && command -v sysctl >/dev/null; then
    section "sysctl"; sysctl -n machdep.cpu.brand_string hw.memsize hw.ncpu hw.physicalcpu hw.logicalcpu 2>/dev/null || true
  fi
  if command -v system_profiler >/dev/null; then section "system_profiler SPHardwareDataType"; system_profiler SPHardwareDataType 2>/dev/null || true; fi
  if command -v vm_stat >/dev/null; then section "vm_stat"; vm_stat; fi
  if command -v memory_pressure >/dev/null; then section "memory_pressure"; memory_pressure 2>/dev/null | head -20 || true; fi
  if [ -r /proc/cpuinfo ]; then section "cpuinfo"; grep -m1 'model name' /proc/cpuinfo || true; nproc; fi
  if [ -r /proc/meminfo ]; then section "meminfo"; grep -E 'MemTotal|MemAvailable' /proc/meminfo || true; fi
  section "df -h ."; df -h .
  if command -v networksetup >/dev/null; then section "wifi power (en0)"; networksetup -getairportpower en0 2>/dev/null || true; fi
  if command -v scutil >/dev/null; then section "scutil --nwi (network interfaces in use)"; scutil --nwi 2>/dev/null | head -20 || true; fi
  if command -v ollama >/dev/null; then
    section "ollama --version"; ollama --version 2>/dev/null || true
    section "ollama list"; ollama list 2>/dev/null || true
    section "ollama ps"; ollama ps 2>/dev/null || true
  fi
  section "python"; if [ -x .venv/bin/python ]; then .venv/bin/python --version; else python3 --version; fi
} > "$RUN_DIR/device.txt" 2>&1
echo "wrote $RUN_DIR/device.txt"
