import random
import subprocess
import matplotlib.pyplot as plt

REP = 10
MAX_VALUE = 2000
MIN_VALUE = 200
PATH = "../since/"
PROGAMS = ["since1", "since2", "since3"]
Trace = list[tuple[int, list[tuple[str, int]]]]
Window = list[tuple[int,list[int]]]


def filter_window(ts_new:int, max:int, cache:Window) -> Window:
    i = 0
    while i < len(cache):
        ts, _ = cache[i]
        if (ts_new - ts > max):
            cache.pop(i)
        else:
            i += 1
        
    return cache

def filter_with_probability(probability:float) -> bool:
    return random.random() < probability


def event_generator_1(num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    events = []
    cache = []
    for ts in range(num_ts):
        curr_events = [("P", elem) for elem in cache if filter_with_probability(p)]

        chosen = []
        for _ in range(evr):
            while True:
                elem = random.randint(0, MAX_VALUE)
                if elem not in cache:
                    cache.append(elem)
                if elem not in chosen:
                    chosen.append(elem)
                    break
            curr_events.append(("Q", elem))

        events.append((ts, curr_events))
    return events


"""
Observe that evr, p and intervall_max are not used here.
It is included because originally there were more 
event_generator functions, who all had the below signature 
except this one. This simplified the generation of the 
events for the measuring functions, since they only needed the 
name of the event_generator. However, 
most of the other generators are discarded but the 
signature is unchanged since it is highly coupled 
with the  measure_ddlog(), measure_MonPoly() 
and event_generator() functions.
"""
def event_generator_2(num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    #id pool consists of [1,2,3,..200]
    events = []

    for ts in range(num_ts):
        curr_events = [("P", elem) for elem in [i for i in range(1,201,1)]]

        if(ts%2==0):
            for elem in range(1,101,1): #evr is kind of half of id pool
                curr_events.append(("Q", elem))
        else:
            for elem in range(101,201,1): 
                curr_events.append(("Q", elem))
        events.append((ts, curr_events))
    return events


def input_ddlog_gen(events: Trace, filename: str, min:int, max:int):
    nr_tps = len(events)
    with open(filename, 'w') as file:
        file.write("start;\n")
        file.write(f'insert Intervall({min}, {max});\n')
        file.write("commit dump_changes;\n\n")
        for tp in range(nr_tps):
            file.write("start;\n")
            ts, elems = events[tp]
            file.write("insert Timestamp(" + str(tp) + ", " + str(ts) + ");\n")
            for rel, elem in elems:
                file.write("insert " + rel + "(" + str(tp) + ", " + str(elem) + ");\n")
            file.write("commit dump_changes;\n\n")

def input_MonPoly_gen(events: Trace, filename: str):
    with open(filename, 'w') as file:
        for ts,elems in events:
            file.write(f'@{ts} ')
            for rel,elem in elems:
                file.write(rel + f'({elem}) ')
            file.write('\n')

def measure_ddlog(func, numt_ts:int, evr:int, p:float, intervall_min:int,intervall_max:int, args:list[str]) -> float:


    input_file = "input.dat"
    events = event_generator(func,numt_ts,evr,p,intervall_max)
    input_ddlog_gen(events,input_file,intervall_min,intervall_max)

    mem_acc = 0.0
    time_acc = 0.0

    for _ in range(0, REP):
        with open(input_file, 'rb') as input:
            proc = subprocess.run(args, stdin=input, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        proc.check_returncode()
        measurements = proc.stderr.decode().strip().split()
        elapsed, mem = [float(item.replace("'", "")) for item in measurements]
        time_acc += float(elapsed)
        mem_acc += float(mem)
    avg = time_acc / REP
    avg_mem =  mem_acc / REP
    print(f"{avg:.2f}\n")

    subprocess.run(["rm", input_file])
    return avg, round(avg_mem/1024.0)

def event_generator(func, num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    return func(num_ts,evr,p,intervall_max)


def measure_MonPoly(func,numt_ts:int, evr:int, p:float, intervall_min:int,intervall_max:int) -> float:
    
    mftol_file = "mply.mfotl"
    sig_file = "mply.sig"
    log_file = "mply.log"

    with open(mftol_file,'w') as file:
        file.write(f'P(x) SINCE[{intervall_min},{intervall_max}] Q(x)')

    with open(sig_file,'w') as file:
        file.write('P(x:int) \n')
        file.write('Q(x:int) \n')
    

    events = func(numt_ts,evr,p,intervall_max)
    input_MonPoly_gen(events,log_file)

    args = ["/usr/bin/time",  "-f'%e %M'", "monpoly", "-sig", sig_file, "-formula", mftol_file, "-log", log_file]

    mem_acc = 0.0
    time_acc = 0.0

    for _ in range(0, REP):
        proc = subprocess.run(args,stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        proc.check_returncode()
        measurements = proc.stderr.decode().strip().split()
        elapsed, mem = [float(item.replace("'", "")) for item in measurements]
        time_acc += float(elapsed)
        mem_acc += float(mem)
    avg = time_acc / REP
    avg_mem =  mem_acc / REP
    print(f"{avg:.2f}\n")

    subprocess.run(["rm", mftol_file])
    subprocess.run(["rm", log_file])
    subprocess.run(["rm", sig_file])
    
    return avg, round(avg_mem/1024.0)


def plot(program:str, x:list[int], y:list[int], id:int):
    plt.figure(id)
    plt.plot(x,y,label=program)
    plt.legend(loc='best')

def figure(x_label:str, y_label:str, path:str,id:int):
        plt.figure(id)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.savefig(path,dpi=500)
        plt.close(id)

"""
Assumption/idea: since1 will keep a lot of outdated tuples because "chains" never stop and 
new id's enter frequently. Since2 and Since3 should perform much better due to "garbage collecting"
"""
def bench1():
    total_events = [i*1000 for i in range(1,30,3)]
    evr = 100

    intervall_min = 2
    intervall_max = 15

    x = [i//evr for i in total_events]
    exp = 0
    
    for p in [0.9999]:
        for program in PROGAMS:
            print(f'program: {program}, prob. = {p}')
            args_ddlog = ["/usr/bin/time", "-f'%e %M'", f"{PATH}{program}_ddlog/target/release/{program}_cli"]
            arr = [measure_ddlog(event_generator_1,ts,evr,p,intervall_min,intervall_max,args_ddlog) for ts in x]
            runtime = [x[0] for x in arr]
            mem = [x[1] for x in arr]
            plot(program,x,runtime,2*exp)
            plot(program,x,mem,2*exp+1)
            
            
        figure("Number of timepoints","runtime[s]", f"./since_plots/bench1/runtime_ddlog_{exp}",2*exp)
        #figure("Number of timepoints","memory usage[MiB]", f"./since_plots/bench1/memory_ddlog_{exp}",2*exp+1)
        exp +=1


    

    exp = 0
    for p in [0.9999]:
        print(f'program: MonPoly, prob. = {p}')
        arr = [measure_MonPoly(event_generator_1,ts,evr,p,intervall_min,intervall_max) for ts in x]
        runtime = [x[0] for x in arr]
        mem = [x[1] for x in arr]
        plot("MonPoly",x,runtime,2*exp)
        plot("MonPoly",x,mem,2*exp+1)


        figure("Number of timepoints","runtime[s]", f"./since_plots/bench1/runtime_monpoly_{exp}",2*exp)
        figure("Number of timepoints","memory usage[MiB]", f"./since_plots/bench1/memory_{exp}",2*exp+1)
        exp += 1



"""
Pool of "ids"- p(id) always occurs, whereas Q(id) occurs for each id 2 tp later again.
Thus, since3 does much more work than the other 2 versions due to the group_by.
since2 should be worse than since1, because it does more work but obtains the same result.
probability is not used here. 

"""
def bench2():
    total_events = [i*70 for i in range(1,10,1)]
    evr = -1 #not used

    intervall_min = 2
    intervall_max = 25

    x = [i for i in total_events]
    exp = 0
    p = -1 #p not used
    for program in PROGAMS:
        print(f'program: {program}, prob. = {p}')
        args_ddlog = ["/usr/bin/time", "-f'%e %M ", f"{PATH}{program}_ddlog/target/release/{program}_cli"]
        arr = [measure_ddlog(event_generator_2,ts,evr,p,intervall_min,intervall_max,args_ddlog) for ts in x]
        runtime = [x[0] for x in arr]
        mem = [x[1] for x in arr]
        plot(program,x,runtime,2*exp)
        plot(program,x,mem,2*exp+1)
    
    figure("Number of timepoints","runtime[s]", f"./since_plots/bench2/runtime_ddlog",2*exp)
    #figure("Number of timepoints","memory usage[MiB]", f"./since_plots/bench2/memory_ddlog",2*exp+1)



    exp = 0


    arr = [measure_MonPoly(event_generator_2,ts,evr,p,intervall_min,intervall_max) for ts in x]
    runtime = [x[0] for x in arr]
    mem = [x[1] for x in arr]
    plot("MonPoly",x,runtime,2*exp)
    plot("MonPoly",x,mem,2*exp+1)


    figure("Number of timepoints","runtime[s]", f"./since_plots/bench2/runtime_monpoly",2*exp)
    figure("Number of timepoints","memory usage[MiB]", f"./since_plots/bench2/memory",2*exp+1)

        


if __name__ == '__main__':
    bench1()
    bench2()





    