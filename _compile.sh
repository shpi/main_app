#!/bin/bash

python3 -m nuitka main.py \
    --plugin-enable=numpy,pyside2 \
    --show-progress \
    --follow-imports \
    --plugin-enable=pylint-warnings \
    --nofollow-import-to=numpy # \
#    --file-reference-choice=runtime
