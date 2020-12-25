from motion_profiles import s_curve_profile
from pytest import approx

def validate_s_curve_solution(acceleration, distance, t):
    
    # acceleration should be zero at the start
    assert acceleration[0] == approx(0)
    # and at the end
    assert acceleration[t] == approx(0)

    velocity = acceleration.integrate()

    # velocity should start as zero
    assert velocity[t] == approx(0, abs=1e-6)
    # and end as zero
    assert velocity[0] == approx(0)

    position = velocity.integrate()

    # position should start at zero
    assert position[0] == approx(0)
    # and end at distance
    assert position[t] == approx(distance, rel=1e-5)

def run_case(distance, speed, accel, jerk):
    profile = s_curve_profile(distance, speed, accel, jerk)
    t = profile.range_max()

    validate_s_curve_solution(profile, distance, t)

def test_s_curve_profile():
    for i in range(8):
        speed = 10
        accel = 1000
        jerk  = 1000

        # blow up different combinations of variables to force all different corner cases
        if i & 1 == 1:
            speed **= 2
        if i & 2 == 2:
            accel **= 2
        if i & 4 == 4:
            jerk **= 2

        run_case(0, speed, accel, jerk)
        run_case(1, speed, accel, jerk)
        run_case(10, speed, accel, jerk)
        run_case(100, speed, accel, jerk)
        run_case(1000, speed, accel, jerk)
        run_case(10000, speed, accel, jerk)
        
    
