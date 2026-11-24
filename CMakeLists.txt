cmake_minimum_required(VERSION 3.20)
project(PlayStationBIOSRecomp VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)
set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp")
set(PSX_RECOMP_UI OFF CACHE BOOL "" FORCE)
set(PSX_NETPLAY OFF CACHE BOOL "" FORCE)
set(PSX_REWIND OFF CACHE BOOL "" FORCE)
set(PSXRECOMP_BIOS_STEMS "OpenBIOS" CACHE STRING "" FORCE)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

psxrecomp_add_runtime_target(playstation-bios
    DEBUG_PORT 4370
    WINDOW_TITLE "PlayStation BIOS"
    DEFAULT_BIOS_PATH "bios/openbios.bin"
    EXE_NAME "PlayStationBIOS")
target_sources(playstation-bios PRIVATE src/boot_defaults.c)
