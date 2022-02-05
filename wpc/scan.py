#!/usr/bin/env python3
import collections
import pathlib
import shutil
import subprocess
import tempfile
import typing
import urllib.request

import netifaces


def list_interfaces() -> typing.List[str]:
    return netifaces.interfaces()


def guess_interface():
    for i in list_interfaces():
        cmd = f"iwconfig {i}"
        try:
            result = subprocess.check_output(cmd.split(), stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            continue
        result = result.decode('utf-8')
        if "Mode:Monitor" in result:
            return i
    return None


def scan(interface: str, outfile: typing.Union[str, pathlib.Path], duration_in_sec: int = 60):
    interfaces = list_interfaces()
    if interface not in list_interfaces():
        raise ValueError(f"Interface {interface} is not a valid interface. Found: {interfaces}")

    if not shutil.which("tshark"):
        raise ValueError("tshark is not installed")

    duration = f"duration:{duration_in_sec}"
    cmd = f"tshark -i {interface} -a {duration} -w {str(outfile)}"

    proc = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc


def load_ouis(file):
    oui = {}
    with open(file, 'r') as f:
        for line in f:
            if '(hex)' in line:
                data = line.split('(hex)')
                key = data[0].replace('-', ':').lower().strip()
                company = data[1].strip()
                oui[key] = company
    return oui


def analyze(outfile: typing.Union[str, pathlib.Path], ouis):
    cmd = f"tshark -r {outfile} -T fields -e wlan.sa -e wlan.bssid -e wlan_radio.signal_dbm"
    output = subprocess.check_output(cmd.split())
    found_macs = collections.defaultdict(lambda: list())

    for line in output.decode('utf-8').splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        rows = stripped.split()

        if len(rows) == 3:
            mac, _, signal_dbm = rows
            found_macs[mac].append(int(signal_dbm))

    print("Found:", len(found_macs), "unique macs:")
    for mac, signal_dbm in found_macs.items():
        oui = ouis.get(mac[:8], "N.A.")
        print("\t", mac, f"({oui})", ":", f"{int(sum(signal_dbm) / len(signal_dbm))}", "dBm")
