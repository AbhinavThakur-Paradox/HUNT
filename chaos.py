import time

def mysterious_num(lower_limit, upper_limit) :
    seed = time.time_ns()
    num = int(seed) 
    n = num % (upper_limit - lower_limit + 1) + lower_limit
    return n