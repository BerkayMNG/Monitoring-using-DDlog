import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import runTest_since

def test(test_description, Data, datFile, logFile, I_min,I_max):
    print('\x1b[6;30;47m' + test_description + ' \x1b[0m')
    runTest_since(Data, datFile, logFile, I_min,I_max)

#Formula is P(x) SINCE[0,0] Q(x), So I_min=I_max = I_const = 0
I_const = 0
size = 1000
logFile = "since_test3.log"
datFile = "since_test3.dat"

print()
print('\x1b[6;30;47m' + 'Testing formula p(x) SINCE[' + str(I_const) + ',' + str(I_const) + '] q(x)' + ' \x1b[0m')
print()


#All satisfied
Data = []
ts = I_const
for id in range(size):
    ts = ts + random.randint(I_const+1,2*I_const+1)
    Data.append([2,id,ts])
    if(id < size):
        Data.append([1,id,ts + ts+1]) # @ts q(x) and @ts+1 p(x) - stll satisfied, doesn't matter in case [0,0]
    else:
        Data.append([1,id,ts + ts+11]) # @ts p(x)  q(x),  also  satisfied
    
test_description = 'All satisfied'
test(test_description,Data, datFile, logFile, I_const,I_const)

# Second test(s): No satisfactions- only possible if no q(x)
Data = []
ts = I_const
for id in range(size):
    ts = ts + random.randint(0,3)
    Data.append([1,id,ts])
test_description = 'No satisfactions'
test(test_description,Data, datFile, logFile, I_const,I_const)



# Third test case: random input (mainly here to check wheter output of ddlog matches with MonPoly's output)
Data = []
ts = I_const
for i in range(size):
    ts = ts + random.randint(0,5)
    id = random.randint(1,10)
    signature = random.randint(1,2)
    Data.append([signature,id,ts])

test_description = 'Random input, checks wheter DDlog produces same output as MonPoly'
test(test_description,Data, datFile, logFile, I_const,I_const)