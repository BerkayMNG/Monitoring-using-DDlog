import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from myLib import test_unary


#Formula is PREV[0,4] P(3)
print()
print('\x1b[6;30;47m' + 'Testing formula PREV[0,4] p(3)' + ' \x1b[0m')
print()

I_min = 0
I_max = 4
identifier = 3

size = 10 #asymptotic size i.e. testsize is O(size) inputs of p(x)'s or q(x)'s
path = "/home/berkay/Monitoring-using-DDlog/translations/previous/prev_formula1_ddlog/target/release/prev_formula1_cli <"


logFile = "prev_test1.log"
datFile = "prev_test1.dat"

#Random
Data = []
ts_data = []
ts = 0
for i in range (size):
    ts = ts + random.randint(0, I_max)
    ts_data.append(ts)

for i in range(size):
    id = random.randint(2,4)
    dist = random.randint(I_min, I_max)
    if ((i>0) & id == identifier):
        Data.append([id,ts_data[i-1]])
    else:
        Data.append([id,ts_data[i]])
test_description = 'Random but tries to get satisfactions. All wrapped, output "Satisfied"'
test_unary(path,test_description,1,1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=-1,vary=False)
test_description = 'Test above Events with random wrapping'
test_unary(path,test_description,1,1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=3,vary=True)
test_description = 'Same as before but now unwrapped and output "Violations"'
test_unary(path,test_description,1,-1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=-1,vary=False)
test_description = 'Same as before but now "randomly" wrapped and output "Violations"'
test_unary(path,test_description,1,-1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=3,vary=True)

print()

Data = []
ts = 0
for i in range (size):
    id = random.randint(0, identifier*2)
    ts = random.randint(0,3)
    Data.append([id,ts])
test_description = 'Completely random events but tries to be "dense" (lots of similar ids with low ts differences), randomly wrapped"'
test_unary(path,test_description,1,1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=4,vary=True)
test_description = 'Test above Events with no wrapping'
test_unary(path,test_description,1,1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=1,vary=False)
test_description = 'Same as before but now randomly wrapped and comparing output "Violations"'
test_unary(path,test_description,1,-1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=3,vary=True)
test_description = 'Same as before but now never wrapped and comparing output "Violations"'
test_unary(path,test_description,1,-1,Data,datFile,logFile,I_min,I_max,id=identifier,wrapSize=3,vary=True)