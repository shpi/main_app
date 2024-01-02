

## QRC / QML

after changing qml files, please run:

pyside2-rcc files.qrc -o files.py --compress 9 --threshold 9



## Hint

please run "gcc keymap.c -o keymap" in keymap directory to get a valid binary.


## Compiling with Nuitka


python3 -m nuitka main.py   --plugin-enable=numpy,pyside2 --show-progress --follow-imports  --plugin-enable=pylint-warnings  --nofollow-import-to=numpy





