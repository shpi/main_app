from typing import Callable
from PySide2.QtCore import Property, __version_info__

"""
    # Perfect world as with Python's own 'property' (since 5.15.2):
    @Property(int, notify=nightmodeChanged)
    def function(self):
        getter_code

    @function.setter
    def function(self, value):
        setter_code


    # Setter layout until 5.15.1 (different function name required)
    @function.setter
    def set_function(self, value):
        setter_code


    # Fix for all versions
    def function(self):
        getter_code

    @Pre_5_15_2_fix(function, int, notify=nightmodeChanged)
    def function(self, value):
        setter_code


    Use this decorator only on setter functions which have the same name. Keep getter function undecorated.
    
    For read only properties just use regular @Property on getter as usual.
"""


def Pre_5_15_2_fix(type: type,
                   fget: Callable = None,
                   freset: Callable = None,
                   fdel: Callable = None,
                   doc='',
                   notify: Callable = None,
                   designable=True,
                   scriptable=True,
                   stored=True,
                   user=False,
                   constant=False,
                   final=False
                   ):
    """
    Use this decorator only on setter functions which have the same name.
    Keep getter function undecorated.

    For read only properties just use regular @Property on getter as usual.
    """

    def setter_fix(setter_func):
        if __version_info__ < (5, 15, 2):  # PySide2 < (5, 15, 2):
            # Function name MUST be DIFFERENT from getter's name
            # Create new function which has another name
            def dummy_function_with_other_name(*args, **kwargs):
                # Call setter function
                setter_func(*args, **kwargs)

            fset = dummy_function_with_other_name

        else:  # PySide2 >= (5, 15, 2)
            # Function name MUST be EQUAL to getter's name.
            # Passthrough original setter_func
            fset = setter_func

        # Create full Property in just one call!
        return Property(
            type=type,
            fget=fget,
            fset=fset,
            freset=freset,
            fdel=fdel,
            doc=doc,
            notify=notify,
            designable=designable,
            scriptable=scriptable,
            stored=stored,
            user=user,
            constant=constant,
            final=final
        )

    return setter_fix
