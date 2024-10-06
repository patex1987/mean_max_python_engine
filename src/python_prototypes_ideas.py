def path_printer(s=500, m=0.5, v0=0, f=0.2, max_time=10):
    for t in range(1, max_time + 1):
        res = ((s * m) / ((t**2) * (1 - f))) - (v0 * m / t)
        print(f'round: {t}, throttle: {res}')
        if res < 300:
            break


def path_printer_max_default(s=500, mass=0.5, v0=0, f=0.2, max_time=10):
    """
    how to control the throttle to reach the desired distance (s)

    TODO: we still don't know how to stop at a given a point. options are:
    - once we reach the desired distance, we can start to move in the opposite direction with the same speed. so essentially it stops there
    - once we reach the desired distance, we use wait (still dont what happens with wait, does it move with the actual speed vector?)
    """

    s_left = s
    v = v0
    for t in range(1, max_time + 1):
        res = ((s * mass) / (t**2 * (1 - f))) - (v * mass / t)
        if res >= 300:
            res = 300
        v += res
        s_left = s_left - v
        print(f'round: {t}, speed: {v} throttle: {res}, distance left: {s_left}')
        if s_left <= 0:
            break


def path_printer_max_default(s=500, mass=0.5, v0=0, f=0.2, max_time=10):
    """
    how to control the throttle to reach the desired distance (s)

    TODO: we still don't know how to stop at a given a point. options are:
    - once we reach the desired distance, we can start to move in the opposite direction with the same speed. so essentially it stops there
    - once we reach the desired distance, we use wait (still dont what happens with wait, does it move with the actual speed vector?)
    """

    s_left = s
    v = v0
    print(f'BEFORE speed: {v} throttle: 0, distance left: {s_left}')
    for t in range(1, max_time + 1):
        res = ((s_left * mass) / ((1 - f))) - (v * mass)
        if res >= 300:
            res = 300
        v = (v + (res / mass)) * (1 - f)
        s_left = s_left - v
        if res <= 0:
            res = 0

        print(f'round: {t}, speed: {v} throttle: {res}, distance left: {s_left}')
        if s_left <= 0:
            break
