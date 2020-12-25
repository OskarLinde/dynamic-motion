#!/usr/bin/env python3

import gcode_parser
from dataclasses import dataclass
import sys
import copy
from math import nan, isnan
import gcode_adjuster
from config import *

MIN_PYTHON = (3, 7)
assert sys.version_info >= MIN_PYTHON, f"requires Python {'.'.join([str(n) for n in MIN_PYTHON])} or newer"

@dataclass
class State:
    modifying = False
    e_relative = False
    g_relative = False
    x = nan
    y = nan
    z = nan
    e = nan
    f = nan
    autostart = True

current_state = State()

count = 0
for line in sys.stdin.readlines():
    count += 1
    c = gcode_parser.parse(line)

    consumed = False

    if c and 'G' in c:
        # detect G0/1
        if not current_state.g_relative and (c['G'] == 0 or c['G'] == 1):
            new_state = copy.deepcopy(current_state)
            if 'X' in c:
                new_state.x = c['X']
            if 'Y' in c:
                new_state.y = c['Y']
            if 'Z' in c:
                new_state.z = c['Z']
            if 'E' in c:
                if current_state.e_relative:
                    new_state.e += c['E']
                else:
                    new_state.e = c['E']
            if 'F' in c:
                new_state.f = c['F']

            if c['G'] == 1 and current_state.modifying:
                
                if gcode_adjuster.process([current_state.x, current_state.y, current_state.z, current_state.e],
                                        [new_state.x, new_state.y, new_state.z, new_state.e], new_state.f/60, current_state.e_relative, motion_parameters, curve_parameters, calibration_adjustment):
                    consumed = True
                else:
                    if not 'F' in c:
                        # We likely have an extruder-only move, but without a speed tagged. We will need to patch it.
                        print(line.rstrip() + f" F{new_state.f} ; note: added F to extruder-only move")
                        consumed = True

            current_state = new_state

            if current_state.autostart and not current_state.modifying and not isnan(current_state.x) and not isnan(current_state.y) and not isnan(current_state.z) and not isnan(current_state.e) and not isnan(current_state.f):
                current_state.modifying = True
                disable_acceleration_control()
            
            if count % 100 == 0:
                print(f'\rz = {current_state.z:.2f} mm', file=sys.stderr, end='', flush=True)

        if c['G'] == 92:
            if 'X' in c:
                current_state.x = c['X']
            if 'Y' in c:
                current_state.y = c['Y']
            if 'Z' in c:
                current_state.z = c['Z']
            if 'E' in c:
                current_state.e = c['E']
        if c['G'] == 91:
            # we don't support relative G0/G1 moves, leave unmodified
            current_state.g_relative = True
            if current_state.modifying:
                current_state.modifying = False
                restore_acceleration_control()
            # declare ourselves lost
            current_state.x = nan
            current_state.y = nan
            current_state.z = nan
        if c['G'] == 90:
            current_state.g_relative = False

    if c and 'M' in c:
        if c['M'] == 82:
            current_state.e_relative = False
        if c['M'] == 83:
            current_state.e_relative = True
    
    if '--- MODIFY START ---' in line:
        if not current_state.modifying:
            current_state.modifying = True
            disable_acceleration_control()
    if '--- MODIFY END ---' in line:
        current_state.autostart = False # after encountering a "--- MODIFY END ---", smoothing doesn't resume until a "--- MODIFY START ---"
        if current_state.modifying:
            current_state.modifying = False
            restore_acceleration_control()

    if not consumed:
        print(line, end='')

if current_state.modifying:    
    restore_acceleration_control()

print(f'\rDone.         ', file=sys.stderr, flush=True)
