from math import inf, nan, isnan
import matplotlib.pyplot as plt
import numpy as np
import sys
import gcode_parser
import matplotlib as mpl
import argparse
#mpl.use('tkagg')


parser = argparse.ArgumentParser(description='Visualize the motion profiles of a slice of a G-Code file')
parser.add_argument('file', type=argparse.FileType('r'), nargs='?', default=(None if sys.stdin.isatty() else sys.stdin), help='G-Code file to be processed (or stdin)')
parser.add_argument('-z', type=float, help='the z height for the slice in mm', required=True)
parser.add_argument('-e', type=float, default=0.01, help='the z tolerance for the slice in mm (default: 0.01 mm)')

args = parser.parse_args()

zs = set()

current_x = nan
current_y = nan
current_z = nan
current_e = nan
current_f = nan

offset_e = 0
e_relative = False

output = []

for line in args.file.readlines():
    c = gcode_parser.parse(line)

    if c and 'G' in c:
        if c['G'] == 0 or c['G'] == 1:            
            current_x = c['X'] if 'X' in c else current_x
            current_y = c['Y'] if 'Y' in c else current_y
            current_z = c['Z'] if 'Z' in c else current_z
            
            current_f = c['F'] if 'F' in c else current_f

            last_e = current_e
            if e_relative:
                current_e += c['E'] if 'E' in c else 0
            else: 
                current_e = c['E'] if 'E' in c else current_e

            # TODO: add support for relative E moves
            new_pos = (current_x, current_y, current_z, current_e + offset_e, current_f / 60)

            zs.add(current_z)

            dist = inf
            if output:
                dist = np.linalg.norm(np.array(new_pos[:4])-np.array(output[-1][:4]))
            
            if dist > 0 and not isnan(current_f + current_x + current_y + current_z + current_e) and abs(current_z - args.z) < args.e:
                output.append(new_pos)
        if c['G'] == 92:
            if 'E' in c:
                if isnan(current_e):
                    current_e = 0
                offset_e += current_e - c['E']
                current_e = c['E']
    if c and 'M' in c:
        if c['M'] == 82:
            e_relative = False
        if c['M'] == 83:
            e_relative = True


if not output:
    print(f'No slice found at {args.z}. Available slices:')
    print(f'   {sorted(list(zs))}')
    sys.exit(1)

output = np.array(output)
d_euclidean = np.linalg.norm(output[1:,0:3] - output[:-1,0:3], axis=1)
d_extruder = np.abs(output[1:,3] - output[:-1,3])
dist = [d_euclidean[i] if d_euclidean[i] > 0 else d_extruder[i] for i in range(len(d_euclidean))]
time = dist / output[1:,4]
t = np.cumsum(time)

ax = plt.subplot(2,1,1)
ax.plot(t, output[1:,0], 'o-', markersize = 2, label = '$X$')
ax.plot(t, output[1:,1], 'o-', markersize = 2, label = '$Y$')
ax.plot(t, output[1:,3], 'o-', markersize = 2, label = '$E$')
ax.margins(0, 0.01, tight=True)
ax.legend()
plt.ylabel('mm')
ax2 = plt.subplot(2,1,2, sharex = ax)

velocity = (output[2:,:4]-output[1:-1,:4])/(np.transpose([t[1:]-t[:-1]]))
ax2.step(t[:-1], velocity[:,0], where='post', label = '$\\dot X$')
ax2.step(t[:-1], velocity[:,1], where='post', label = '$\\dot Y$')
ax2.step(t[:-1], velocity[:,3], where='post', label = '$\\dot E$')
plt.xlabel('time (s)')
plt.ylabel('mm/s')
ax2.legend()

plt.gcf().tight_layout()
plt.show()
