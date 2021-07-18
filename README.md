# developer repository for main_app

the actual main_app is not fully open source right now, but we will make anything public to allow users to write their own modules asap.

the goal is to make it completely public, but this is only possible when funding of my SHPI GmbH
does not depend fully on my own private pocket. 

## QRC / QML

after changing qml files, please run:

`./_create_resfile.py` (if qml files have been added or removed)  
`./_compile_res.sh`  (the actual compiling into qtres.py)

or just use the wrapper which calls both files above:  
`./_res.sh`


## Hint

please run "gcc keymap.c -o keymap" in keymap directory to get a valid binary.


## Compiling with Nuitka

python3 -m nuitka main.py   --plugin-enable=numpy,pyside2 --show-progress --follow-imports  --plugin-enable=pylint-warnings  --nofollow-import-to=numpy --file-reference-choice=runtime


## Command line
### Loglevel
Run with one of these arguments to set the loglevel: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`  

`WARNING` is default.

### Stack traces
Run with `STACKTRACE` to force stack_trace=True on each LogCall.

## Root privileges?
The mainapp does not require to run as root.

### Accessing /dev/input/event*
Put the user into group `input` or check the correct group name with `stat /dev/input/event0`.   
Then add the user to that group (and relogin): `sudo usermod -aG input pi`

### Wifi
TODO


## ToDos
- segfault analysis (qt problem)
- Property models for use in qml
- mqtt
