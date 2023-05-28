import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import test_binary

#Formula is P(x) SINCE[5,5] Q(x), So I_min=I_max = I_const = 5
I_const = 5
size = 100
path = "/home/berkay/Monitoring-using-DDlog/translations/since/since3_ddlog/target/release/since3_cli <"

logFile = "since_test2.log"
datFile = "since_test2.dat"

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
        for i in range(I_const):
            Data.append([1,id,ts + i+1]) # p(x) & q(x) never occur at same ts together
    else:
        for i in range(I_const+1):
            Data.append([1,id,ts + i]) # p(x) & q(x) occur at same ts together
    
test_description = 'Satisfactions here'
test_binary(path,test_description,Data, datFile, logFile, I_const,I_const,-1,False)

# Second test(s): No satisfactions, random distance (but no equal 5)
Data = []
ts = I_const
for id in range(size):
    ts = ts + random.randint(0,3)
    Data.append([2,id,ts + random.randint(0,4)])
    if(id < size/2):
        Data.append([1,id,ts + random.randint(0,4)]) #before intervall
    else:
        Data.append([1,id,ts + random.randint(6,15)]) #after intervall

test_description = 'No satisfactions, "randomly" wrapped'
test_binary(path,test_description,Data, datFile, logFile, I_const,I_const,4,True)

#third test case: not satisfied but distance between p & q is constant 5
Data = []
ts = I_const
for id in range(size):
    ts = ts + random.randint(0,3)
    Data.append([2,id,ts])
    Data.append([1,id,ts + I_const])

test_description = 'Never satisfied but constant distance of I_const, "randomly" wrapped'
test_binary(path,test_description,Data, datFile, logFile, I_const,I_const,4,True)


# 4h test case: random input (mainly here to check wheter output of ddlog matches with MonPoly's output)
Data = []
ts = I_const
for i in range(size):
    ts = ts + random.randint(0,5)
    id = random.randint(1,10)
    signature = random.randint(1,2)
    Data.append([signature,id,ts])

test_description = 'Random input, checks wheter DDlog produces same output as MonPoly, "randomly" wrapped'
test_binary(path,test_description,Data, datFile, logFile, I_const,I_const,4,True)