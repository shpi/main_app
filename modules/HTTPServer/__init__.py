# -*- coding: utf-8 -*-

from typing import Optional, Any
from logging import getLogger

from interfaces.DataTypes import DataType
from interfaces.Module import ThreadModuleBase
from interfaces.PropertySystem import Property, Input

logger = getLogger(__name__)


class HTTPServer(ThreadModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = "HTTP Server"
    categories = ()

    def __init__(self, parent, instancename: str = None):
        ThreadModuleBase.__init__(self, parent=parent, instancename=instancename)

        self._pr_bindaddr = Property(Input, DataType.STRING, '0.0.0.0', desc='Local servr bind address')
        self._pr_port = Property(Input, DataType.INTEGER, 8080, desc='Local server port')

        self.properties.update(
            bind_address=self._pr_bindaddr,
            port=self._pr_port,
        )

        self._server: Optional[Any] = None  # BaseWSGIServer

    @classmethod
    def available(cls) -> bool:
        ok = True

        try:
            from werkzeug.serving import make_server, BaseWSGIServer
        except ModuleNotFoundError:
            logger.warning('HTTPServer: Missing package "werkzeug"')
            ok = False

        try:
            from flask import Flask
        except ModuleNotFoundError:
            logger.warning('HTTPServer: Missing package "flask"')
            ok = False

        return ok

    def stop(self):
        self._server.shutdown()

    def load(self):
        from werkzeug.serving import make_server
        from modules.HTTPServer.App import app
        import modules.HTTPServer.PropertyExplorer
        self._server = make_server(self._pr_bindaddr.value, self._pr_port.value, app, threaded=True, passthrough_errors=True)
        self._server.allow_reuse_address = True

    def unload(self):
        self._server.server_close()
        self._server = None

    def run(self) -> None:
        self._server.serve_forever()


def runtest():
    _server = None
    try:
        from werkzeug.serving import make_server
        from modules.HTTPServer.App import app
        import modules.HTTPServer.PropertyExplorer
        _server = make_server('0.0.0.0', 8080, app, threaded=True, passthrough_errors=True)
        _server.allow_reuse_address = True
        _server.serve_forever()
        print("\nExiting...")
    except Exception as e:
        print("\nException: " + repr(e))
    finally:
        if _server:
            _server.server_close()
