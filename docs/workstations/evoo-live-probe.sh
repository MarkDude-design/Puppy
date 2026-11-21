#!/usr/bin/env bash
# EVOO live-Linux inventory. Meraki, 2026-11-20.
# Read-only checks: no sudo, installs, network requests, mounts, or disk writes.
# Run: bash evoo-live-probe.sh
# Optional local log: bash evoo-live-probe.sh > evoo-hardware.txt 2>&1
# Inspect before sharing: lsusb can identify attached personal peripherals.
set -u
run_check() {
    local title="$1"
    shift
    printf '\n--- %s ---\n' "$title"
    if ! command -v "$1" >/dev/null 2>&1; then
        printf 'UNAVAILABLE: %s\n' "$1"
        return 0
    fi
    "$@" 2>&1
    local result=$?
    printf 'check_exit=%s\n' "$result"
    return 0
}
printf 'EVOO Linux inventory; not a hardware compatibility PASS.\n'
run_check 'Kernel and architecture' uname -srmo
printf '\n--- Distribution ---\n'
if [[ -r /etc/os-release ]]; then
    cat /etc/os-release
fi
printf '\n--- Firmware mode ---\n'
if [[ -d /sys/firmware/efi ]]; then
    printf 'Booted in UEFI mode\n'
else
    printf 'EFI interface absent; legacy mode or environment limitation\n'
fi
printf '\n--- Model (serial numbers intentionally omitted) ---\n'
for field in sys_vendor product_name product_version board_name; do
    if [[ -r "/sys/class/dmi/id/$field" ]]; then
        printf '%s=' "$field"
        cat "/sys/class/dmi/id/$field"
    fi
done
run_check 'CPU' lscpu
run_check 'RAM' free -h
run_check 'Storage; NAME/SIZE/TYPE/RO/FSTYPE only' lsblk -o NAME,SIZE,TYPE,RO,FSTYPE
run_check 'PCI device IDs and kernel drivers' lspci -nnk
run_check 'USB device IDs (internal Wi-Fi can be USB)' lsusb
run_check 'Wireless block state' rfkill list
run_check 'Audio devices' aplay -l
run_check 'Secure Boot status, if tool available' mokutil --sb-state
printf '\nManual checks: Wi-Fi browsing, touchpad, keyboard, sound, shutdown.\n'
printf 'Do not infer working Wi-Fi or healthy storage from inventory alone.\n'
