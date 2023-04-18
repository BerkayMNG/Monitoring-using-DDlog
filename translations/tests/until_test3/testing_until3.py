import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import runTest_until

def test(cat,test_description, Data, datFile, logFile, I_min,I_max):
    print('\x1b[6;30;47m' + test_description + ' \x1b[0m')
    runTest_until(cat,Data, datFile, logFile, I_min,I_max)
    


#Formula is p(x) UNTIL[0,0] q(x)
I_min = 0
I_max = 0
size = 200

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
        id = random.randint(0,5)
        Data.append([1,id,ts])
        Data.append([2,id,ts])
        ts =  ts + random.randint(0,3)
    else:
        Data.append([2,id,ts])
        ts =  ts + random.randint(0,3)


test_description = 'Test where each id satisfies the Formula, with wrapping'
test(1,test_description,Data, datFile, logFile, I_min,I_max)


# Case2: No satisfaction, only possible when no q(x) occurs
Data = []
I_const = I_max
ts = I_const
for id in range(size):
    id = random.randint(0,5)
    ts = ts + random.randint(0,3)
    Data.append([1,id,ts])

test_description = 'No satisfactions, with wrapping'
test(1,test_description,Data, datFile, logFile, I_const,I_const)


#random
Data = []
ts = I_const
for i in range(size):
    ts = ts + random.randint(0,3)
    id = random.randint(1,10)
    signature = random.randint(1,2)
    Data.append([signature,id,ts])


test_description = 'Random- might or might not be satisfied, with wrapping'
test(1,test_description,Data, datFile, logFile, I_min,I_max)



