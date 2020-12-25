import spline
from math import sqrt
import numpy as np

# constant jerk for time T followed by -jerk until 2*T, yields p(T) = T**3 * jerk / 6, p(2*T) = T**3 * jerk
# solve for T given a symmetric motion profile, p(2*T) == distance/2
def s_curve_max_jerk_t(distance, jerk):
	return (distance / (2*jerk)) ** (1/3)

def s_curve_distance_during_jerk(jerk, jerk_time):
	return jerk * jerk_time**3
	
# peak speed when doing a jerk up ramp, immediately followed by a jerk down ramp
def constant_jerk_peak_speed(jerk_time, jerk):
	return jerk * (jerk_time**2)
	
def constant_jerk_time_to_max_speed(jerk, speed_to_hit):
	return (speed_to_hit / jerk) ** (1/2)
	
def s_curve_half_distance(jerk, jerk_time, constant_accel_time):
	return jerk * jerk_time * (1.5*(jerk_time * constant_accel_time) + (constant_accel_time**2)/2 + jerk_time**2)
	
def s_curve_time_to_half_distance(jerk, jerk_time, half_distance):
	# solve the above for constant_accel_time
	return 1/2 * (-3 * jerk_time + sqrt((8 * half_distance + jerk * (jerk_time**3))/(jerk*jerk_time))) + 2*jerk_time

def s_curve_time_to_max_speed(jerk, jerk_time, max_speed):
	max_accel = jerk * jerk_time
	coast_time = (max_speed - max_accel * jerk_time) / max_accel
	return coast_time + 2 * jerk_time
	
# simple symmetric s_curve_profile starting from 0 speed, 0 accel, ramping up and then down again
def s_curve_profile(distance, max_speed, max_accel, jerk):
    if distance == 0:
        return spline.curve([0],[0])
    
    time_to_constant_accel = max_accel / jerk

    max_jerk_time = s_curve_max_jerk_t(distance, jerk)
    speed_limit_time = constant_jerk_time_to_max_speed(jerk, max_speed)

    if max_jerk_time <= time_to_constant_accel or speed_limit_time <= time_to_constant_accel:

        # no constant acceleration phase
                
        # 2 cases: we hit (and are limited by) max speed or we don't
        peak_speed = constant_jerk_peak_speed(max_jerk_time, jerk)
        if peak_speed <= max_speed:
            # peak speed not hit; no coasting
            jerk_time = max_jerk_time
            peak_accel = jerk_time*jerk
            # resulting acceleration profile:
            accel = [(0, 0), (jerk_time, peak_accel), (3*jerk_time, -peak_accel), (4*jerk_time, 0)]
        else:
            # peak speed hit; add coasting
            jerk_time = constant_jerk_time_to_max_speed(jerk, max_speed)
            peak_accel = jerk_time * jerk
            
            assert peak_accel <= max_accel
                
            jerk_distance = s_curve_distance_during_jerk(jerk, jerk_time)

            coasting_distance = distance - jerk_distance * 2
            assert coasting_distance > 0

            coasting_time = coasting_distance / max_speed

            #resulting acceleration profile    
            accel = [(0,0), (jerk_time, peak_accel), (2*jerk_time, 0), (2*jerk_time + coasting_time, 0), (3*jerk_time + coasting_time, -peak_accel), (4*jerk_time + coasting_time, 0)]
    else:
        # add constant acceleration phase
        # we know (from the earlier condition) that we won't hit the speed limit until the constant acceleration phase
        jerk_time = time_to_constant_accel
        
        half_distance_time = s_curve_time_to_half_distance(jerk, jerk_time, distance/2)
        assert half_distance_time >= jerk_time*2
                
        time_to_max_speed = s_curve_time_to_max_speed(jerk, jerk_time, max_speed)
        
        if half_distance_time <= time_to_max_speed:
            # not speed limited, no coasting
            constant_accel_time = half_distance_time - 2*jerk_time
            
            #assert constant_accel_time > 0
            
            accel = [(0,0),(jerk_time, max_accel), (jerk_time + constant_accel_time, max_accel), (3*jerk_time + constant_accel_time, -max_accel), (2*constant_accel_time + 3*jerk_time, -max_accel), (2*constant_accel_time + 4*jerk_time, 0)]
            if constant_accel_time <= 0:
                accel = [(0,0),(jerk_time, max_accel), (3*jerk_time, -max_accel), (4*jerk_time, 0)]

        else:
            # speed limited, add coasting
            constant_accel_time = time_to_max_speed - 2*jerk_time
            accel_phase_distance = s_curve_half_distance(jerk, jerk_time, constant_accel_time)
            coasting_distance = distance - 2 * accel_phase_distance
            coasting_time = coasting_distance / max_speed

            accel = [(0,0),(jerk_time, max_accel), (jerk_time+constant_accel_time, max_accel), (2*jerk_time + constant_accel_time, 0),
            (coasting_time + 2*jerk_time + constant_accel_time, 0),
            (coasting_time + 3*jerk_time + constant_accel_time, -max_accel), (coasting_time + 2*constant_accel_time + 3*jerk_time, -max_accel), (coasting_time + 2*constant_accel_time + 4*jerk_time, 0)]

            if accel[4][0] == accel[3][0]: # coasting_time == 0
                del accel[4]
                
    a = np.array(accel)
    return spline.curve(a[:,0],a[:,1])


