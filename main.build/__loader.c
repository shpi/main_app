
/* Code to register embedded modules for meta path based loading if any. */

#include <Python.h>

#include "nuitka/constants_blob.h"

#include "nuitka/unfreezing.h"

/* Type bool */
#ifndef __cplusplus
#include "stdbool.h"
#endif

#if 0 > 0
static unsigned char *bytecode_data[0];
#else
static unsigned char **bytecode_data = NULL;
#endif

/* Table for lookup to find compiled or bytecode modules included in this
 * binary or module, or put along this binary as extension modules. We do
 * our own loading for each of these.
 */
extern PyObject *modulecode_PySide2(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_PySide2$$45$postLoad(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode___main__(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$Appearance(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$CircularBuffer(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$DataTypes(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$Git(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$HTTPServer(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$Inputs(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$Logger(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$MLX90615(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$ModuleManager(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$Property(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$Toolbox(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_core$Wifi(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_files(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$Alsa(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$AlsaRecord(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$Backlight(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$CPU(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$Disk(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$HWMon(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$IIO(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$InputDevs(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$Leds(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$System(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_hardware$iio(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_shiboken2(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);

static struct Nuitka_MetaPathBasedLoaderEntry meta_path_loader_entries[] = {
    {"PySide2", modulecode_PySide2, 0, 0, NUITKA_PACKAGE_FLAG},
    {"PySide2-postLoad", modulecode_PySide2$$45$postLoad, 0, 0, },
    {"__main__", modulecode___main__, 0, 0, },
    {"core", modulecode_core, 0, 0, NUITKA_PACKAGE_FLAG},
    {"core.Appearance", modulecode_core$Appearance, 0, 0, },
    {"core.CircularBuffer", modulecode_core$CircularBuffer, 0, 0, },
    {"core.DataTypes", modulecode_core$DataTypes, 0, 0, },
    {"core.Git", modulecode_core$Git, 0, 0, },
    {"core.HTTPServer", modulecode_core$HTTPServer, 0, 0, },
    {"core.Inputs", modulecode_core$Inputs, 0, 0, },
    {"core.Logger", modulecode_core$Logger, 0, 0, },
    {"core.MLX90615", modulecode_core$MLX90615, 0, 0, },
    {"core.ModuleManager", modulecode_core$ModuleManager, 0, 0, },
    {"core.Property", modulecode_core$Property, 0, 0, },
    {"core.Toolbox", modulecode_core$Toolbox, 0, 0, },
    {"core.Wifi", modulecode_core$Wifi, 0, 0, },
    {"files", modulecode_files, 0, 0, },
    {"hardware", modulecode_hardware, 0, 0, NUITKA_PACKAGE_FLAG},
    {"hardware.Alsa", modulecode_hardware$Alsa, 0, 0, },
    {"hardware.AlsaRecord", modulecode_hardware$AlsaRecord, 0, 0, },
    {"hardware.Backlight", modulecode_hardware$Backlight, 0, 0, },
    {"hardware.CPU", modulecode_hardware$CPU, 0, 0, },
    {"hardware.Disk", modulecode_hardware$Disk, 0, 0, },
    {"hardware.HWMon", modulecode_hardware$HWMon, 0, 0, },
    {"hardware.IIO", modulecode_hardware$IIO, 0, 0, },
    {"hardware.InputDevs", modulecode_hardware$InputDevs, 0, 0, },
    {"hardware.Leds", modulecode_hardware$Leds, 0, 0, },
    {"hardware.System", modulecode_hardware$System, 0, 0, },
    {"hardware.iio", modulecode_hardware$iio, 0, 0, },
    {"shiboken2", modulecode_shiboken2, 0, 0, NUITKA_PACKAGE_FLAG},
    {NULL, NULL, 0, 0, 0}
};

static void _loadBytesCodesBlob()
{
    static bool init_done = false;

    if (init_done == false) {
        loadConstantsBlob((PyObject **)bytecode_data, ".bytecode");

        init_done = true;
    }
}


void setupMetaPathBasedLoader(void) {
    static bool init_done = false;
    if (init_done == false) {
        _loadBytesCodesBlob();
        registerMetaPathBasedUnfreezer(meta_path_loader_entries, bytecode_data);

        init_done = true;
    }


}

// This provides the frozen (compiled bytecode) files that are included if
// any.

// These modules should be loaded as bytecode. They may e.g. have to be loadable
// during "Py_Initialize" already, or for irrelevance, they are only included
// in this un-optimized form. These are not compiled by Nuitka, and therefore
// are not accelerated at all, merely bundled with the binary or module, so
// that CPython library can start out finding them.

struct frozen_desc {
    char const *name;
    int index;
    int size;
};

static struct frozen_desc _frozen_modules[] = {

    {NULL, 0, 0}
};


void copyFrozenModulesTo(struct _frozen *destination) {
    _loadBytesCodesBlob();

    struct frozen_desc *current = _frozen_modules;

    for (;;) {
        destination->name = (char *)current->name;
        destination->code = bytecode_data[current->index];
        destination->size = current->size;

        if (destination->name == NULL) break;

        current += 1;
        destination += 1;
    };
}


