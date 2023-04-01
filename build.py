#!/usr/bin/env python3
"""
build.py
Copyright 2020 Henrik Böving
"""
import pathlib
import subprocess
import logging

from generator.scripts import makemodules, patch, makecrates

# logger setup
logging.basicConfig(format='[%(funcName)s:%(levelname)s] %(message)s', level=logging.INFO)

# grab absolute path to the CWD, just in case something fiddles with the CWD...
CWD = pathlib.Path().absolute()
SVD = CWD / "svd"
DEVICES = CWD / "devices"

logging.info("Cleaning")
for patched in SVD.glob("*.patched"):
    logging.debug("deleting {}".format(patched.absolute()))
    patched.unlink()
# idk how to do this in pathlib without making a giant mess...
subprocess.check_call(["rm", "-rf", "ht32f*"])
logging.info("Creating crates")
makecrates.make_crates(DEVICES, True)
logging.info("Patching SVD files")
patch.patch_files(DEVICES)
logging.info("Generating code")
makemodules.make_modules()
