#!/usr/bin/env python3
"""
makemodules.py
Copyright 2020 Henrik Böving
Licensed under the MIT and Apache 2.0 licenses.

Usage: python3 scripts/makemodules.py devices/
"""
import pathlib
import subprocess
import logging

from .shared import read_device_table

ROOT = pathlib.Path().absolute()
SVD_DIR = ROOT / "svd"
RUST_FMT = ROOT / "rustfmt.toml"


def make_modules():
    table = read_device_table()

    for crate in table:

        for module in table[crate]:
            output_patch = SVD_DIR / f"{module}.svd.patched"
            logging.info("Generating code for {}".format(output_patch.absolute()))
            module_dir = ROOT / crate / "src" / module
            module_dir.mkdir(parents=True, exist_ok=True)
            logging.debug("entering {}".format(module_dir.absolute()))
            svd_result = subprocess.call(
                ["svd2rust", "-m", "-g", "--strict", "--pascal_enum_values",
                 "--max_cluster_size", "-i", f"{output_patch.absolute()}"],
                cwd=module_dir
            )
            logging.debug("subprocess call svd2rust := {}".format(svd_result))
            (module_dir / "build.rs").unlink()
            (module_dir / "generic.rs").replace(module_dir / ".." / "generic.rs")
            form_result = subprocess.call(["form", "-i", "mod.rs", "-o", "."], cwd=module_dir)
            logging.debug("subprocess call form := {}".format(form_result))
            (module_dir / "lib.rs").replace(module_dir / "mod.rs")
            rustfmt_args = ["rustfmt", f"--config-path={RUST_FMT.absolute()}"]
            rustfmt_args.extend([str(i) for i in module_dir.glob("*.rs")])
            rustfmt_result = subprocess.call(rustfmt_args, cwd=module_dir)
            logging.debug("subprocess call rustfmt := {}".format(rustfmt_result))
            lines = (module_dir / "mod.rs").read_text().splitlines(keepends=True)

            # these are lines that annoy rustc
            banned = [
                "#![deny(legacy_directory_ownership)]",
                "#![deny(plugin_as_library)]",
                "#![deny(safe_extern_statics)]",
                "#![deny(unions_with_drop_fields)]",
                "#![no_std]",
            ]
            to_remove = [i for i, line in enumerate(lines) if line.strip() in banned]
            for i in reversed(to_remove):
                del lines[i]
            with (module_dir / "mod.rs").open("w") as ofile:
                ofile.writelines(lines)


if __name__ == "__main__":
    make_modules()
