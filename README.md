

## QRC / QML

after changing qml files, please run:

pyside2-rcc files.qrc -o files.py --compress 9 --threshold 9



## Hint

please run "gcc keymap.c -o keymap" in keymap directory to get a valid binary.


## Compiling with Nuitka


python3 -m nuitka main.py   --plugin-enable=numpy,pyside2 --show-progress --follow-imports  --plugin-enable=pylint-warnings  --nofollow-import-to=numpy


## hwmon sensors

The application reads sensor values from the Linux *hwmon* subsystem.
Properties discovered from `/sys/class/hwmon` now provide better
descriptions based on the channel name or the optional `*_label` files.
Threshold attributes such as `*_max`, `*_crit` or `*_lcrit_alarm` are
recognised and described accordingly. Alarm, fault, beep and intrusion
files are detected too. Additionally the new `FREQUENCY` datatype and
power capping attributes are understood.





