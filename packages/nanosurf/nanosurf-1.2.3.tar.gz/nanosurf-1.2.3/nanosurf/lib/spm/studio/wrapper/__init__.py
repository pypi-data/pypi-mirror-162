# studio node base class.py

import os
import pathlib
import enum
import re
import lupa
from typing import Any
import hashlib
import importlib
import nanosurf.lib.datatypes.sci_val as sci_val

g_this_compiler_version = "1.0"
g_context_package_name_prefix = "cmd_tree_"
g_cmd_tree_root_name = "root"

class LuaType(enum.Enum):
    Nil = "nil"
    Table = "list"
    Float = "float"
    Int = "int"
    Str = "str"
    Bool = "bool"
    Function = "function"

def get_lua_type(obj) -> LuaType:
    """ Get the type of a lua object as LuaType enum """
    lua_type = lupa.lua_type(obj) if lupa.lua_type(obj) else type(obj)

    if lua_type == "function":
        return LuaType.Function
    elif lua_type == "table":
        return LuaType.Table
    elif lua_type == list:
        return LuaType.Table
    elif lua_type == str:
        return LuaType.Str
    elif lua_type == float:
        return LuaType.Float
    elif lua_type == int:
        return LuaType.Int
    elif lua_type == bool:
        return LuaType.Bool
    return LuaType.Nil

def get_lua_type_str(obj) -> str:
    """ Get the type of a lua object as string representation """
    # if argument is not already a LuaType, try to convert it
    if not(isinstance(obj, LuaType)):
        lua_type = get_lua_type(obj)
    else:
        lua_type = obj
    try:
        return lua_type.value
    except:
        pass
    return LuaType.Nil.value

class CmdTreeNode():
    def __init__(self):
        self._lua_tree_name = ""
        self._context : 'StudioScriptContext' = None
        
    def __getitem__(self, key):
        return self._context.get(f"{self._lua_tree_name}[{key}]")

    def __setitem__(self, key, value):
        return self._context.set(f"{self._lua_tree_name}[{key}]",value)

class CmdTreeProp(CmdTreeNode):
    def __init__(self):
        super().__init__()
        self._lua_value_type = LuaType.Nil

    def __repr__(self) -> str:
        if self._lua_value_type == LuaType.Float or self._lua_value_type == LuaType.Int:
            return sci_val.SciVal(self).to_string()
        return super().__repr__()

class CmdTreeCompiler():
    def __init__(self):
        self._file_content = [""]
        self._last_error = ""
        self.my_own_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
        self.regex_non_enum_chars = re.compile('[^0-9a-zA-Z]+', flags=re.UNICODE); 

    def build_wrapper_class(self, context_name: str, cmd_table) -> bool:
        self.cmd_package_name = g_context_package_name_prefix + context_name 

        # check if recompilation of command tree is necessary
        runtime_cmd_tree_hash = self.get_table_version(cmd_table, g_cmd_tree_root_name)
        compiled_cmd_tree_hash, compiled_compiler_version = self.get_compiled_versions()

        if (runtime_cmd_tree_hash != compiled_cmd_tree_hash) or (compiled_compiler_version != g_this_compiler_version):
            compiled_tree_file = self.my_own_path / (self.cmd_package_name + '.py')
            if self.compile_command_tree_to_file(cmd_table, runtime_cmd_tree_hash, compiled_tree_file, root_node_name=g_cmd_tree_root_name):
                # after compiling load the new generated wrapper
                mod = importlib.import_module("nanosurf.lib.spm.studio.wrapper."+self.cmd_package_name)
                importlib.reload(mod)
            else:
                self._last_error = f"Could not import dynamically created package from:\n{compiled_tree_file}"
                return False
        return True

    @property
    def last_error(self) -> str:
        return self._last_error

    def get_compiled_versions(self) -> tuple[str, str]:
        tree_hash = ""
        compiler_version = ""
        try:
            mod = importlib.import_module("nanosurf.lib.spm.studio.wrapper."+self.cmd_package_name)
            tree_hash = mod.g_cmd_tree_hash
            compiler_version = mod.g_compiler_version
        except:
            pass
        return (tree_hash, compiler_version)

    def get_table_version(self, table, lua_tree_name: str) -> str:
        hash_str = ""
        hash_str = self._get_table_hash_str(table, lua_tree_name)
        hash_str_sorted = ";".join(sorted(hash_str.split(";")))
        table_hash = hashlib.md5(bytes(hash_str_sorted, encoding='ascii'))
        return table_hash.hexdigest()

    def _get_table_hash_str(self, table, lua_tree_name: str) -> str:
        hash_str = lua_tree_name
        for item_name, item_value in table.items():
            item_type = get_lua_type(item_value) 
            if item_type == LuaType.Table:
                new_lua_tree_name = str(lua_tree_name+"."+item_name)
                hash_str += str(";" + self._get_table_hash_str(item_value, new_lua_tree_name))
            elif (item_type != LuaType.Nil) and type(item_name) == str:
                new_lua_tree_name = str(lua_tree_name+"."+item_name)
                hash_str += str(";" + new_lua_tree_name)
        return hash_str 

    def _has_table_functions(self, table) -> bool:
        for _, item_value in table.items():
            if get_lua_type(item_value) == LuaType.Function:
                return True
        return False

    def _is_property_access_func(self, func_name:str) -> bool:
        suffix = func_name[-4:]
        return (suffix == "_set") or (suffix == "_get")

    def _is_table_a_studio_property(self, table) -> bool:
        """ Detect if a lua table contains a studio property definition
        
        Implementation
        --------------
        This detection method is coupled with the studio lua script "make_property.lua"
        This script implements the metatable implementation to access variables.
        for each variable it create a pair of set/get function.
        """
        found_access_func = False
        found_value = False

        # search for key word
        for item_name, _ in table.items():
            if item_name == "value":
                found_value = True  
                break

        # if key word found check for accessor function
        if found_value:
            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if (item_type == LuaType.Function) and self._is_property_access_func(item_name):
                    found_access_func = True
                    break

        # if key value and accessor found, it is a property definition
        return found_access_func and found_value 

    def _is_enum_property(self, prop_elements:dict[str, str]) -> bool:
        return "enum" in prop_elements
        
    def _convert_enum_str_to_enum_class_name(self, enum_name:str) -> str:
        class_name = self.regex_non_enum_chars.sub('_', enum_name)
        return class_name

    def _get_studio_property_elements(self, prop_table) -> dict[str, str]:
        """ Extract from property style lua_table a list of all property names and their types
            returns a dict with key:name, val:type
        """
        property_elements: dict[str, str] = {}
        for item_name, item_value in prop_table.items():
            item_type = get_lua_type(item_value)
            if item_type != LuaType.Function:
                property_elements[item_name] = get_lua_type_str(item_type)
        return property_elements

    def compile_command_tree_to_file(self, studio_cmd_tree, table_version_hash: str, python_file: pathlib.Path, root_node_name:str) -> bool:
        done = False

        # create file content
        self._file_content = [""]
        self._write_cmd_tree_node(studio_cmd_tree, class_name=root_node_name.capitalize(), lua_tree_name=root_node_name)
        self.write_header(table_version_hash, g_this_compiler_version)

        # write content to file
        try:
            f =  open(python_file, "w")    
        except:
            self._last_error = "could not create file: '{python_file}'"
            return done
        
        try:
            for l in self._file_content:
                f.write(l)
            done = True
        except:
            self._last_error = "could not write to file: '{python_file}'"

        f.close()
        return done

    def create_pretty_print_command_table(self, table) -> str:
        self.dump = ""
        self._dump_command_table(table, indent="")
        return self.dump

    def _dump_command_table(self, table, indent:str) -> str:
        for item_name, item_value in table.items():
            item_type = get_lua_type(item_value)
            self.dump += f"{indent}{item_name}={get_lua_type_str(item_type)}"
            if item_type == LuaType.Table:
                self._dump_command_table(item_value, indent + "   "  )

    def write_header(self, table_version_hash: str, compiler_version: str):
        class_list = [] 
        class_list.append(f"# studio_wrapper.py\n")
        class_list.append(f"\n")
        class_list.append(f"from enum import Enum\n")
        class_list.append(f"from typing import Any\n")
        class_list.append(f"import nanosurf.lib.spm.studio.wrapper as wrap\n")
        class_list.append(f"\n")
        class_list.append(f"g_cmd_tree_hash = '{table_version_hash}'\n")
        class_list.append(f"g_compiler_version = '{compiler_version}'\n")
        class_list.append(f"\n")
        
        self._file_content = class_list + self._file_content

    def _write_cmd_tree_node(self, table, class_name:str, lua_tree_name: str) -> list[str]:
        class_list = []

        if self._is_table_a_studio_property(table):
            class_list.append(f"class {class_name}(wrap.CmdTreeProp):\n")
            prop_elements = self._get_studio_property_elements(table)

            is_prop_enum_type = self._is_enum_property(prop_elements)
            if is_prop_enum_type:
                enum_table = table["enum"]
                class_list.append("\n")
                class_list.append(f"    class EnumType(Enum):\n")
                for _, enum_name in enum_table.items():
                    class_list.append(f"        {self._convert_enum_str_to_enum_class_name(enum_name)} = '{enum_name}'\n")
                class_list.append("\n")

            class_list.append(f"    def __init__(self, context: 'StudioScriptContext'):\n")
            class_list.append(f"        super().__init__()\n")
            class_list.append(f"        self._context = context\n")
            class_list.append(f"        self._lua_tree_name = '{lua_tree_name}'\n")
            class_list.append(f"        self._lua_value_type = wrap.LuaType('{prop_elements['value']}')\n")
            class_list.append("\n")

            for value_name, value_type in prop_elements.items():
                if (value_name == "value") and is_prop_enum_type:
                    value_type = "EnumType"
                    class_list.append(f"    @property\n")
                    class_list.append(f"    def {value_name}(self) -> {value_type}:\n")
                    class_list.append(f"        return {class_name}.{value_type}(self._context.get('{lua_tree_name}.{value_name}'))\n")
                    class_list.append("\n")
                    class_list.append(f"    @{value_name}.setter\n")
                    class_list.append(f"    def {value_name}(self, new_val:{value_type}):\n")
                    class_list.append(f"        self._context.set('{lua_tree_name}.{value_name}', new_val.value)\n")
                    class_list.append("\n")
                else:
                    class_list.append(f"    @property\n")
                    class_list.append(f"    def {value_name}(self) -> {value_type}:\n")
                    class_list.append(f"        return {value_type}(self._context.get('{lua_tree_name}.{value_name}'))\n")
                    class_list.append("\n")
                    class_list.append(f"    @{value_name}.setter\n")
                    class_list.append(f"    def {value_name}(self, new_val:{value_type}):\n")
                    class_list.append(f"        self._context.set('{lua_tree_name}.{value_name}', {value_type}(new_val))\n")
                    class_list.append("\n")

            class_list.append("\n")

            self._file_content = class_list + self._file_content
        else:
            class_list.append(f"class {class_name}(wrap.CmdTreeNode):\n")
            class_list.append(f"    def __init__(self, context: 'StudioScriptContext'):\n")
            class_list.append(f"        super().__init__()\n")
            class_list.append(f"        self._context = context\n")
            class_list.append(f"        self._lua_tree_name = '{lua_tree_name}'\n")

            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if item_type == LuaType.Table:
                    class_list.append(f"        self.{item_name} = {class_name+item_name.capitalize()}(self._context)\n")
            class_list.append(f"\n")

            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if item_type == LuaType.Function:
                    if not(self._is_property_access_func(item_name)):
                        class_list.append(f"    def {item_name}(self, *args) -> Any:\n")
                        class_list.append(f"        return self._context.call('{lua_tree_name}.{item_name}', *args)\n")
                        class_list.append(f"\n")
                elif (item_type != LuaType.Nil) and (item_type != LuaType.Table) and type(item_name) == str:
                    type_str = get_lua_type_str(item_type)
                    class_list.append(f"    @property\n")
                    class_list.append(f"    def {item_name}(self) -> {type_str}:\n")
                    class_list.append(f"        return {type_str}(self._context.get('{lua_tree_name}.{item_name}'))\n")
                    class_list.append("\n")
                    class_list.append(f"    @{item_name}.setter\n")
                    class_list.append(f"    def {item_name}(self, new_val:{type_str}):\n")
                    class_list.append(f"        self._context.set('{lua_tree_name}.{item_name}', {type_str}(new_val))\n")
                    class_list.append("\n")        

            class_list.append("\n")

            # add new class on top of base classes
            self._file_content = class_list + self._file_content

            # follow cmd_tree nodes recursively
            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if item_type == LuaType.Table:
                    new_class_name = str(class_name+item_name.capitalize())
                    new_lua_tree_name = str(lua_tree_name+"."+item_name)
                    self._write_cmd_tree_node(item_value, new_class_name, new_lua_tree_name)


