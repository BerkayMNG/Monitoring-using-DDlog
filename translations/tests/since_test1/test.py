import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from helper_functions import runTest



INTERVALL_MIN = 0
INTERVALL_MAX= 3
USED_IDS = [1,2]
PATH1 = "/home/berkay/Monitoring-using-DDlog/translations/since/since1_ddlog/target/release/since1_cli"
PATH2 = "/home/berkay/Monitoring-using-DDlog/translations/since/since2_ddlog/target/release/since2_cli"
PATH3 = "/home/berkay/Monitoring-using-DDlog/translations/since/since3_ddlog/target/release/since3_cli"
MONPOLY_PROGRAM = "since_test"


"""
Here we test the formula: P(x) SINCE[0,3] Q(x)
"""
def test1(min,max):
    formula = f'P(x) SINCE[{min},{max}] Q(x)'

    with open(MONPOLY_PROGRAM + ".mfotl", 'w') as file:
        file.write(formula)
    
    used_ids = USED_IDS
    events = []
    for ts in range(50):
        curr_events = [("P", elem) for elem in used_ids]
        id = random.randint(1,4)
        curr_events.append(("Q",id))
        events.append((ts,curr_events))
    
    runTest(events,min,max,PATH1,MONPOLY_PROGRAM, "since1, " + formula + " chain has no gap")
    runTest(events,min,max,PATH2,MONPOLY_PROGRAM, "since2, " + formula + " chain has no gap")
    runTest(events,min,max,PATH3,MONPOLY_PROGRAM, "since3, " + formula + " chain has no gap")
        

if __name__ == '__main__':
    test1(0,3)
    test1(5,5)
    test1(0,0)
    test1(5,10)