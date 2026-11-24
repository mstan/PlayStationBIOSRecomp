# PlayStation BIOS Recomp

Standalone PlayStation system-menu consumer for the [psxrecomp](https://github.com/RetroPortingToolKit/psxrecomp) engine. This repository owns the BIOS player, its release profile and packaging. The engine provides the HLE services, recompiler and existing BIOS selection interface.

## Windows x64 preview

Extract the ZIP and open **PlayStationBIOS.exe**. In recomp-ui, choose your original Sony SCPH-1001 BIOS dump and select **Play**. The release builds the matching native BIOS module locally the first time, then opens the original PlayStation menu. The BIOS image stays in its original location.

Keep memory cards and settings when updating an existing installation. See the [engine's BIOS selection documentation](psxrecomp/docs/BIOS_SELECTION.md) for accepted revisions and locally generated modules.

## Build

Use Windows x64, Python 3.11 or later, MinGW-w64, CMake and Ninja. Run the build and packaging commands from this repository. The toolchain stage verifies pinned dependency downloads and includes the matching module compiler.

```powershell
git submodule update --init
python -B tools/build.py --work-root G:/Temp/PlayStationBIOSBuild
python -B tools/package.py --work-root G:/Temp/PlayStationBIOSBuild --out G:/Temp/PlayStationBIOS-windows-x64.zip
```

The package includes OpenBIOS and its notice. Original Sony BIOS images, their generated modules, discs and player data stay local.
