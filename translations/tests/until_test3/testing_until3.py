import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import test

    


#Formula is p(x) UNTIL[0,0] q(x)
I_min = 0
I_max = 0
size = 200
path = "/home/berkay/Monitoring-using-DDlog/translations/until/until_ddlog/target/release/until_cli <"
logFile = "until_test3.log"
datFile = "until_test3.dat"

print()
print('\x1b[6;30;47m' + 'Testing formula p(x) UNTIL[' + str(I_min) + ',' + str(I_max) + '] q(x)' + ' \x1b[0m')
print()


# Generals note: List Data has structure: [[class,id,ts]] meaning: class = 1 means P(id), class = 2 means Q(id). id is identity integer, ts is timestamp

# Case1: all id's get satisfied
Data = []
ts = I_max
for i in range(size):
    if(i < size/2):
        #P(x) Q(x) at same ts (and tp)
        id = random.randint(0,5)
        Data.append([1,id,ts])
        Data.append([2,id,ts])
        ts =  ts + random.randint(0,3)
    else:
        # Single Q's satisfy
        Data.append([2,id,ts])
        ts =  ts + random.randint(0,3)

test_description = 'Test where each id satisfies the Formula, with "random" wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,3,True)


# Case2: No satisfaction, only possible when no q(x) occurs
Data = []
I_const = I_max
ts = I_const
for id in range(size):
    id = random.randint(0,5)
    ts = ts + random.randint(0,3)
    Data.append([1,id,ts])

test_description = 'No satisfactions, with "random" wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,3,True)


#random
Data = []
ts = I_const
for i in range(size):
    ts = ts + random.randint(0,3)
    id = random.randint(1,10)
    signature = random.randint(1,2)
    Data.append([signature,id,ts])

test_description = 'Random- might or might not be satisfied, with "random" wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,3,True)



