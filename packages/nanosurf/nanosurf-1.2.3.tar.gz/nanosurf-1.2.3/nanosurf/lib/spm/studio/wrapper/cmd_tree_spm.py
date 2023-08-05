# studio_wrapper.py

from enum import Enum
from typing import Any
import nanosurf.lib.spm.studio.wrapper as wrap

g_cmd_tree_hash = '3d52492f98ec6d6572f7a81dad22a138'
g_compiler_version = '1.0'

class RootLu(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.lu'


class RootUtil(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.util'

    def list_table_functions(self, *args) -> Any:
        return self._context.call('root.util.list_table_functions', *args)

    def list_table_all(self, *args) -> Any:
        return self._context.call('root.util.list_table_all', *args)

    def list_table_vars(self, *args) -> Any:
        return self._context.call('root.util.list_table_vars', *args)

    def deep_copy(self, *args) -> Any:
        return self._context.call('root.util.deep_copy', *args)

    def array_concat(self, *args) -> Any:
        return self._context.call('root.util.array_concat', *args)

    def list_table_elements(self, *args) -> Any:
        return self._context.call('root.util.list_table_elements', *args)

    def list_table_tables(self, *args) -> Any:
        return self._context.call('root.util.list_table_tables', *args)

    def table_append(self, *args) -> Any:
        return self._context.call('root.util.table_append', *args)

    def make_property(self, *args) -> Any:
        return self._context.call('root.util.make_property', *args)

    def filter_string_array_begin(self, *args) -> Any:
        return self._context.call('root.util.filter_string_array_begin', *args)

    def to_string(self, *args) -> Any:
        return self._context.call('root.util.to_string', *args)


class RootWorkflowCamera_properties(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.camera_properties'


class RootWorkflowFrequency_sweep(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.frequency_sweep'


class RootWorkflowApproach_motorsSignalMotor_move_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.signal.motor_move_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_finished.connect', *args)


class RootWorkflowApproach_motorsSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.procedure_info.connect', *args)


class RootWorkflowApproach_motorsSignalMotor_move_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.signal.motor_move_started'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.signal.motor_move_started.connect', *args)


class RootWorkflowApproach_motorsSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.signal'
        self.motor_move_started = RootWorkflowApproach_motorsSignalMotor_move_started(self._context)
        self.procedure_info = RootWorkflowApproach_motorsSignalProcedure_info(self._context)
        self.motor_move_finished = RootWorkflowApproach_motorsSignalMotor_move_finished(self._context)


class RootWorkflowApproach_motorsPropertyMotor_step(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.motor_step'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.motor_step.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.motor_step.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.approach_motors.property.motor_step.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.approach_motors.property.motor_step.value', float(new_val))


class RootWorkflowApproach_motorsPropertyMotor_left_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.motor_left_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.motor_left_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.motor_left_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach_motors.property.motor_left_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach_motors.property.motor_left_position.value', int(new_val))


class RootWorkflowApproach_motorsPropertyMotor_right_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.motor_right_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.motor_right_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.motor_right_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach_motors.property.motor_right_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach_motors.property.motor_right_position.value', int(new_val))


class RootWorkflowApproach_motorsPropertyMotor_speed_approach_motors(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.motor_speed_approach_motors'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.motor_speed_approach_motors.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.motor_speed_approach_motors.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.approach_motors.property.motor_speed_approach_motors.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.approach_motors.property.motor_speed_approach_motors.value', float(new_val))


class RootWorkflowApproach_motorsPropertyRelative_tip_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.relative_tip_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.relative_tip_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.relative_tip_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach_motors.property.relative_tip_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach_motors.property.relative_tip_position.value', int(new_val))


class RootWorkflowApproach_motorsPropertyMotor_speed_advance_retract(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.motor_speed_advance_retract'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.motor_speed_advance_retract.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.motor_speed_advance_retract.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.approach_motors.property.motor_speed_advance_retract.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.approach_motors.property.motor_speed_advance_retract.value', float(new_val))


class RootWorkflowApproach_motorsPropertyMotor_front_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.motor_front_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.motor_front_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.motor_front_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach_motors.property.motor_front_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach_motors.property.motor_front_position.value', int(new_val))


class RootWorkflowApproach_motorsPropertyMotor_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property.motor_speed'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach_motors.property.motor_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach_motors.property.motor_speed.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.approach_motors.property.motor_speed.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.approach_motors.property.motor_speed.value', float(new_val))


class RootWorkflowApproach_motorsProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors.property'
        self.motor_speed = RootWorkflowApproach_motorsPropertyMotor_speed(self._context)
        self.motor_front_position = RootWorkflowApproach_motorsPropertyMotor_front_position(self._context)
        self.motor_speed_advance_retract = RootWorkflowApproach_motorsPropertyMotor_speed_advance_retract(self._context)
        self.relative_tip_position = RootWorkflowApproach_motorsPropertyRelative_tip_position(self._context)
        self.motor_speed_approach_motors = RootWorkflowApproach_motorsPropertyMotor_speed_approach_motors(self._context)
        self.motor_right_position = RootWorkflowApproach_motorsPropertyMotor_right_position(self._context)
        self.motor_left_position = RootWorkflowApproach_motorsPropertyMotor_left_position(self._context)
        self.motor_step = RootWorkflowApproach_motorsPropertyMotor_step(self._context)


class RootWorkflowApproach_motors(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors'
        self.property = RootWorkflowApproach_motorsProperty(self._context)
        self.signal = RootWorkflowApproach_motorsSignal(self._context)

    def stop_motors(self, *args) -> Any:
        return self._context.call('root.workflow.approach_motors.stop_motors', *args)


class RootWorkflowParameters(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.parameters'


class RootWorkflowPreset_loader(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.preset_loader'


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


class RootWorkflowOrtSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.procedure_info.connect', *args)


class RootWorkflowOrtSignalChanging_excitation_done(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.signal.changing_excitation_done'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation_done.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation_done.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation_done.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation_done.connect', *args)


class RootWorkflowOrtSignalUpdating_free_wave(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.signal.updating_free_wave'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave.connect', *args)


class RootWorkflowOrtSignalChanging_excitation(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.signal.changing_excitation'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.changing_excitation.connect', *args)


class RootWorkflowOrtSignalOscilloscope_data(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.signal.oscilloscope_data'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.oscilloscope_data.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.oscilloscope_data.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.oscilloscope_data.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.oscilloscope_data.connect', *args)


class RootWorkflowOrtSignalUpdating_free_wave_done(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.signal.updating_free_wave_done'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave_done.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave_done.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave_done.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.ort.signal.updating_free_wave_done.connect', *args)


class RootWorkflowOrtSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.signal'
        self.updating_free_wave_done = RootWorkflowOrtSignalUpdating_free_wave_done(self._context)
        self.oscilloscope_data = RootWorkflowOrtSignalOscilloscope_data(self._context)
        self.changing_excitation = RootWorkflowOrtSignalChanging_excitation(self._context)
        self.updating_free_wave = RootWorkflowOrtSignalUpdating_free_wave(self._context)
        self.changing_excitation_done = RootWorkflowOrtSignalChanging_excitation_done(self._context)
        self.procedure_info = RootWorkflowOrtSignalProcedure_info(self._context)


class RootWorkflowOrtPropertyBaseline_window_begin(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.baseline_window_begin'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.ort.property.baseline_window_begin.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.ort.property.baseline_window_begin.value', float(new_val))


class RootWorkflowOrtPropertySamples_per_period(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.samples_per_period'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.samples_per_period.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.samples_per_period.value', int(new_val))


class RootWorkflowOrtPropertyWave_frequency(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.wave_frequency'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.wave_frequency.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.wave_frequency.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.wave_frequency.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.wave_frequency.value', int(new_val))


class RootWorkflowOrtPropertyAdhesion_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.adhesion_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.adhesion_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.adhesion_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.adhesion_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.adhesion_value.value', int(new_val))


class RootWorkflowOrtPropertyBaseline_controller_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.baseline_controller_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.workflow.ort.property.baseline_controller_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.workflow.ort.property.baseline_controller_enabled.value', bool(new_val))


class RootWorkflowOrtPropertyAmplitude_reduction(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.amplitude_reduction'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.amplitude_reduction.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.amplitude_reduction.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.amplitude_reduction.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.amplitude_reduction.value', int(new_val))


class RootWorkflowOrtPropertyInput_select(wrap.CmdTreeProp):

    class EnumType(Enum):
        Fast_In_Deflection = 'Fast In Deflection'
        Hi_Res_In_Deflection = 'Hi Res In Deflection'
        Fast_In_User = 'Fast In User'
        Hi_Res_In_User1 = 'Hi Res In User1'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.input_select'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.ort.property.input_select.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.ort.property.input_select.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowOrtPropertyInput_select.EnumType(self._context.get('root.workflow.ort.property.input_select.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.ort.property.input_select.value', new_val.value)


class RootWorkflowOrtPropertyFree_wave_delay(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.free_wave_delay'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.free_wave_delay.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.free_wave_delay.value', int(new_val))


class RootWorkflowOrtPropertyCantilever_samples_per_period(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.cantilever_samples_per_period'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.cantilever_samples_per_period.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.cantilever_samples_per_period.value', int(new_val))


class RootWorkflowOrtPropertyLift_height(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.lift_height'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.lift_height.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.lift_height.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.ort.property.lift_height.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.ort.property.lift_height.value', float(new_val))


class RootWorkflowOrtPropertyBaseline_amplitude(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.baseline_amplitude'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.baseline_amplitude.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.baseline_amplitude.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.baseline_amplitude.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.baseline_amplitude.value', int(new_val))


class RootWorkflowOrtPropertyExcitation_amplitude(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.excitation_amplitude'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.excitation_amplitude.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.excitation_amplitude.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.ort.property.excitation_amplitude.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.ort.property.excitation_amplitude.value', float(new_val))


class RootWorkflowOrtPropertyBaseline_frequency(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.baseline_frequency'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.baseline_frequency.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.baseline_frequency.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.baseline_frequency.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.baseline_frequency.value', int(new_val))


class RootWorkflowOrtPropertyBaseline_window_end(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.baseline_window_end'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.baseline_window_end.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.baseline_window_end.value', int(new_val))


class RootWorkflowOrtPropertyAverage_periods(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.average_periods'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.average_periods.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.average_periods.value', int(new_val))


class RootWorkflowOrtPropertyBaseline_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.baseline_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.baseline_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.baseline_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.baseline_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.baseline_value.value', int(new_val))


class RootWorkflowOrtPropertyWave_amplitude(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.wave_amplitude'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.ort.property.wave_amplitude.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.ort.property.wave_amplitude.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.wave_amplitude.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.wave_amplitude.value', int(new_val))


class RootWorkflowOrtPropertyFeedback_amplitude_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.feedback_amplitude_position'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.ort.property.feedback_amplitude_position.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.ort.property.feedback_amplitude_position.value', float(new_val))


class RootWorkflowOrtPropertyAdhesion_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property.adhesion_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.ort.property.adhesion_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.ort.property.adhesion_position.value', int(new_val))


class RootWorkflowOrtProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort.property'
        self.adhesion_position = RootWorkflowOrtPropertyAdhesion_position(self._context)
        self.feedback_amplitude_position = RootWorkflowOrtPropertyFeedback_amplitude_position(self._context)
        self.wave_amplitude = RootWorkflowOrtPropertyWave_amplitude(self._context)
        self.baseline_value = RootWorkflowOrtPropertyBaseline_value(self._context)
        self.average_periods = RootWorkflowOrtPropertyAverage_periods(self._context)
        self.baseline_window_end = RootWorkflowOrtPropertyBaseline_window_end(self._context)
        self.baseline_frequency = RootWorkflowOrtPropertyBaseline_frequency(self._context)
        self.excitation_amplitude = RootWorkflowOrtPropertyExcitation_amplitude(self._context)
        self.baseline_amplitude = RootWorkflowOrtPropertyBaseline_amplitude(self._context)
        self.lift_height = RootWorkflowOrtPropertyLift_height(self._context)
        self.cantilever_samples_per_period = RootWorkflowOrtPropertyCantilever_samples_per_period(self._context)
        self.free_wave_delay = RootWorkflowOrtPropertyFree_wave_delay(self._context)
        self.input_select = RootWorkflowOrtPropertyInput_select(self._context)
        self.amplitude_reduction = RootWorkflowOrtPropertyAmplitude_reduction(self._context)
        self.baseline_controller_enabled = RootWorkflowOrtPropertyBaseline_controller_enabled(self._context)
        self.adhesion_value = RootWorkflowOrtPropertyAdhesion_value(self._context)
        self.wave_frequency = RootWorkflowOrtPropertyWave_frequency(self._context)
        self.samples_per_period = RootWorkflowOrtPropertySamples_per_period(self._context)
        self.baseline_window_begin = RootWorkflowOrtPropertyBaseline_window_begin(self._context)


class RootWorkflowOrt(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort'
        self.property = RootWorkflowOrtProperty(self._context)
        self.signal = RootWorkflowOrtSignal(self._context)

    def update_free_wave(self, *args) -> Any:
        return self._context.call('root.workflow.ort.update_free_wave', *args)

    def update_excitation(self, *args) -> Any:
        return self._context.call('root.workflow.ort.update_excitation', *args)

    def wait_for_async_sm_tasks_to_finish(self, *args) -> Any:
        return self._context.call('root.workflow.ort.wait_for_async_sm_tasks_to_finish', *args)


class RootWorkflowStorageSignalMeasurement_image_opened(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.signal.measurement_image_opened'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.measurement_image_opened.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.measurement_image_opened.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.measurement_image_opened.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.measurement_image_opened.connect', *args)


class RootWorkflowStorageSignalCurrent_measurement_image_changed(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.signal.current_measurement_image_changed'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.current_measurement_image_changed.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.current_measurement_image_changed.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.current_measurement_image_changed.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.storage.signal.current_measurement_image_changed.connect', *args)


class RootWorkflowStorageSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.signal'
        self.current_measurement_image_changed = RootWorkflowStorageSignalCurrent_measurement_image_changed(self._context)
        self.measurement_image_opened = RootWorkflowStorageSignalMeasurement_image_opened(self._context)


class RootWorkflowStoragePropertyGwy_auto_store_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Off = 'Off'
        Store_to_file = 'Store to file'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property.gwy_auto_store_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.storage.property.gwy_auto_store_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.storage.property.gwy_auto_store_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowStoragePropertyGwy_auto_store_mode.EnumType(self._context.get('root.workflow.storage.property.gwy_auto_store_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.storage.property.gwy_auto_store_mode.value', new_val.value)


class RootWorkflowStoragePropertyName_pattern(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property.name_pattern'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def value(self) -> str:
        return str(self._context.get('root.workflow.storage.property.name_pattern.value'))

    @value.setter
    def value(self, new_val:str):
        self._context.set('root.workflow.storage.property.name_pattern.value', str(new_val))


class RootWorkflowStoragePropertyNidx_auto_store_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Off = 'Off'
        New_File = 'New File'
        Current_File = 'Current File'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property.nidx_auto_store_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.storage.property.nidx_auto_store_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.storage.property.nidx_auto_store_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowStoragePropertyNidx_auto_store_mode.EnumType(self._context.get('root.workflow.storage.property.nidx_auto_store_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.storage.property.nidx_auto_store_mode.value', new_val.value)


class RootWorkflowStoragePropertyGallery_directory(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property.gallery_directory'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def value(self) -> str:
        return str(self._context.get('root.workflow.storage.property.gallery_directory.value'))

    @value.setter
    def value(self, new_val:str):
        self._context.set('root.workflow.storage.property.gallery_directory.value', str(new_val))


class RootWorkflowStoragePropertyGwy_backend_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property.gwy_backend_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.workflow.storage.property.gwy_backend_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.workflow.storage.property.gwy_backend_enabled.value', bool(new_val))


class RootWorkflowStoragePropertyNidx_backend_enabled_(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property.nidx_backend_enabled_'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.workflow.storage.property.nidx_backend_enabled_.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.workflow.storage.property.nidx_backend_enabled_.value', bool(new_val))


class RootWorkflowStoragePropertyAuto_save_partial_measurements(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property.auto_save_partial_measurements'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.workflow.storage.property.auto_save_partial_measurements.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.workflow.storage.property.auto_save_partial_measurements.value', bool(new_val))


class RootWorkflowStorageProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage.property'
        self.auto_save_partial_measurements = RootWorkflowStoragePropertyAuto_save_partial_measurements(self._context)
        self.nidx_backend_enabled_ = RootWorkflowStoragePropertyNidx_backend_enabled_(self._context)
        self.gwy_backend_enabled = RootWorkflowStoragePropertyGwy_backend_enabled(self._context)
        self.gallery_directory = RootWorkflowStoragePropertyGallery_directory(self._context)
        self.nidx_auto_store_mode = RootWorkflowStoragePropertyNidx_auto_store_mode(self._context)
        self.name_pattern = RootWorkflowStoragePropertyName_pattern(self._context)
        self.gwy_auto_store_mode = RootWorkflowStoragePropertyGwy_auto_store_mode(self._context)


class RootWorkflowStorage(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage'
        self.property = RootWorkflowStorageProperty(self._context)
        self.signal = RootWorkflowStorageSignal(self._context)

    def close_file(self, *args) -> Any:
        return self._context.call('root.workflow.storage.close_file', *args)

    def create_measurement(self, *args) -> Any:
        return self._context.call('root.workflow.storage.create_measurement', *args)

    def open_file(self, *args) -> Any:
        return self._context.call('root.workflow.storage.open_file', *args)


class RootWorkflowSystem_startup(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.system_startup'


class RootWorkflowWorkflow_spectroscopy_setupSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.workflow_spectroscopy_setup.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.workflow_spectroscopy_setup.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.workflow_spectroscopy_setup.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.workflow_spectroscopy_setup.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.workflow_spectroscopy_setup.signal.procedure_info.connect', *args)


class RootWorkflowWorkflow_spectroscopy_setupSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.workflow_spectroscopy_setup.signal'
        self.procedure_info = RootWorkflowWorkflow_spectroscopy_setupSignalProcedure_info(self._context)


class RootWorkflowWorkflow_spectroscopy_setup(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.workflow_spectroscopy_setup'
        self.signal = RootWorkflowWorkflow_spectroscopy_setupSignal(self._context)

    def add_new_segment(self, *args) -> Any:
        return self._context.call('root.workflow.workflow_spectroscopy_setup.add_new_segment', *args)

    def create_stress_relaxation_experiment(self, *args) -> Any:
        return self._context.call('root.workflow.workflow_spectroscopy_setup.create_stress_relaxation_experiment', *args)

    def create_f_d_curve_experiment(self, *args) -> Any:
        return self._context.call('root.workflow.workflow_spectroscopy_setup.create_f_d_curve_experiment', *args)


class RootWorkflowThermal_tuneSignalNew_average(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.new_average'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_average.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_average.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_average.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_average.connect', *args)


class RootWorkflowThermal_tuneSignalNew_fit(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.new_fit'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_fit.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_fit.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_fit.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_fit.connect', *args)


class RootWorkflowThermal_tuneSignalNew_calibration_data(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.new_calibration_data'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_calibration_data.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_calibration_data.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_calibration_data.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_calibration_data.connect', *args)


class RootWorkflowThermal_tuneSignalNew_frequency_list(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.new_frequency_list'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_frequency_list.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_frequency_list.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_frequency_list.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.new_frequency_list.connect', *args)


class RootWorkflowThermal_tuneSignalProgress(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.progress'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.progress.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.progress.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.progress.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.progress.connect', *args)


class RootWorkflowThermal_tuneSignalStarted(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.started'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.started.connect', *args)


class RootWorkflowThermal_tuneSignalCurrent_calibration_changed(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.current_calibration_changed'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.current_calibration_changed.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.current_calibration_changed.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.current_calibration_changed.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.current_calibration_changed.connect', *args)


class RootWorkflowThermal_tuneSignalEnded(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.ended'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.ended.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.ended.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.ended.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.ended.connect', *args)


class RootWorkflowThermal_tuneSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.signal.procedure_info.connect', *args)


class RootWorkflowThermal_tuneSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.signal'
        self.procedure_info = RootWorkflowThermal_tuneSignalProcedure_info(self._context)
        self.ended = RootWorkflowThermal_tuneSignalEnded(self._context)
        self.current_calibration_changed = RootWorkflowThermal_tuneSignalCurrent_calibration_changed(self._context)
        self.started = RootWorkflowThermal_tuneSignalStarted(self._context)
        self.progress = RootWorkflowThermal_tuneSignalProgress(self._context)
        self.new_frequency_list = RootWorkflowThermal_tuneSignalNew_frequency_list(self._context)
        self.new_calibration_data = RootWorkflowThermal_tuneSignalNew_calibration_data(self._context)
        self.new_fit = RootWorkflowThermal_tuneSignalNew_fit(self._context)
        self.new_average = RootWorkflowThermal_tuneSignalNew_average(self._context)


class RootWorkflowThermal_tunePropertyMax_frequency(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property.max_frequency'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.thermal_tune.property.max_frequency.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.thermal_tune.property.max_frequency.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.thermal_tune.property.max_frequency.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.thermal_tune.property.max_frequency.value', int(new_val))


class RootWorkflowThermal_tunePropertyIterations(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property.iterations'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.thermal_tune.property.iterations.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.thermal_tune.property.iterations.value', int(new_val))


class RootWorkflowThermal_tunePropertyFit_frequency_lower_bound(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property.fit_frequency_lower_bound'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.thermal_tune.property.fit_frequency_lower_bound.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.thermal_tune.property.fit_frequency_lower_bound.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.thermal_tune.property.fit_frequency_lower_bound.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.thermal_tune.property.fit_frequency_lower_bound.value', int(new_val))


class RootWorkflowThermal_tunePropertyFit_frequency_upper_bound(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property.fit_frequency_upper_bound'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.thermal_tune.property.fit_frequency_upper_bound.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.thermal_tune.property.fit_frequency_upper_bound.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.thermal_tune.property.fit_frequency_upper_bound.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.thermal_tune.property.fit_frequency_upper_bound.value', int(new_val))


class RootWorkflowThermal_tunePropertyMeasurement_environment(wrap.CmdTreeProp):

    class EnumType(Enum):
        Air = 'Air'
        Liquid = 'Liquid'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property.measurement_environment'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.thermal_tune.property.measurement_environment.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.thermal_tune.property.measurement_environment.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowThermal_tunePropertyMeasurement_environment.EnumType(self._context.get('root.workflow.thermal_tune.property.measurement_environment.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.thermal_tune.property.measurement_environment.value', new_val.value)


class RootWorkflowThermal_tunePropertyResolution(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property.resolution'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.thermal_tune.property.resolution.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.thermal_tune.property.resolution.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.thermal_tune.property.resolution.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.thermal_tune.property.resolution.value', int(new_val))


class RootWorkflowThermal_tunePropertyTemperature(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property.temperature'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.thermal_tune.property.temperature.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.thermal_tune.property.temperature.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.thermal_tune.property.temperature.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.thermal_tune.property.temperature.value', int(new_val))


class RootWorkflowThermal_tuneProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune.property'
        self.temperature = RootWorkflowThermal_tunePropertyTemperature(self._context)
        self.resolution = RootWorkflowThermal_tunePropertyResolution(self._context)
        self.measurement_environment = RootWorkflowThermal_tunePropertyMeasurement_environment(self._context)
        self.fit_frequency_upper_bound = RootWorkflowThermal_tunePropertyFit_frequency_upper_bound(self._context)
        self.fit_frequency_lower_bound = RootWorkflowThermal_tunePropertyFit_frequency_lower_bound(self._context)
        self.iterations = RootWorkflowThermal_tunePropertyIterations(self._context)
        self.max_frequency = RootWorkflowThermal_tunePropertyMax_frequency(self._context)


class RootWorkflowThermal_tune(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune'
        self.property = RootWorkflowThermal_tuneProperty(self._context)
        self.signal = RootWorkflowThermal_tuneSignal(self._context)

    def wait_for_async_tasks_to_finish(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.wait_for_async_tasks_to_finish', *args)

    def apply(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.apply', *args)

    def current_calibration(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.current_calibration', *args)

    def refit(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.refit', *args)

    def start(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.start', *args)

    def abort(self, *args) -> Any:
        return self._context.call('root.workflow.thermal_tune.abort', *args)


class RootWorkflowSpm_resource_requester(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.spm_resource_requester'


class RootWorkflowWorkspace(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.workspace'

    def item_name_exists(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.item_name_exists', *args)

    def get_item_name(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.get_item_name', *args)

    def item_exists(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.item_exists', *args)

    def delete_all_items(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.delete_all_items', *args)

    def set_item_size(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.set_item_size', *args)

    def set_item_rotation(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.set_item_rotation', *args)

    def active_item_id(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.active_item_id', *args)

    def selected_item_id(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.selected_item_id', *args)

    def item_id_by_name(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.item_id_by_name', *args)

    def add_grid(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.add_grid', *args)

    def set_item_visible(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.set_item_visible', *args)

    def all_item_ids_in_layer(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.all_item_ids_in_layer', *args)

    def item_count(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.item_count', *args)

    def set_item_name(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.set_item_name', *args)

    def set_item_resolution(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.set_item_resolution', *args)

    def set_item_position(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.set_item_position', *args)

    def all_item_ids(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.all_item_ids', *args)

    def delete_item(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.delete_item', *args)

    def default_afm_item_id(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.default_afm_item_id', *args)

    def set_item_transparency(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.set_item_transparency', *args)

    def add_point(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.add_point', *args)

    def add_frame(self, *args) -> Any:
        return self._context.call('root.workflow.workspace.add_frame', *args)


class RootWorkflowXy_closed_loop(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.xy_closed_loop'


class RootWorkflowLaser_alignSignalMotor_move_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.signal.motor_move_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_finished.connect', *args)


class RootWorkflowLaser_alignSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.procedure_info.connect', *args)


class RootWorkflowLaser_alignSignalMotor_move_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.signal.motor_move_started'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.signal.motor_move_started.connect', *args)


class RootWorkflowLaser_alignSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.signal'
        self.motor_move_started = RootWorkflowLaser_alignSignalMotor_move_started(self._context)
        self.procedure_info = RootWorkflowLaser_alignSignalProcedure_info(self._context)
        self.motor_move_finished = RootWorkflowLaser_alignSignalMotor_move_finished(self._context)


class RootWorkflowLaser_alignPropertyMotor_step(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_step'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_step.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_step.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.laser_align.property.motor_step.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.laser_align.property.motor_step.value', float(new_val))


class RootWorkflowLaser_alignPropertyMotor_beam_shifter_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_beam_shifter_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_beam_shifter_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_beam_shifter_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_beam_shifter_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_beam_shifter_position.value', int(new_val))


class RootWorkflowLaser_alignPropertyUpdate_detector_rate(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.update_detector_rate'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.update_detector_rate.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.update_detector_rate.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.update_detector_rate.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.update_detector_rate.value', int(new_val))


class RootWorkflowLaser_alignPropertyLaser_clean_drive_power(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.laser_clean_drive_power'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.laser_clean_drive_power.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.laser_clean_drive_power.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.laser_align.property.laser_clean_drive_power.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.laser_align.property.laser_clean_drive_power.value', float(new_val))


class RootWorkflowLaser_alignPropertyMotor_speed_max_laser_motors(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_speed_max_laser_motors'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_speed_max_laser_motors.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_speed_max_laser_motors.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_speed_max_laser_motors.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_speed_max_laser_motors.value', int(new_val))


class RootWorkflowLaser_alignPropertyMotor_speed_laser_motors(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_speed_laser_motors'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_speed_laser_motors.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_speed_laser_motors.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.laser_align.property.motor_speed_laser_motors.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.laser_align.property.motor_speed_laser_motors.value', float(new_val))


class RootWorkflowLaser_alignPropertyDeflection_lateral(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.deflection_lateral'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.deflection_lateral.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.deflection_lateral.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.deflection_lateral.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.deflection_lateral.value', int(new_val))


class RootWorkflowLaser_alignPropertyLaser_readout_power(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.laser_readout_power'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.laser_readout_power.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.laser_readout_power.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.laser_align.property.laser_readout_power.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.laser_align.property.laser_readout_power.value', float(new_val))


class RootWorkflowLaser_alignPropertyScan_mode(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.scan_mode'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.workflow.laser_align.property.scan_mode.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.workflow.laser_align.property.scan_mode.value', bool(new_val))


class RootWorkflowLaser_alignPropertySensor_status(wrap.CmdTreeProp):

    class EnumType(Enum):
        Undefined = 'Undefined'
        Low = 'Low'
        Ok = 'Ok'
        High = 'High'
        Fail = 'Fail'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.sensor_status'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.laser_align.property.sensor_status.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.laser_align.property.sensor_status.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowLaser_alignPropertySensor_status.EnumType(self._context.get('root.workflow.laser_align.property.sensor_status.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.laser_align.property.sensor_status.value', new_val.value)


class RootWorkflowLaser_alignPropertyMotor_laser_focus_z_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_laser_focus_z_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_laser_focus_z_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_laser_focus_z_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_laser_focus_z_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_laser_focus_z_position.value', int(new_val))


class RootWorkflowLaser_alignPropertyMotor_laser_clean_drive_x_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_laser_clean_drive_x_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_laser_clean_drive_x_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_laser_clean_drive_x_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_laser_clean_drive_x_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_laser_clean_drive_x_position.value', int(new_val))


class RootWorkflowLaser_alignPropertyLaser_spot_intensity(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.laser_spot_intensity'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.laser_spot_intensity.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.laser_spot_intensity.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.laser_spot_intensity.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.laser_spot_intensity.value', int(new_val))


class RootWorkflowLaser_alignPropertyMotor_laser_photodetector_x_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_laser_photodetector_x_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_laser_photodetector_x_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_laser_photodetector_x_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_laser_photodetector_x_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_laser_photodetector_x_position.value', int(new_val))


class RootWorkflowLaser_alignPropertyLaser_clean_drive_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.laser_clean_drive_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.workflow.laser_align.property.laser_clean_drive_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.workflow.laser_align.property.laser_clean_drive_enabled.value', bool(new_val))


class RootWorkflowLaser_alignPropertyDeflection_normal(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.deflection_normal'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.deflection_normal.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.deflection_normal.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.deflection_normal.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.deflection_normal.value', int(new_val))


class RootWorkflowLaser_alignPropertyMotor_laser_photodetector_y_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_laser_photodetector_y_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_laser_photodetector_y_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_laser_photodetector_y_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_laser_photodetector_y_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_laser_photodetector_y_position.value', int(new_val))


class RootWorkflowLaser_alignPropertyDeflection_offset_calibration_status(wrap.CmdTreeProp):

    class EnumType(Enum):
        No_Error = 'No Error'
        Calibration_Error = 'Calibration Error'
        Sensor_Signal_Failed = 'Sensor Signal Failed'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.deflection_offset_calibration_status'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.laser_align.property.deflection_offset_calibration_status.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.laser_align.property.deflection_offset_calibration_status.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowLaser_alignPropertyDeflection_offset_calibration_status.EnumType(self._context.get('root.workflow.laser_align.property.deflection_offset_calibration_status.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.laser_align.property.deflection_offset_calibration_status.value', new_val.value)


class RootWorkflowLaser_alignPropertyMotor_laser_readout_y_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_laser_readout_y_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_laser_readout_y_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_laser_readout_y_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_laser_readout_y_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_laser_readout_y_position.value', int(new_val))


class RootWorkflowLaser_alignPropertyMotor_laser_clean_drive_y_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_laser_clean_drive_y_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_laser_clean_drive_y_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_laser_clean_drive_y_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_laser_clean_drive_y_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_laser_clean_drive_y_position.value', int(new_val))


class RootWorkflowLaser_alignPropertyLaser_readout_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.laser_readout_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.workflow.laser_align.property.laser_readout_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.workflow.laser_align.property.laser_readout_enabled.value', bool(new_val))


class RootWorkflowLaser_alignPropertyLaser_clean_drive_amplitude(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.laser_clean_drive_amplitude'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.laser_clean_drive_amplitude.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.laser_clean_drive_amplitude.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.laser_clean_drive_amplitude.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.laser_clean_drive_amplitude.value', int(new_val))


class RootWorkflowLaser_alignPropertyMotor_laser_readout_x_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property.motor_laser_readout_x_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.laser_align.property.motor_laser_readout_x_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.laser_align.property.motor_laser_readout_x_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.laser_align.property.motor_laser_readout_x_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.laser_align.property.motor_laser_readout_x_position.value', int(new_val))


class RootWorkflowLaser_alignProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align.property'
        self.motor_laser_readout_x_position = RootWorkflowLaser_alignPropertyMotor_laser_readout_x_position(self._context)
        self.laser_clean_drive_amplitude = RootWorkflowLaser_alignPropertyLaser_clean_drive_amplitude(self._context)
        self.laser_readout_enabled = RootWorkflowLaser_alignPropertyLaser_readout_enabled(self._context)
        self.motor_laser_clean_drive_y_position = RootWorkflowLaser_alignPropertyMotor_laser_clean_drive_y_position(self._context)
        self.motor_laser_readout_y_position = RootWorkflowLaser_alignPropertyMotor_laser_readout_y_position(self._context)
        self.deflection_offset_calibration_status = RootWorkflowLaser_alignPropertyDeflection_offset_calibration_status(self._context)
        self.motor_laser_photodetector_y_position = RootWorkflowLaser_alignPropertyMotor_laser_photodetector_y_position(self._context)
        self.deflection_normal = RootWorkflowLaser_alignPropertyDeflection_normal(self._context)
        self.laser_clean_drive_enabled = RootWorkflowLaser_alignPropertyLaser_clean_drive_enabled(self._context)
        self.motor_laser_photodetector_x_position = RootWorkflowLaser_alignPropertyMotor_laser_photodetector_x_position(self._context)
        self.laser_spot_intensity = RootWorkflowLaser_alignPropertyLaser_spot_intensity(self._context)
        self.motor_laser_clean_drive_x_position = RootWorkflowLaser_alignPropertyMotor_laser_clean_drive_x_position(self._context)
        self.motor_laser_focus_z_position = RootWorkflowLaser_alignPropertyMotor_laser_focus_z_position(self._context)
        self.sensor_status = RootWorkflowLaser_alignPropertySensor_status(self._context)
        self.scan_mode = RootWorkflowLaser_alignPropertyScan_mode(self._context)
        self.laser_readout_power = RootWorkflowLaser_alignPropertyLaser_readout_power(self._context)
        self.deflection_lateral = RootWorkflowLaser_alignPropertyDeflection_lateral(self._context)
        self.motor_speed_laser_motors = RootWorkflowLaser_alignPropertyMotor_speed_laser_motors(self._context)
        self.motor_speed_max_laser_motors = RootWorkflowLaser_alignPropertyMotor_speed_max_laser_motors(self._context)
        self.laser_clean_drive_power = RootWorkflowLaser_alignPropertyLaser_clean_drive_power(self._context)
        self.update_detector_rate = RootWorkflowLaser_alignPropertyUpdate_detector_rate(self._context)
        self.motor_beam_shifter_position = RootWorkflowLaser_alignPropertyMotor_beam_shifter_position(self._context)
        self.motor_step = RootWorkflowLaser_alignPropertyMotor_step(self._context)


class RootWorkflowLaser_align(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align'
        self.property = RootWorkflowLaser_alignProperty(self._context)
        self.signal = RootWorkflowLaser_alignSignal(self._context)

    def start_updating_detector_status(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.start_updating_detector_status', *args)

    def stop_updating_detector_status(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.stop_updating_detector_status', *args)

    def stop_motors(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.stop_motors', *args)

    def start_auto_align(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.start_auto_align', *args)

    def adjust_motor_speed(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.adjust_motor_speed', *args)

    def start_moving_motors(self, *args) -> Any:
        return self._context.call('root.workflow.laser_align.start_moving_motors', *args)


class RootWorkflowZ_controllerSignalActivate_feedback_measurement(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.signal.activate_feedback_measurement'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.activate_feedback_measurement.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.activate_feedback_measurement.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.activate_feedback_measurement.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.activate_feedback_measurement.connect', *args)


class RootWorkflowZ_controllerSignalMonitor_values_changed(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.signal.monitor_values_changed'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.monitor_values_changed.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.monitor_values_changed.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.monitor_values_changed.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.signal.monitor_values_changed.connect', *args)


class RootWorkflowZ_controllerSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.signal'
        self.monitor_values_changed = RootWorkflowZ_controllerSignalMonitor_values_changed(self._context)
        self.activate_feedback_measurement = RootWorkflowZ_controllerSignalActivate_feedback_measurement(self._context)


class RootWorkflowZ_controllerPropertyI_gain(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.i_gain'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.z_controller.property.i_gain.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.z_controller.property.i_gain.value', int(new_val))


class RootWorkflowZ_controllerPropertySetpoint(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.setpoint'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.z_controller.property.setpoint.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.z_controller.property.setpoint.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.z_controller.property.setpoint.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.z_controller.property.setpoint.value', float(new_val))


class RootWorkflowZ_controllerPropertyMax_z_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.max_z_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.z_controller.property.max_z_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.z_controller.property.max_z_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.z_controller.property.max_z_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.z_controller.property.max_z_value.value', int(new_val))


class RootWorkflowZ_controllerPropertyD_gain(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.d_gain'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.z_controller.property.d_gain.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.z_controller.property.d_gain.value', int(new_val))


class RootWorkflowZ_controllerPropertyActual_tip_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.actual_tip_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.z_controller.property.actual_tip_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.z_controller.property.actual_tip_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.z_controller.property.actual_tip_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.z_controller.property.actual_tip_position.value', int(new_val))


class RootWorkflowZ_controllerPropertyP_gain(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.p_gain'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.z_controller.property.p_gain.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.z_controller.property.p_gain.value', int(new_val))


class RootWorkflowZ_controllerPropertyFeedback(wrap.CmdTreeProp):

    class EnumType(Enum):
        Deflection = 'Deflection'
        WaveMode_Amplitude_Reduction = 'WaveMode Amplitude Reduction'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.feedback'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.z_controller.property.feedback.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.z_controller.property.feedback.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowZ_controllerPropertyFeedback.EnumType(self._context.get('root.workflow.z_controller.property.feedback.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.z_controller.property.feedback.value', new_val.value)


class RootWorkflowZ_controllerPropertyIdle_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Enable_Z_Controller = 'Enable Z Controller'
        Retract_Tip = 'Retract Tip'
        Keep_Last_Z_Position = 'Keep Last Z Position'
        Absolute_Z_Position = 'Absolute Z Position'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.idle_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.z_controller.property.idle_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.z_controller.property.idle_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowZ_controllerPropertyIdle_mode.EnumType(self._context.get('root.workflow.z_controller.property.idle_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.z_controller.property.idle_mode.value', new_val.value)


class RootWorkflowZ_controllerPropertyAbsolute_idle_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.absolute_idle_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.z_controller.property.absolute_idle_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.z_controller.property.absolute_idle_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.z_controller.property.absolute_idle_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.z_controller.property.absolute_idle_position.value', int(new_val))


class RootWorkflowZ_controllerPropertyActual_feedback_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property.actual_feedback_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.z_controller.property.actual_feedback_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.z_controller.property.actual_feedback_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.z_controller.property.actual_feedback_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.z_controller.property.actual_feedback_value.value', int(new_val))


class RootWorkflowZ_controllerProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller.property'
        self.actual_feedback_value = RootWorkflowZ_controllerPropertyActual_feedback_value(self._context)
        self.absolute_idle_position = RootWorkflowZ_controllerPropertyAbsolute_idle_position(self._context)
        self.idle_mode = RootWorkflowZ_controllerPropertyIdle_mode(self._context)
        self.feedback = RootWorkflowZ_controllerPropertyFeedback(self._context)
        self.p_gain = RootWorkflowZ_controllerPropertyP_gain(self._context)
        self.actual_tip_position = RootWorkflowZ_controllerPropertyActual_tip_position(self._context)
        self.d_gain = RootWorkflowZ_controllerPropertyD_gain(self._context)
        self.max_z_value = RootWorkflowZ_controllerPropertyMax_z_value(self._context)
        self.setpoint = RootWorkflowZ_controllerPropertySetpoint(self._context)
        self.i_gain = RootWorkflowZ_controllerPropertyI_gain(self._context)


class RootWorkflowZ_controller(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller'
        self.property = RootWorkflowZ_controllerProperty(self._context)
        self.signal = RootWorkflowZ_controllerSignal(self._context)

    def setpoint_limits_from_calibration(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.setpoint_limits_from_calibration', *args)

    def retract_tip(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.retract_tip', *args)

    def tip_position_lower_limit(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.tip_position_lower_limit', *args)

    def retracted_do(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.retracted_do', *args)

    def setpoint_upper_limit(self, *args) -> Any:
        return self._context.call('root.workflow.z_controller.setpoint_upper_limit', *args)


class RootWorkflowImagingSignalRemaining_scan_time_changed(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.remaining_scan_time_changed'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.connect', *args)


class RootWorkflowImagingSignalScanning_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.scanning_started'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.connect', *args)


class RootWorkflowImagingSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.connect', *args)


class RootWorkflowImagingSignalScanning_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.scanning_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.connect', *args)


class RootWorkflowImagingSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal'
        self.scanning_finished = RootWorkflowImagingSignalScanning_finished(self._context)
        self.procedure_info = RootWorkflowImagingSignalProcedure_info(self._context)
        self.scanning_started = RootWorkflowImagingSignalScanning_started(self._context)
        self.remaining_scan_time_changed = RootWorkflowImagingSignalRemaining_scan_time_changed(self._context)


class RootWorkflowImagingVarScript_test_var_array(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.var.script_test_var_array'


class RootWorkflowImagingVar(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.var'
        self.script_test_var_array = RootWorkflowImagingVarScript_test_var_array(self._context)

    @property
    def script_test_var_double(self) -> float:
        return float(self._context.get('root.workflow.imaging.var.script_test_var_double'))

    @script_test_var_double.setter
    def script_test_var_double(self, new_val:float):
        self._context.set('root.workflow.imaging.var.script_test_var_double', float(new_val))

    @property
    def script_test_var_string(self) -> str:
        return str(self._context.get('root.workflow.imaging.var.script_test_var_string'))

    @script_test_var_string.setter
    def script_test_var_string(self, new_val:str):
        self._context.set('root.workflow.imaging.var.script_test_var_string', str(new_val))

    @property
    def script_test_var_int(self) -> int:
        return int(self._context.get('root.workflow.imaging.var.script_test_var_int'))

    @script_test_var_int.setter
    def script_test_var_int(self, new_val:int):
        self._context.set('root.workflow.imaging.var.script_test_var_int', int(new_val))


class RootWorkflowImagingPropertyScan_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Continuous = 'Continuous'
        Single_Frame = 'Single Frame'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.scan_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.imaging.property.scan_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.imaging.property.scan_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowImagingPropertyScan_mode.EnumType(self._context.get('root.workflow.imaging.property.scan_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.imaging.property.scan_mode.value', new_val.value)


class RootWorkflowImagingPropertyMove_speed_xy(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.move_speed_xy'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.move_speed_xy.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.move_speed_xy.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.move_speed_xy.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.move_speed_xy.value', float(new_val))


class RootWorkflowImagingPropertyLines_per_frame(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.lines_per_frame'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.lines_per_frame.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.lines_per_frame.value', int(new_val))


class RootWorkflowImagingPropertyScan_range_fast_axis(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.scan_range_fast_axis'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.scan_range_fast_axis.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.scan_range_fast_axis.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.scan_range_fast_axis.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.scan_range_fast_axis.value', float(new_val))


class RootWorkflowImagingPropertyImage_offset_y(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.image_offset_y'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.image_offset_y.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.image_offset_y.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.image_offset_y.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.image_offset_y.value', int(new_val))


class RootWorkflowImagingPropertyRotation(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.rotation'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.rotation.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.rotation.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.rotation.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.rotation.value', int(new_val))


class RootWorkflowImagingPropertySlope_x(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.slope_x'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.slope_x.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.slope_x.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.slope_x.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.slope_x.value', int(new_val))


class RootWorkflowImagingPropertyOverscan(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.overscan'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.overscan.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.overscan.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.overscan.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.overscan.value', int(new_val))


class RootWorkflowImagingPropertyTime_per_line(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.time_per_line'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.time_per_line.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.time_per_line.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.time_per_line.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.time_per_line.value', float(new_val))


class RootWorkflowImagingPropertyScan_range_slow_axis(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.scan_range_slow_axis'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.scan_range_slow_axis.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.scan_range_slow_axis.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.scan_range_slow_axis.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.scan_range_slow_axis.value', float(new_val))


class RootWorkflowImagingPropertySlow_axis_scan_direction(wrap.CmdTreeProp):

    class EnumType(Enum):
        Downward = 'Downward'
        Upward = 'Upward'
        Bounce = 'Bounce'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.slow_axis_scan_direction'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.imaging.property.slow_axis_scan_direction.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.imaging.property.slow_axis_scan_direction.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowImagingPropertySlow_axis_scan_direction.EnumType(self._context.get('root.workflow.imaging.property.slow_axis_scan_direction.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.imaging.property.slow_axis_scan_direction.value', new_val.value)


class RootWorkflowImagingPropertyImage_offset_x(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.image_offset_x'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.image_offset_x.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.image_offset_x.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.image_offset_x.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.image_offset_x.value', int(new_val))


class RootWorkflowImagingPropertyPoints_per_line(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.points_per_line'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.points_per_line.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.points_per_line.value', int(new_val))


class RootWorkflowImagingPropertyLine_rate(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.line_rate'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.line_rate.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.line_rate.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.line_rate.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.line_rate.value', int(new_val))


class RootWorkflowImagingPropertySlope_y(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.slope_y'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.slope_y.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.slope_y.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.slope_y.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.slope_y.value', int(new_val))


class RootWorkflowImagingPropertyTip_velocity(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.tip_velocity'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.tip_velocity.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.tip_velocity.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.tip_velocity.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.tip_velocity.value', float(new_val))


class RootWorkflowImagingProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property'
        self.tip_velocity = RootWorkflowImagingPropertyTip_velocity(self._context)
        self.slope_y = RootWorkflowImagingPropertySlope_y(self._context)
        self.line_rate = RootWorkflowImagingPropertyLine_rate(self._context)
        self.points_per_line = RootWorkflowImagingPropertyPoints_per_line(self._context)
        self.image_offset_x = RootWorkflowImagingPropertyImage_offset_x(self._context)
        self.slow_axis_scan_direction = RootWorkflowImagingPropertySlow_axis_scan_direction(self._context)
        self.scan_range_slow_axis = RootWorkflowImagingPropertyScan_range_slow_axis(self._context)
        self.time_per_line = RootWorkflowImagingPropertyTime_per_line(self._context)
        self.overscan = RootWorkflowImagingPropertyOverscan(self._context)
        self.slope_x = RootWorkflowImagingPropertySlope_x(self._context)
        self.rotation = RootWorkflowImagingPropertyRotation(self._context)
        self.image_offset_y = RootWorkflowImagingPropertyImage_offset_y(self._context)
        self.scan_range_fast_axis = RootWorkflowImagingPropertyScan_range_fast_axis(self._context)
        self.lines_per_frame = RootWorkflowImagingPropertyLines_per_frame(self._context)
        self.move_speed_xy = RootWorkflowImagingPropertyMove_speed_xy(self._context)
        self.scan_mode = RootWorkflowImagingPropertyScan_mode(self._context)


class RootWorkflowImaging(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging'
        self.property = RootWorkflowImagingProperty(self._context)
        self.var = RootWorkflowImagingVar(self._context)
        self.signal = RootWorkflowImagingSignal(self._context)

    def is_scanning(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.is_scanning', *args)

    def stop_imaging(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.stop_imaging', *args)

    def start_imaging(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.start_imaging', *args)


class RootWorkflowSignal_selection(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.signal_selection'


class RootWorkflowCantilever(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.cantilever'


class RootWorkflowApproachSignalApproach_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.signal.approach_started'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_started.connect', *args)


class RootWorkflowApproachSignalWithdraw_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.signal.withdraw_started'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.withdraw_started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.withdraw_started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.withdraw_started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.withdraw_started.connect', *args)


class RootWorkflowApproachSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.procedure_info.connect', *args)


class RootWorkflowApproachSignalApproach_or_withdraw_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.signal.approach_or_withdraw_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_or_withdraw_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_or_withdraw_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_or_withdraw_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.approach.signal.approach_or_withdraw_finished.connect', *args)


class RootWorkflowApproachSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.signal'
        self.approach_or_withdraw_finished = RootWorkflowApproachSignalApproach_or_withdraw_finished(self._context)
        self.procedure_info = RootWorkflowApproachSignalProcedure_info(self._context)
        self.withdraw_started = RootWorkflowApproachSignalWithdraw_started(self._context)
        self.approach_started = RootWorkflowApproachSignalApproach_started(self._context)


class RootWorkflowApproachPropertyApproach_pos(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.approach_pos'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach.property.approach_pos.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach.property.approach_pos.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach.property.approach_pos.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach.property.approach_pos.value', int(new_val))


class RootWorkflowApproachPropertyStep_by_step_approach_result(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.step_by_step_approach_result'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def value(self) -> str:
        return str(self._context.get('root.workflow.approach.property.step_by_step_approach_result.value'))

    @value.setter
    def value(self, new_val:str):
        self._context.set('root.workflow.approach.property.step_by_step_approach_result.value', str(new_val))


class RootWorkflowApproachPropertyStep_by_step_coarse_step_size_percentage(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.step_by_step_coarse_step_size_percentage'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach.property.step_by_step_coarse_step_size_percentage.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach.property.step_by_step_coarse_step_size_percentage.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach.property.step_by_step_coarse_step_size_percentage.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach.property.step_by_step_coarse_step_size_percentage.value', int(new_val))


class RootWorkflowApproachPropertyMotor_source(wrap.CmdTreeProp):

    class EnumType(Enum):
        Internal = 'Internal'
        External = 'External'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.motor_source'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.approach.property.motor_source.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.approach.property.motor_source.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowApproachPropertyMotor_source.EnumType(self._context.get('root.workflow.approach.property.motor_source.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.approach.property.motor_source.value', new_val.value)


class RootWorkflowApproachPropertyStep_by_step_deflection_offset_voltage(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.step_by_step_deflection_offset_voltage'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach.property.step_by_step_deflection_offset_voltage.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach.property.step_by_step_deflection_offset_voltage.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach.property.step_by_step_deflection_offset_voltage.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach.property.step_by_step_deflection_offset_voltage.value', int(new_val))


class RootWorkflowApproachPropertyApproach_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.approach_speed'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach.property.approach_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach.property.approach_speed.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach.property.approach_speed.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach.property.approach_speed.value', int(new_val))


class RootWorkflowApproachPropertyStep_by_step_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Position_Controlled = 'Position Controlled'
        Not_Controlled = 'Not Controlled'
        Tip_Position_Ignored = 'Tip Position Ignored'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.step_by_step_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.approach.property.step_by_step_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.approach.property.step_by_step_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowApproachPropertyStep_by_step_mode.EnumType(self._context.get('root.workflow.approach.property.step_by_step_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.approach.property.step_by_step_mode.value', new_val.value)


class RootWorkflowApproachPropertyStep_by_step_fine_step_size_percentage(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.step_by_step_fine_step_size_percentage'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach.property.step_by_step_fine_step_size_percentage.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach.property.step_by_step_fine_step_size_percentage.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach.property.step_by_step_fine_step_size_percentage.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach.property.step_by_step_fine_step_size_percentage.value', int(new_val))


class RootWorkflowApproachPropertyStep_by_step_slope(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.step_by_step_slope'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.approach.property.step_by_step_slope.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.approach.property.step_by_step_slope.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.approach.property.step_by_step_slope.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.approach.property.step_by_step_slope.value', float(new_val))


class RootWorkflowApproachPropertyApproach_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Continuous = 'Continuous'
        Step_by_Step = 'Step by Step'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.approach_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.approach.property.approach_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.approach.property.approach_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootWorkflowApproachPropertyApproach_mode.EnumType(self._context.get('root.workflow.approach.property.approach_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.approach.property.approach_mode.value', new_val.value)


class RootWorkflowApproachPropertyStep_by_step_time(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.step_by_step_time'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.approach.property.step_by_step_time.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.approach.property.step_by_step_time.value', float(new_val))


class RootWorkflowApproachPropertyApproach_steps(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.approach_steps'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach.property.approach_steps.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach.property.approach_steps.value', int(new_val))


class RootWorkflowApproachPropertyWithdraw_steps(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property.withdraw_steps'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.approach.property.withdraw_steps.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.approach.property.withdraw_steps.value', int(new_val))


class RootWorkflowApproachProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach.property'
        self.withdraw_steps = RootWorkflowApproachPropertyWithdraw_steps(self._context)
        self.approach_steps = RootWorkflowApproachPropertyApproach_steps(self._context)
        self.step_by_step_time = RootWorkflowApproachPropertyStep_by_step_time(self._context)
        self.approach_mode = RootWorkflowApproachPropertyApproach_mode(self._context)
        self.step_by_step_slope = RootWorkflowApproachPropertyStep_by_step_slope(self._context)
        self.step_by_step_fine_step_size_percentage = RootWorkflowApproachPropertyStep_by_step_fine_step_size_percentage(self._context)
        self.step_by_step_mode = RootWorkflowApproachPropertyStep_by_step_mode(self._context)
        self.approach_speed = RootWorkflowApproachPropertyApproach_speed(self._context)
        self.step_by_step_deflection_offset_voltage = RootWorkflowApproachPropertyStep_by_step_deflection_offset_voltage(self._context)
        self.motor_source = RootWorkflowApproachPropertyMotor_source(self._context)
        self.step_by_step_coarse_step_size_percentage = RootWorkflowApproachPropertyStep_by_step_coarse_step_size_percentage(self._context)
        self.step_by_step_approach_result = RootWorkflowApproachPropertyStep_by_step_approach_result(self._context)
        self.approach_pos = RootWorkflowApproachPropertyApproach_pos(self._context)


class RootWorkflowApproach(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach'
        self.property = RootWorkflowApproachProperty(self._context)
        self.signal = RootWorkflowApproachSignal(self._context)

    def stop_approach_or_withdraw(self, *args) -> Any:
        return self._context.call('root.workflow.approach.stop_approach_or_withdraw', *args)

    def start_withdraw(self, *args) -> Any:
        return self._context.call('root.workflow.approach.start_withdraw', *args)

    def start_approach(self, *args) -> Any:
        return self._context.call('root.workflow.approach.start_approach', *args)

    def abort(self, *args) -> Any:
        return self._context.call('root.workflow.approach.abort', *args)


class RootWorkflowAutomationPropertyQueue_index(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.automation.property.queue_index'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.automation.property.queue_index.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.automation.property.queue_index.value', int(new_val))


class RootWorkflowAutomationPropertyQueue_size(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.automation.property.queue_size'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.automation.property.queue_size.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.automation.property.queue_size.value', int(new_val))


class RootWorkflowAutomationProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.automation.property'
        self.queue_size = RootWorkflowAutomationPropertyQueue_size(self._context)
        self.queue_index = RootWorkflowAutomationPropertyQueue_index(self._context)


class RootWorkflowAutomation(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.automation'
        self.property = RootWorkflowAutomationProperty(self._context)

    def add_all_accessible_items_to_queue(self, *args) -> Any:
        return self._context.call('root.workflow.automation.add_all_accessible_items_to_queue', *args)

    def start(self, *args) -> Any:
        return self._context.call('root.workflow.automation.start', *args)

    def remove_from_queue(self, *args) -> Any:
        return self._context.call('root.workflow.automation.remove_from_queue', *args)

    def abort(self, *args) -> Any:
        return self._context.call('root.workflow.automation.abort', *args)

    def resume(self, *args) -> Any:
        return self._context.call('root.workflow.automation.resume', *args)

    def insert_in_queue(self, *args) -> Any:
        return self._context.call('root.workflow.automation.insert_in_queue', *args)

    def queue_size(self, *args) -> Any:
        return self._context.call('root.workflow.automation.queue_size', *args)

    def queue_as_string(self, *args) -> Any:
        return self._context.call('root.workflow.automation.queue_as_string', *args)

    def process(self, *args) -> Any:
        return self._context.call('root.workflow.automation.process', *args)

    def pause(self, *args) -> Any:
        return self._context.call('root.workflow.automation.pause', *args)

    def add_to_queue(self, *args) -> Any:
        return self._context.call('root.workflow.automation.add_to_queue', *args)


class RootWorkflow(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow'
        self.automation = RootWorkflowAutomation(self._context)
        self.approach = RootWorkflowApproach(self._context)
        self.cantilever = RootWorkflowCantilever(self._context)
        self.signal_selection = RootWorkflowSignal_selection(self._context)
        self.imaging = RootWorkflowImaging(self._context)
        self.z_controller = RootWorkflowZ_controller(self._context)
        self.laser_align = RootWorkflowLaser_align(self._context)
        self.xy_closed_loop = RootWorkflowXy_closed_loop(self._context)
        self.workspace = RootWorkflowWorkspace(self._context)
        self.spm_resource_requester = RootWorkflowSpm_resource_requester(self._context)
        self.thermal_tune = RootWorkflowThermal_tune(self._context)
        self.workflow_spectroscopy_setup = RootWorkflowWorkflow_spectroscopy_setup(self._context)
        self.system_startup = RootWorkflowSystem_startup(self._context)
        self.storage = RootWorkflowStorage(self._context)
        self.ort = RootWorkflowOrt(self._context)
        self.manager = RootWorkflowManager(self._context)
        self.preset_loader = RootWorkflowPreset_loader(self._context)
        self.parameters = RootWorkflowParameters(self._context)
        self.approach_motors = RootWorkflowApproach_motors(self._context)
        self.frequency_sweep = RootWorkflowFrequency_sweep(self._context)
        self.camera_properties = RootWorkflowCamera_properties(self._context)


class RootSession(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.session'

    @property
    def name(self) -> str:
        return str(self._context.get('root.session.name'))

    @name.setter
    def name(self, new_val:str):
        self._context.set('root.session.name', str(new_val))

    def list(self, *args) -> Any:
        return self._context.call('root.session.list', *args)

    def select_main(self, *args) -> Any:
        return self._context.call('root.session.select_main', *args)

    def select(self, *args) -> Any:
        return self._context.call('root.session.select', *args)

    @property
    def current_connection(self) -> str:
        return str(self._context.get('root.session.current_connection'))

    @current_connection.setter
    def current_connection(self, new_val:str):
        self._context.set('root.session.current_connection', str(new_val))


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
    def str(self) -> str:
        return str(self._context.get('root.test.str'))

    @str.setter
    def str(self, new_val:str):
        self._context.set('root.test.str', str(new_val))

    def func(self, *args) -> Any:
        return self._context.call('root.test.func', *args)

    @property
    def num_i(self) -> int:
        return int(self._context.get('root.test.num_i'))

    @num_i.setter
    def num_i(self, new_val:int):
        self._context.set('root.test.num_i', int(new_val))

    @property
    def num_f(self) -> float:
        return float(self._context.get('root.test.num_f'))

    @num_f.setter
    def num_f(self, new_val:float):
        self._context.set('root.test.num_f', float(new_val))


class RootCoreOscilloscope(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.oscilloscope'


class RootCoreLaser_align_drive_implSignalMotor_move_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal.motor_move_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_finished.connect', *args)


class RootCoreLaser_align_drive_implSignalCenter_detector_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal.center_detector_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.center_detector_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.center_detector_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.center_detector_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.center_detector_finished.connect', *args)


class RootCoreLaser_align_drive_implSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.procedure_info.connect', *args)


class RootCoreLaser_align_drive_implSignalAuto_align_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal.auto_align_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_finished.connect', *args)


class RootCoreLaser_align_drive_implSignalAuto_align_search_step_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal.auto_align_search_step_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_search_step_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_search_step_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_search_step_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_search_step_finished.connect', *args)


class RootCoreLaser_align_drive_implSignalAuto_align_pte_aligned(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal.auto_align_pte_aligned'

    def call(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_pte_aligned.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_pte_aligned.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_pte_aligned.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.auto_align_pte_aligned.connect', *args)


class RootCoreLaser_align_drive_implSignalMotor_move_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal.motor_move_started'

    def call(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.signal.motor_move_started.connect', *args)


class RootCoreLaser_align_drive_implSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.signal'
        self.motor_move_started = RootCoreLaser_align_drive_implSignalMotor_move_started(self._context)
        self.auto_align_pte_aligned = RootCoreLaser_align_drive_implSignalAuto_align_pte_aligned(self._context)
        self.auto_align_search_step_finished = RootCoreLaser_align_drive_implSignalAuto_align_search_step_finished(self._context)
        self.auto_align_finished = RootCoreLaser_align_drive_implSignalAuto_align_finished(self._context)
        self.procedure_info = RootCoreLaser_align_drive_implSignalProcedure_info(self._context)
        self.center_detector_finished = RootCoreLaser_align_drive_implSignalCenter_detector_finished(self._context)
        self.motor_move_finished = RootCoreLaser_align_drive_implSignalMotor_move_finished(self._context)


class RootCoreLaser_align_drive_implPropertyLaser_readout_power(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.laser_readout_power'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.laser_readout_power.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.laser_readout_power.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.laser_align_drive_impl.property.laser_readout_power.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.laser_align_drive_impl.property.laser_readout_power.value', float(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_speed_max_beam_shifter(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_speed_max_beam_shifter'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_max_beam_shifter.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_max_beam_shifter.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_max_beam_shifter.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_max_beam_shifter.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_laser_focus_z_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_laser_focus_z_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_focus_z_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_focus_z_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_focus_z_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_focus_z_position.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyLaser_clean_drive_power(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.laser_clean_drive_power'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.laser_clean_drive_power.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.laser_clean_drive_power.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.laser_align_drive_impl.property.laser_clean_drive_power.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.laser_align_drive_impl.property.laser_clean_drive_power.value', float(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_beam_shifter_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_beam_shifter_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_beam_shifter_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_beam_shifter_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_beam_shifter_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_beam_shifter_position.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_speed_laser_motors(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_speed_laser_motors'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_laser_motors.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_laser_motors.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_laser_motors.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_laser_motors.value', float(new_val))


class RootCoreLaser_align_drive_implPropertyDeflection_lateral(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.deflection_lateral'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.deflection_lateral.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.deflection_lateral.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.deflection_lateral.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.deflection_lateral.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_speed_max_laser_focus(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_speed_max_laser_focus'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_max_laser_focus.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_max_laser_focus.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_max_laser_focus.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_max_laser_focus.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_speed_max_laser_motors(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_speed_max_laser_motors'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_max_laser_motors.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_max_laser_motors.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_speed_max_laser_motors.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_speed_max_laser_motors.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyScan_mode(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.scan_mode'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.core.laser_align_drive_impl.property.scan_mode.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.core.laser_align_drive_impl.property.scan_mode.value', bool(new_val))


class RootCoreLaser_align_drive_implPropertySensor_status(wrap.CmdTreeProp):

    class EnumType(Enum):
        Undefined = 'Undefined'
        Low = 'Low'
        Ok = 'Ok'
        High = 'High'
        Fail = 'Fail'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.sensor_status'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.laser_align_drive_impl.property.sensor_status.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.laser_align_drive_impl.property.sensor_status.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreLaser_align_drive_implPropertySensor_status.EnumType(self._context.get('root.core.laser_align_drive_impl.property.sensor_status.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.laser_align_drive_impl.property.sensor_status.value', new_val.value)


class RootCoreLaser_align_drive_implPropertyMotor_laser_clean_drive_x_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_laser_clean_drive_x_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_x_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_x_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_x_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_x_position.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyLaser_spot_intensity(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.laser_spot_intensity'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.laser_spot_intensity.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.laser_spot_intensity.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.laser_spot_intensity.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.laser_spot_intensity.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_laser_photodetector_x_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_laser_photodetector_x_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_photodetector_x_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_photodetector_x_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_photodetector_x_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_photodetector_x_position.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyLaser_clean_drive_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.laser_clean_drive_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.core.laser_align_drive_impl.property.laser_clean_drive_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.core.laser_align_drive_impl.property.laser_clean_drive_enabled.value', bool(new_val))


class RootCoreLaser_align_drive_implPropertyDeflection_normal(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.deflection_normal'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.deflection_normal.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.deflection_normal.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.deflection_normal.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.deflection_normal.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_laser_photodetector_y_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_laser_photodetector_y_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_photodetector_y_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_photodetector_y_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_photodetector_y_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_photodetector_y_position.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyDeflection_offset_calibration_status(wrap.CmdTreeProp):

    class EnumType(Enum):
        No_Error = 'No Error'
        Calibration_Error = 'Calibration Error'
        Sensor_Signal_Failed = 'Sensor Signal Failed'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.deflection_offset_calibration_status'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.laser_align_drive_impl.property.deflection_offset_calibration_status.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.laser_align_drive_impl.property.deflection_offset_calibration_status.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreLaser_align_drive_implPropertyDeflection_offset_calibration_status.EnumType(self._context.get('root.core.laser_align_drive_impl.property.deflection_offset_calibration_status.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.laser_align_drive_impl.property.deflection_offset_calibration_status.value', new_val.value)


class RootCoreLaser_align_drive_implPropertyMotor_laser_readout_y_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_laser_readout_y_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_readout_y_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_readout_y_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_readout_y_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_readout_y_position.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_laser_clean_drive_y_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_laser_clean_drive_y_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_y_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_y_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_y_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_clean_drive_y_position.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyLaser_readout_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.laser_readout_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.core.laser_align_drive_impl.property.laser_readout_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.core.laser_align_drive_impl.property.laser_readout_enabled.value', bool(new_val))


class RootCoreLaser_align_drive_implPropertyLaser_clean_drive_amplitude(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.laser_clean_drive_amplitude'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.laser_clean_drive_amplitude.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.laser_clean_drive_amplitude.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.laser_clean_drive_amplitude.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.laser_clean_drive_amplitude.value', int(new_val))


class RootCoreLaser_align_drive_implPropertyMotor_laser_readout_x_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property.motor_laser_readout_x_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_readout_x_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_readout_x_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.laser_align_drive_impl.property.motor_laser_readout_x_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.laser_align_drive_impl.property.motor_laser_readout_x_position.value', int(new_val))


class RootCoreLaser_align_drive_implProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl.property'
        self.motor_laser_readout_x_position = RootCoreLaser_align_drive_implPropertyMotor_laser_readout_x_position(self._context)
        self.laser_clean_drive_amplitude = RootCoreLaser_align_drive_implPropertyLaser_clean_drive_amplitude(self._context)
        self.laser_readout_enabled = RootCoreLaser_align_drive_implPropertyLaser_readout_enabled(self._context)
        self.motor_laser_clean_drive_y_position = RootCoreLaser_align_drive_implPropertyMotor_laser_clean_drive_y_position(self._context)
        self.motor_laser_readout_y_position = RootCoreLaser_align_drive_implPropertyMotor_laser_readout_y_position(self._context)
        self.deflection_offset_calibration_status = RootCoreLaser_align_drive_implPropertyDeflection_offset_calibration_status(self._context)
        self.motor_laser_photodetector_y_position = RootCoreLaser_align_drive_implPropertyMotor_laser_photodetector_y_position(self._context)
        self.deflection_normal = RootCoreLaser_align_drive_implPropertyDeflection_normal(self._context)
        self.laser_clean_drive_enabled = RootCoreLaser_align_drive_implPropertyLaser_clean_drive_enabled(self._context)
        self.motor_laser_photodetector_x_position = RootCoreLaser_align_drive_implPropertyMotor_laser_photodetector_x_position(self._context)
        self.laser_spot_intensity = RootCoreLaser_align_drive_implPropertyLaser_spot_intensity(self._context)
        self.motor_laser_clean_drive_x_position = RootCoreLaser_align_drive_implPropertyMotor_laser_clean_drive_x_position(self._context)
        self.sensor_status = RootCoreLaser_align_drive_implPropertySensor_status(self._context)
        self.scan_mode = RootCoreLaser_align_drive_implPropertyScan_mode(self._context)
        self.motor_speed_max_laser_motors = RootCoreLaser_align_drive_implPropertyMotor_speed_max_laser_motors(self._context)
        self.motor_speed_max_laser_focus = RootCoreLaser_align_drive_implPropertyMotor_speed_max_laser_focus(self._context)
        self.deflection_lateral = RootCoreLaser_align_drive_implPropertyDeflection_lateral(self._context)
        self.motor_speed_laser_motors = RootCoreLaser_align_drive_implPropertyMotor_speed_laser_motors(self._context)
        self.motor_beam_shifter_position = RootCoreLaser_align_drive_implPropertyMotor_beam_shifter_position(self._context)
        self.laser_clean_drive_power = RootCoreLaser_align_drive_implPropertyLaser_clean_drive_power(self._context)
        self.motor_laser_focus_z_position = RootCoreLaser_align_drive_implPropertyMotor_laser_focus_z_position(self._context)
        self.motor_speed_max_beam_shifter = RootCoreLaser_align_drive_implPropertyMotor_speed_max_beam_shifter(self._context)
        self.laser_readout_power = RootCoreLaser_align_drive_implPropertyLaser_readout_power(self._context)


class RootCoreLaser_align_drive_impl(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl'
        self.property = RootCoreLaser_align_drive_implProperty(self._context)
        self.signal = RootCoreLaser_align_drive_implSignal(self._context)

    def abort_center_detector(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.abort_center_detector', *args)

    def reference_motor(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.reference_motor', *args)

    def start_search_algorithm(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.start_search_algorithm', *args)

    def start_updating_detector_status(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.start_updating_detector_status', *args)

    def stop_updating_detector_status(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.stop_updating_detector_status', *args)

    def start_moving_motors(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.start_moving_motors', *args)

    def center_detector(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.center_detector', *args)

    def abort_auto_align(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.abort_auto_align', *args)

    def stop_motors(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.stop_motors', *args)

    def move_motors_by_step(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.move_motors_by_step', *args)

    def start_optimizing(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.start_optimizing', *args)

    def zero_position(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.zero_position', *args)

    def auto_align(self, *args) -> Any:
        return self._context.call('root.core.laser_align_drive_impl.auto_align', *args)


class RootCoreFrequency_sweep(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.frequency_sweep'


class RootCoreDirect_motor_control(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.direct_motor_control'


class RootCoreScan_head_calibration(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.scan_head_calibration'


class RootCoreCore_monitoring(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_monitoring'


class RootCoreSpectroscopySignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.signal'


class RootCoreSpectroscopyPropertyBackward_sampling_rate(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_sampling_rate'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_sampling_rate.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_sampling_rate.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.backward_sampling_rate.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.backward_sampling_rate.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_pause_datapoints(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_pause_datapoints'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_pause_datapoints.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_pause_datapoints.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.forward_pause_datapoints.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.forward_pause_datapoints.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_pause_time(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_pause_time'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_pause_time.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_pause_time.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.forward_pause_time.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.forward_pause_time.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_sampling_rate(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_sampling_rate'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_sampling_rate.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_sampling_rate.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.forward_sampling_rate.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.forward_sampling_rate.value', int(new_val))


class RootCoreSpectroscopyPropertyStart_offset(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.start_offset'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.start_offset.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.start_offset.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.start_offset.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.start_offset.value', int(new_val))


class RootCoreSpectroscopyPropertyStart_offste_move_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.start_offste_move_speed'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.start_offste_move_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.start_offste_move_speed.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.spectroscopy.property.start_offste_move_speed.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.spectroscopy.property.start_offste_move_speed.value', float(new_val))


class RootCoreSpectroscopyPropertyBackward_pause_sampling_rate(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_pause_sampling_rate'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_pause_sampling_rate.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_pause_sampling_rate.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.backward_pause_sampling_rate.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.backward_pause_sampling_rate.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_modulation_stop_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Is_Less_Than = 'Is Less Than'
        Is_Greater_Than = 'Is Greater Than'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_modulation_stop_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.forward_modulation_stop_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.forward_modulation_stop_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertyForward_modulation_stop_mode.EnumType(self._context.get('root.core.spectroscopy.property.forward_modulation_stop_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.forward_modulation_stop_mode.value', new_val.value)


class RootCoreSpectroscopyPropertyForward_modulation_stop_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_modulation_stop_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_modulation_stop_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_modulation_stop_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.forward_modulation_stop_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.forward_modulation_stop_value.value', int(new_val))


class RootCoreSpectroscopyPropertySample_mask(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.sample_mask'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.sample_mask.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.sample_mask.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.sample_mask.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.sample_mask.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_modulation_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Fixed_Length = 'Fixed Length'
        Stop_by_Value = 'Stop by Value'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_modulation_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.forward_modulation_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.forward_modulation_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertyForward_modulation_mode.EnumType(self._context.get('root.core.spectroscopy.property.forward_modulation_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.forward_modulation_mode.value', new_val.value)


class RootCoreSpectroscopyPropertyModulation_relative_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.modulation_relative_value'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.core.spectroscopy.property.modulation_relative_value.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.core.spectroscopy.property.modulation_relative_value.value', bool(new_val))


class RootCoreSpectroscopyPropertyForward_pause_sampling_rate(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_pause_sampling_rate'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_pause_sampling_rate.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_pause_sampling_rate.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.forward_pause_sampling_rate.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.forward_pause_sampling_rate.value', int(new_val))


class RootCoreSpectroscopyPropertyRepetition_count(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.repetition_count'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.repetition_count.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.repetition_count.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.repetition_count.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.repetition_count.value', int(new_val))


class RootCoreSpectroscopyPropertyFeedback_active(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.feedback_active'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.core.spectroscopy.property.feedback_active.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.core.spectroscopy.property.feedback_active.value', bool(new_val))


class RootCoreSpectroscopyPropertyBackward_modulation_stop_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_modulation_stop_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_modulation_stop_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_modulation_stop_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.backward_modulation_stop_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.backward_modulation_stop_value.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_move_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_move_speed'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_move_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_move_speed.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.spectroscopy.property.forward_move_speed.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.spectroscopy.property.forward_move_speed.value', float(new_val))


class RootCoreSpectroscopyPropertyForward_modulation_time(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_modulation_time'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_modulation_time.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_modulation_time.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.forward_modulation_time.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.forward_modulation_time.value', int(new_val))


class RootCoreSpectroscopyPropertyBackward_pause_time(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_pause_time'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_pause_time.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_pause_time.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.backward_pause_time.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.backward_pause_time.value', int(new_val))


class RootCoreSpectroscopyPropertyXy_move_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.xy_move_speed'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.xy_move_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.xy_move_speed.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.spectroscopy.property.xy_move_speed.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.spectroscopy.property.xy_move_speed.value', float(new_val))


class RootCoreSpectroscopyPropertyBackward_modulation_time(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_modulation_time'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_modulation_time.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_modulation_time.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.backward_modulation_time.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.backward_modulation_time.value', int(new_val))


class RootCoreSpectroscopyPropertyBackward_modulation_range(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_modulation_range'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_modulation_range.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_modulation_range.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.spectroscopy.property.backward_modulation_range.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.spectroscopy.property.backward_modulation_range.value', float(new_val))


class RootCoreSpectroscopyPropertyBackward_pause_datapoints(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_pause_datapoints'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_pause_datapoints.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_pause_datapoints.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.backward_pause_datapoints.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.backward_pause_datapoints.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_pause_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Z_Off = 'Z Off'
        Z_On = 'Z On'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_pause_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.forward_pause_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.forward_pause_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertyForward_pause_mode.EnumType(self._context.get('root.core.spectroscopy.property.forward_pause_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.forward_pause_mode.value', new_val.value)


class RootCoreSpectroscopyPropertyModulation_output(wrap.CmdTreeProp):

    class EnumType(Enum):
        Position_Z = 'Position Z'
        Tip_Voltage = 'Tip Voltage'
        External_Z = 'External Z'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.modulation_output'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.modulation_output.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.modulation_output.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertyModulation_output.EnumType(self._context.get('root.core.spectroscopy.property.modulation_output.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.modulation_output.value', new_val.value)


class RootCoreSpectroscopyPropertyBackward_modulation_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Fixed_Length = 'Fixed Length'
        Stop_by_Value = 'Stop by Value'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_modulation_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.backward_modulation_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.backward_modulation_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertyBackward_modulation_mode.EnumType(self._context.get('root.core.spectroscopy.property.backward_modulation_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.backward_modulation_mode.value', new_val.value)


class RootCoreSpectroscopyPropertySpec_end_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Keep_Last_Z_Position = 'Keep Last Z Position'
        Z_Controller_Active = 'Z-Controller Active'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.spec_end_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.spec_end_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.spec_end_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertySpec_end_mode.EnumType(self._context.get('root.core.spectroscopy.property.spec_end_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.spec_end_mode.value', new_val.value)


class RootCoreSpectroscopyPropertyBackward_modulation_stop_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Is_Less_Than = 'Is Less Than'
        Is_Greater_Than = 'Is Greater Than'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_modulation_stop_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.backward_modulation_stop_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.backward_modulation_stop_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertyBackward_modulation_stop_mode.EnumType(self._context.get('root.core.spectroscopy.property.backward_modulation_stop_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.backward_modulation_stop_mode.value', new_val.value)


class RootCoreSpectroscopyPropertyForward_modulation_range(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_modulation_range'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_modulation_range.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_modulation_range.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.spectroscopy.property.forward_modulation_range.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.spectroscopy.property.forward_modulation_range.value', float(new_val))


class RootCoreSpectroscopyPropertyBackward_datapoints(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_datapoints'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_datapoints.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_datapoints.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.backward_datapoints.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.backward_datapoints.value', int(new_val))


class RootCoreSpectroscopyPropertyBackward_pause_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Z_Off = 'Z Off'
        Z_On = 'Z On'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_pause_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.spectroscopy.property.backward_pause_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.spectroscopy.property.backward_pause_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreSpectroscopyPropertyBackward_pause_mode.EnumType(self._context.get('root.core.spectroscopy.property.backward_pause_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.spectroscopy.property.backward_pause_mode.value', new_val.value)


class RootCoreSpectroscopyPropertyBackward_move_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.backward_move_speed'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.backward_move_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.backward_move_speed.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.spectroscopy.property.backward_move_speed.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.spectroscopy.property.backward_move_speed.value', float(new_val))


class RootCoreSpectroscopyPropertyAuto_recalibrate_probe_interval(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.auto_recalibrate_probe_interval'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.auto_recalibrate_probe_interval.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.auto_recalibrate_probe_interval.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.auto_recalibrate_probe_interval.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.auto_recalibrate_probe_interval.value', int(new_val))


class RootCoreSpectroscopyPropertyForward_datapoints(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property.forward_datapoints'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.spectroscopy.property.forward_datapoints.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.spectroscopy.property.forward_datapoints.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.spectroscopy.property.forward_datapoints.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.spectroscopy.property.forward_datapoints.value', int(new_val))


class RootCoreSpectroscopyProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy.property'
        self.forward_datapoints = RootCoreSpectroscopyPropertyForward_datapoints(self._context)
        self.auto_recalibrate_probe_interval = RootCoreSpectroscopyPropertyAuto_recalibrate_probe_interval(self._context)
        self.backward_move_speed = RootCoreSpectroscopyPropertyBackward_move_speed(self._context)
        self.backward_pause_mode = RootCoreSpectroscopyPropertyBackward_pause_mode(self._context)
        self.backward_datapoints = RootCoreSpectroscopyPropertyBackward_datapoints(self._context)
        self.forward_modulation_range = RootCoreSpectroscopyPropertyForward_modulation_range(self._context)
        self.backward_modulation_stop_mode = RootCoreSpectroscopyPropertyBackward_modulation_stop_mode(self._context)
        self.spec_end_mode = RootCoreSpectroscopyPropertySpec_end_mode(self._context)
        self.backward_modulation_mode = RootCoreSpectroscopyPropertyBackward_modulation_mode(self._context)
        self.modulation_output = RootCoreSpectroscopyPropertyModulation_output(self._context)
        self.forward_pause_mode = RootCoreSpectroscopyPropertyForward_pause_mode(self._context)
        self.backward_pause_datapoints = RootCoreSpectroscopyPropertyBackward_pause_datapoints(self._context)
        self.backward_modulation_range = RootCoreSpectroscopyPropertyBackward_modulation_range(self._context)
        self.backward_modulation_time = RootCoreSpectroscopyPropertyBackward_modulation_time(self._context)
        self.xy_move_speed = RootCoreSpectroscopyPropertyXy_move_speed(self._context)
        self.backward_pause_time = RootCoreSpectroscopyPropertyBackward_pause_time(self._context)
        self.forward_modulation_time = RootCoreSpectroscopyPropertyForward_modulation_time(self._context)
        self.forward_move_speed = RootCoreSpectroscopyPropertyForward_move_speed(self._context)
        self.backward_modulation_stop_value = RootCoreSpectroscopyPropertyBackward_modulation_stop_value(self._context)
        self.feedback_active = RootCoreSpectroscopyPropertyFeedback_active(self._context)
        self.repetition_count = RootCoreSpectroscopyPropertyRepetition_count(self._context)
        self.forward_pause_sampling_rate = RootCoreSpectroscopyPropertyForward_pause_sampling_rate(self._context)
        self.modulation_relative_value = RootCoreSpectroscopyPropertyModulation_relative_value(self._context)
        self.forward_modulation_mode = RootCoreSpectroscopyPropertyForward_modulation_mode(self._context)
        self.sample_mask = RootCoreSpectroscopyPropertySample_mask(self._context)
        self.forward_modulation_stop_value = RootCoreSpectroscopyPropertyForward_modulation_stop_value(self._context)
        self.forward_modulation_stop_mode = RootCoreSpectroscopyPropertyForward_modulation_stop_mode(self._context)
        self.backward_pause_sampling_rate = RootCoreSpectroscopyPropertyBackward_pause_sampling_rate(self._context)
        self.start_offste_move_speed = RootCoreSpectroscopyPropertyStart_offste_move_speed(self._context)
        self.start_offset = RootCoreSpectroscopyPropertyStart_offset(self._context)
        self.forward_sampling_rate = RootCoreSpectroscopyPropertyForward_sampling_rate(self._context)
        self.forward_pause_time = RootCoreSpectroscopyPropertyForward_pause_time(self._context)
        self.forward_pause_datapoints = RootCoreSpectroscopyPropertyForward_pause_datapoints(self._context)
        self.backward_sampling_rate = RootCoreSpectroscopyPropertyBackward_sampling_rate(self._context)


class RootCoreSpectroscopy(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spectroscopy'
        self.property = RootCoreSpectroscopyProperty(self._context)
        self.signal = RootCoreSpectroscopySignal(self._context)

    def start(self, *args) -> Any:
        return self._context.call('root.core.spectroscopy.start', *args)

    def abort(self, *args) -> Any:
        return self._context.call('root.core.spectroscopy.abort', *args)


class RootCoreCore_options(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_options'


class RootCoreThermal_tuneSignalNew_average(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal.new_average'

    def call(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_average.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_average.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_average.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_average.connect', *args)


class RootCoreThermal_tuneSignalStarted(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal.started'

    def call(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.started.connect', *args)


class RootCoreThermal_tuneSignalNew_fit(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal.new_fit'

    def call(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_fit.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_fit.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_fit.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_fit.connect', *args)


class RootCoreThermal_tuneSignalProgress(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal.progress'

    def call(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.progress.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.progress.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.progress.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.progress.connect', *args)


class RootCoreThermal_tuneSignalEnded(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal.ended'

    def call(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.ended.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.ended.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.ended.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.ended.connect', *args)


class RootCoreThermal_tuneSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal.procedure_info'

    def call(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.procedure_info.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.procedure_info.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.procedure_info.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.procedure_info.connect', *args)


class RootCoreThermal_tuneSignalNew_frequency_list(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal.new_frequency_list'

    def call(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_frequency_list.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_frequency_list.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_frequency_list.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.signal.new_frequency_list.connect', *args)


class RootCoreThermal_tuneSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.signal'
        self.new_frequency_list = RootCoreThermal_tuneSignalNew_frequency_list(self._context)
        self.procedure_info = RootCoreThermal_tuneSignalProcedure_info(self._context)
        self.ended = RootCoreThermal_tuneSignalEnded(self._context)
        self.progress = RootCoreThermal_tuneSignalProgress(self._context)
        self.new_fit = RootCoreThermal_tuneSignalNew_fit(self._context)
        self.started = RootCoreThermal_tuneSignalStarted(self._context)
        self.new_average = RootCoreThermal_tuneSignalNew_average(self._context)


class RootCoreThermal_tunePropertyMax_frequency(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property.max_frequency'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.thermal_tune.property.max_frequency.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.thermal_tune.property.max_frequency.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.thermal_tune.property.max_frequency.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.thermal_tune.property.max_frequency.value', int(new_val))


class RootCoreThermal_tunePropertyIterations(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property.iterations'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.thermal_tune.property.iterations.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.thermal_tune.property.iterations.value', int(new_val))


class RootCoreThermal_tunePropertyFit_frequency_lower_bound(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property.fit_frequency_lower_bound'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.thermal_tune.property.fit_frequency_lower_bound.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.thermal_tune.property.fit_frequency_lower_bound.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.thermal_tune.property.fit_frequency_lower_bound.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.thermal_tune.property.fit_frequency_lower_bound.value', int(new_val))


class RootCoreThermal_tunePropertyFit_frequency_upper_bound(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property.fit_frequency_upper_bound'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.thermal_tune.property.fit_frequency_upper_bound.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.thermal_tune.property.fit_frequency_upper_bound.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.thermal_tune.property.fit_frequency_upper_bound.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.thermal_tune.property.fit_frequency_upper_bound.value', int(new_val))


class RootCoreThermal_tunePropertyMeasurement_environment(wrap.CmdTreeProp):

    class EnumType(Enum):
        Air = 'Air'
        Liquid = 'Liquid'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property.measurement_environment'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.thermal_tune.property.measurement_environment.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.thermal_tune.property.measurement_environment.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreThermal_tunePropertyMeasurement_environment.EnumType(self._context.get('root.core.thermal_tune.property.measurement_environment.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.thermal_tune.property.measurement_environment.value', new_val.value)


class RootCoreThermal_tunePropertyResolution(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property.resolution'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.thermal_tune.property.resolution.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.thermal_tune.property.resolution.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.thermal_tune.property.resolution.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.thermal_tune.property.resolution.value', int(new_val))


class RootCoreThermal_tunePropertyTemperature(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property.temperature'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.thermal_tune.property.temperature.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.thermal_tune.property.temperature.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.thermal_tune.property.temperature.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.thermal_tune.property.temperature.value', int(new_val))


class RootCoreThermal_tuneProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune.property'
        self.temperature = RootCoreThermal_tunePropertyTemperature(self._context)
        self.resolution = RootCoreThermal_tunePropertyResolution(self._context)
        self.measurement_environment = RootCoreThermal_tunePropertyMeasurement_environment(self._context)
        self.fit_frequency_upper_bound = RootCoreThermal_tunePropertyFit_frequency_upper_bound(self._context)
        self.fit_frequency_lower_bound = RootCoreThermal_tunePropertyFit_frequency_lower_bound(self._context)
        self.iterations = RootCoreThermal_tunePropertyIterations(self._context)
        self.max_frequency = RootCoreThermal_tunePropertyMax_frequency(self._context)


class RootCoreThermal_tune(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune'
        self.property = RootCoreThermal_tuneProperty(self._context)
        self.signal = RootCoreThermal_tuneSignal(self._context)

    def calculate_cantilever_calibration(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.calculate_cantilever_calibration', *args)

    def add_raw_data_to_fft_average_buffer(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.add_raw_data_to_fft_average_buffer', *args)

    def set_fit_window_range(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.set_fit_window_range', *args)

    def start(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.start', *args)

    def abort(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.abort', *args)

    def auto_calc_properties(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.auto_calc_properties', *args)

    def generate_frequency_list(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.generate_frequency_list', *args)

    def create_fit_from_fft_average_buffer(self, *args) -> Any:
        return self._context.call('root.core.thermal_tune.create_fit_from_fft_average_buffer', *args)


class RootCoreCore_environment(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_environment'


class RootCorePosition_control(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.position_control'


class RootCoreCore_cantilever(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_cantilever'


class RootCoreZ_controllerSignalMonitor_values_changed(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.signal.monitor_values_changed'

    def call(self, *args) -> Any:
        return self._context.call('root.core.z_controller.signal.monitor_values_changed.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.z_controller.signal.monitor_values_changed.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.z_controller.signal.monitor_values_changed.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.z_controller.signal.monitor_values_changed.connect', *args)


class RootCoreZ_controllerSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.signal'
        self.monitor_values_changed = RootCoreZ_controllerSignalMonitor_values_changed(self._context)


class RootCoreZ_controllerPropertyI_gain(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.i_gain'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.z_controller.property.i_gain.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.z_controller.property.i_gain.value', int(new_val))


class RootCoreZ_controllerPropertySetpoint(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.setpoint'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.z_controller.property.setpoint.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.z_controller.property.setpoint.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.z_controller.property.setpoint.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.z_controller.property.setpoint.value', float(new_val))


class RootCoreZ_controllerPropertyMax_z_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.max_z_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.z_controller.property.max_z_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.z_controller.property.max_z_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.z_controller.property.max_z_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.z_controller.property.max_z_value.value', int(new_val))


class RootCoreZ_controllerPropertyD_gain(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.d_gain'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.z_controller.property.d_gain.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.z_controller.property.d_gain.value', int(new_val))


class RootCoreZ_controllerPropertyBase_work_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Control_Z_by_Z_Sensor = 'Control Z by Z-Sensor'
        Drive_Z = 'Drive Z'
        Control_Z_by_Measurement_Mode = 'Control Z by Measurement Mode'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.base_work_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.z_controller.property.base_work_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.z_controller.property.base_work_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreZ_controllerPropertyBase_work_mode.EnumType(self._context.get('root.core.z_controller.property.base_work_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.z_controller.property.base_work_mode.value', new_val.value)


class RootCoreZ_controllerPropertyActual_tip_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.actual_tip_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.z_controller.property.actual_tip_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.z_controller.property.actual_tip_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.z_controller.property.actual_tip_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.z_controller.property.actual_tip_position.value', int(new_val))


class RootCoreZ_controllerPropertyP_gain(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.p_gain'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.z_controller.property.p_gain.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.z_controller.property.p_gain.value', int(new_val))


class RootCoreZ_controllerPropertyFeedback(wrap.CmdTreeProp):

    class EnumType(Enum):
        Deflection = 'Deflection'
        WaveMode_Amplitude_Reduction = 'WaveMode Amplitude Reduction'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.feedback'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.z_controller.property.feedback.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.z_controller.property.feedback.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreZ_controllerPropertyFeedback.EnumType(self._context.get('root.core.z_controller.property.feedback.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.z_controller.property.feedback.value', new_val.value)


class RootCoreZ_controllerPropertyIdle_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Enable_Z_Controller = 'Enable Z Controller'
        Retract_Tip = 'Retract Tip'
        Keep_Last_Z_Position = 'Keep Last Z Position'
        Absolute_Z_Position = 'Absolute Z Position'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.idle_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.z_controller.property.idle_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.z_controller.property.idle_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreZ_controllerPropertyIdle_mode.EnumType(self._context.get('root.core.z_controller.property.idle_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.z_controller.property.idle_mode.value', new_val.value)


class RootCoreZ_controllerPropertyAbsolute_idle_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.absolute_idle_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.z_controller.property.absolute_idle_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.z_controller.property.absolute_idle_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.z_controller.property.absolute_idle_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.z_controller.property.absolute_idle_position.value', int(new_val))


class RootCoreZ_controllerPropertyActual_feedback_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property.actual_feedback_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.z_controller.property.actual_feedback_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.z_controller.property.actual_feedback_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.z_controller.property.actual_feedback_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.z_controller.property.actual_feedback_value.value', int(new_val))


class RootCoreZ_controllerProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller.property'
        self.actual_feedback_value = RootCoreZ_controllerPropertyActual_feedback_value(self._context)
        self.absolute_idle_position = RootCoreZ_controllerPropertyAbsolute_idle_position(self._context)
        self.idle_mode = RootCoreZ_controllerPropertyIdle_mode(self._context)
        self.feedback = RootCoreZ_controllerPropertyFeedback(self._context)
        self.p_gain = RootCoreZ_controllerPropertyP_gain(self._context)
        self.actual_tip_position = RootCoreZ_controllerPropertyActual_tip_position(self._context)
        self.base_work_mode = RootCoreZ_controllerPropertyBase_work_mode(self._context)
        self.d_gain = RootCoreZ_controllerPropertyD_gain(self._context)
        self.max_z_value = RootCoreZ_controllerPropertyMax_z_value(self._context)
        self.setpoint = RootCoreZ_controllerPropertySetpoint(self._context)
        self.i_gain = RootCoreZ_controllerPropertyI_gain(self._context)


class RootCoreZ_controller(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller'
        self.property = RootCoreZ_controllerProperty(self._context)
        self.signal = RootCoreZ_controllerSignal(self._context)

    def setpoint_limits_from_calibration(self, *args) -> Any:
        return self._context.call('root.core.z_controller.setpoint_limits_from_calibration', *args)

    def retract_tip(self, *args) -> Any:
        return self._context.call('root.core.z_controller.retract_tip', *args)

    def tip_position_lower_limit(self, *args) -> Any:
        return self._context.call('root.core.z_controller.tip_position_lower_limit', *args)

    def setpoint_upper_limit(self, *args) -> Any:
        return self._context.call('root.core.z_controller.setpoint_upper_limit', *args)


class RootCoreImaging(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.imaging'


class RootCoreConverter_channel_correction(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.converter_channel_correction'


class RootCoreApproach_motors_driveSignalMotor_move_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.signal.motor_move_finished'

    def call(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_finished.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_finished.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_finished.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_finished.connect', *args)


class RootCoreApproach_motors_driveSignalMotor_move_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.signal.motor_move_started'

    def call(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_started.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_started.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_started.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.signal.motor_move_started.connect', *args)


class RootCoreApproach_motors_driveSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.signal'
        self.motor_move_started = RootCoreApproach_motors_driveSignalMotor_move_started(self._context)
        self.motor_move_finished = RootCoreApproach_motors_driveSignalMotor_move_finished(self._context)


class RootCoreApproach_motors_drivePropertyMotor_speed_approach_motors(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property.motor_speed_approach_motors'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach_motors_drive.property.motor_speed_approach_motors.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach_motors_drive.property.motor_speed_approach_motors.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.approach_motors_drive.property.motor_speed_approach_motors.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.approach_motors_drive.property.motor_speed_approach_motors.value', float(new_val))


class RootCoreApproach_motors_drivePropertyMotor_left_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property.motor_left_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach_motors_drive.property.motor_left_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach_motors_drive.property.motor_left_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach_motors_drive.property.motor_left_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach_motors_drive.property.motor_left_position.value', int(new_val))


class RootCoreApproach_motors_drivePropertyMotor_right_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property.motor_right_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach_motors_drive.property.motor_right_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach_motors_drive.property.motor_right_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach_motors_drive.property.motor_right_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach_motors_drive.property.motor_right_position.value', int(new_val))


class RootCoreApproach_motors_drivePropertyRelative_tip_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property.relative_tip_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach_motors_drive.property.relative_tip_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach_motors_drive.property.relative_tip_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach_motors_drive.property.relative_tip_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach_motors_drive.property.relative_tip_position.value', int(new_val))


class RootCoreApproach_motors_drivePropertyMotor_speed_advance_retract(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property.motor_speed_advance_retract'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach_motors_drive.property.motor_speed_advance_retract.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach_motors_drive.property.motor_speed_advance_retract.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.approach_motors_drive.property.motor_speed_advance_retract.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.approach_motors_drive.property.motor_speed_advance_retract.value', float(new_val))


class RootCoreApproach_motors_drivePropertyMotor_front_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property.motor_front_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach_motors_drive.property.motor_front_position.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach_motors_drive.property.motor_front_position.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach_motors_drive.property.motor_front_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach_motors_drive.property.motor_front_position.value', int(new_val))


class RootCoreApproach_motors_drivePropertyMotor_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property.motor_speed'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach_motors_drive.property.motor_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach_motors_drive.property.motor_speed.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.approach_motors_drive.property.motor_speed.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.approach_motors_drive.property.motor_speed.value', float(new_val))


class RootCoreApproach_motors_driveProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive.property'
        self.motor_speed = RootCoreApproach_motors_drivePropertyMotor_speed(self._context)
        self.motor_front_position = RootCoreApproach_motors_drivePropertyMotor_front_position(self._context)
        self.motor_speed_advance_retract = RootCoreApproach_motors_drivePropertyMotor_speed_advance_retract(self._context)
        self.relative_tip_position = RootCoreApproach_motors_drivePropertyRelative_tip_position(self._context)
        self.motor_right_position = RootCoreApproach_motors_drivePropertyMotor_right_position(self._context)
        self.motor_left_position = RootCoreApproach_motors_drivePropertyMotor_left_position(self._context)
        self.motor_speed_approach_motors = RootCoreApproach_motors_drivePropertyMotor_speed_approach_motors(self._context)


class RootCoreApproach_motors_drive(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive'
        self.property = RootCoreApproach_motors_driveProperty(self._context)
        self.signal = RootCoreApproach_motors_driveSignal(self._context)

    def stop_motors(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.stop_motors', *args)

    def move_motors_by_step(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.move_motors_by_step', *args)

    def start_moving_motors(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.start_moving_motors', *args)

    def reference_motors(self, *args) -> Any:
        return self._context.call('root.core.approach_motors_drive.reference_motors', *args)


class RootCoreHv_amp_control(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.hv_amp_control'


class RootCoreSignal_store(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.signal_store'


class RootCoreAcquisition(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.acquisition'

    def write_data(self, *args) -> Any:
        return self._context.call('root.core.acquisition.write_data', *args)


class RootCoreApproachPropertyApproach_pos(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.approach_pos'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach.property.approach_pos.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach.property.approach_pos.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach.property.approach_pos.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach.property.approach_pos.value', int(new_val))


class RootCoreApproachPropertyApproach_steps(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.approach_steps'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach.property.approach_steps.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach.property.approach_steps.value', int(new_val))


class RootCoreApproachPropertyDeflection_offset_voltage(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.deflection_offset_voltage'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach.property.deflection_offset_voltage.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach.property.deflection_offset_voltage.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach.property.deflection_offset_voltage.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach.property.deflection_offset_voltage.value', int(new_val))


class RootCoreApproachPropertyMotor_source(wrap.CmdTreeProp):

    class EnumType(Enum):
        Internal = 'Internal'
        External = 'External'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.motor_source'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.approach.property.motor_source.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.approach.property.motor_source.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreApproachPropertyMotor_source.EnumType(self._context.get('root.core.approach.property.motor_source.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.approach.property.motor_source.value', new_val.value)


class RootCoreApproachPropertyStep_period(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.step_period'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.approach.property.step_period.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.approach.property.step_period.value', float(new_val))


class RootCoreApproachPropertyApproach_speed(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.approach_speed'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach.property.approach_speed.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach.property.approach_speed.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach.property.approach_speed.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach.property.approach_speed.value', int(new_val))


class RootCoreApproachPropertyStep_by_step_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Position_Controlled = 'Position Controlled'
        Not_Controlled = 'Not Controlled'
        Tip_Position_Ignored = 'Tip Position Ignored'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.step_by_step_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.approach.property.step_by_step_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.approach.property.step_by_step_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreApproachPropertyStep_by_step_mode.EnumType(self._context.get('root.core.approach.property.step_by_step_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.approach.property.step_by_step_mode.value', new_val.value)


class RootCoreApproachPropertyStep_by_step_fine_step_size_percentage(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.step_by_step_fine_step_size_percentage'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach.property.step_by_step_fine_step_size_percentage.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach.property.step_by_step_fine_step_size_percentage.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach.property.step_by_step_fine_step_size_percentage.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach.property.step_by_step_fine_step_size_percentage.value', int(new_val))


class RootCoreApproachPropertyStep_by_step_slope(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.step_by_step_slope'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach.property.step_by_step_slope.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach.property.step_by_step_slope.unit', str(new_val))

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.approach.property.step_by_step_slope.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.approach.property.step_by_step_slope.value', float(new_val))


class RootCoreApproachPropertyStep_by_step_coarse_step_size_percentage(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.step_by_step_coarse_step_size_percentage'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.approach.property.step_by_step_coarse_step_size_percentage.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.approach.property.step_by_step_coarse_step_size_percentage.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach.property.step_by_step_coarse_step_size_percentage.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach.property.step_by_step_coarse_step_size_percentage.value', int(new_val))


class RootCoreApproachPropertyApproach_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Continuous = 'Continuous'
        Step_by_Step = 'Step by Step'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.approach_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.approach.property.approach_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.approach.property.approach_mode.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreApproachPropertyApproach_mode.EnumType(self._context.get('root.core.approach.property.approach_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.approach.property.approach_mode.value', new_val.value)


class RootCoreApproachPropertyStep_by_step_time(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.step_by_step_time'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.approach.property.step_by_step_time.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.approach.property.step_by_step_time.value', float(new_val))


class RootCoreApproachPropertyApproach_result(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.approach_result'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def value(self) -> str:
        return str(self._context.get('root.core.approach.property.approach_result.value'))

    @value.setter
    def value(self, new_val:str):
        self._context.set('root.core.approach.property.approach_result.value', str(new_val))


class RootCoreApproachPropertyWithdraw_steps(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property.withdraw_steps'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.approach.property.withdraw_steps.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.approach.property.withdraw_steps.value', int(new_val))


class RootCoreApproachProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.property'
        self.withdraw_steps = RootCoreApproachPropertyWithdraw_steps(self._context)
        self.approach_result = RootCoreApproachPropertyApproach_result(self._context)
        self.step_by_step_time = RootCoreApproachPropertyStep_by_step_time(self._context)
        self.approach_mode = RootCoreApproachPropertyApproach_mode(self._context)
        self.step_by_step_coarse_step_size_percentage = RootCoreApproachPropertyStep_by_step_coarse_step_size_percentage(self._context)
        self.step_by_step_slope = RootCoreApproachPropertyStep_by_step_slope(self._context)
        self.step_by_step_fine_step_size_percentage = RootCoreApproachPropertyStep_by_step_fine_step_size_percentage(self._context)
        self.step_by_step_mode = RootCoreApproachPropertyStep_by_step_mode(self._context)
        self.approach_speed = RootCoreApproachPropertyApproach_speed(self._context)
        self.step_period = RootCoreApproachPropertyStep_period(self._context)
        self.motor_source = RootCoreApproachPropertyMotor_source(self._context)
        self.deflection_offset_voltage = RootCoreApproachPropertyDeflection_offset_voltage(self._context)
        self.approach_steps = RootCoreApproachPropertyApproach_steps(self._context)
        self.approach_pos = RootCoreApproachPropertyApproach_pos(self._context)


class RootCoreApproachSignalApproach_or_withdraw_done(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.signal.approach_or_withdraw_done'

    def call(self, *args) -> Any:
        return self._context.call('root.core.approach.signal.approach_or_withdraw_done.call', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.core.approach.signal.approach_or_withdraw_done.empty', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.core.approach.signal.approach_or_withdraw_done.connect_extended', *args)

    def connect(self, *args) -> Any:
        return self._context.call('root.core.approach.signal.approach_or_withdraw_done.connect', *args)


class RootCoreApproachSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach.signal'
        self.approach_or_withdraw_done = RootCoreApproachSignalApproach_or_withdraw_done(self._context)


class RootCoreApproach(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach'
        self.signal = RootCoreApproachSignal(self._context)
        self.property = RootCoreApproachProperty(self._context)

    def approach(self, *args) -> Any:
        return self._context.call('root.core.approach.approach', *args)

    def withdraw(self, *args) -> Any:
        return self._context.call('root.core.approach.withdraw', *args)

    def abort(self, *args) -> Any:
        return self._context.call('root.core.approach.abort', *args)


class RootCoreOrtPropertyBaseline_amplitude(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.baseline_amplitude'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.ort.property.baseline_amplitude.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.ort.property.baseline_amplitude.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.baseline_amplitude.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.baseline_amplitude.value', int(new_val))


class RootCoreOrtPropertyBaseline_frequency(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.baseline_frequency'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.ort.property.baseline_frequency.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.ort.property.baseline_frequency.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.baseline_frequency.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.baseline_frequency.value', int(new_val))


class RootCoreOrtPropertyBaseline_window_begin(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.baseline_window_begin'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.ort.property.baseline_window_begin.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.ort.property.baseline_window_begin.value', float(new_val))


class RootCoreOrtPropertyExcitation_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.excitation_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.core.ort.property.excitation_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.core.ort.property.excitation_enabled.value', bool(new_val))


class RootCoreOrtPropertyAdhesion_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.adhesion_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.ort.property.adhesion_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.ort.property.adhesion_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.adhesion_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.adhesion_value.value', int(new_val))


class RootCoreOrtPropertyBaseline_controller_enabled(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.baseline_controller_enabled'
        self._lua_value_type = wrap.LuaType('bool')

    @property
    def value(self) -> bool:
        return bool(self._context.get('root.core.ort.property.baseline_controller_enabled.value'))

    @value.setter
    def value(self, new_val:bool):
        self._context.set('root.core.ort.property.baseline_controller_enabled.value', bool(new_val))


class RootCoreOrtPropertyAmplitude_reduction(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.amplitude_reduction'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.ort.property.amplitude_reduction.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.ort.property.amplitude_reduction.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.amplitude_reduction.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.amplitude_reduction.value', int(new_val))


class RootCoreOrtPropertyBaseline_window_end(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.baseline_window_end'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.baseline_window_end.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.baseline_window_end.value', int(new_val))


class RootCoreOrtPropertyFree_wave_delay(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.free_wave_delay'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.free_wave_delay.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.free_wave_delay.value', int(new_val))


class RootCoreOrtPropertyAverage_periods(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.average_periods'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.average_periods.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.average_periods.value', int(new_val))


class RootCoreOrtPropertyBaseline_value(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.baseline_value'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def unit(self) -> str:
        return str(self._context.get('root.core.ort.property.baseline_value.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.core.ort.property.baseline_value.unit', str(new_val))

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.baseline_value.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.baseline_value.value', int(new_val))


class RootCoreOrtPropertyInput_select(wrap.CmdTreeProp):

    class EnumType(Enum):
        Fast_In_Deflection = 'Fast In Deflection'
        Hi_Res_In_Deflection = 'Hi Res In Deflection'
        Fast_In_User = 'Fast In User'
        Hi_Res_In_User1 = 'Hi Res In User1'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.input_select'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def enum(self) -> list:
        return list(self._context.get('root.core.ort.property.input_select.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.core.ort.property.input_select.enum', list(new_val))

    @property
    def value(self) -> EnumType:
        return RootCoreOrtPropertyInput_select.EnumType(self._context.get('root.core.ort.property.input_select.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.core.ort.property.input_select.value', new_val.value)


class RootCoreOrtPropertyCantilever_samples_per_period(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.cantilever_samples_per_period'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.cantilever_samples_per_period.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.cantilever_samples_per_period.value', int(new_val))


class RootCoreOrtPropertySamples_per_period(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.samples_per_period'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.samples_per_period.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.samples_per_period.value', int(new_val))


class RootCoreOrtPropertyFeedback_amplitude_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.feedback_amplitude_position'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.core.ort.property.feedback_amplitude_position.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.core.ort.property.feedback_amplitude_position.value', float(new_val))


class RootCoreOrtPropertyAdhesion_position(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property.adhesion_position'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.core.ort.property.adhesion_position.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.core.ort.property.adhesion_position.value', int(new_val))


class RootCoreOrtProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort.property'
        self.adhesion_position = RootCoreOrtPropertyAdhesion_position(self._context)
        self.feedback_amplitude_position = RootCoreOrtPropertyFeedback_amplitude_position(self._context)
        self.samples_per_period = RootCoreOrtPropertySamples_per_period(self._context)
        self.cantilever_samples_per_period = RootCoreOrtPropertyCantilever_samples_per_period(self._context)
        self.input_select = RootCoreOrtPropertyInput_select(self._context)
        self.baseline_value = RootCoreOrtPropertyBaseline_value(self._context)
        self.average_periods = RootCoreOrtPropertyAverage_periods(self._context)
        self.free_wave_delay = RootCoreOrtPropertyFree_wave_delay(self._context)
        self.baseline_window_end = RootCoreOrtPropertyBaseline_window_end(self._context)
        self.amplitude_reduction = RootCoreOrtPropertyAmplitude_reduction(self._context)
        self.baseline_controller_enabled = RootCoreOrtPropertyBaseline_controller_enabled(self._context)
        self.adhesion_value = RootCoreOrtPropertyAdhesion_value(self._context)
        self.excitation_enabled = RootCoreOrtPropertyExcitation_enabled(self._context)
        self.baseline_window_begin = RootCoreOrtPropertyBaseline_window_begin(self._context)
        self.baseline_frequency = RootCoreOrtPropertyBaseline_frequency(self._context)
        self.baseline_amplitude = RootCoreOrtPropertyBaseline_amplitude(self._context)


class RootCoreOrt(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort'
        self.property = RootCoreOrtProperty(self._context)

    def apply_sample_values(self, *args) -> Any:
        return self._context.call('root.core.ort.apply_sample_values', *args)

    def is_averaging(self, *args) -> Any:
        return self._context.call('root.core.ort.is_averaging', *args)

    def excitation_amplitude(self, *args) -> Any:
        return self._context.call('root.core.ort.excitation_amplitude', *args)

    def update_free_wave(self, *args) -> Any:
        return self._context.call('root.core.ort.update_free_wave', *args)

    def apply_samples_per_period(self, *args) -> Any:
        return self._context.call('root.core.ort.apply_samples_per_period', *args)

    def select_input(self, *args) -> Any:
        return self._context.call('root.core.ort.select_input', *args)


class RootCore(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core'
        self.ort = RootCoreOrt(self._context)
        self.approach = RootCoreApproach(self._context)
        self.acquisition = RootCoreAcquisition(self._context)
        self.signal_store = RootCoreSignal_store(self._context)
        self.hv_amp_control = RootCoreHv_amp_control(self._context)
        self.approach_motors_drive = RootCoreApproach_motors_drive(self._context)
        self.converter_channel_correction = RootCoreConverter_channel_correction(self._context)
        self.imaging = RootCoreImaging(self._context)
        self.z_controller = RootCoreZ_controller(self._context)
        self.core_cantilever = RootCoreCore_cantilever(self._context)
        self.position_control = RootCorePosition_control(self._context)
        self.core_environment = RootCoreCore_environment(self._context)
        self.thermal_tune = RootCoreThermal_tune(self._context)
        self.core_options = RootCoreCore_options(self._context)
        self.spectroscopy = RootCoreSpectroscopy(self._context)
        self.core_monitoring = RootCoreCore_monitoring(self._context)
        self.scan_head_calibration = RootCoreScan_head_calibration(self._context)
        self.direct_motor_control = RootCoreDirect_motor_control(self._context)
        self.frequency_sweep = RootCoreFrequency_sweep(self._context)
        self.laser_align_drive_impl = RootCoreLaser_align_drive_impl(self._context)
        self.oscilloscope = RootCoreOscilloscope(self._context)


class Root(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root'
        self.core = RootCore(self._context)
        self.test = RootTest(self._context)
        self.session = RootSession(self._context)
        self.workflow = RootWorkflow(self._context)
        self.util = RootUtil(self._context)
        self.lu = RootLu(self._context)

    def log_info(self, *args) -> Any:
        return self._context.call('root.log_info', *args)

    def log_warn(self, *args) -> Any:
        return self._context.call('root.log_warn', *args)

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

    def log_debug(self, *args) -> Any:
        return self._context.call('root.log_debug', *args)


