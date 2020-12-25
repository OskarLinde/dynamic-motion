from math import *
import numpy as np
import polynomial as poly
import spline

from motion_profiles import s_curve_profile
from dataclasses import dataclass

import sys # TMP


@dataclass
class spring_damper_parameters:
    f_n: float  = 0
    zeta: float = 0

@dataclass
class asymmetric_spring_damper_parameters:
    f_n_positive: float = 0
    f_n_negative: float = 0
    zeta:         float = 0

@dataclass
class pressure_advance_parameters:
    k: float = 0

@dataclass
class axis_limits:
    speed: float = inf
    accel: float = inf
    jerk:  float = inf

# a machine vector is an np.array of coordinates [x, y, z, e, ...]. The first 3 are assumed to be euclidean x,y,z coordinates

# generate a spring-damper-corrected motion profile, return spline curves for each axis
def generate_move(source, destination, max_speed, max_accel, max_jerk, dynamic_model, axis_limits):
    delta = np.array(destination) - np.array(source)
    distance = np.linalg.norm(delta[0:3])

    if distance == 0:
        distance = np.linalg.norm(delta)

    if distance == 0:
        return None

    # determine acceleration curve (over the arc length)
    arc_acceleration = s_curve_profile(distance, max_speed, max_accel, max_jerk)
    #plot_spline_accel(arc_acceleration)
    arc_speed = arc_acceleration.integrate()
    arc_position = arc_speed.integrate()    

    positions = []
    # calculate spring-damper correction for each axis
    for i in range(len(delta)):
        k = delta[i] / distance

        position = arc_position * k

        if isinstance(dynamic_model[i], spring_damper_parameters):
            omega_n = dynamic_model[i].f_n * tau
            zeta    = dynamic_model[i].zeta

            if omega_n > 0:
                correction = arc_acceleration * (k * omega_n**-2) + arc_speed * (k * 2*zeta * omega_n**-1)
                position = position + correction

        elif isinstance(dynamic_model[i], asymmetric_spring_damper_parameters):
            omega_n_pos = dynamic_model[i].f_n_positive * tau
            omega_n_neg = dynamic_model[i].f_n_negative * tau
            b_div_m     = dynamic_model[i].zeta * (omega_n_pos + omega_n_neg)

            if omega_n_pos > 0 or omega_n_neg > 0:
                correction = spline.composite(spline.kinked_line(omega_n_neg**-2, omega_n_pos**-2), arc_acceleration * k + arc_speed * (k * b_div_m))
                position = position + correction

        elif isinstance(dynamic_model[i], pressure_advance_parameters):
            if dynamic_model[i].k > 0:
                corrected_speed = arc_speed * k + arc_acceleration * (k * dynamic_model[i].k)
                position = corrected_speed.integrate()

        positions.append(position + source[i])
    
    # check axis limits
    if axis_limits:
        throttle_speed = 1.0
        throttle_accel = 1.0
        throttle_jerk = 1.0
        eps = 1e-4

        for i in range(len(axis_limits)):
            if axis_limits[i]:
                speed = positions[i].differentiate()
                accel = speed.differentiate()
                jerk  = accel.differentiate()

                top_speed = max([abs(y) for y in speed.minmax()])
                top_accel = max([abs(y) for y in accel.minmax()])
                top_jerk  = max([abs(y) for y in jerk.minmax()])

                with np.errstate(divide='ignore'):
                    throttle_speed = min(throttle_speed, axis_limits[i].speed / top_speed)
                    throttle_accel = min(throttle_accel, axis_limits[i].accel / top_accel)
                    throttle_jerk  = min(throttle_jerk,  axis_limits[i].jerk / top_jerk)

        if throttle_jerk < 1 - eps:
            positions = generate_move(source, destination, max_speed, max_accel, max_jerk * throttle_jerk, dynamic_model, axis_limits)
        elif throttle_accel < 1 - eps:
            positions = generate_move(source, destination, max_speed, max_accel * throttle_accel, max_jerk * throttle_accel, dynamic_model, axis_limits)
        elif throttle_speed < 1 - eps:
            # HACK, throttle accel instead of speed, since this is likely due to too high spring compensation (a function of accel)
            positions = generate_move(source, destination, max_speed * throttle_speed**.25, max_accel * throttle_speed, max_jerk * throttle_speed, dynamic_model, axis_limits)
            #positions = generate_move(source, destination, max_speed * throttle_speed, max_accel, max_jerk, dynamic_model, axis_limits)

    # ensure that all curves have equal knots
    spline.harmonize_knots(positions)
    
    return positions 

