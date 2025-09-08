#!/usr/bin/env bash
# Blue-X Mode Selector with Role-based Access Control for Attack Mode (manual only)
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
MODULE_DIR="$BASE_DIR/modules"
MANUAL_DIR="$BASE_DIR/manual_attacks"
SESS_DIR="$BASE_DIR/sessions"
REPORT_DIR="$BASE_DIR/reports"
CONFIG_DIR="$BASE_DIR/config"
USERS_CONF="$CONFIG_DIR/users.json"
AUDIT_LOG="$SESS_DIR/audit.log"
mkdir -p "$SESS_DIR" "$REPORT_DIR" "$CONFIG_DIR"

# Colors
RED="\e[31m"; GREEN="\e[32m"; YELLOW="\e[33m"; CYAN="\e[36m"; RESET="\e[0m"

banner(){ if command -v figlet &>/dev/null; then figlet "Blue-X" || true; else echo "Blue-X"; fi; echo -e "${GREEN}Mode Selector (Safe vs Attack Manual Helper)${RESET}"; echo -e "${YELLOW}Attack Mode requires role 'redteam' or 'instructor'. This script will not automate attacks.${RESET}\n"; }

audit(){ echo "$(date --iso-8601=seconds) - $(whoami) - $1" >> "$AUDIT_LOG"; }

# check role helper
check_role(){ python3 - <<PY
import json, getpass, hashlib, sys, os
conf='"$USERS_CONF"'
if not os.path.exists(conf):
    print('NO_CONF'); sys.exit(2)
users=json.load(open(conf))
u=input('Username: ')
pw=getpass.getpass('Password: ')
user=users.get(u)
if not user:
    print('NOUSER'); sys.exit(3)
salt=user['salt']; h=user['hash']; role=user.get('role','student')
if hashlib.sha256((salt+pw).encode()).hexdigest()!=h:
    print('BADPASS'); sys.exit(4)
print(role); sys.exit(0)
PY
}

list_sim_modules(){ local i=0; for f in "$MODULE_DIR"/*.sh; do [ -e "$f" ] || continue; name=$(grep -m1 '^# MODULE_NAME:' "$f" 2>/dev/null | sed -E 's/# MODULE_NAME:\s*//'); if [[ "$f" =~ SIM_ ]] || [[ "$name" =~ SIM_ ]]; then i=$((i+1)); printf "%2d) %s - %s\n" "$i" "${name:-$(basename $f)}" "$(grep -m1 '^# MODULE_DESC:' "$f" 2>/dev/null | sed -E 's/# MODULE_DESC:\s*//')"; fi; done; if [ $i -eq 0 ]; then echo "(no safe modules found)"; fi; }

run_sim_module(){ local file="$1"; ts=$(date +%s); session_file="$SESS_DIR/$(basename "$file" .sh)_$ts.log"; report_file="$REPORT_DIR/$(basename "$file" .sh)_$ts.json"; echo -e "${CYAN}Running SAFE simulation: $(basename "$file")${RESET}"; SAFE=1 bash "$file" "$report_file" |& tee "$session_file"; echo -e "${GREEN}Done. Report: $report_file  Log: $session_file${RESET}"; audit "SIM_MODULE_RUN $(basename $file) report=$report_file log=$session_file"; }

attack_mode_helper(){ echo -e "${RED}ATTACK MODE (Manual Helper) - ROLE CHECK REQUIRED${RESET}\n"; role_out=$(check_role); rc=$?; if [ $rc -ne 0 ]; then echo "Role check failed or cancelled (code $rc)."; audit "ATTACK_ROLECHECK_FAIL code=$rc"; return 1; fi; role=$(echo "$role_out" | tr -d '\n'); if [[ "$role" != "redteam" && "$role" != "instructor" ]]; then echo "Insufficient role ($role). Attack Mode requires redteam/instructor."; audit "ATTACK_ROLE_INSUFFICIENT role=$role"; return 1; fi; audit "ATTACK_ROLECHECK_OK user_role=$role"; echo "Role OK: $role"; # proceed with manual helper (same as previous implementation) ; PS3='Choose an action: ' ; options=("Show legal checklist" "Show hardware checklist" "List playbooks" "Open playbook" "Open printable worksheet" "Open operator terminal" "Back to main menu") ; select opt in "${options[@]}"; do case $opt in "Show legal checklist") cat "$MANUAL_DIR/legal_checklist.txt" ; audit "VIEW_PLAYBOOK legal_checklist.txt" ;; "Show hardware checklist") cat "$MANUAL_DIR/hardware_checklist.txt" ; audit "VIEW_PLAYBOOK hardware_checklist.txt" ;; "List playbooks") ls -1 "$MANUAL_DIR"/*.md | xargs -n1 basename ; audit "LIST_PLAYBOOKS" ;; "Open playbook") read -rp "Enter playbook filename (e.g., recon.md): " pb; if [ -f "$MANUAL_DIR/$pb" ]; then less "$MANUAL_DIR/$pb"; audit "VIEW_PLAYBOOK $pb"; else echo "Not found"; fi ;; "Open printable worksheet") read -rp "Enter worksheet filename (e.g., recon_worksheet.md): " ws; if [ -f "$MANUAL_DIR/$ws" ]; then less "$MANUAL_DIR/$ws"; audit "VIEW_WORKSHEET $ws"; else echo "Not found"; fi ;; "Open operator terminal") echo "Opening interactive shell for manual operator commands (you must run commands yourself)..."; audit "OPEN_OPERATOR_TERMINAL"; if command -v xterm &>/dev/null; then xterm -e bash & else bash ; fi ;; "Back to main menu") break ;; *) echo "Invalid" ;; esac; done; }

main_menu(){ while true; do banner; echo "s) Safe Mode (Simulations)"; echo "a) Attack Mode (Manual Helper - role check required)"; echo "q) Quit"; read -rp "Choice: " ch; case $ch in s) echo "Available simulation modules:"; list_sim_modules; read -rp "Enter number to run or b to back: " num; if [[ "$num" =~ ^[0-9]+$ ]]; then idx=0; sel=""; for f in "$MODULE_DIR"/*.sh; do [ -e "$f" ] || continue; name=$(grep -m1 '^# MODULE_NAME:' "$f" 2>/dev/null | sed -E 's/# MODULE_NAME:\s*//'); if [[ "$f" =~ SIM_ ]] || [[ "$name" =~ SIM_ ]]; then idx=$((idx+1)); if [ "$idx" -eq "$num" ]; then sel="$f"; break; fi; fi; done; if [ -n "$sel" ]; then run_sim_module "$sel"; else echo "Invalid selection"; fi; fi ;; a) attack_mode_helper || true ;; q) echo "Bye"; exit 0 ;; *) echo "Unknown" ;; esac; read -rp "Press Enter to continue..."; done; }

main_menu
