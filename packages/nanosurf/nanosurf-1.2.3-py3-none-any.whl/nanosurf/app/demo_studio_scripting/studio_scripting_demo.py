# studio_scripting_demo client.py

import nanosurf
import nanosurf.lib.datatypes.sci_val as sci_val

studio = nanosurf.Studio()
if studio.connect():
    print(f"Available sessions: {studio.main.session.list()}")
    print(f"Connected with session = '{studio.session_id}'")

    # set a value 
    studio.spm.workflow.imaging.property.points_per_line.value = 200

    # set values with more direct access
    imaging = studio.spm.workflow.imaging
    imaging.property.scan_range_fast_axis.value = 2e-6
    imaging.property.scan_range_slow_axis.value = 2e-6

    # or even direct property shortening
    scan_mode = imaging.property.scan_mode
    scan_mode.value = scan_mode.EnumType.Single_Frame

    # call a workflow action
    studio.spm.workflow.imaging.start_imaging()

    # different methods to iterate over enum properties
    print("possible scan modes by list: "+str(imaging.property.scan_mode.enum))
    print("possible scan modes by enum: ")
    for mode in imaging.property.scan_mode.EnumType:
        print(mode)

    # converting a property to SciVal
    scan_range = sci_val.SciVal(imaging.property.scan_range_fast_axis)
    print(f"Fast scan range converted to SciVal is {scan_range}")
    print(f"But also this give the same result: {imaging.property.scan_range_fast_axis}")

    studio.disconnect()
else:
    print(f"Connecting to studio failed: {studio.last_error}")

