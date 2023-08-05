""" Helper function to connect gui widgets to Property classes
Copyright Nanosurf AG 2021
License - MIT
"""
from PySide2 import QtWidgets
from nanosurf.lib.gui import nsf_sci_edit
from nanosurf.lib.datatypes import sci_val
from nanosurf.lib.datatypes.prop_val import PropVal

def connect_to_property(widget: QtWidgets.QWidget, prop: PropVal) -> bool:
   """
   Connect the value of a property to a widgets. Keeps the widget content and the property value in sync
   Note: Not every QWidget can be connected to any Property type. 
   """
   is_supported = True
   if isinstance(widget, nsf_sci_edit.NSFSciEdit) and isinstance(prop.var, sci_val.SciVal):
      widget.set_value(prop.value)
      widget.set_unit(prop.var.unit())
      prop.sig_value_changed.connect(lambda : 
         widget.set_value(prop.value)
      )
      widget.value_changed_event.connect(lambda : 
         prop.set_value(widget.value())
      )
   elif isinstance(widget, nsf_sci_edit.NSFSciEdit) and isinstance(prop.var, float):
      widget.set_value(prop.value)
      prop.sig_value_changed.connect(lambda : 
         widget.set_value(prop.value)
      )
      widget.value_changed_event.connect(lambda : 
         prop.set_value(widget.value())
      )
   elif isinstance(widget, nsf_sci_edit.NSFSciEdit) and isinstance(prop.var, int):
      widget.set_value(prop.value)
      widget.set_precision(0)
      prop.sig_value_changed.connect(lambda : 
         widget.set_value(prop.value)
      )
      widget.value_changed_event.connect(lambda : 
         prop.set_value(int(widget.value()))
      )
   elif isinstance(widget, QtWidgets.QLineEdit) and isinstance(prop.var, str):
      widget.setText(prop.value)
      prop.sig_value_changed.connect(lambda : 
         widget.setText(prop.value)
      )
      widget.textEdited.connect(lambda : 
         prop.set_value(widget.text())
      )
   elif isinstance(widget, QtWidgets.QCheckBox) and isinstance(prop.var, bool):
      widget.setChecked(prop.value)
      prop.sig_value_changed.connect(lambda : 
         widget.setChecked(prop.value)
      )
      widget.stateChanged.connect(lambda : 
         prop.set_value(widget.checkState() > 0)
      )
   elif isinstance(widget, QtWidgets.QLabel):
      widget.setText(str(prop.value))
      prop.sig_value_changed.connect(lambda : 
         widget.setText(str(prop.value))
      )
   elif isinstance(widget, QtWidgets.QComboBox) and isinstance(prop.var, int):
      widget.setCurrentIndex(prop.value)
      prop.sig_value_changed.connect(lambda : 
         widget.setCurrentIndex(prop.value)
      )
      widget.currentIndexChanged.connect(lambda : 
         prop.set_value(int(widget.currentIndex()))
      )
   else:
      is_supported = False

   assert is_supported, f"Error: Widget of type '{type(widget)}' cannot be connected to property of type '{type(prop.var)}'"
   return is_supported

   
   
  