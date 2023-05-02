import random
import os
import matplotlib.pyplot as plt

def input_generator(numts:int, evr:int, lw:int, up:int):

    timestamps = []
    events = []
    ts = 0
    for it1 in range(numts):
        ts = ts + random.randint(0,2*up)
        timestamps.append(ts)
        curr_events = []
        for it2 in range(evr):
            curr_events.append(random.randint(0,100))
        events.append(curr_events)

    return timestamps,events

def file_generator(timestamps:list,events:list,type:str, batchsize:int,lw:int, up:int,filename:str):

    file = open(filename,"w")
    file.write("start;\n")
    file.write("insert Intervall(" + str(abs(lw)) + "," + str(up)  + ");\n")
    file.write("commit dump_changes;\n\n")

    if not (len(timestamps) == len(events)):
        raise Exception("Size mismatch")
    elif(type == "not batched"):
        size = len(timestamps)
        for tp in range(size):
            file.write("start;\n")
            file.write("insert Timestamp(" + str(tp) + ", " + str(timestamps[tp]) + ");\n")
            for ev in events[tp]:
                file.write("insert P(" + str(tp) + ", " + str(ev) + ");\n")
            file.write("commit dump_changes;\n")
    elif(type == "batched"):
        split_ts = [timestamps[i:i + batchsize] for i in range(0, len(timestamps), batchsize)]
        split_events = [events[i:i + batchsize] for i in range(0, len(events), batchsize)]
        new_size = len(split_ts)
        for it1 in range(new_size):
            file.write("start;\n")
            for it2 in range(len(split_ts[it1])):
                file.write("insert Timestamp(" + str(it1*batchsize+it2) + ", " + str(split_ts[it1][it2]) + ");\n")
                for elem in split_events[it1][it2]:
                    file.write("insert P(" + str(it1*batchsize+it2) + ", " + str(elem) + ");\n")
            file.write("commit dump_changes;\n\n")

    else:
        raise Exception("Please give a valid type, either 'batched' or 'not batched")




def eval(filename:str):
    sizes = []
    times = []
    lineNumber = 1
    file1 = open(filename,"r")
    for line in file1:
        rtime, memusg = line.split(" ")
        times.append(float(rtime))
    file1.close()
    return times,sizes

def plot(input_size:list, runtimes:list,description:str):
    plt.plot(input_size, runtimes, label = description)
    plt.legend(loc='best')
    plt.title("Comparision")
    plt.xlabel("size")
    plt.ylabel("time")
    plt.show()
    plt.savefig('comparision.png')


if __name__ == '__main__':
    #choose Intervall here
    lw = 5
    up = 12
    print("Intervall is: [" + str(lw) + ", " + str(up) + "]")

    numts = [i*100 for i in range(1,100,5)]
    rep = 10
    evr = 2

    runtimes = []
    input_size = []
    
    table = open("table.txt", "w")

    table.write("time,size\n")
    table.write("No batching, differential evaluation:\n")
    for ns in numts:
        ts, ev = input_generator(ns,evr,lw,up)
        file_generator(ts,ev,"not batched",1,lw,up,"no_batching.dat")

        os.system("touch results.txt")
        for i in range(0,rep):
            os.system("/usr/bin/time -f'%e %M' --append --output=results.txt ./no_batching_ddlog/target/release/no_batching_cli < no_batching.dat > /dev/null")
        times, _ = eval("results.txt")
        os.system("rm results.txt")
        rt = sum(times)/rep
        sz = ns*evr
        table.write( str(round(rt,3)) + " " + str(sz) + "\n")
        runtimes.append(rt)
        input_size.append(sz)
    plot(input_size=input_size, runtimes=runtimes,description="no batching, differential evaluation")

    table.write("\n\nBatching:\n")

    for batchsize in [5,10,100]:
            table.write("\nBatchsize=" + str(batchsize) + "\n")
            runtimes = []
            input_size = []
            for ns in numts:
                ts, ev = input_generator(ns,evr,lw,up)
                file_generator(ts,ev,"batched",batchsize,lw,up,"batching.dat")
                os.system("touch results.txt")
                for i in range(0,rep):
                    os.system("/usr/bin/time -f'%e %M' --append --output=results.txt ./batching_ddlog/target/release/batching_cli < batching.dat > /dev/null")
                times, _ = eval("results.txt")
                os.system("rm results.txt")
                rt = sum(times)/rep
                sz = ns*evr
                table.write( str(round(rt,3)) + " " + str(sz) + "\n")
                runtimes.append(rt)
                input_size.append(sz)

            plot(input_size=input_size, runtimes=runtimes,description="batchsize="+str(batchsize))
    
    table.close()





