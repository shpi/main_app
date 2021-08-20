# -*- coding: utf-8 -*-

from modules.HTTPServer.App import app
from html import escape
from interfaces.PropertySystem import Property, PropertyDict


@app.route("/properties")
def properties():
    return ""


@app.route("/property/<int:pid>")
def view_property_by_id(pid: int):
    prop = Property.get_by_id(pid)
    if prop is None:
        return "Property not found"
    return view_property(prop)


@app.route("/property/<path:path>")
def view_property_by_path(path: str):
    prop = PropertyDict._root_instance.get(path)
    if prop is None:
        return "Property not found"
    return view_property(prop)


def view_property(p: Property):
    return escape(str(p.value))
