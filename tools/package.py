# SPDX-License-Identifier: MIT
"""Package the PSX BIOS host and the engine's local BIOS module toolchain."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

from build import ENGINE, ROOT


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--toolchain-bin", type=Path, default=Path("C:/msys64/mingw64/bin"))
    args = parser.parse_args()
    work = args.work_root.resolve()
    host = work / "menu"
    with tempfile.TemporaryDirectory(prefix="package-0.2.0-", dir=work) as staging:
        stage = Path(staging)
        files = {"PlayStationBIOS.exe": host / "PlayStationBIOS.exe",
                 "PlayStationBIOSRuntime.exe": host / "PlayStationBIOSRuntime.exe",
                 "README.md": ROOT / "SETUP.md",
                 "LICENSE": ROOT / "LICENSE", "psxrecomp-LICENSE": ENGINE / "LICENSE",
                 "PERMISSIONS.md": ENGINE / "PERMISSIONS.md",
                 "THIRD_PARTY_ATTRIBUTION.md": ENGINE / "THIRD_PARTY_ATTRIBUTION.md",
                 "licenses/recomp-ui-LICENSE": ROOT / "recomp-ui/LICENSE",
                 "licenses/imgui-LICENSE.txt": ROOT / "recomp-ui/src/third_party/imgui/LICENSE.txt",
                 "licenses/SDL3-LICENSE.txt": args.toolchain_bin.parent / "share/licenses/SDL3/LICENSE.txt",
                 "bios/openbios.bin": ENGINE / "bios/openbios.bin",
                 "bios/OpenBIOS.LICENSE": ENGINE / "bios/OpenBIOS.LICENSE"}
        for destination, source in files.items():
            target = stage / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        shutil.copytree(ENGINE / "runtime/licenses", stage / "licenses", dirs_exist_ok=True)
        shutil.copytree(host / "assets", stage / "assets")
        for mod in ("psx.integration.debug-server", "psx.integration.playable-replays"):
            path = Path("mods/bundled") / mod
            shutil.copytree(host / path, stage / path)
        subprocess.run([sys.executable, "-B", ENGINE / "tools/release_stage.py", "stage-toolchain",
                        "--stage", stage, "--recomp-dir", work / "emitter",
                        "--recomp-tools", ENGINE / "tools", "--recomp-include", ENGINE / "runtime/include",
                        "--dl-cache", work / "downloads", "--platform", "win", "--mingw-bin", args.toolchain_bin],
                       check=True)
        members = sorted(file for file in stage.rglob("*") if file.is_file())
        metadata = {
            "source": subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip(),
            "psxrecomp": subprocess.check_output(["git", "-C", ENGINE, "rev-parse", "HEAD"], text=True).strip(),
            "recomp_ui": subprocess.check_output(["git", "-C", ROOT / "recomp-ui", "rev-parse", "HEAD"], text=True).strip(),
            "openbios_sha256": digest(stage / "bios/openbios.bin"),
            "host_sha256": digest(stage / "PlayStationBIOSRuntime.exe"),
            "launcher_sha256": digest(stage / "PlayStationBIOS.exe"),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.out, "x", zipfile.ZIP_DEFLATED) as archive:
            for file in members:
                archive.write(file, file.relative_to(stage).as_posix())
            archive.writestr("build.json", json.dumps(metadata, indent=2) + "\n")
        with zipfile.ZipFile(args.out) as archive:
            if archive.testzip() is not None:
                raise ValueError("Package integrity check failed")
        print(f"{digest(args.out)}  {args.out}")


if __name__ == "__main__":
    main()
