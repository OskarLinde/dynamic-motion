import move

# EXAMPLE CONFIGURATION, PLEASE EDIT BEFORE USING
class motion_parameters:
    dynamic_model = [
        move.spring_damper_parameters(f_n = 60.5, zeta = 0), # x
        move.spring_damper_parameters(f_n = 52, zeta = 0.025), # y
        #move.asymmetric_spring_damper_parameters(f_n_negative = 52.5, f_n_positive = 56.9, zeta = 0.02), # y
        move.spring_damper_parameters(f_n = 0, zeta = 0.0), # z
        move.pressure_advance_parameters(k = 0.08)     # e
    ]
    max_speed = 200
    accel = 10000
    jerk = 2000000
    non_motion_max_speed = 100 # i.e. extrusion-only moves
    non_motion_accel = 20000
    non_motion_jerk  = 5000000
    axis_limits = [
        move.axis_limits(speed = 500), # x
        move.axis_limits(speed = 500), # y
        move.axis_limits(speed = 24, accel = 1000, jerk = 1000000), # z
        None, #e
    ]

# adjust a parameter dynamically based on the z height
def calibration_adjustment(z):
    # example
    value_min = 30
    value_max = 75
    z_max = 20     # mm

    value = z / z_max * (value_max - value_min) + value_min

    #motion_parameters.dynamic_model[0].zeta = value  # adjust x zeta
    #motion_parameters.dynamic_model[1].zeta = value  # adjust y zeta
    #motion_parameters.dynamic_model[0].f_n = value   # adjust x f_n
    #motion_parameters.dynamic_model[1].f_n = value   # adjust y f_n
    #motion_parameters.dynamic_model[1].f_n_negative = value   # adjust y f_n
    #motion_parameters.dynamic_model[1].f_n_positive = value   # adjust y f_n
    #motion_parameters.dynamic_model[3].k = value     # adjust pressure advance

# adjust these to adjust the linear interpolation and coarseness of the generated output
# reducing the tolerances will increase the size of the output file (and more likely cause the printer motion planner to choke)
class curve_parameters:
    tolerances = [
        0.002, # x (2µm)
        0.002, # y (2µm)
        0.050, # z (50µm)
        0.100, # e (0.1mm) # low tolerance to prevent pressure advance from adding nodes at the potential detriment of the xy spring-damper control
    ]
    min_dt = 1/200
    
def disable_acceleration_control():
    print('M566 P1') # RRF Jerk Policy 1
    print('M572 D0 S0') #  disable pressure advance
    print('M201 X100000 Y100000 Z100000 E100000') # disable acceleration
    print('M205 X10000 Y10000 Z10000 E10000') # infinite instantaneous velocity change

def restore_acceleration_control():
    print('M201 X2000 Y2000 Z2000 E2000') # reset acceleration
    print('M205 X10 Y10 Z10 E10000') # reset instantaneous velocity change

