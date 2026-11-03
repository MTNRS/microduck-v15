#!/usr/bin/env bash
# Run as the operator account on Raspberry Pi OS; no movement is started.
set -euo pipefail
if [[ $EUID -eq 0 ]]; then
  printf '%s\n' 'Ejecuta como tu usuario habitual, sin sudo delante del script.' >&2
  exit 2
fi
model=$(tr -d '\0' </proc/device-tree/model 2>/dev/null || true)
if [[ "$model" != *'Raspberry Pi Zero 2'* ]] || ! command -v raspi-config >/dev/null; then
  printf '%s\n' 'Se requiere Raspberry Pi Zero 2 W con Raspberry Pi OS.' >&2
  exit 2
fi
sudo apt-get update
sudo apt-get install -y python3 python3-smbus2 python3-gpiozero python3-lgpio
sudo raspi-config nonint do_i2c 0
sudo usermod -aG i2c,gpio "$(id -un)"
python3 -c 'import sys, smbus2, gpiozero, lgpio; assert sys.version_info >= (3, 10)'
printf '%s\n' 'Preparación terminada. Reinicia con sudo reboot y prueba doctor con los servos desconectados.'
