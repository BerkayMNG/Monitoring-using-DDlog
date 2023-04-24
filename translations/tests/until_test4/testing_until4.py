import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import test



#Formula under testis p(x) UNTIL[2,5] q(x)
I_min = 2
I_max = 5
size = 10  #asymptotic size i.e. testsize is O(size) inputs of p(x)'s or q(x)'s
path = "/home/berkay/Monitoring-using-DDlog/translations/until/until_ddlog/target/release/until_cli <"


logFile = "until_test4.log"
datFile = "until_test4.dat"

print()
print('\x1b[6;30;47m' + 'Testing formula p(x) UNTIL[' + str(I_min) + ',' + str(I_max) + '] q(x)' + ' \x1b[0m')
print()


# Generals note: List Data has structure: [[class,id,ts]] meaning: class = 1 means P(id), class = 2 means Q(id). id is identity integer, ts is timestamp

# Case1: all id's get satisfied, "in intervall", few id's
Data = []
ts = I_max
for i in range(size):
    id = random.randint(0,5)
    ts = ts + random.randint(I_max+1,2*I_max+1) #to ensure no "intersection" which might break longest chain otherwise
    coin = random.randint(0,1)
    chainlength = random.randint(I_min, I_max)
    Data.append([2,id,ts])
    for dist in range(chainlength):
        if(coin == 1):
            Data.append([1,id,ts - (dist+1)])  # p(x) & q(x) don't occur at same ts together 
        else:
            Data.append([1,id,ts - (dist)])   # p(x) & q(x) occur at same ts together 
        
test_description = 'Test where each id satisfies the Formula, no wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,1,False)

#Case2: Never satisfied, "before" intervall:
Data = []
ts = I_max
for id in range(size):
    ts = ts + random.randint(0,3)
    chainlength = random.randint(0, I_min-1)
    Data.append([2,id,ts])
    for dist in range(chainlength):
        Data.append([1,id,ts - (dist+1)])

test_description = 'Each P(x) chain stops before being in the intervall, with "random" wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,3,True)

#Case3: Never satisfied, "after" intervall:
Data = []
ts = I_max
for id in range(size):
    ts = ts + random.randint(0,3)
    chainlength = random.randint(I_max+1, 2*I_max+1)
    Data.append([2,id,ts])
    for dist in range(chainlength):
        Data.append([1,id,ts + dist])

test_description = 'Each P(x) chain starts outside the intervall (again never gets satisfied), "total wrapping'
test(path,test_description,Data, datFile, logFile, I_min,I_max,-1,False)