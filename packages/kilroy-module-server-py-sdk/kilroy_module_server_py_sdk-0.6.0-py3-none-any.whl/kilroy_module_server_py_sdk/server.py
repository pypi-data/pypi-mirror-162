from kilroy_ws_server_py_sdk import Server

from kilroy_module_server_py_sdk.controller import ModuleController
from kilroy_module_server_py_sdk.module import Module


class ModuleServer(Server):
    def __init__(self, module: Module, *args, **kwargs) -> None:
        super().__init__(ModuleController(module), *args, **kwargs)
