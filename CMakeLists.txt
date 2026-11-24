cmake_minimum_required(VERSION 3.20)
project(PlayStationBIOSRecomp VERSION 0.2.0 LANGUAGES C CXX)

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
    EXE_NAME "PlayStationBIOSRuntime")
target_sources(playstation-bios PRIVATE src/boot_defaults.c)

add_executable(PlayStationBIOS WIN32 src/menu_launcher.cpp)
target_link_options(PlayStationBIOS PRIVATE $<$<CXX_COMPILER_ID:GNU>:-municode>)
target_link_options(PlayStationBIOS PRIVATE $<$<CXX_COMPILER_ID:GNU>:-static>)
set(RECOMP_UI_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/recomp-ui")
set(RECOMP_UI_SDL3 ON CACHE BOOL "" FORCE)
find_package(SDL3 CONFIG REQUIRED)
include("${RECOMP_UI_ROOT}/recomp_ui.cmake")
recomp_target_launcher_ui(PlayStationBIOS CONSOLE psx
    PAD "${RECOMP_UI_ROOT}/assets/consoles/psx/img/pad_digital.tga")
target_link_libraries(PlayStationBIOS PRIVATE SDL3::SDL3-static shell32)
