""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""
from nanosurf.lib.datatypes import sci_stream
import numpy as np
import math
from PySide2 import QtWidgets
import nanosurf.lib.datatypes.sci_val as sci_val
from nanosurf.lib.gui import nsf_sci_edit, nsf_tables, nsf_plots, bind_gui
from nanosurf.lib.math import sci_math 
from app import module_base
from app import app_gui
from modules.scan_module import module, settings

class ResultTableID(nsf_tables.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    Items = 0
    Marker_X = 1
    Marker_Y = 2
    Noise_Floor = 3

""" some usefull list of allowed prefixes used by nsf_sci_edit widgets"""
allowed_count_units = [sci_val.up.Prefix.base]
allowed_time_units = [sci_val.up.Prefix.base, sci_val.up.Prefix.milli]
allowed_meter_units = [sci_val.up.Prefix.milli, sci_val.up.Prefix.micro, sci_val.up.Prefix.nano]

class ScanScreen(module_base.ModuleScreen):
    def __init__(self):
        super().__init__()

    def do_setup_screen(self, module: module.ScanModule):
        """ create here your gui with all controlls and their layout"""
        self.module = module

        # left layout - main controls ------------------------------------------------------------

        self.scival_image_size = nsf_sci_edit.NSFSciEdit("Image Size")
        self.scival_image_size.set_allowed_prefix_ids(allowed_meter_units)
        self.scival_image_size.set_prefix_id(sci_val.up.Prefix.micro)
        self.scival_image_size.set_precision(2)
        self.scival_image_size.set_value_min_max(0.0, 1.0)

        self.scival_time_per_line = nsf_sci_edit.NSFSciEdit("Time per Line")
        self.scival_time_per_line.set_allowed_prefix_ids(allowed_time_units)
        self.scival_time_per_line.set_prefix_id(sci_val.up.Prefix.base)
        self.scival_time_per_line.set_precision(2)
        self.scival_time_per_line.set_value_min_max(0.01, 5.0)

        self.scival_points = nsf_sci_edit.NSFSciEdit("Data points")
        self.scival_points.set_allowed_prefix_ids(allowed_count_units)
        self.scival_points.set_prefix_id(sci_val.up.Prefix.base)
        self.scival_points.set_precision(0)
        self.scival_points.set_value_min_max(2, 1024)
        
        self.label_channel_dir = QtWidgets.QLabel("Channel")
        self.combo_channel_dir = QtWidgets.QComboBox()
        self.combo_channel_dir.addItems(settings.ChannelNames)
        
        self.button_start_stop = QtWidgets.QPushButton("Start")

        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_left.addWidget(self.scival_image_size)
        self.layout_left.addWidget(self.scival_time_per_line)
        self.layout_left.addWidget(self.scival_points)
        self.layout_left.addWidget(self.label_channel_dir)
        self.layout_left.addWidget(self.combo_channel_dir)
        self.layout_left.addStretch()
        self.layout_left.addWidget(self.button_start_stop)

        # mid layout - plots and result ---------------------------------------------------------
        self.chart_plot = nsf_plots.NSFChart()
        self.colormap_plot = nsf_plots.NSFColormap()
        self.spec_plot = nsf_plots.NSFChart(logmodex=True, logmodey=True)

        self.check_show_histogram = QtWidgets.QCheckBox("Show Histogram")
        self.check_show_backward = QtWidgets.QCheckBox("Show Backward line")
        self.check_show_power_spec = QtWidgets.QCheckBox("Show Powerspectrum")
        self.tableResults = nsf_tables.NSFNameValueTable(ResultTableID)
        self.tableResults.define_entry(ResultTableID.Items,"Current line")
        self.tableResults.define_entry(ResultTableID.Marker_X,"Peak X")
        self.tableResults.define_entry(ResultTableID.Marker_Y,"Peak Y")
        self.tableResults.define_entry(ResultTableID.Noise_Floor,"Noise floor")

        self.layout_mid  = QtWidgets.QVBoxLayout()
        self.layout_color_plot  = QtWidgets.QHBoxLayout()
        self.layout_color_plot.addWidget(self.colormap_plot)
        self.layout_color_plot.addWidget(self.colormap_plot.histogram)
        self.layout_colormap  = QtWidgets.QVBoxLayout()
        self.layout_colormap.addLayout(self.layout_color_plot)
        self.layout_colormap.addWidget(self.check_show_histogram)

        self.layout_line_chart  = QtWidgets.QVBoxLayout()
        self.layout_line_chart.addWidget(self.chart_plot)
        self.layout_line_chart.addWidget(self.check_show_backward)
        self.layout_spec_chart  = QtWidgets.QVBoxLayout()
        self.layout_spec_chart.addWidget(self.spec_plot)
        self.layout_spec_chart.addWidget(self.check_show_power_spec)
        self.layout_charts  = QtWidgets.QVBoxLayout()
        self.layout_charts.addLayout(self.layout_line_chart)
        self.layout_charts.addLayout(self.layout_spec_chart)
        self.layout_plots  = QtWidgets.QHBoxLayout()
        self.layout_plots.addLayout(self.layout_colormap)
        self.layout_plots.addLayout(self.layout_charts)
        self.layout_mid.addLayout(self.layout_plots)
        self.layout_mid.addWidget(self.tableResults)

        # right layout - additional user inputs

        self.layout_right= QtWidgets.QVBoxLayout()
        # self.layout_right.addSpacerItem(app_gui.StdVSpacer())

        # set GUI controls
        self.screen_layout = QtWidgets.QHBoxLayout()
        # stretch only plot area and keep controls fix in size
        self.screen_layout.addLayout(self.layout_left, 0)
        self.screen_layout.addLayout(self.layout_mid,  1) 
        self.screen_layout.addLayout(self.layout_right,0)
        self.setLayout(self.screen_layout)

        self.bind_gui_elements()
        self.init_plot()
        self.enter_gui_state_idle()

    def bind_gui_elements(self):
        """ connect here all gui widgets to settings of the module or any other source"""
        
        # binding ProVal to widgets ensure that they are alway in sync 
        bind_gui.connect_to_property(self.combo_channel_dir, self.module.settings.channel_id)
        bind_gui.connect_to_property(self.scival_image_size, self.module.settings.image_size)
        bind_gui.connect_to_property(self.scival_time_per_line, self.module.settings.time_per_line)
        bind_gui.connect_to_property(self.scival_points, self.module.settings.points_per_line)
        bind_gui.connect_to_property(self.check_show_backward, self.module.settings.show_backward)
        bind_gui.connect_to_property(self.check_show_power_spec, self.module.settings.show_power_spec)
        
        self.check_show_histogram.stateChanged.connect(self._show_histogram_clicked)
        self.check_show_backward.stateChanged.connect(self._show_backward_clicked)
        self.check_show_power_spec.stateChanged.connect(self._show_power_spec_clicked)

        # buttons have to be connected separately
        self.button_start_stop.clicked.connect(self.on_button_start_stop_clicked)    
        
        # listen to signals from the core module to react and update the gui
        self.module.sig_work_start_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_stop_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_active.connect(self.enter_gui_state_active)
        self.module.sig_work_done.connect(self.enter_gui_state_idle)
        self.module.sig_new_data_available.connect(self.show_new_data)
        self.module.sig_data_invalid.connect(self.set_data_invalid)

    def init_plot(self):
        #x , y , z = self.makeSine2D(1.0)
        self.colormap_plot.set_title(f"Scan image - {settings.ChannelNames[self.module.settings.channel_id.value]}")
        self.colormap_plot.set_label(nsf_plots.NSFColormap.Axis.bottom, "X-Axis")
        self.colormap_plot.set_unit(nsf_plots.NSFColormap.Axis.bottom, "m")
        self.colormap_plot.set_label(nsf_plots.NSFColormap.Axis.left, "Y-Axis")
        self.colormap_plot.set_unit(nsf_plots.NSFColormap.Axis.left, "m")  
        self.colormap_plot.set_unit(nsf_plots.NSFColormap.Axis.z, "m")  

        scan_line = np.linspace(0, self.module.settings.image_size.value, self.module.settings.points_per_line.value)
        self.colormap_plot.set_xy_range(scan_line, scan_line)
        self.colormap_plot.set_data_points(self.module.settings.points_per_line.value, self.module.settings.points_per_line.value)

        self.chart_plot.set_title(f"Current line chart - {settings.ChannelNames[self.module.settings.channel_id.value]}")
        self.chart_plot.set_label(nsf_plots.NSFChart.Axis.bottom, "X-Axis")
        self.chart_plot.set_unit(nsf_plots.NSFChart.Axis.bottom, "m")
        self.chart_plot.set_label(nsf_plots.NSFChart.Axis.left, "Data")
        self.chart_plot.set_unit(nsf_plots.NSFChart.Axis.left, "m")  
        self.chart_plot.plot.setXRange(0, self.module.settings.image_size.value)
        self.chart_plot.clear_plots()

        self.spec_plot.set_title(f"Sepctrum of - {settings.ChannelNames[self.module.settings.channel_id.value]}")
        self.spec_plot.set_label(nsf_plots.NSFChart.Axis.bottom, "Frq")
        self.spec_plot.set_unit(nsf_plots.NSFChart.Axis.bottom, "Hz")
        self.spec_plot.set_label(nsf_plots.NSFChart.Axis.left, "Amplitude")
        self.spec_plot.set_unit(nsf_plots.NSFChart.Axis.left, "")  
        self.spec_plot.clear_plots()

    def makeSine2D(self, scale):
        n = scale
        X, Y = np.meshgrid(np.linspace(-4*math.pi, 4*math.pi, 199), np.linspace(-4*math.pi, 4*math.pi, 200))
        Z = (1/2)**n * (np.cos(2**n * X) + np.cos(2**n * Y))
        data = [X, Y, Z]
        return data        

    def on_button_start_stop_clicked(self):
        if self.module.is_worker_busy():
            self.module.stop_worker()
        else:
            self.module.start_worker()

    def _show_histogram_clicked(self):
        if self.check_show_histogram.isChecked():
            self.colormap_plot.histogram.show()
        else:
            self.colormap_plot.histogram.hide()

    def _show_backward_clicked(self):
        self.update_plot()

    def _show_power_spec_clicked(self):
        self.update_plot()

    def enter_gui_state_wait(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True)

    def enter_gui_state_active(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_worker_busy())
        self.init_plot()

    def enter_gui_state_idle(self):
        self.set_parameter_widget_enable_state(enabled=True)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_worker_busy())

    def set_parameter_widget_enable_state(self, enabled: bool = True):
        self.scival_image_size.setEnabled(enabled)
        self.scival_time_per_line.setEnabled(enabled)
        self.scival_points.setEnabled(enabled)
        self.combo_channel_dir.setEnabled(enabled)

    def start_stop_button_state(self, wait: bool = False, stop_state: bool = False):
        if wait:
            self.button_start_stop.setEnabled(False)
            self.button_start_stop.setText("Wait...")
        else:
            self.button_start_stop.setEnabled(True)
            self.button_start_stop.setText("Stop" if stop_state else "Start")

    def show_new_data(self):
        self.update_plot()
        self.update_result()

    def set_data_invalid(self):
        self.chart_plot.clear_plots()
        self.tableResults.clear_values()

    def update_result(self):
        res = self.module.get_worker_result()
        self.tableResults.set_value(ResultTableID.Items, res.scan_line_index, "", precision=0)

    def update_plot(self): 
        current_data = self.module.get_worker_result()
        if current_data.stream.get_stream_length() > 1:
            # color map update
            self.colormap_plot.plot_channel(current_data.stream.get_channel(0), current_data.scan_line_index)

            self.chart_plot.plot_stream(current_data.stream, 0, layer_index=0)
            
            if self.module.settings.show_backward.value:
                self.chart_plot.plot_stream(current_data.stream, 1, layer_index=1)
            else:
                self.chart_plot.plot_data([], layer_index=1)
            
            calc_power_spec = self.module.settings.show_power_spec.value
            samplefrq = current_data.stream.get_stream_length()/self.module.settings.time_per_line.value
            spec = sci_math.calc_fft(current_data.stream.get_channel(0), samplerate=samplefrq, powerspectrum=calc_power_spec)
            #spec = sci_math.create_compress_log_spectrum_mean(spec)
            found, peak_x ,peak_y = sci_math.find_highest_peak(spec)
            if found:
                self.spec_plot.set_marker(peak_x, peak_y)
                self.tableResults.set_value(ResultTableID.Marker_X, peak_x, spec.get_stream_unit())
                self.tableResults.set_value(ResultTableID.Marker_Y, peak_y, spec.get_channel(0).unit)
            else:
                self.spec_plot.clear_marker()
                self.tableResults.clear_value(ResultTableID.Marker_X)
                self.tableResults.clear_value(ResultTableID.Marker_Y)
            
            noise_floor = sci_math.get_noise_floor(spec)
            self.spec_plot.plot_stream(spec)
            self.spec_plot.plot_data(y=[noise_floor for i in range(spec.get_stream_length())], x=spec.get_stream_range().value, layer_index=1)
            self.tableResults.set_value(ResultTableID.Noise_Floor, noise_floor, spec.get_channel(0).unit)
