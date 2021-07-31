# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from html import escape

from core.Toolbox import KwReplace
from interfaces.PropertySystem import Property, SelectProperty, FunctionProperty, PropertyDict
from interfaces.DataTypes import DataType


_html_template_file = Path('properties_export.template.html')
_html_export_file = Path('properties_export.html')

if _html_template_file.is_file():
    _html_template = KwReplace(_html_template_file.read_text())
else:
    _html_template = KwReplace('{nested}')

_html_property = '\n{level}<li id="{id}" class="property"><p class="property">{nested}</p></li>'


def _export_prop(prop: Property, level=0):
    try:
        value = escape(str(prop.value))
    except Exception as e:
        value = '<span class="error">[' + escape(repr(e)) + ']</span>'

    value2 = ''
    loaded_status = '' if prop._loaded else ' <span class="error">NOT LOADED!</span>'

    if isinstance(prop, SelectProperty):
        value2 = '<br>\n' + ('  ' * level) + 'Allowed DataType: ' + ("All" if prop.expected_datatype is None else '<span class="datatype">' + escape(prop.expected_datatype.name) + '</span>')

        if prop.is_selected:
            value2 = '<br>\n' + _html_propertydict.format(level='  ' * (level+1), id='', name='Selected Property', nested=_export_prop(prop.selected_property, level=level+1))

    if isinstance(prop, FunctionProperty):
        value2 = '<br>\n' + ('  ' * level) + '<span class="function">' + escape(str(prop.func)) + '</span>, maxage=' + escape(str(prop.maxage))

    additional = '<br>\n' + ('  ' * level) + ('<span class="persistent">persistent</span>, ' if prop.is_persistent else '') + \
                 'default: <span class="value defaultvalue">' + \
                 escape(str(prop.default_value)) + '</span>' + value2 + '<br>\n' + ('  ' * level) + '<span class="datatype">' + escape(prop.datatype.name) + '</span> <span class="value">' + value + '</span>'

    nested = '<span class="propertyname">' + escape(str(prop.key)) + f'{loaded_status}</span> <span class="propid">id={prop.id}</span> ' \
             '<span class="classname">[' + escape(prop.__class__.__name__) + ']</span> ' \
             '<span class="path">\'' + escape(str(prop.path)) + '\'</span> ' \
             '<span class="desc">' + escape(str(prop.desc)) + '</span> ' + additional

    return _html_property.format(id='property_' + str(prop.id), nested=nested, level='  ' * level)


_html_propertydict = '{level}<li id="{id}"><span class="caret">{name}</span>\n' \
                     '{level}<ul class="nested">\n' \
                     '{nested}' \
                     '{level}</ul>\n' \
                     '{level}</li>'


def _export_pd(pd: PropertyDict, level=0) -> str:
    loaded_status = '' if pd._loaded else ' <span class="error">NOT LOADED!</span>'

    if pd.is_root:
        pd_id = 'root'
        name = f'<span class="propertydict root">ROOT{loaded_status}</span>'
    else:
        pd_id = 'property_' + str(pd.parentproperty.id)
        name = '<span class="propertydict">' + escape(pd.parentproperty.key) + f'{loaded_status}</span>'

    name += ' <span class="classname">[' + escape(pd.__class__.__name__) + ']</span> <span class="path">' + escape(str(pd.path)) + '</span>'

    if not pd.is_root:
        name += ' <span class="desc">' + escape(str(pd.parentproperty.desc)) + '</span>'

    pds = (prop.value for prop in pd.values() if prop.datatype is DataType.PROPERTYDICT)
    props = (prop for prop in pd.values() if prop.datatype is not DataType.PROPERTYDICT)

    nested = '\n'.join((_export_pd(pd_sub, level+1) for pd_sub in pds)) + \
             '\n'.join((_export_prop(prop, level+1) for prop in props))

    if 'PDPROPS' in sys.argv:
        pdprops = (prop for prop in pd.values() if prop.datatype is DataType.PROPERTYDICT)
        nested += '\n'.join((_export_prop(prop, level+1) for prop in pdprops))

    return _html_propertydict.format(id=pd_id, name=name, nested=nested, level='  ' * level)


def propertydict_to_html(pd: PropertyDict, dest: Path = None):
    data = _html_template.format(nested=_export_pd(pd))

    if dest is None:
        dest = _html_export_file

    dest.write_text(data)
