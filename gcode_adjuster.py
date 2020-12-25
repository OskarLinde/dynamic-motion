from math import sqrt, isnan
import move
import discretize

def norm(vector):
    return sqrt(sum([x**2 for x in vector]))

def distance(p1, p2):
    return norm([p2[i]-p1[i] for i in range(len(p1))])

# return True if the move was processed
def process(source, destination, target_speed, e_relative, motion_parameters, curve_parameters, calibration_adjustment):

    calibration_adjustment(destination[2])

    e_offset = source[3] # improve conditioning by centering extrusion around zero
    source[3] -= e_offset
    destination[3] -= e_offset

    move_distance = distance(source[:3], destination[:3]) # euclidian distance in xyz space

    if move_distance == 0:
        # extruder-only move
        if distance(source, destination) == 0:
            return True # a non-move, ignore

        return False # optional: don't adjust extruder-only moves

        target_speed = min(target_speed, motion_parameters.non_motion_max_speed)
        target_accel = motion_parameters.non_motion_accel
        target_jerk = motion_parameters.non_motion_jerk
    else:
        target_speed = min(target_speed, motion_parameters.max_speed)
        target_accel = motion_parameters.accel
        target_jerk = motion_parameters.jerk

    move_profile = move.generate_move(source, destination, max_speed = target_speed, max_accel = target_accel, max_jerk = target_jerk, dynamic_model = motion_parameters.dynamic_model, axis_limits = motion_parameters.axis_limits)
    
    if not move_profile:
        # A zero move. Skip it and continue.
        return True

    points = discretize.linear_interpolate(move_profile, curve_parameters.tolerances, curve_parameters.min_dt)
        
    for j in range(1, len(points[0])):
        last = points[:,j-1]
        curr = points[:,j]
        # how long is the move in time
        dt = curr[-1] - last[-1]
        # and in distance
        ds = distance(last[:3], curr[:3])
        
        if ds == 0:
            ds = distance(last, curr)

        feedrate = ds / dt

        if e_relative:
            e_value = curr[3] - last[3]
        else:
            e_value = curr[3] + e_offset

        if isnan(norm(curr)) or isnan(e_value) or isnan(feedrate):
            assert False, "Sanity Check Failed: NaN encountered in output, aborting"

        print(f'G1 X{curr[0]:.4f} Y{curr[1]:.4f} Z{curr[2]:.4f} E{e_value:.5f} F{60 * feedrate:.3f}')
    
    return True
