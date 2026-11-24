/* SPDX-License-Identifier: MIT */
#include <stdlib.h>

/* The BIOS app keeps the shell visible while enabling native services for
 * compatible BIOS images. The engine checks the selected image's support. */
__attribute__((constructor))
static void enable_menu_services(void) {
#ifdef _WIN32
    _putenv_s("PSX_BIOS_HLE", "1");
    _putenv_s("PSX_BIOS_HLE_KEEP_INTRO", "1");
#else
    setenv("PSX_BIOS_HLE", "1", 1);
    setenv("PSX_BIOS_HLE_KEEP_INTRO", "1", 1);
#endif
}
