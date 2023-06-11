import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from helper_functions import runTest


SIZE = 10
EVR = 3
MAX_VALUE = 1_000_000_000
MIN_VALUE = 10
PROBABILITY = 0.8

INTERVALL_MIN = 0
INTERVALL_MAX= 3
USED_IDS = [1,2,3,4]
PATH = "/home/berkay/Monitoring-using-DDlog/translations/until/until_ddlog/target/release/until_cli"

MONPOLY_PROGRAM = "until_test"

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



def test1(min,max):
    formula = f'P(x) UNTIL[{min},{max}] Q(x)'

    with open(MONPOLY_PROGRAM + ".mfotl", 'w') as file:
        file.write(formula)
    
    used_ids = USED_IDS
    events = []
    for ts in range(SIZE):
        curr_events = [("P", elem) for elem in used_ids]
        id = random.randint(1,8)
        curr_events.append(("Q",id))
        events.append((ts,curr_events))
    runTest(events,min,max,PATH,MONPOLY_PROGRAM, "until, " + formula + "lots of satisfied id's")



#chain length l -> p^l
def test2(min:int, max:int):
    formula = f'P(x) UNTIL[{min},{max}] Q(x)'

    with open(MONPOLY_PROGRAM + ".mfotl", 'w') as file:
        file.write(formula)

    events = []
    cache = []
    for ts in range(SIZE):
        curr_events = [("P", elem) for _,elem in cache if filter_with_probability(0.99)]
        for _, elem in cache:
            curr_events.append(("Q", elem))
        for _ in range(EVR):
            elem = random.randint(0, MAX_VALUE)
            cache.append((ts,elem))
        events.append((ts, curr_events))
    runTest(events,min,max,PATH,MONPOLY_PROGRAM, "until, " + formula + " long chains of P(id) (with high probab.), occuring with corresponding Q(id)")



def test3(min:int, max:int):
    formula = f'P(x) UNTIL[{min},{max}] Q(x)'
    
    with open(MONPOLY_PROGRAM + ".mfotl", 'w') as file:
        file.write(formula)

    events = []

    for ts in range(SIZE):
        curr_events = [("P", elem) for elem in [i for i in range(1,201,1)]]

        if(ts%2==0):
            for elem in range(1,101,1): #evr is kind of half of id pool
                curr_events.append(("Q", elem))
        else:
            for elem in range(101,201,1): 
                curr_events.append(("Q", elem))
        events.append((ts, curr_events))

    
    runTest(events,min,max,PATH,MONPOLY_PROGRAM, "until, " + formula + " P's same in every tp, Q's set one out")



if __name__ == '__main__':
    test1(0,3)
    test1(3,3)
    test1(0,0)
    test1(2,4)
    print()
    test2(0,3)
    test2(3,3)
    test2(0,0)
    test2(2,4)
    print()
    test3(0,3)
    test3(3,3)
    test3(0,0)
    test3(2,4)
    print()
