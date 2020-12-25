# Dynamic Motion
## Experimental Model-Based Control G-Code Pre-Processor for 3D Printing

This is an experimental Python script that pre-processes (or post-process) G-Code from a slicer to incorporate model-based control using a spring-damper model to reduce or eliminate ringing. The script turns linear moves into simulated segmented s-curve profiles with dynamic correction. See [https://digitalvision.blog/spring-damper-control](https://digitalvision.blog/spring-damper-control) for details.

### Limitations
* This code will generate a substantial amount of small segmented moves that may overwhelm the firmware motion planner. On RepRap Firmware 2.03 or later is required to support the `M566 P1` jerk policy. The granularity of segmented output can be controlled in `config.py` to a degree, but the results of reducing the segment counts are largely untested.
* This code does not (yet) support smoothing of approximately curved segments. The print quality of radii and curves will be poor.

## Configuration

*Note:* Edit the file `config.py` before usage.

## Usage

```sh
python3 process.py < input_file.gcode > output_file.gcode
```
## Calibration
Here's a suggested approach for calibrating the spring-damper parameters. Slice a plain 20x20x20mm cube. (In Slic3r Add Shape -> Box). Use “Spiral Vase” mode if possible, otherwise 1 perimeter. 1 single bottom layer will speed up the print as you will print many of these. If you trust your bed adhesion, you can even go without a bottom layer.  Ensure that the slicer outputs the print speed that you want to calibrate for. You may want to inspect the G-Code to make sure. It’s possible that you need to reduce your slicers “minimum layer time” to get it to the right speed. If your part cooling fan is unable to keep the part cooled during printing, reduce the layer height (and/or increase the size of the cube). I found 0.2 mm to work fine up to 80mm/s, but I needed to go down to 0.1 mm layers for 120mm/s.

In `config.py` edit the `calibration_adjustment(z)` part of the config script to sweep parameters as a function of the z-height. 
1. Enter your target acceleration and jerk values to calibrate for under `motion_parameters` `accel` and `jerk` respectively. 5-10 m/s² acceleration and 1-3 km/s³ jerk seem to be reasonable ranges, although you may want to go even lower initially.
2. Enter your initial pressure advance k value for the E axis in the `move.pressure_advance_parameters(k=…)` section of the `dynamic_model ` array. Use a value of `0.0` if you don't know your approximate value. You can calibrate this later.
3. Start with calibrating the spring `f_n` for X and Y. 
a. On a delta-printer you can probably do both axes at the same time if you want, but in general and (definitely on a cartesian printer) you should only change one variable at the time. Start with sweeping a broad range of values from the bottom to the top of the print. In order to isolate one axis at the time, set the acceleration limit of the other axis to a very low value. E.g `move.axis_limits(speed = 500, accel=500)`. Don’t go below ~20 Hz with 10 m/s² accelerations to avoid excessive corrections (if you go too low, your printer will lose steps as its tring to shake itself apart). Increase the lower limit with higher accelerations. A good starting range may be 30–100 Hz. Printing a regular print with high accelerations and measuring the ringing frequency with a ruler could be a good way to narrow down the interval.
4. Observe the ringing pattern on the print. You should see a phase inversion happen somewhere on the print. Measure the height and calculate the `f_n` value. Enter the `f_n` value into the `motion_parameters` `dynamic_model` for the corresponding axis.
5. Calibrate zeta by keeping `f_n` constant and sweep across zeta value. Start with 0.0 at the bottom and go up to maybe 0.5 at the top. You may get a similar phase inversion at a certain z-height. It is also possible that the ideal `zeta` value is very close to zero.
6. Enter the zeta values and repeat step 3, possibly with a more zoomed in sweep. If you zoom in too much, it may be hard to clearly spot the ideal location.
7. Repeat another zeta calibration if necessary.
8. Repeat for the other axis.
9. You may want to recalibrate your pressure advance k parameter. I found I had to use a slightly lower setting with the substantially higher acceleration this method allows. Note that you can’t use the machine pressure advance setting – you need to use the one in the script.

## License
[MIT](https://choosealicense.com/licenses/mit/)
