# SPDX-License-Identifier: MIT
"""Build the standalone Windows BIOS host and the matching BIOS compiler."""

import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "psxrecomp"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--toolchain-bin", type=Path, default=Path("C:/msys64/mingw64/bin"))
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    work = args.work_root.resolve()
    if work.is_relative_to(ROOT) or args.jobs < 1:
        parser.error("Use an out-of-tree work directory and positive jobs")
    env = dict(os.environ)
    env["PATH"] = str(args.toolchain_bin) + os.pathsep + env["PATH"]
    cmake = args.toolchain_bin / "cmake.exe"

    def run(*command):
        subprocess.run(command, env=env, cwd=ENGINE, check=True)

    emitter = work / "emitter"
    menu = work / "menu"
    run(cmake, "-S", ENGINE / "recompiler", "-B", emitter, "-G", "Ninja",
        "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=OFF")
    run(cmake, "--build", emitter, "--target", "psxrecomp-bios", "psxrecomp-game",
        "--parallel", str(args.jobs))
    # runtime.cmake discovers the stock OpenBIOS bank in the engine's ignored
    # generation directory. Use only the redistributable OpenBIOS profile here.
    run(emitter / "psxrecomp-bios.exe", "--config", "bios/OpenBIOS.toml")
    run(cmake, "-S", ROOT, "-B", menu, "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release",
        "-DPSX_ENABLE_VULKAN=OFF", "-DBUILD_TESTING=OFF")
    run(cmake, "--build", menu, "--target", "playstation-bios", "PlayStationBIOS",
        "--parallel", str(args.jobs))


if __name__ == "__main__":
    main()
