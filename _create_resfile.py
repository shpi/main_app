#!/usr/bin/env python3

from pathlib import Path

file_template = '<!DOCTYPE RCC><RCC version="1.0">\n<qresource>\n{body}\n</qresource>\n</RCC>\n'
line_template = '<file>{filename}</file>'

source_defs =\
    'fonts/*',\
    'info/citylist.csv',\
    'weathersprites/*.png',\
    'modules/*.qml',\
    'qml/*.qml',\
    'qml/core/*.qml',\
    'qml/weather/*.qml',\
    'qml/info/*.qml',\
    'qml/ui/*.qml',\
    'qml/logic/*.qml',\
    'qml/connections/*.qml',\
    'qml/hardware/*.qml',\
    'qml/keyboard/*.qml',\
    'qml/thermostat/*.qml'

destfile = Path('qtres.qrc')


this_dir = Path()


def expand_globlist(globlist):
    for glob in globlist:
        for item in this_dir.glob(glob):
            if item.is_file():
                yield line_template.format(filename=str(item))


destfile.write_text(file_template.format(body='\n'.join(expand_globlist(source_defs))))
