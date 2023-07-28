import random
import subprocess
import os
import matplotlib.pyplot as plt
import re

# Parameters
REP = 15
TOTAL_EVENTS = [i*50 for i in range(1,20,5)]
#tOTAL_EVENTS = [50]
PROGRAMS = ["optimized", "ex"]
START_ID = 1
EVR = 60

DIFFERENCE = 0


Trace = list[tuple[int, list[tuple[str, int]]]]

def input_generator(total_events: int) -> Trace:
    num_ts = total_events
    events = []
    num_tp = 0
    elem = START_ID
    for ts in range(num_ts):
        elem1 = elem-DIFFERENCE
        elem2 = elem
        elem = elem + random.randint(1,3)
        events.append((ts,[("Withdraw", elem1),("P", elem2)]))
    return events

def translate_file(file_path_read:str, file_path_write:str):
    
    pattern1 = r'@(\d+)'
    pattern2 = r'(\w+)\((.*?)\)'
    
    timestamps_nested = []
    events = []
    with open(file_path_read, 'r') as file:
        for line in file:
            timestamps_nested.append(re.findall(pattern1, line))
            events.append(re.findall(pattern2, line))

    timestamps = [int(item) for sublist in timestamps_nested for item in sublist]


    with open(file_path_write, 'w') as file:
        for tp in range(len(timestamps)):
            file.write('start;\n')
            file.write('insert Timestamp(' + str(tp) + "," + str(timestamps[tp]) + ");\n")
            for event, inpts in events[tp]:
                file.write('insert ' + event + "(" + str(tp) + "," + inpts + ");\n")
                

            file.write('commit dump_changes;\n \n')

            file.write('echo --------------------;')

def measure(program: str, total_events: int) -> float:
    INPUT_FILE = 'input.txt'
    monpoly_input_generator(total_events, 'input2.log')
    translate_file('input2.log',INPUT_FILE)
    args = ["/usr/bin/time",  "-f'%e %M MiB'", f"./{program}_ddlog/target/release/{program}_cli"]

    mem_acc = 0.0
    time_acc = 0.0
    for _ in range(0, REP):
        with open(INPUT_FILE, 'rb') as input_file:
            proc = subprocess.run(args, stdin=input_file, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        proc.check_returncode()
        measurements = proc.stderr.decode().strip().split()
        elapsed, mem =  [float(item.replace("'", "")) for item in measurements[:-1]]
        #print(f"{elapsed:.2f}")
        time_acc += float(elapsed)
        mem_acc += float(mem)
    avg = time_acc / REP
    avg_mem =  mem_acc / REP
    print(f"{avg:.2f}")
    return avg, avg_mem

def measure_series(program: str) -> list[float]:
    arr = [measure(program, x) for x in TOTAL_EVENTS]
    runtime = [x[0] for x in arr]
    mem = [x[1] for x in arr]
    return runtime, mem

def monpoly_input_generator(total_events: int, filename:str):

    with open(filename, 'w') as file:
        for ts in range(total_events):
            file.write(f"@{ts} ")
            for _ in range(0,EVR):
                id1 = random.randrange(0,3000)
                val = random.randrange(2000,7000)
                file.write(f"Withdraw({id1},{val})  \n")
    
def measure2 (program: str, total_events: int) -> float:
    INPUT_FILE = f"input2.log"
    monpoly_input_generator(total_events,INPUT_FILE)
    args = ["/usr/bin/time", "-f'%e %M MiB'", "monpoly","-negate", "-sig", "ex.sig", "-formula", "ex.mfotl", "-log" , "input2.log"]
    
    mem_acc = 0.0
    time_acc = 0.0
    for _ in range(0, REP):
        proc = subprocess.run(args, stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        proc.check_returncode()
        measurements = proc.stderr.decode().strip().split()
        elapsed, mem =  [float(item.replace("'", "")) for item in measurements[:-1]]
        #print(f"{elapsed:.2f}")
        time_acc += float(elapsed)
        mem_acc += float(mem)
    avg = time_acc / REP
    avg_mem =  mem_acc / REP
    print(f"{avg:.2f}")
    return avg, avg_mem

def measure_monpoly(program: str) -> list[float]:
    arr = [measure2(program, x) for x in TOTAL_EVENTS]
    runtime = [x[0] for x in arr]
    mem = [x[1] for x in arr]
    return runtime, mem



def main():
    for program in PROGRAMS:
        label = f"{program}"
        runtime, mem = measure_series(program)
        plt.figure(1)
        plt.plot(TOTAL_EVENTS, runtime, label=label)
        plt.figure(2)
        plt.plot(TOTAL_EVENTS, mem, label=label)


    label = "Monpoly"
    runtime, mem = measure_monpoly("ex")
    plt.figure(1)
    plt.plot(TOTAL_EVENTS,runtime, label=label)
    plt.legend(loc='best')
    plt.figure(2)
    plt.plot(TOTAL_EVENTS,mem, label=label)
    plt.legend(loc='best')



    plt.figure(1)
    plt.xlabel("tumber timepoints")
    plt.ylabel("runtime [s]")
    plt.legend(loc='best')
    plt.savefig("Runtime.png", dpi = 500)

    plt.figure(2)
    plt.xlabel("tumber timepoints")
    plt.ylabel("memory usage [MiB]")
    plt.legend(loc='best')
    plt.savefig("Memory.png", dpi = 500)

if __name__ == '__main__':
    main()