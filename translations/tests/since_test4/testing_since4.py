import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import runTest_since

def test(test_description, Data, datFile, logFile, I_min,I_max):
    print()
    print('\x1b[6;30;47m' + test_description + ' \x1b[0m')
    runTest_since(Data, datFile, logFile, I_min,I_max)
    print()

#Formula is P(x) SINCE[20,30] Q(x)
I_min = 20
I_max = 30
size = 30

logFile = "since_test4.log"
datFile = "since_test4.dat"

# Data has structure: [[class,id,ts]] meaning: class = 1 means P(id), class = 2 means Q(id). id is identity integer, ts is timestamp
Data = []
ts = I_max
for id in range(size):
    ts = ts + random.randint(I_max+1,2*I_max+1)
    coin = random.randint(0,1)
    chainlength = random.randint(I_min, I_max)
    Data.append([2,id,ts])
    for dist in range(chainlength):
        if(coin == 1):
            Data.append([1,id,ts + (dist+1)])  # p(x) & q(x) never occur at same ts together (p's chain starts after occurence of q)
        else:
            Data.append([1,id,ts + (dist)])   # p(x) & q(x) never occur at same ts together 

test_description = 'Test where each id satisfies the Formula'
#test(test_description,Data, datFile, logFile, I_min,I_max)


# Second test(s): No satisfactions, chain stops before lower bound of intervall is reached
Data = []
ts = I_max
for id in range(size):
    ts = ts + random.randint(I_max+1,2*I_max+1)
    coin = random.randint(0,1)
    chainlength = random.randint(0, I_min-1)
    Data.append([2,id,ts])
    for dist in range(chainlength):
        if(coin == 1):
            Data.append([1,id,ts + (dist+1)])  # p(x) & q(x) never occur at same ts together (p's chain starts after occurence of q)
        else:
            Data.append([1,id,ts + (dist)])   # p(x) & q(x) never occur at same ts together 

test_description = 'Test where a "chain" stops before being satisfied'
#test(test_description,Data, datFile, logFile, I_min,I_max)

# Third test case: random input (mainly here to check wheter output of ddlog matches with MonPoly's output)
Data = []
ts = I_max
for i in range(size):
    ts = ts + random.randint(0,5)
    id = random.randint(1,10)
    signature = random.randint(1,2)
    Data.append([signature,id,ts])

test_description = 'Random input, checks wheter DDlog produces same output as MonPoly'
test(test_description,Data, datFile, logFile, I_min,I_max)