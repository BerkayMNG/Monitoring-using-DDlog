import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import test
    




#Formula is P(x) SINCE[0,3] Q(x)
I_min = 0
I_max = 3
size = 5
path = "/home/berkay/Monitoring-using-DDlog/translations/since/since_ddlog/target/release/since_cli <"

logFile = "since_test1.log"
datFile = "since_test1.dat"

print()
print('\x1b[6;30;47m' + 'Testing formula p(x) SINCE[' + str(I_min) + ',' + str(I_max) + '] q(x)' + ' \x1b[0m')
print()

# First test for since_test1: for each Q(x), we insert P(x)'s such that is gets satisfied
# Namely for each q(x) we insert p(x)'s resulting in a "chainlength" lying between [i_min, I_max]
# We also test for different batchsize- especially interesting are the cases batchsize = 1 and batchsize != 1

# Data has structure: [[class,id,ts]] meaning: class = 1 means P(id), class = 2 means Q(id). id is identity integer, ts is timestamp
Data = []
ts = I_max
for id in range(size):
    ts = ts + random.randint(0,3)
    chainlength = random.randint(I_min, I_max)
    Data.append([2,id,ts])
    for dist in range(chainlength):
        Data.append([1,id,ts - (dist+1)])

#special case where we have @ts p(x) q(x) (should be still satisfied since I_min == 0)
ts = ts + random.randint(0,3)
Data.append([2,size,ts])
Data.append([1,size,ts])

test_description = 'Test where each id satisfies the Formula, completely wrapped'
test(path,test_description,Data, datFile, logFile, I_min,I_max,-1,False)


# Second test(s): No satisfactions- only possible if there is no q(x)
Data = []
ts = I_max
for id in range(size):
    ts = ts + random.randint(0,3)
    Data.append([1,id,ts])

test_description = 'Test where no id is satisfied, no q(x) occur,"randomly" wrapped'
test(path,test_description,Data, datFile, logFile, I_min,I_max,1,False)

# Third test case: random input (mainly here to check wheter output of ddlog matches with MonPoly's output)
Data = []
ts = I_max
for i in range(size):
    ts = ts + random.randint(0,5)
    id = random.randint(1,10)
    signature = random.randint(1,2)
    Data.append([signature,id,ts])

test_description = 'Random input, checks wheter DDlog produces same output as MonPoly, "randomly" wrapped'
test(path,test_description,Data, datFile, logFile, I_min,I_max,3,True)

print()