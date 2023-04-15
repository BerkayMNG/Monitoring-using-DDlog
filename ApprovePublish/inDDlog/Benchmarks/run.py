import os
import random
import matplotlib.pyplot as plt

# Formula: publish(r) -> ONCE[8,20] approve(r)
# Might be possible that appub.dl is not handling above formula anymore -> need to check
I_min = 8
I_max = 20

maxSize = 50000
stepSize = 5000
batchSize = 10


#self explanatory
def plot(name, batchsize):
    sizes = []
    times = []
    lineNumber = 1
    file1 = open("results.txt","r")
    for line in file1:
        if(lineNumber % 2 == 1):
            sizes.append(float(line))
        else:
            rtime, memusg = line.split(" ")
            times.append(float(rtime))
        lineNumber= lineNumber+1
    file1.close()


    plt.plot(sizes, times, label=name)
    plt.legend(loc='best')
    plt.title("Approve-publish, batchsize " + str(batchSize))
    plt.xlabel("size")
    plt.ylabel("time")
    plt.savefig('plots.png')


#makes the corresponding .dat file, measures time & plots results
def evaluate(Data, name):

    os.system("rm results.txt")
    os.system("touch results.txt")
    size = stepSize-1
    while size < maxSize:
        tp = 0 
        count = 0
        file = open("../appub.dat", "w")

        while tp < size:
            file.write("start;\n")
            j = 0

            while j < batchSize:
                if(tp+j >= size ):
                    break

                file.write("insert Timestamp(" + str(tp+j) + "," + str(Data[tp+j][2]) + ");\n")
                if(Data[tp+j][0] == 1):
                    file.write("insert Publish(" + str(tp+j) + "," + str(Data[tp+j][1]) + ");\n")
                else:
                    file.write("insert Approve(" + str(tp+j) + "," + str(Data[tp+j][1]) + ");\n")
                j = j + 1 


            tp = tp + j
            file.write("commit dump_changes;\n")
            file.write("\n")

        os.system("echo " + str(size+1) + " >> results.txt")
        os.system("/usr/bin/time -f'%e %M' --append --output=results.txt ../appub_ddlog/target/release/appub_cli < ../appub.dat > /dev/null")

        file.close()
        size = size + stepSize

    plot(name, batchSize)


# important: timestamps should increase in the list Data

# Case1: The Approve happens "before" the intervall (Still in data_prev but not in data_in)
# Data has structure: [[class,id,ts]] meaning: class = 1 means publish, class = 2 means approve. id is identity integer, ts is timestamp
Data = []
ts = I_max
for id in range(maxSize):
    #Use randomness to have not boring cases
    ts = ts + random.randint(1,4) #short distance between events
    dist_before = random.randint(0, I_min-1)
    Data.append([2,id,ts-dist_before])
    Data.append([1,id,ts])
Data.sort(key=lambda x: x[2])
evaluate(Data, "before intervall")


# Case2: All approved after intervall (not in data_in anymore)
# Data has structure: [[class,id,ts]] meaning: class = 1 means publish, class = 2 means approve. id is identity integer, ts is timestamp
Data = []
ts = 2*I_max 
for id in range(maxSize):
    ts = ts + random.randint(1,4)
    dist_after = random.randint(I_max+1,2*I_max+1)
    Data.append([1,id,ts])
    Data.append([2,id,ts - dist_after])
Data.sort(key=lambda x: x[2])
evaluate(Data, "after intervall")

# Case3: In intervall, i.e. no violations
# Data has structure: [[class,id,ts]] meaning: class = 1 means publish, class = 2 means approve. id is identity integer, ts is timestamp
Data = []
ts = I_max
for id in range(maxSize):
    ts = ts + random.randint(1,4)
    dist_in = random.randint(0, I_max)
    Data.append([1,id,ts])
    Data.append([2,id,ts - dist_in])
Data.sort(key=lambda x: x[2])
evaluate(Data, "in intervall")