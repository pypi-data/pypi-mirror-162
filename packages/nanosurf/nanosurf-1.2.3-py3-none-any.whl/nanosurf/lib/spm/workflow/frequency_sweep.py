"""Frequency Sweep configuration and execution
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import matplotlib.pyplot as plt
import numpy as np
import time

import nanosurf
import nanosurf.lib.spm as spm

class _ModulationOutput():
    def __init__(self):
        pass

    def __del__(self):
        pass


class _NormalExcitation(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._fast_out1 = lowlevel.AnalogFastOut(
            lowlevel.AnalogFastOut.Instance.EXCITATION)
        self._old_input = self._fast_out1.input.value
        self._fast_out1.input.value = self._fast_out1.InputChannels.Analyzer2_Reference

    def __del__(self):
        self._fast_out1.input.value = self._old_input
        super().__del__()


class _TipVoltage(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._fast_out2 = lowlevel.AnalogFastOut(
            lowlevel.AnalogFastOut.Instance.USER)
        self._hi_res_tip_voltage = lowlevel.AnalogHiResOut(
            lowlevel.AnalogHiResOut.Instance.TIPVOLTAGE)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_tip_voltage_modulation = self._hi_res_tip_voltage.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._hi_res_tip_voltage.modulation.value = (
                self._hi_res_tip_voltage.Modulation.Enabled)

    def __del__(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._hi_res_tip_voltage.modulation.value = self._old_tip_voltage_modulation
        super().__del__()


class _FastUser(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._fast_out2 = lowlevel.AnalogFastOut(
            lowlevel.AnalogFastOut.Instance.USER)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_fast2_analog = self._fast_out2.analog_output.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._fast_out2.analog_output.value = (
                self._fast_out2.AnalogOutput.Enabled)

    def __del__(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._fast_out2.analog_output.value = self._old_fast2_analog
        super().__del__()


class _OutUser1(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._fast_out2 = lowlevel.AnalogFastOut(
            lowlevel.AnalogFastOut.Instance.USER)
        self._hi_res_user_1 = lowlevel.AnalogHiResOut(
            lowlevel.AnalogHiResOut.Instance.USER1)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_hires4_modulation = self._hi_res_user_1.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._hi_res_user_1.modulation.value = (
                self._hi_res_user_1.Modulation.Enabled)

    def __del__(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._hi_res_user_1.modulation.value = self._old_hires4_modulation
        super().__del__()


class _OutUser2(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._fast_out2 = lowlevel.AnalogFastOut(
            lowlevel.AnalogFastOut.Instance.USER)
        self._hi_res_user2 = lowlevel.AnalogHiResOut(
            lowlevel.AnalogHiResOut.Instance.USER2)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_user2_modulation = self._hi_res_user2.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._hi_res_user2.modulation.value = (
                self._hi_res_user2.Modulation.Enabled)

    def __del__(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._hi_res_user2.modulation.value = self._old_user2_modulation
        super().__del__()


class _OutUser3(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._fast_out2 = lowlevel.AnalogFastOut(
            lowlevel.AnalogFastOut.Instance.USER)
        self._out_user3 = lowlevel.AnalogHiResOut(
            lowlevel.AnalogHiResOut.Instance.USER3)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_user3_modulation = self._out_user3.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._out_user3.modulation.value = (
                self._out_user3.Modulation.Enabled)

    def __del__(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._out_user3.modulation.value = self._old_user3_modulation
        super().__del__()


class _OutUser4(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._fast_out2 = lowlevel.AnalogFastOut(
            lowlevel.AnalogFastOut.Instance.USER)
        self._monitor_out2 = lowlevel.AnalogHiResOut(
            lowlevel.AnalogHiResOut.Instance.USER4)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_monitor2_modulation = self._monitor_out2.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._monitor_out2.modulation.value = (
                self._monitor_out2.Modulation.Enabled)

    def __del__(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._monitor_out2.modulation.value = self._old_monitor2_modulation
        super().__del__()


class _OutPositionX(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._scan_x_out = lowlevel.AnalogHiResOut(
                lowlevel.AnalogHiResOut.Instance.POSITIONX)
        self._old_scan_x_out = self._scan_x_out.input.value
        self._scan_x_out.input = self._scan_x_out.InputChannels.GenTest_Dynamic

    def __del__(self):
        self._scan_x_out.input = self._old_scan_x_out
        super().__del__()


class _OutPositionY(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._scan_y_out = lowlevel.AnalogHiResOut(
                lowlevel.AnalogHiResOut.Instance.POSITIONY)
        self._old_scan_y_out = self._scan_y_out.input.value
        self._scan_y_out.input = self._scan_y_out.InputChannels.GenTest_Dynamic

    def __del__(self):
        self._scan_y_out.input = self._old_scan_y_out
        super().__del__()


class _OutPositionZ(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._hi_res_pos_out_z = lowlevel.AnalogHiResOut(
            lowlevel.AnalogHiResOut.Instance.POSITIONZ)
        self._old_posz_input = self._hi_res_pos_out_z.input.value
        self._hi_res_pos_out_z.input.value = (
                self._hi_res_pos_out_z.InputChannels.GenTest_Dynamic)

    def __del__(self):
        self._hi_res_pos_out_z.input.value = self._old_posz_input
        super().__del__()


class _ModOutZ(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._hi_res_pos_out_z = lowlevel.AnalogHiResOut(
            lowlevel.AnalogHiResOut.Instance.POSITIONZ)
        self._old_posz_modulation = self._hi_res_pos_out_z.modulation.value
        self._hi_res_pos_out_z.modulation.value = (
                self._hi_res_pos_out_z.Modulation.Enabled)

    def __del__(self):
        self._hi_res_pos_out_z.modulation.value = self._old_posz_modulation
        super().__del__()


class _ModXControlSet(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._pid_control = lowlevel.PIDController(lowlevel.PIDController.Instance.PIDX)
        try:
            self._old_value = self._pid_control.set_point_modulation_enable.value
            self._pid_control.set_point_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False


    def __del__(self):
        if self.new_style:
            self._pid_control.set_point_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value
        super().__del__()


class _ModYControlSet(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._pid_control = lowlevel.PIDController(lowlevel.PIDController.Instance.PIDY)
        try:
            self._old_value = self._pid_control.set_point_modulation_enable.value
            self._pid_control.set_point_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False

    def __del__(self):
        if self.new_style:
            self._pid_control.set_point_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value
        super().__del__()


class _ModZControlSet(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._pid_control = lowlevel.ZControllerEx()
        try:
            self._old_value = self._pid_control.set_point_modulation_enable.value
            self._pid_control.set_point_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False

    def __del__(self):
        if self.new_style:
            self._pid_control.set_point_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value
        super().__del__()


class _ModZControlOutput(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__()
        self._pid_control = lowlevel.ZControllerEx()
        try:
            self._old_value = self._pid_control.output_modulation_enable.value
            self._pid_control.output_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False

    def __del__(self):
        if self.new_style:
            self._pid_control.output_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value
        super().__del__()

class FrequencySweepOutput(enum.Enum):
    """Enumeration for the modulation output selection"""
    Normal_Excitation = enum.auto(),
    FastUser_OutB = enum.auto(),
    TipVoltage_UserOutA = enum.auto(),
    UserOut1_UserC = enum.auto(),
    UserOut2_UserA = enum.auto(),
    UserOut3_Monitor1 = enum.auto(),
    UserOut4_Monitor2 = enum.auto(),
    PositionX = enum.auto(),
    PositionY = enum.auto(),
    PositionZ = enum.auto(),
    ModOutZ = enum.auto(),
    ModXControlSet = enum.auto(),
    ModYControlSet = enum.auto(),
    ModZControlSet = enum.auto(),
    ModZControlOutput = enum.auto()

class InputSource(enum.Enum):
    Deflection = enum.auto(),
    Fast2_CX = enum.auto(),
    Fast_User_CX = enum.auto(),
    Friction = enum.auto(),
    UserIn1 = enum.auto(),
    UserIn2_UserB = enum.auto(),
    UserIn3_UserA = enum.auto(),
    UserIn4_CX = enum.auto(),
    TipCurrent = enum.auto(),
    TestGND_C3000 = enum.auto(),
    TesRef_C3000 = enum.auto(),
    TestMixedOut3_C3000 = enum.auto(),
    AxisInX = enum.auto(),
    AxisInY = enum.auto(),
    AxisInZ = enum.auto(),
    MainLockIn_Amplitude = enum.auto(),
    MainPLL_FreqShift = enum.auto(),
    ZControllerOut = enum.auto()

class InputRanges(enum.Enum):
    Full = enum.auto(),
    OneOverFour = enum.auto(),
    OneOverSixteen = enum.auto(),

class Bandwidths(enum.IntEnum):
    Hz_23 = 0,
    Hz_45 = 1,
    Hz_90 = 2,
    Hz_180 = 3,
    Hz_360 = 4,
    Hz_740 = 5,
    Hz_1500 = 6,
    Hz_3000 = 7,
    Hz_6000 = 8,
    Hz_12k = 9,
    Hz_24k= 10,
    Hz_48k = 11,
    Hz_100k = 12,
    Hz_230k = 13,
    Hz_500k = 14

class FrequencySweep():
    """Workflow for acquiring and plotting frequency sweeps."""

    # Output = enum.Enum('Output', {
    Output = {
        FrequencySweepOutput.Normal_Excitation.name: _NormalExcitation,
        FrequencySweepOutput.FastUser_OutB.name: _FastUser,
        FrequencySweepOutput.TipVoltage_UserOutA.name: _TipVoltage,
        FrequencySweepOutput.UserOut1_UserC.name: _OutUser1,
        FrequencySweepOutput.UserOut2_UserA.name: _OutUser2,
        FrequencySweepOutput.UserOut3_Monitor1.name: _OutUser3,
        FrequencySweepOutput.UserOut4_Monitor2.name: _OutUser4,
        FrequencySweepOutput.PositionX.name: _OutPositionX,
        FrequencySweepOutput.PositionY.name: _OutPositionY,
        FrequencySweepOutput.PositionZ.name: _OutPositionZ,
        FrequencySweepOutput.ModOutZ.name: _ModOutZ,
        FrequencySweepOutput.ModXControlSet.name: _ModXControlSet,
        FrequencySweepOutput.ModYControlSet.name: _ModYControlSet,
        FrequencySweepOutput.ModZControlSet.name: _ModZControlSet,
        FrequencySweepOutput.ModZControlOutput.name: _ModZControlOutput
        }

    input_sources_names: dict[InputSource, str] = {
        InputSource.Deflection : "Deflection",
        InputSource.Fast2_CX :  "Fast2 (CX)",
        InputSource.Fast_User_CX : "Fast User (CX)",
        InputSource.Friction : "Friction",
        InputSource.UserIn1: "User In 1",
        InputSource.UserIn2_UserB : "User In 2 / B",
        InputSource.UserIn3_UserA : "User In 3 / A",
        InputSource.UserIn4_CX : "User In 4 (CX)",
        InputSource.TipCurrent : "TipCurrent",
        InputSource.TestGND_C3000 : "Test GND (C3000)",
        InputSource.TesRef_C3000 : "Test Ref (C3000)",
        InputSource.TestMixedOut3_C3000 : "Test MixedOut3 (C3000)",
        InputSource.AxisInX : "Axis In X",
        InputSource.AxisInY : "Axis In Y",
        InputSource.AxisInZ : "Axis In Z",
        InputSource.MainLockIn_Amplitude : "Main Lock-In Amplitude",
        InputSource.MainPLL_FreqShift : "Main PLL Frequency Shift",
        InputSource.ZControllerOut : "Z-Controller Out"
    }

    bandwidths_names = {
        Bandwidths.Hz_23: "23Hz",
        Bandwidths.Hz_45:"45Hz",
        Bandwidths.Hz_90:"90Hz",
        Bandwidths.Hz_180:"180Hz",
        Bandwidths.Hz_360:"360Hz",
        Bandwidths.Hz_740:"740Hz",
        Bandwidths.Hz_1500:"1500Hz",
        Bandwidths.Hz_3000:"3kHz",
        Bandwidths.Hz_6000:"6kHz",
        Bandwidths.Hz_12k:"12kHz",
        Bandwidths.Hz_24k:"23kHz",
        Bandwidths.Hz_48k:"45kHz",
        Bandwidths.Hz_100k:"100kHz",
        Bandwidths.Hz_230k:"230kHz",
        Bandwidths.Hz_500k:"500kHz"
    }

    input_ranges_names: dict[InputRanges,str] = {
        InputRanges.Full:           "Full",
        InputRanges.OneOverFour:    "1/4",
        InputRanges.OneOverSixteen: "1/16"
    }

    output_names: dict[FrequencySweepOutput, str] = {
        FrequencySweepOutput.Normal_Excitation:"Normal Excitation",
        FrequencySweepOutput.FastUser_OutB: "Fast User / Out B",
        FrequencySweepOutput.TipVoltage_UserOutA:"Tip Voltage / User Out A",
        FrequencySweepOutput.UserOut1_UserC:"User 1 / C",
        FrequencySweepOutput.UserOut2_UserA:"User 2 / A",
        FrequencySweepOutput.UserOut3_Monitor1:"User 3 / Monitor 1",
        FrequencySweepOutput.UserOut4_Monitor2:"User 4 / Monitor 2",
        FrequencySweepOutput.PositionX:"X Position",
        FrequencySweepOutput.PositionY:"Y Position",
        FrequencySweepOutput.PositionZ:"PosOutZ",
        FrequencySweepOutput.ModOutZ:"ModOutZ",
        FrequencySweepOutput.ModXControlSet:"ModXControlSet",
        FrequencySweepOutput.ModYControlSet:"ModYControlSet",
        FrequencySweepOutput.ModZControlSet:"ModZControlSet",
        FrequencySweepOutput.ModZControlOutput:"ModZControlOutput"
    }

    def __init__(self, spm: spm.Spm):
        self.is_busy = False
        self.output_setup = None
        self.data_group_name = "Frequency sweep"
        self.data_channel_amplitude = 2
        self.data_channel_phase = 3
        self._spm = spm
        self._ll = spm.lowlevel
        self._internal_transfer_time = 5.0

        self._analyzer = self._ll.SignalAnalyzer(spm.lowlevel.SignalAnalyzer.Instance.INST2)
        self._system_infra = self._ll.SystemInfra()
        self._frequency_sweep_generator = self._ll.FrequencySweepGen()

        self.input_sources_to_lu_map: dict[InputSource, int] = {
            InputSource.Deflection: self._analyzer.Input.FastInDeflection,
            InputSource.Fast2_CX: self._analyzer.Input.FastIn2,
            InputSource.Fast_User_CX: self._analyzer.Input.FastInUser,
            InputSource.Friction: self._analyzer.Input.InLateral,
            InputSource.UserIn1: self._analyzer.Input.InUser1,
            InputSource.UserIn2_UserB: self._analyzer.Input.InUser2,
            InputSource.UserIn3_UserA: self._analyzer.Input.InUser3,
            InputSource.UserIn4_CX: self._analyzer.Input.InUser4,
            InputSource.TipCurrent: self._analyzer.Input.InTipCurrent,
            InputSource.TestGND_C3000: self._analyzer.Input.Test_AnaGND,
            InputSource.TesRef_C3000: self._analyzer.Input.Test_Ref,
            InputSource.TestMixedOut3_C3000: self._analyzer.Input.Test_TipVoltage,
            InputSource.AxisInX: self._analyzer.Input.InPositionX,
            InputSource.AxisInY: self._analyzer.Input.InPositionY,
            InputSource.AxisInZ: self._analyzer.Input.InPositionZ,
            InputSource.MainLockIn_Amplitude: self._analyzer.Input.Analyzer1_Amplitude,
            InputSource.MainPLL_FreqShift: self._analyzer.Input.Analyzer1_CtrlDeltaF,
            InputSource.ZControllerOut: self._analyzer.Input.CtrlZ_Out,
        }

        self.input_range_to_gain_map: dict[InputRanges, float] = {
            InputRanges.Full:           self._system_infra.main_in_2_gain.value_min,
            InputRanges.OneOverFour:    self._system_infra.main_in_2_gain.value_max / self._system_infra.main_in_2_gain.value_max,
            InputRanges.OneOverSixteen: self._system_infra.main_in_2_gain.value_max
        }

        self.bandwidths_to_lu_map : dict[Bandwidths, int] = {
            Bandwidths.Hz_23 : self._analyzer.DemodulatorBW.BW_23Hz,
            Bandwidths.Hz_45: self._analyzer.DemodulatorBW.BW_45Hz,
            Bandwidths.Hz_90: self._analyzer.DemodulatorBW.BW_90Hz,
            Bandwidths.Hz_180: self._analyzer.DemodulatorBW.BW_180Hz,
            Bandwidths.Hz_360: self._analyzer.DemodulatorBW.BW_360Hz,
            Bandwidths.Hz_740: self._analyzer.DemodulatorBW.BW_750Hz,
            Bandwidths.Hz_1500: self._analyzer.DemodulatorBW.BW_1500Hz,
            Bandwidths.Hz_3000: self._analyzer.DemodulatorBW.BW_3kHz,
            Bandwidths.Hz_6000: self._analyzer.DemodulatorBW.BW_6kHz,
            Bandwidths.Hz_12k: self._analyzer.DemodulatorBW.BW_12kHz,
            Bandwidths.Hz_24k: self._analyzer.DemodulatorBW.BW_23kHz,
            Bandwidths.Hz_48k: self._analyzer.DemodulatorBW.BW_45kHz,
            Bandwidths.Hz_100k: self._analyzer.DemodulatorBW.BW_100kHz,
            Bandwidths.Hz_230k: self._analyzer.DemodulatorBW.BW_230kHz,
            Bandwidths.Hz_500k: self._analyzer.DemodulatorBW.BW_500kHz,
            }

    def __del__(self):
        if self.output_setup is not None:
            del self.output_setup

    def _get_active_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns transfer function and frequencies of the active chart."""

        class ActiveError():
            """Exception raised when there is no active data."""
            def __init__(self, expression, message):
                self._expression = expression
                self._message = message

        def check_if_active(document):
            if document is None:
                raise ActiveError(document, "No document selected!")

        document = self._spm.application.DocGetActive
        check_if_active(document)

        group = document.DataGetGroupPos(self.data_group_name)

        new_data = document.DataGetByPos(group, self.data_channel_amplitude)
        assert new_data is not None, "No data!"
        data_line:str = new_data.GetLine(0, spm.Spm.DataFilter.RAW, spm.Spm.DataConversion.Physical)
        # in some countries numbers have ',' as dot but float(str) has problems with this localization
        usa_style_data_line = data_line.replace(",", ".")
        amplitude = np.array(usa_style_data_line.split(";")).astype(float)

        new_data = document.DataGetByPos(group, self.data_channel_phase)
        assert new_data is not None, "No data!"
        data_line:str = new_data.GetLine(0, spm.Spm.DataFilter.RAW, spm.Spm.DataConversion.Physical)
        # in some countries numbers have ',' as dot but float(str) has problems with this localisation
        usa_style_data_line = data_line.replace(",", ".")
        phase = np.array(usa_style_data_line.split(";")).astype(float)

        frequencies = np.arange(
            new_data.AxisPointMin,
            new_data.AxisPointMin + new_data.AxisPointRange + 0.1,
            new_data.AxisPointRange / (new_data.Points - 1))
        complex_transfer = amplitude * np.exp(1j * 2*np.pi * phase/360.0)

        return (complex_transfer, frequencies)

    def _start(
            self, start_frequency: float, end_frequency: float, points: int,
            step_time: float, settle_time: float, amplitude: float) -> float:
        """Starts Frequency Sweep.

        Parameters
        ----------
        start_frequency
            Start frequency [Hz]
        end_frequency
            End frequency [Hz]
        points
            Number of points in the sweep.
        step_time
            Time between measurement points. [s]
        settle_time
            Time to wait between setting up signal_analyzer and
            starting the frequency sweep. [s]
        amplitude: float
            Normalized Amplitude [0..1.0]
        """
        limited_step_time = max(step_time, 0.01)

        generator = self._frequency_sweep_generator
        generator.lusig_analyzer_inst_no.value = (
            generator.LUSigAnalyzerInstNo.INST2)

        generator.start_frequency.value = start_frequency
        generator.end_frequency.value = end_frequency
        generator.data_points.value = points

        # Settle time before starting the measurement...
        generator.settle_time.value = settle_time
        generator.step_time.value = limited_step_time
        generator.sweep_amplitude.value = amplitude

        self.start_time = time.time()
        self.start_frequency = start_frequency
        self.end_frequency = end_frequency
        self.is_busy = True
        generator.start_frequency_sweep()

        return limited_step_time*points + 2*settle_time + self._internal_transfer_time/2

    def _finish(self):
        """Stop FrequencySweep and capture measured data into new document"""
        self._frequency_sweep_generator.user_abort()
        time.sleep(0.1)
        self._spm.application.OperatingMode.CaptureFreqSearchChart
        time.sleep(self._internal_transfer_time/2)
        self.is_busy = False

    def _to_hz(self, mixer_bw_sel: Bandwidths) -> float:
        """Converts MixerBW enumeration to bandwidth in Hz."""
        mixer_base_filter_frequency = 11.1
        mixer_filter_step_factor = 2.0
        return mixer_base_filter_frequency * mixer_filter_step_factor**mixer_bw_sel.value

    def start_execute(
            self, start_frequency: float, end_frequency: float, frequency_step: float,
            sweep_amplitude: float,
            input_source: InputSource,
            input_range: InputRanges,
            mixer_bw_select: Bandwidths,
            reference_phase: float, output: FrequencySweepOutput) -> float:
        """Prepares and executes the Frequency Sweep.

        Parameters
        ----------
        start_frequency
            Start frequency [Hz]
        end_frequency
            End frequency [Hz]
        frequency_step
            Frequency difference between two consecutive points [Hz]
        sweep_amplitude
            Normalized Amplitude [0..1.0]
        input_source: InputSource
            Lock-in input channel
        input_range: InputRanges
            Input range switch
        mixer_bw_select : Bandwidths
            Mixer bandwidth
        reference_phase : float
            Phase shift of the reference output relative to the internal reference [°]
        output :  FrequencySweepOutput
            Selects the output

        Returns
        ----------
        total_time: float
            returns the calculated measuring time in [s]
        """
        sweep_amplitude = max(min(float(sweep_amplitude), 1.0), 0.0)
        step_time = 1/self._to_hz(mixer_bw_select)
        settle_time = 100 * step_time
        points = int((end_frequency - start_frequency)/frequency_step) + 1

        self._analyzer.operating_mode.value = self._analyzer.OperatingMode.LockIn
        self._analyzer.reference_phase.value = reference_phase
        self._analyzer.input.value = self.input_sources_to_lu_map[input_source]

        self._system_infra.main_in_2_gain.value = self.input_range_to_gain_map[input_range]

        # activate output for modulation
        self.output_setup = self.Output[output.name](self._ll)

        self.measure_time = self._start(
            start_frequency, end_frequency, points, step_time, settle_time,
            float(sweep_amplitude) * (self._analyzer.current_reference_amplitude.value_max)
        )
        return self.measure_time

    def finish_execution(self) -> tuple[np.ndarray, np.ndarray]:
        """ cleanup freq execution and extract data

        result
        -------
            two dimensional array with measured data (complex measurement data, frequency array)
        """
        self._finish()

        # cleanup and restore original setting of output
        del self.output_setup
        self.output_setup = None

        return self._get_active_data()

    def is_executing(self) -> bool:
        """ Polls the measuring status.

        Returns
        -------
        returns True if still measuring. False if finished

        """
        if self.is_busy:
            return (time.time() - self.start_time) <= self.measure_time
        return False

    def get_current_sweep_frequency(self) -> float:
        cur_freq =  self._analyzer.reference_frequency.value
        return cur_freq

    def execute(self, *args, **kwargs):
        """ Do the freq sweep and wait until sweep is finished.
        If blocking is not desired, then use the commands start_execute(), is_executing() and finish_execute()

        Parameters
        ----------
        See start_execute()

        Result
        ------
        see result of finish_execute()
        """

        total_time = self.start_execute(*args, **kwargs)

        print(f"Wait for {total_time:.1f}s.")
        while self.is_executing():
            time.sleep(0.1)

        return self.finish_execution()

    def bode_plot(self, complex_transfer: np.ndarray, frequencies: np.ndarray):
        """Plots Frequency sweep data to Bode Plot.

        complex_transfer
            transfer function as complex numbers
        frequencies
            frequencies where the complex transfer function is given.
        """
        plt.figure()

        plt.subplot(2, 1, 1)
        plt.plot(frequencies, np.abs(complex_transfer))
        plt.title('2nd Lock-In Amplitude - Frequency Sweep')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Amplitude V')

        plt.subplot(2, 1, 2)
        plt.plot(frequencies,
            np.unwrap(np.angle(complex_transfer, deg=True), discont=180))
        plt.title('2nd Lock-In Phase - Frequency Sweep')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Phase shift [°]')

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    """This test requires hardware:
    C3000: Connect cable connectors *Out B* and *User In 1*.
    CX: Connect cable connectors *Fast Out* and *User Input 1*.
    """
    spm_ctrl = nanosurf.SPM()
    spm_ctrl.application.Visible = True
    ll = spm_ctrl.lowlevel
    my_fs = FrequencySweep(spm_ctrl)

    # test if all output configurations work
    for name, output in my_fs.Output.items():
        try:
            my_output = output(ll)
        except:
            print("problem with output : " + name + ":")
            raise
        else:
            del my_output

    data = my_fs.execute(
        start_frequency=100e3, end_frequency=1e6,
        frequency_step=20e3, sweep_amplitude=0.3,
        input_source=InputSource.UserIn1,
        input_range=InputRanges.Full,
        mixer_bw_select=Bandwidths.Hz_360,
        reference_phase=0.0,
        output=FrequencySweepOutput.FastUser_OutB
    )
    my_fs.bode_plot(data[0], data[1])
