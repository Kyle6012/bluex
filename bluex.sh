#!/usr/bin/env bash
# Blue-X Safe Launcher (Simulation-only)
set -euo pipefail
IFS=$'\n\t'
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
MODULE_DIR="$BASE_DIR/modules"
SESS_DIR="$BASE_DIR/sessions"
REPORT_DIR="$BASE_DIR/reports"
LOG_DIR="$BASE_DIR/logs"
SAFE_MODE=1

mkdir -p "$MODULE_DIR" "$SESS_DIR" "$REPORT_DIR" "$LOG_DIR"

banner(){
  if command -v figlet &>/dev/null; then figlet "Blue-X (Safe)" || true; else echo "Blue-X (Safe)"; fi
  echo "Safe Simulation Mode: NO RADIO TRANSMISSIONS will be performed."
}

list_modules(){
  local i=0
  for f in "$MODULE_DIR"/*.sh; do
    [ -e "$f" ] || continue
    i=$((i+1))
    name=$(grep -m1 '^# MODULE_NAME:' "$f" || true | sed -E 's/# MODULE_NAME:\s*//')
    desc=$(grep -m1 '^# MODULE_DESC:' "$f" || true | sed -E 's/# MODULE_DESC:\s*//')
    printf "%2d) %s - %s\n" "$i" "${name:-$(basename $f)}" "${desc:-No description}"
  done
  if [ $i -eq 0 ]; then echo "(no modules found)"; fi
}

run_module(){
  local f="$1"
  ts=$(date +%s)
  session_file="$SESS_DIR/$(basename "$f" .sh)_$ts.log"
  report_file="$REPORT_DIR/$(basename "$f" .sh)_$ts.json"
  echo "Running (SIMULATION) module: $f"
  SAFE=1 bash "$f" "$report_file" |& tee "$session_file"
  echo "Report saved to: $report_file"
}

if [ "${1:-}" = "--install" ]; then
  if [ -x "$BASE_DIR/install.sh" ]; then bash "$BASE_DIR/install.sh"; else echo "Installer missing"; fi
  exit 0
fi

while true; do
  banner
  echo "Available simulation modules:"
  list_modules
  echo
  echo "i) Run installer (safe)"
  echo "q) Quit"
  read -rp "Select module number or command: " CHOICE
  if [[ "$CHOICE" =~ ^[0-9]+$ ]]; then
    idx=0; sel=""
    for f in "$MODULE_DIR"/*.sh; do [ -e "$f" ] || continue; idx=$((idx+1)); if [ "$idx" -eq "$CHOICE" ]; then sel="$f"; break; fi; done
    if [ -n "$sel" ]; then run_module "$sel"; read -rp "Press Enter to continue..."; fi
  else
    case "$CHOICE" in
      i) bash "$BASE_DIR/install.sh" ;;
      q) echo "Bye"; exit 0 ;;
      *) echo "Unknown"; sleep 1 ;;
    esac
  fi
done
