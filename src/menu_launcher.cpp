// SPDX-License-Identifier: MIT
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include "launcher_profile.h"
#include "recomp_launcher.h"
#include "sha256.h"

#include <array>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>

namespace fs = std::filesystem;

static constexpr char bios_sha256[] =
    "71af94d1e47a68c11e8fdb9f8368040601514a42a5a399cda48c7d3bff1e99d3";

static bool verify_bios(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    std::vector<uint8_t> bytes(512 * 1024);
    std::array<uint8_t, 32> digest{};
    std::array<char, 65> hex{};
    if (input.read(reinterpret_cast<char*>(bytes.data()), bytes.size()) &&
        input.peek() == std::char_traits<char>::eof()) {
        recompui_sha256_compute(bytes.data(), bytes.size(), digest.data());
        for (size_t i = 0; i < digest.size(); ++i) {
            std::snprintf(hex.data() + 2 * i, 3, "%02x", static_cast<unsigned>(digest[i]));
        }
        return std::string_view(hex.data()) == bios_sha256;
    }
    return false;
}

static int boot(const fs::path& root, const fs::path& firmware, LPWSTR* options, int count) {
    if (!verify_bios(firmware)) return 2;
    const auto runtime = root / L"PlayStationBIOSRuntime.exe";
    std::wstring command = L"\"" + runtime.native() + L"\" --no-launcher --bios \"" + firmware.native() + L"\"";
    for (int i = 0; i < count; ++i) {
        command += L" \"" + std::wstring(options[i]) + L"\"";
    }
    STARTUPINFOW startup{};
    startup.cb = sizeof(startup);
    PROCESS_INFORMATION child{};
    if (!CreateProcessW(runtime.c_str(), command.data(), nullptr, nullptr, FALSE,
                        CREATE_NO_WINDOW, nullptr, root.c_str(), &startup, &child)) {
        return 2;
    }
    CloseHandle(child.hThread);
    WaitForSingleObject(child.hProcess, INFINITE);
    DWORD result = 2;
    GetExitCodeProcess(child.hProcess, &result);
    CloseHandle(child.hProcess);
    return static_cast<int>(result);
}

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    try {
        std::wstring executable(32768, L'\0');
        const DWORD length = GetModuleFileNameW(nullptr, executable.data(), static_cast<DWORD>(executable.size()));
        if (!length || length == executable.size()) return 2;
        executable.resize(length);
        const auto root = fs::path(executable).parent_path();
        int argc = 0;
        LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
        if (!argv) return 2;
        if (argc >= 3 && std::wstring(argv[1]) == L"--bios") {
            const int result = boot(root, fs::absolute(argv[2]), argv + 3, argc - 3);
            LocalFree(argv);
            return result;
        }
        LocalFree(argv);

        const auto preference = root / "menu-bios.cfg";
        std::string last;
        std::getline(std::ifstream(preference), last);
        RecompLauncherCSettings settings{};
        settings.window_scale = 2;
        settings.enable_audio = 1;
        settings.audio_freq = 44100;
        settings.volume = 100;
        RecompLauncherCGameInfo game{};
        static const char* patterns[] = {"*.bin", "*.rom"};
        static const RecompLauncherCRomRevision revisions[] = {
            {"Sony PlayStation SCPH-1001", bios_sha256, nullptr, nullptr, 1, nullptr},
        };
        game.name = "PlayStation BIOS";
        // Keep the PlayStation theme while using the verified-file panel.
        game.platform = "SONY PLAYSTATION";
        game.num_players = 1;
        game.theme = "psx";
        game.rom_noun = "BIOS";
        game.rom_filter_desc = "PlayStation BIOS";
        game.rom_patterns = patterns;
        game.num_rom_patterns = 2;
        game.rom_revisions = revisions;
        game.num_rom_revisions = 1;
        game.has_bios = 0;
        game.setup_wizard_supported = 1;
        const auto assets = (root / "assets").u8string();
        char selected[2048]{};
        const auto result = recomp_launcher_run_window("PlayStation BIOS", &settings, &game,
            assets.c_str(), last.c_str(), selected, sizeof selected);
        if (result == RECOMP_LAUNCHER_RESULT_QUIT) return 0;
        if (result != RECOMP_LAUNCHER_RESULT_LAUNCH || !selected[0]) return 2;
        std::ofstream(preference) << selected << '\n';
        return boot(root, fs::absolute(fs::u8path(selected)), nullptr, 0);
    } catch (const std::exception&) {
        return 2;
    }
}
