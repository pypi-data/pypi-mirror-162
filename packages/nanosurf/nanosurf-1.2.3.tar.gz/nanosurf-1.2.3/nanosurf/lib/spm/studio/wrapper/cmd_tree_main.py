# studio_wrapper.py

from enum import Enum
from typing import Any
import nanosurf.lib.spm.studio.wrapper as wrap

g_cmd_tree_hash = '56454ac880b58ed1bd89cf5533b84f36'
g_compiler_version = '1.0'

class RootCoreCamera(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.camera'


class RootCoreHw_modules(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.hw_modules'


class RootCoreI2c(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.i2c'


class RootCoreVshi(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.vshi'


class RootCoreSpm_controller_discovery(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spm_controller_discovery'


class RootCoreStorage(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.storage'

    def close_file(self, *args) -> Any:
        return self._context.call('root.core.storage.close_file', *args)

    def is_file_open(self, *args) -> Any:
        return self._context.call('root.core.storage.is_file_open', *args)

    def open_file(self, *args) -> Any:
        return self._context.call('root.core.storage.open_file', *args)


class RootCoreScript_server(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.script_server'


class RootCore(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core'
        self.script_server = RootCoreScript_server(self._context)
        self.storage = RootCoreStorage(self._context)
        self.spm_controller_discovery = RootCoreSpm_controller_discovery(self._context)
        self.vshi = RootCoreVshi(self._context)
        self.i2c = RootCoreI2c(self._context)
        self.hw_modules = RootCoreHw_modules(self._context)
        self.camera = RootCoreCamera(self._context)


class RootTestTabel(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.test.tabel'


class RootTest(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.test'
        self.tabel = RootTestTabel(self._context)

    @property
    def bool(self) -> bool:
        return bool(self._context.get('root.test.bool'))

    @bool.setter
    def bool(self, new_val:bool):
        self._context.set('root.test.bool', bool(new_val))

    @property
    def num_f(self) -> float:
        return float(self._context.get('root.test.num_f'))

    @num_f.setter
    def num_f(self, new_val:float):
        self._context.set('root.test.num_f', float(new_val))

    @property
    def num_i(self) -> int:
        return int(self._context.get('root.test.num_i'))

    @num_i.setter
    def num_i(self, new_val:int):
        self._context.set('root.test.num_i', int(new_val))

    @property
    def str(self) -> str:
        return str(self._context.get('root.test.str'))

    @str.setter
    def str(self, new_val:str):
        self._context.set('root.test.str', str(new_val))

    def func(self, *args) -> Any:
        return self._context.call('root.test.func', *args)


class RootUtil(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.util'

    def make_property(self, *args) -> Any:
        return self._context.call('root.util.make_property', *args)

    def array_concat(self, *args) -> Any:
        return self._context.call('root.util.array_concat', *args)

    def deep_copy(self, *args) -> Any:
        return self._context.call('root.util.deep_copy', *args)

    def list_table_functions(self, *args) -> Any:
        return self._context.call('root.util.list_table_functions', *args)

    def list_table_tables(self, *args) -> Any:
        return self._context.call('root.util.list_table_tables', *args)

    def filter_string_array_begin(self, *args) -> Any:
        return self._context.call('root.util.filter_string_array_begin', *args)

    def list_table_elements(self, *args) -> Any:
        return self._context.call('root.util.list_table_elements', *args)

    def table_append(self, *args) -> Any:
        return self._context.call('root.util.table_append', *args)

    def to_string(self, *args) -> Any:
        return self._context.call('root.util.to_string', *args)

    def list_table_vars(self, *args) -> Any:
        return self._context.call('root.util.list_table_vars', *args)

    def list_table_all(self, *args) -> Any:
        return self._context.call('root.util.list_table_all', *args)


class RootWorkflowCamera(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.camera'


class RootWorkflowManager(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.manager'

    @property
    def session_name(self) -> str:
        return str(self._context.get('root.workflow.manager.session_name'))

    @session_name.setter
    def session_name(self, new_val:str):
        self._context.set('root.workflow.manager.session_name', str(new_val))


class RootWorkflowHardware_detection(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.hardware_detection'


class RootWorkflowCantilever_browser(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.cantilever_browser'


class RootWorkflow(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow'
        self.cantilever_browser = RootWorkflowCantilever_browser(self._context)
        self.hardware_detection = RootWorkflowHardware_detection(self._context)
        self.manager = RootWorkflowManager(self._context)
        self.camera = RootWorkflowCamera(self._context)


class RootSession(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.session'

    @property
    def current_connection(self) -> str:
        return str(self._context.get('root.session.current_connection'))

    @current_connection.setter
    def current_connection(self, new_val:str):
        self._context.set('root.session.current_connection', str(new_val))

    def select(self, *args) -> Any:
        return self._context.call('root.session.select', *args)

    def select_main(self, *args) -> Any:
        return self._context.call('root.session.select_main', *args)

    def list(self, *args) -> Any:
        return self._context.call('root.session.list', *args)

    @property
    def name(self) -> str:
        return str(self._context.get('root.session.name'))

    @name.setter
    def name(self, new_val:str):
        self._context.set('root.session.name', str(new_val))


class Root(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root'
        self.session = RootSession(self._context)
        self.workflow = RootWorkflow(self._context)
        self.util = RootUtil(self._context)
        self.test = RootTest(self._context)
        self.core = RootCore(self._context)

    @property
    def init_complete(self) -> bool:
        return bool(self._context.get('root.init_complete'))

    @init_complete.setter
    def init_complete(self, new_val:bool):
        self._context.set('root.init_complete', bool(new_val))

    def log_error(self, *args) -> Any:
        return self._context.call('root.log_error', *args)

    def log_fatal(self, *args) -> Any:
        return self._context.call('root.log_fatal', *args)

    def log_warn(self, *args) -> Any:
        return self._context.call('root.log_warn', *args)

    def log_debug(self, *args) -> Any:
        return self._context.call('root.log_debug', *args)

    def log_info(self, *args) -> Any:
        return self._context.call('root.log_info', *args)


