"""Module for scripting the logical units of the low level scripting interface.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import nanosurf.lib.spm.lowlevel.ctrlunits.factory as ctrl_factory

class Lowlevel():
    ctrlunits = ctrl_factory._CtrlUnitFactory()

    """Contains the low-level interface classes."""
    def __init__(self, spm_ctrl_manager = None, lu_shared_file_path: str = ""):
        """Creates the objects of the low-level interface.

        Parameters
        ----------
        spm_ctrl_manager:
            COM object `application.SpmCtrlManager`

        lu_shared_file_path: str
            The file path of the file that describes the logical unit
            interface. (Usually `LogicalUnit_InterfaceShared.h`)
        """
        if spm_ctrl_manager is not None:
            self._logical_unit_com = spm_ctrl_manager.LogicalUnit
            self._create_data_buffer_interface(spm_ctrl_manager.DataBuffer)

            # Try to auto detect the LU Interface declaration
            if lu_shared_file_path == "":
                try:
                    # only v3.10.1 or newer has this property
                    lu_shared_file_path = self._logical_unit_com.GetInterfaceDescriptionFile
                except:
                    pass
            if lu_shared_file_path != "":
                self.create_logical_unit_interface(lu_shared_file_path)

    def _create_data_buffer_interface(self, data_buffer_com):
        import nanosurf.lib.spm.lowlevel.data_buffer_interface as nsf_data
        type_dict = {'_data_buffer_com': data_buffer_com}
        Interface = type(
            'DataBuffer', (nsf_data.DataBufferInterface,), type_dict)
        setattr(self, 'DataBuffer', Interface)

    def create_logical_unit_interface(self, lu_shared_file_path):
        import nanosurf.lib.spm.lowlevel.logical_unit_interface as lu
        import nanosurf.lib.spm.lowlevel.logical_unit_interface_parser as lu_parse
        
        type_items = lu_parse.ParseShared(
            lu_shared_file_path).lu_type_definitions.items()
        for type_name, type_definition in type_items:
            Interface = lu.logical_unit_type(
                    type_name, self._logical_unit_com, type_definition)
            setattr(self, type_name, Interface)


if __name__ == '__main__':
    import nanosurf.lib.spm.lowlevel.manager_mock

    lowlevel = Lowlevel(
        nanosurf.lib.spm.lowlevel.manager_mock.SPMCtrlManager(),
        r"..\..\test\LogicalUnit_InterfaceShared.h")
