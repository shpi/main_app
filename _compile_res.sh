#!/bin/bash
for cmd in pyside2-rcc ~/.local/bin/pyside2-rcc; do
    command -v $cmd > /dev/null && $cmd qtres.qrc -o qtres.py --compress 9 --threshold 9 && echo "Compiled with $cmd" && exit 0
done
