


def path_printer(s=500, m=0.5,v0=0, f=0.2, max_time = 10): 
    for t in range(1, max_time+1): 
        res = ((s*m)/((t**2)*(1-f))) - (v0*m/t) 
        print(f'round: {t}, throttle: {res}') 
        if res < 300: 
            break 
             
def path_printer_max_default(s=500, m=0.5,v0=0, f=0.2, max_time = 10):
    s_left = s
    v=v0
    for t in range(1, max_time+1):
        res = ((s*m)/(t**2*(1-f))) - (v*m/t)
        if res >=300:
            res = 300
        v += res
        s_left = s_left - v
        print(f'round: {t}, speed: {v} throttle: {res}, distance left: {s_left}')
        if s_left <= 0:
            break 
