#!/usr/bin/env python3
"""
patch.py
Copyright 2020 Henrik Böving

Patch all the SVDs mentioned in a certain directory

Usage: python3 scripts/patch.py devices/
"""

import argparse
from pathlib import Path

import subprocess
import logging


def patch_files(device_path: Path):
    device_files = [f for f in device_path.iterdir() if f.is_file()]
    for path in device_files:
        logging.debug("patching {}...".format(path))
        svdtools_result = subprocess.call(["svdtools", "patch", f"{path.absolute()}"])
        logging.debug("subprocess call svdtools := {}".format(svdtools_result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("devices", help="Path to device YAML files")
    args = parser.parse_args()
    patch_files(Path(args.devices))
