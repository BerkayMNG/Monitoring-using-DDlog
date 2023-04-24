import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import test
    


#Formula is p(x) UNTIL[5,5] q(x)
I_min = 5
I_max = 5
size = 200
path = "/home/berkay/Monitoring-using-DDlog/translations/until/until_ddlog/target/release/until_cli <"

logFile = "until_test2.log"
datFile = "until_test2.dat"

print()
print('\x1b[6;30;47m' + 'Testing formula p(x) UNTIL[' + str(I_min) + ',' + str(I_max) + '] q(x)' + ' \x1b[0m')
print()


# Generals note: List Data has structure: [[class,id,ts]] meaning: class = 1 means P(id), class = 2 means Q(id). id is identity integer, ts is timestamp

# Case1: all id's get satisfied
Data = []
ts = I_max
for i in range(size):
    id = random.randint(0,5)
    Data.append([1,id,ts])
    ts = ts + I_max + 1
    Data.append([2,id,ts])

test_description = 'Test where each id satisfies the Formula, no wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,1,False)



# before or after interval there is a P matching to a Q - so never satisfied
Data = []
I_const = I_max
ts = I_const
for id in range(size):
    id = random.randint(0,5)
    ts = ts + random.randint(I_const+1,2*I_const+1) #no "intersection"
    Data.append([1,id,ts])
    coin = random.randint(0,1)
    if(coin == 0):
        dist = random.randint(0,I_const-1)
    else:
        dist = random.randint(I_const+1, 2*I_const+1)
    ts = ts + dist
    Data.append([2,id,ts])

test_description = 'Never satisfied, no wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,1,False)


#randomly satisfied or not, "wrap" events of same ts to same tp
Data = []
ts = I_max
for i in range(3*size):
    id = random.randint(0,5)
    Data.append([1,id,ts])
    ts = ts + random.randint(I_max-1, I_max+1)
    Data.append([2,id,ts])


test_description = 'Random- might or might not be satisfied. Wrapped events'
test(path,test_description,Data, datFile, logFile, I_min,I_max,-1,False)



