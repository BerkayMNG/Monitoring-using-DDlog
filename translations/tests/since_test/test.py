import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from helper_functions import runTest


SIZE = 100
EVR = 3
MAX_VALUE = 1_000_000_000
PROBABILITY = 0.8

INTERVALL_MIN = 0
INTERVALL_MAX= 3
USED_IDS = [1,2]
PATH1 = "/home/berkay/Monitoring-using-DDlog/translations/since/since1_ddlog/target/release/since1_cli"
PATH2 = "/home/berkay/Monitoring-using-DDlog/translations/since/since2_ddlog/target/release/since2_cli"
PATH3 = "/home/berkay/Monitoring-using-DDlog/translations/since/since3_ddlog/target/release/since3_cli"
MONPOLY_PROGRAM = "since_test"

Window = list[tuple[int,list[int]]]

#auxiliary
def filter_window(ts_new:int, max:int, cache:Window) -> Window:
    i = 0
    while i < len(cache):
        ts, _ = cache[i]
        if (ts_new - ts > max):
            cache.pop(i)
        else:
            i += 1   
    return cache

def filter_with_probability(probability:float) -> bool:
    return random.random() < probability


"""
Here we test the formula: P(x) SINCE[0,3] Q(x)
"""
def test1(min,max):
    formula = f'P(x) SINCE[{min},{max}] Q(x)'

    with open(MONPOLY_PROGRAM + ".mfotl", 'w') as file:
        file.write(formula)
    
    used_ids = USED_IDS
    events = []
    for ts in range(SIZE):
        curr_events = [("P", elem) for elem in used_ids]
        id = random.randint(1,4)
        curr_events.append(("Q",id))
        events.append((ts,curr_events))
    
    runTest(events,min,max,PATH1,MONPOLY_PROGRAM, "since1, " + formula + " chain has no gap")

    runTest(events,min,max,PATH2,MONPOLY_PROGRAM, "since2, " + formula + " chain has no gap")

    runTest(events,min,max,PATH3,MONPOLY_PROGRAM, "since3, " + formula + " chain has no gap")


#chain length l -> p^l
def test2(min:int, max:int):
    formula = f'P(x) SINCE[{min},{max}] Q(x)'

    with open(MONPOLY_PROGRAM + ".mfotl", 'w') as file:
        file.write(formula)

    events = []
    cache = []
    for ts in range(SIZE):
        cache = filter_window(ts,max,cache)
        curr_events = [("P", elem) for _,elem in cache if filter_with_probability(0.99)]
        for _ in range(EVR):
            elem = random.randint(0, MAX_VALUE)
            cache.append((ts,elem))
            curr_events.append(("Q", elem))
        events.append((ts, curr_events))
    
    runTest(events,min,max,PATH1,MONPOLY_PROGRAM, "since1, " + formula + " continue chain with high probability")
    runTest(events,min,max,PATH2,MONPOLY_PROGRAM, "since2, " + formula + " continue chain with high probability")
    runTest(events,min,max,PATH3,MONPOLY_PROGRAM, "since3, " + formula + " continue chain with high probability")


def test3(min:int, max:int):
    formula = f'P(x) SINCE[{min},{max}] Q(x)'
    
    with open(MONPOLY_PROGRAM + ".mfotl", 'w') as file:
        file.write(formula)

    events = []
    cache = []

    for ts in range(SIZE):
        curr_events = [("P", elem) for elem in [i for i in range(1,201,1)]]

        if(ts%2==0):
            for elem in range(1,101,1): #evr is kind of half of id pool
                curr_events.append(("Q", elem))
        else:
            for elem in range(101,201,1): 
                curr_events.append(("Q", elem))
        events.append((ts, curr_events))

    
    runTest(events,min,max,PATH1,MONPOLY_PROGRAM, "since1, " + formula + " P's same in every tp, Q's set one out")
    runTest(events,min,max,PATH2,MONPOLY_PROGRAM, "since2, " + formula + " P's same in every tp, Q's set one out")
    runTest(events,min,max,PATH3,MONPOLY_PROGRAM, "since3, " + formula + " P's same in every tp, Q's set one out")
       

if __name__ == '__main__':
    test1(0,3)
    test1(5,5)
    test1(0,0)
    test1(5,10)
    print()
    test2(0,3)
    test2(5,5)
    test2(0,0)
    test2(5,10)
    print()
    test3(0,3)
    test3(5,5)
    test3(0,0)
    test3(5,10)
    print()
