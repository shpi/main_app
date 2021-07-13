# developer repository for main_app

the actual main_app is not fully open source right now, but we will make anything
public to allow users to write their own modules asap.

the goal is to make it completely public, but this is only possible when funding of my SHPI GmbH
does not depend fully on my own private pocket. 

## QRC / QML

after changing qml files, please run:

pyside2-rcc files.qrc -o files.py --compress 9 --threshold 9



## Hint

please run "gcc keymap.c -o keymap" in keymap directory to get a valid binary.


## Compiling with Nuitka


python3 -m nuitka main.py   --plugin-enable=numpy,pyside2 --show-progress --follow-imports  --plugin-enable=pylint-warnings  --nofollow-import-to=numpy





