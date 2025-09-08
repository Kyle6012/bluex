#!/usr/bin/env bash
# Safe installer - installs only non-destructive, educational dependencies.
set -euo pipefail
IFS=$'\n\t'
echo "[Blue-X Safe Installer] Starting..."

PKGS_COMMON=(python3 python3-pip figlet jq)
PIP_PKGS=(flask pandas)

detect_pm() {
  for pm in apt dnf pacman zypper apk; do
    if command -v "$pm" &>/dev/null; then
      echo $pm; return 0
    fi
  done
  return 1
}

PM=$(detect_pm || true)
if [ -z "$PM" ]; then
  echo "No supported package manager detected. Install: ${PKGS_COMMON[*]} manually."
  exit 1
fi

echo "Detected package manager: $PM"
case "$PM" in
  apt)
    sudo apt update
    sudo apt install -y ${PKGS_COMMON[*]}
    ;;
  dnf)
    sudo dnf install -y ${PKGS_COMMON[*]}
    ;;
  pacman)
    sudo pacman -Sy --noconfirm ${PKGS_COMMON[*]}
    ;;
  zypper)
    sudo zypper install -y ${PKGS_COMMON[*]}
    ;;
  apk)
    sudo apk add ${PKGS_COMMON[*]}
    ;;
  *)
    echo "Unsupported package manager: $PM";;
esac

echo "Installing python packages: ${PIP_PKGS[*]}"
sudo python3 -m pip install --upgrade pip || true
sudo python3 -m pip install ${PIP_PKGS[*]} || true

echo "Installer finished. Note: This safe installer does NOT install or build radio/hardware tools (ubertooth, btlejack)."
mkdir -p sessions logs reports dashboard_data
echo "Created sessions/, logs/, reports/ folders."
