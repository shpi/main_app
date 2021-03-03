
/* Code to register embedded modules for meta path based loading if any. */

#include <Python.h>

#include "nuitka/constants_blob.h"

#include "nuitka/unfreezing.h"

/* Type bool */
#ifndef __cplusplus
#include "stdbool.h"
#endif

#if 111 > 0
static unsigned char *bytecode_data[111];
#else
static unsigned char **bytecode_data = NULL;
#endif

/* Table for lookup to find compiled or bytecode modules included in this
 * binary or module, or put along this binary as extension modules. We do
 * our own loading for each of these.
 */
extern PyObject *modulecode_PySide2(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode___main__(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_appdirs(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_certifi(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_certifi$core(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
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
extern PyObject *modulecode_numpy(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$__config__(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$_distributor_init(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$_globals(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$_pytesttester(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$compat(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$compat$_inspect(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$compat$py3k(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_add_newdocs(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_asarray(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_dtype(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_dtype_ctypes(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_exceptions(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_internal(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_methods(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_string_helpers(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_type_aliases(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$_ufunc_config(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$arrayprint(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$defchararray(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$einsumfunc(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$fromnumeric(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$function_base(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$getlimits(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$machar(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$memmap(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$multiarray(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$numeric(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$numerictypes(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$overrides(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$records(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$shape_base(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$core$umath(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$ctypeslib(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$dual(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$fft(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$fft$_pocketfft(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$fft$helper(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$_datasource(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$_iotools(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$_version(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$arraypad(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$arraysetops(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$arrayterator(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$financial(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$format(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$function_base(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$histograms(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$index_tricks(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$mixins(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$nanfunctions(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$npyio(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$polynomial(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$scimath(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$shape_base(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$stride_tricks(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$twodim_base(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$type_check(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$ufunclike(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$lib$utils(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$linalg(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$linalg$linalg(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$ma(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$ma$core(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$ma$extras(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$ma$mrecords(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$matrixlib(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$matrixlib$defmatrix(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$_polybase(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$chebyshev(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$hermite(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$hermite_e(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$laguerre(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$legendre(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$polynomial(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$polynomial$polyutils(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$random(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$random$_pickle(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_numpy$version(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_packaging(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_packaging$__about__(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_shiboken2(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);
extern PyObject *modulecode_six(PyObject *, struct Nuitka_MetaPathBasedLoaderEntry const *);

static struct Nuitka_MetaPathBasedLoaderEntry meta_path_loader_entries[] = {
    {"PySide2", modulecode_PySide2, 0, 0, NUITKA_PACKAGE_FLAG},
    {"__main__", modulecode___main__, 0, 0, },
    {"appdirs", modulecode_appdirs, 0, 0, },
    {"certifi", modulecode_certifi, 0, 0, NUITKA_PACKAGE_FLAG},
    {"certifi.core", modulecode_certifi$core, 0, 0, },
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
    {"numpy", modulecode_numpy, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.__config__", modulecode_numpy$__config__, 0, 0, },
    {"numpy._distributor_init", modulecode_numpy$_distributor_init, 0, 0, },
    {"numpy._globals", modulecode_numpy$_globals, 0, 0, },
    {"numpy._pytesttester", modulecode_numpy$_pytesttester, 0, 0, },
    {"numpy.compat", modulecode_numpy$compat, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.compat._inspect", modulecode_numpy$compat$_inspect, 0, 0, },
    {"numpy.compat.py3k", modulecode_numpy$compat$py3k, 0, 0, },
    {"numpy.core", modulecode_numpy$core, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.core._add_newdocs", modulecode_numpy$core$_add_newdocs, 0, 0, },
    {"numpy.core._asarray", modulecode_numpy$core$_asarray, 0, 0, },
    {"numpy.core._dtype", modulecode_numpy$core$_dtype, 0, 0, },
    {"numpy.core._dtype_ctypes", modulecode_numpy$core$_dtype_ctypes, 0, 0, },
    {"numpy.core._exceptions", modulecode_numpy$core$_exceptions, 0, 0, },
    {"numpy.core._internal", modulecode_numpy$core$_internal, 0, 0, },
    {"numpy.core._methods", modulecode_numpy$core$_methods, 0, 0, },
    {"numpy.core._string_helpers", modulecode_numpy$core$_string_helpers, 0, 0, },
    {"numpy.core._type_aliases", modulecode_numpy$core$_type_aliases, 0, 0, },
    {"numpy.core._ufunc_config", modulecode_numpy$core$_ufunc_config, 0, 0, },
    {"numpy.core.arrayprint", modulecode_numpy$core$arrayprint, 0, 0, },
    {"numpy.core.defchararray", modulecode_numpy$core$defchararray, 0, 0, },
    {"numpy.core.einsumfunc", modulecode_numpy$core$einsumfunc, 0, 0, },
    {"numpy.core.fromnumeric", modulecode_numpy$core$fromnumeric, 0, 0, },
    {"numpy.core.function_base", modulecode_numpy$core$function_base, 0, 0, },
    {"numpy.core.getlimits", modulecode_numpy$core$getlimits, 0, 0, },
    {"numpy.core.machar", modulecode_numpy$core$machar, 0, 0, },
    {"numpy.core.memmap", modulecode_numpy$core$memmap, 0, 0, },
    {"numpy.core.multiarray", modulecode_numpy$core$multiarray, 0, 0, },
    {"numpy.core.numeric", modulecode_numpy$core$numeric, 0, 0, },
    {"numpy.core.numerictypes", modulecode_numpy$core$numerictypes, 0, 0, },
    {"numpy.core.overrides", modulecode_numpy$core$overrides, 0, 0, },
    {"numpy.core.records", modulecode_numpy$core$records, 0, 0, },
    {"numpy.core.shape_base", modulecode_numpy$core$shape_base, 0, 0, },
    {"numpy.core.umath", modulecode_numpy$core$umath, 0, 0, },
    {"numpy.ctypeslib", modulecode_numpy$ctypeslib, 0, 0, },
    {"numpy.distutils", NULL, 0, 1483, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"numpy.distutils.__config__", NULL, 1, 2508, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils._shell_utils", NULL, 2, 3172, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.ccompiler", NULL, 3, 19072, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command", NULL, 4, 1018, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"numpy.distutils.command.autodist", NULL, 5, 3705, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.bdist_rpm", NULL, 6, 826, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.build", NULL, 7, 1729, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.build_clib", NULL, 8, 7579, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.build_ext", NULL, 9, 12684, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.build_py", NULL, 10, 1357, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.build_scripts", NULL, 11, 1642, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.build_src", NULL, 12, 18352, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.config", NULL, 13, 13905, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.config_compiler", NULL, 14, 3905, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.develop", NULL, 15, 853, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.egg_info", NULL, 16, 1081, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.install", NULL, 17, 2073, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.install_clib", NULL, 18, 1619, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.install_data", NULL, 19, 881, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.install_headers", NULL, 20, 947, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.command.sdist", NULL, 21, 933, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.conv_template", NULL, 22, 8275, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.core", NULL, 23, 4710, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.cpuinfo", NULL, 24, 32662, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.exec_command", NULL, 25, 9149, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.extension", NULL, 26, 2489, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.fcompiler", NULL, 27, 28229, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"numpy.distutils.fcompiler.environment", NULL, 28, 2982, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.from_template", NULL, 29, 7209, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.lib2def", NULL, 30, 3295, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.log", NULL, 31, 2461, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.mingw32ccompiler", NULL, 32, 14371, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.misc_util", NULL, 33, 70345, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.npy_pkg_config", NULL, 34, 12284, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.numpy_distribution", NULL, 35, 774, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.system_info", NULL, 36, 84578, NUITKA_BYTECODE_FLAG},
    {"numpy.distutils.unixccompiler", NULL, 37, 3246, NUITKA_BYTECODE_FLAG},
    {"numpy.dual", modulecode_numpy$dual, 0, 0, },
    {"numpy.f2py", NULL, 38, 2643, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"numpy.f2py.__version__", NULL, 39, 326, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.auxfuncs", NULL, 40, 22031, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.capi_maps", NULL, 41, 17987, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.cb_rules", NULL, 42, 15554, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.cfuncs", NULL, 43, 38497, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.common_rules", NULL, 44, 4780, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.crackfortran", NULL, 45, 76267, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.diagnose", NULL, 46, 3717, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.f2py2e", NULL, 47, 20234, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.f2py_testing", NULL, 48, 1391, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.f90mod_rules", NULL, 49, 7302, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.func2subr", NULL, 50, 6497, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.rules", NULL, 51, 34433, NUITKA_BYTECODE_FLAG},
    {"numpy.f2py.use_rules", NULL, 52, 3041, NUITKA_BYTECODE_FLAG},
    {"numpy.fft", modulecode_numpy$fft, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.fft._pocketfft", modulecode_numpy$fft$_pocketfft, 0, 0, },
    {"numpy.fft.helper", modulecode_numpy$fft$helper, 0, 0, },
    {"numpy.lib", modulecode_numpy$lib, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.lib._datasource", modulecode_numpy$lib$_datasource, 0, 0, },
    {"numpy.lib._iotools", modulecode_numpy$lib$_iotools, 0, 0, },
    {"numpy.lib._version", modulecode_numpy$lib$_version, 0, 0, },
    {"numpy.lib.arraypad", modulecode_numpy$lib$arraypad, 0, 0, },
    {"numpy.lib.arraysetops", modulecode_numpy$lib$arraysetops, 0, 0, },
    {"numpy.lib.arrayterator", modulecode_numpy$lib$arrayterator, 0, 0, },
    {"numpy.lib.financial", modulecode_numpy$lib$financial, 0, 0, },
    {"numpy.lib.format", modulecode_numpy$lib$format, 0, 0, },
    {"numpy.lib.function_base", modulecode_numpy$lib$function_base, 0, 0, },
    {"numpy.lib.histograms", modulecode_numpy$lib$histograms, 0, 0, },
    {"numpy.lib.index_tricks", modulecode_numpy$lib$index_tricks, 0, 0, },
    {"numpy.lib.mixins", modulecode_numpy$lib$mixins, 0, 0, },
    {"numpy.lib.nanfunctions", modulecode_numpy$lib$nanfunctions, 0, 0, },
    {"numpy.lib.npyio", modulecode_numpy$lib$npyio, 0, 0, },
    {"numpy.lib.polynomial", modulecode_numpy$lib$polynomial, 0, 0, },
    {"numpy.lib.scimath", modulecode_numpy$lib$scimath, 0, 0, },
    {"numpy.lib.shape_base", modulecode_numpy$lib$shape_base, 0, 0, },
    {"numpy.lib.stride_tricks", modulecode_numpy$lib$stride_tricks, 0, 0, },
    {"numpy.lib.twodim_base", modulecode_numpy$lib$twodim_base, 0, 0, },
    {"numpy.lib.type_check", modulecode_numpy$lib$type_check, 0, 0, },
    {"numpy.lib.ufunclike", modulecode_numpy$lib$ufunclike, 0, 0, },
    {"numpy.lib.utils", modulecode_numpy$lib$utils, 0, 0, },
    {"numpy.linalg", modulecode_numpy$linalg, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.linalg.linalg", modulecode_numpy$linalg$linalg, 0, 0, },
    {"numpy.ma", modulecode_numpy$ma, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.ma.core", modulecode_numpy$ma$core, 0, 0, },
    {"numpy.ma.extras", modulecode_numpy$ma$extras, 0, 0, },
    {"numpy.ma.mrecords", modulecode_numpy$ma$mrecords, 0, 0, },
    {"numpy.matrixlib", modulecode_numpy$matrixlib, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.matrixlib.defmatrix", modulecode_numpy$matrixlib$defmatrix, 0, 0, },
    {"numpy.polynomial", modulecode_numpy$polynomial, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.polynomial._polybase", modulecode_numpy$polynomial$_polybase, 0, 0, },
    {"numpy.polynomial.chebyshev", modulecode_numpy$polynomial$chebyshev, 0, 0, },
    {"numpy.polynomial.hermite", modulecode_numpy$polynomial$hermite, 0, 0, },
    {"numpy.polynomial.hermite_e", modulecode_numpy$polynomial$hermite_e, 0, 0, },
    {"numpy.polynomial.laguerre", modulecode_numpy$polynomial$laguerre, 0, 0, },
    {"numpy.polynomial.legendre", modulecode_numpy$polynomial$legendre, 0, 0, },
    {"numpy.polynomial.polynomial", modulecode_numpy$polynomial$polynomial, 0, 0, },
    {"numpy.polynomial.polyutils", modulecode_numpy$polynomial$polyutils, 0, 0, },
    {"numpy.random", modulecode_numpy$random, 0, 0, NUITKA_PACKAGE_FLAG},
    {"numpy.random._pickle", modulecode_numpy$random$_pickle, 0, 0, },
    {"numpy.testing", NULL, 53, 719, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"numpy.testing._private", NULL, 54, 155, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"numpy.testing._private.decorators", NULL, 55, 9006, NUITKA_BYTECODE_FLAG},
    {"numpy.testing._private.noseclasses", NULL, 56, 9911, NUITKA_BYTECODE_FLAG},
    {"numpy.testing._private.nosetester", NULL, 57, 14892, NUITKA_BYTECODE_FLAG},
    {"numpy.testing._private.parameterized", NULL, 58, 15658, NUITKA_BYTECODE_FLAG},
    {"numpy.testing._private.utils", NULL, 59, 69962, NUITKA_BYTECODE_FLAG},
    {"numpy.version", modulecode_numpy$version, 0, 0, },
    {"packaging", modulecode_packaging, 0, 0, NUITKA_PACKAGE_FLAG},
    {"packaging.__about__", modulecode_packaging$__about__, 0, 0, },
    {"pkg_resources", NULL, 60, 100378, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"pkg_resources._vendor", NULL, 61, 139, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"pkg_resources._vendor.appdirs", NULL, 62, 20492, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.packaging", NULL, 63, 527, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"pkg_resources._vendor.packaging.__about__", NULL, 64, 689, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.packaging._compat", NULL, 65, 963, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.packaging._structures", NULL, 66, 2745, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.packaging.markers", NULL, 67, 8901, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.packaging.requirements", NULL, 68, 3860, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.packaging.specifiers", NULL, 69, 19769, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.packaging.version", NULL, 70, 10616, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.pyparsing", NULL, 71, 201616, NUITKA_BYTECODE_FLAG},
    {"pkg_resources._vendor.six", NULL, 72, 24412, NUITKA_BYTECODE_FLAG},
    {"pkg_resources.extern", NULL, 73, 2388, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"pkg_resources.py2_warn", NULL, 74, 913, NUITKA_BYTECODE_FLAG},
    {"pkg_resources.py31compat", NULL, 75, 582, NUITKA_BYTECODE_FLAG},
    {"setuptools", NULL, 76, 7735, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"setuptools._deprecation_warning", NULL, 77, 498, NUITKA_BYTECODE_FLAG},
    {"setuptools._imp", NULL, 78, 2037, NUITKA_BYTECODE_FLAG},
    {"setuptools.archive_util", NULL, 79, 5118, NUITKA_BYTECODE_FLAG},
    {"setuptools.command", NULL, 80, 694, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"setuptools.command.bdist_egg", NULL, 81, 14164, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.bdist_rpm", NULL, 82, 1766, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.develop", NULL, 83, 6483, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.easy_install", NULL, 84, 66564, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.egg_info", NULL, 85, 21709, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.install", NULL, 86, 3998, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.install_scripts", NULL, 87, 2306, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.py36compat", NULL, 88, 4592, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.sdist", NULL, 89, 7841, NUITKA_BYTECODE_FLAG},
    {"setuptools.command.setopt", NULL, 90, 4519, NUITKA_BYTECODE_FLAG},
    {"setuptools.config", NULL, 91, 17878, NUITKA_BYTECODE_FLAG},
    {"setuptools.depends", NULL, 92, 5198, NUITKA_BYTECODE_FLAG},
    {"setuptools.dist", NULL, 93, 42308, NUITKA_BYTECODE_FLAG},
    {"setuptools.extension", NULL, 94, 1943, NUITKA_BYTECODE_FLAG},
    {"setuptools.extern", NULL, 95, 2402, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"setuptools.glob", NULL, 96, 3715, NUITKA_BYTECODE_FLAG},
    {"setuptools.installer", NULL, 97, 4084, NUITKA_BYTECODE_FLAG},
    {"setuptools.monkey", NULL, 98, 4626, NUITKA_BYTECODE_FLAG},
    {"setuptools.namespaces", NULL, 99, 3598, NUITKA_BYTECODE_FLAG},
    {"setuptools.package_index", NULL, 100, 32962, NUITKA_BYTECODE_FLAG},
    {"setuptools.py27compat", NULL, 101, 1731, NUITKA_BYTECODE_FLAG},
    {"setuptools.py31compat", NULL, 102, 1173, NUITKA_BYTECODE_FLAG},
    {"setuptools.py33compat", NULL, 103, 1390, NUITKA_BYTECODE_FLAG},
    {"setuptools.py34compat", NULL, 104, 432, NUITKA_BYTECODE_FLAG},
    {"setuptools.sandbox", NULL, 105, 15518, NUITKA_BYTECODE_FLAG},
    {"setuptools.ssl_support", NULL, 106, 6855, NUITKA_BYTECODE_FLAG},
    {"setuptools.unicode_utils", NULL, 107, 1133, NUITKA_BYTECODE_FLAG},
    {"setuptools.version", NULL, 108, 274, NUITKA_BYTECODE_FLAG},
    {"setuptools.wheel", NULL, 109, 7369, NUITKA_BYTECODE_FLAG},
    {"setuptools.windows_support", NULL, 110, 971, NUITKA_BYTECODE_FLAG},
    {"shiboken2", modulecode_shiboken2, 0, 0, NUITKA_PACKAGE_FLAG},
    {"six", modulecode_six, 0, 0, },
    {NULL, NULL, 0, 0, 0}
};


void setupMetaPathBasedLoader(void) {
    static bool init_done = false;
    if (init_done == false) {
        loadConstantsBlob((PyObject **)bytecode_data, ".bytecode", 111);
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
    loadConstantsBlob((PyObject **)bytecode_data, ".bytecode", 111);

    struct frozen_desc *current = _frozen_modules;

    for(;;) {
        destination->name = (char *)current->name;
        destination->code = bytecode_data[current->index];
        destination->size = current->size;

        if (destination->name == NULL) break;

        current += 1;
        destination += 1;
    };
}


